"""Provide a grounded AI assistant for the Customer 360 dataset.

The module builds a compact context from the current filtered dataframe and,
when Ollama is available locally, sends the question to the Ollama API.
A local fallback is provided so the dashboard remains usable even when no
model server is running.
"""

from __future__ import annotations

import os
from urllib import error, request
import json
import re

import pandas as pd
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
DEFAULT_OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def summarize_dataframe(dataframe: pd.DataFrame) -> str:
    """Build a compact business summary from the filtered dataset.

    Args:
        dataframe: Filtered Customer 360 dataset.

    Returns:
        A concise textual summary of the filtered portfolio.
    """
    if dataframe.empty:
        return "No customers match the current filters."

    high_risk_count = int((dataframe["churn_risk_segment"] == "High Risk").sum())
    digitally_dormant_count = int(dataframe.get("is_digitally_dormant", pd.Series(dtype=bool)).fillna(False).sum())
    top_actions = (
        dataframe["next_best_action"]
        .value_counts()
        .head(5)
        .to_dict()
    )
    top_channels = dataframe["preferred_channel"].value_counts().head(5).to_dict()

    return (
        f"Customers in scope: {len(dataframe)}\n"
        f"High-risk customers: {high_risk_count}\n"
        f"Digitally dormant customers: {digitally_dormant_count}\n"
        f"Average balance XOF: {dataframe['total_balance_xof'].mean():,.0f}\n"
        f"Average transactions: {dataframe['nb_transactions'].mean():.1f}\n"
        f"Top next best actions: {top_actions}\n"
        f"Top preferred channels: {top_channels}"
    )


def get_relevant_customers(dataframe: pd.DataFrame, question: str, limit: int = 8) -> pd.DataFrame:
    """Return a small set of relevant customer rows for grounding.

    Args:
        dataframe: Filtered Customer 360 dataset.
        question: User question submitted in the dashboard.
        limit: Maximum number of customer rows to include.

    Returns:
        A subset of customer rows relevant to the question.
    """
    if dataframe.empty:
        return dataframe

    lowered_question = question.lower()

    customer_id_match = dataframe[
        dataframe["customer_id"].astype(str).str.lower().eq(lowered_question.strip())
    ]
    if not customer_id_match.empty:
        return customer_id_match.head(limit)

    extracted_customer = extract_customer_match(dataframe, question)
    if extracted_customer is not None and not extracted_customer.empty:
        return extracted_customer.head(limit)

    if "healthy" in lowered_question and "churn" in lowered_question:
        return get_early_churn_candidates(dataframe).head(limit)

    if "high value" in lowered_question and "risk" in lowered_question:
        return dataframe[
            (dataframe["customer_value_segment"] == "High Value")
            & (dataframe["churn_risk_segment"].isin(["High Risk", "Medium Risk"]))
        ].sort_values("total_balance_xof", ascending=False).head(limit)

    if "loan" in lowered_question:
        return dataframe[dataframe["next_best_action"] == "Personal Loan Offer"].sort_values(
            "monthly_income_xof", ascending=False
        ).head(limit)

    if "card" in lowered_question:
        return dataframe[dataframe["next_best_action"] == "Card Offer"].sort_values(
            "nb_transactions", ascending=False
        ).head(limit)

    if "digital" in lowered_question:
        return dataframe.sort_values(
            ["is_digitally_dormant", "nb_failed_digital_events_30d"],
            ascending=[False, False],
        ).head(limit)

    if "complaint" in lowered_question or "risk" in lowered_question:
        return dataframe.sort_values(
            ["nb_complaints", "nb_negative_interactions", "nb_disputed_transactions"],
            ascending=False,
        ).head(limit)

    return dataframe.sort_values("total_balance_xof", ascending=False).head(limit)


def extract_customer_match(dataframe: pd.DataFrame, question: str) -> pd.DataFrame | None:
    """Extract a customer from the question using ID or full-name matching.

    Args:
        dataframe: Filtered Customer 360 dataset.
        question: User question.

    Returns:
        A matching customer slice when one customer is clearly referenced.
    """
    customer_id_search = re.search(r"\bC\d{4}\b", question, flags=re.IGNORECASE)
    if customer_id_search:
        customer_id = customer_id_search.group(0).upper()
        matches = dataframe[dataframe["customer_id"].astype(str).str.upper() == customer_id]
        if not matches.empty:
            return matches

    lowered_question = question.lower()
    name_matches = dataframe[
        dataframe["full_name"].astype(str).str.lower().apply(lambda name: name in lowered_question)
    ]
    if len(name_matches) == 1:
        return name_matches

    return None


def get_early_churn_candidates(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Return customers who still look commercially healthy but show churn signals.

    Args:
        dataframe: Filtered Customer 360 dataset.

    Returns:
        Customer rows ranked by early churn concern.
    """
    candidates = dataframe[
        (dataframe["customer_value_segment"].isin(["High Value", "Medium Value"]))
        & (dataframe["activity_status"].isin(["Active", "Low Activity"]))
        & (
            (dataframe["nb_complaints"] > 0)
            | (dataframe["nb_negative_interactions"] > 0)
            | (dataframe["nb_disputed_transactions"] > 0)
            | (dataframe["is_digitally_dormant"].fillna(False))
        )
    ].copy()

    if candidates.empty:
        return candidates

    candidates["early_churn_score"] = (
        candidates["nb_complaints"].fillna(0) * 3
        + candidates["nb_negative_interactions"].fillna(0) * 2
        + candidates["nb_disputed_transactions"].fillna(0) * 3
        + candidates["is_digitally_dormant"].fillna(False).astype(int) * 2
        + candidates["nb_failed_digital_events_30d"].fillna(0)
    )

    return candidates.sort_values(
        ["early_churn_score", "total_balance_xof", "nb_transactions"],
        ascending=[False, False, False],
    )


def explain_customer_flags(customer_row: pd.Series) -> str:
    """Explain why a customer is at risk or cross-sell eligible.

    Args:
        customer_row: One customer record from `customer_360`.

    Returns:
        A grounded explanation based on available rule inputs.
    """
    reasons: list[str] = []

    if customer_row["nb_high_severity_complaints"] > 0:
        reasons.append("has at least one high-severity complaint")
    elif customer_row["nb_complaints"] > 0:
        reasons.append(f"has {int(customer_row['nb_complaints'])} complaint(s)")

    if customer_row["nb_negative_interactions"] > 0:
        reasons.append(
            f"has {int(customer_row['nb_negative_interactions'])} negative interaction(s)"
        )

    if customer_row["nb_disputed_transactions"] > 0:
        reasons.append(
            f"has {int(customer_row['nb_disputed_transactions'])} disputed transaction(s)"
        )

    if customer_row["nb_transactions"] < 3:
        reasons.append("shows very low transaction activity")
    elif customer_row["activity_status"] == "Low Activity":
        reasons.append("shows lower-than-ideal activity")

    if bool(customer_row.get("is_digitally_dormant", False)):
        reasons.append("has no recent digital activity")

    action = customer_row["next_best_action"]
    action_explanation = {
        "Personal Loan Offer": (
            "is eligible for a personal loan because the customer has no active loan, "
            "has sufficient income, and has zero days past due"
        ),
        "Card Offer": "is eligible for a card offer because the customer has no card and is active",
        "Digital Activation": "is flagged for digital activation because recent digital activity is missing",
        "Service Recovery": "is flagged for service recovery because service-related issues are present",
        "Savings / Loyalty Offer": "is currently best suited for a savings or loyalty action",
    }.get(action, f"is currently tagged with `{action}`")

    reason_text = "; ".join(reasons) if reasons else "has no strong negative signal in the current filtered view"
    return (
        f"{customer_row['full_name']} ({customer_row['customer_id']}) is tagged as "
        f"`{customer_row['churn_risk_segment']}` because the customer {reason_text}. "
        f"The next best action is `{action}` because the model determined that the customer {action_explanation}."
    )


def build_prompt(dataframe: pd.DataFrame, question: str) -> str:
    """Build a grounded prompt from the filtered dataset and question.

    Args:
        dataframe: Filtered Customer 360 dataset.
        question: User question.

    Returns:
        Prompt text to send to the model.
    """
    summary = summarize_dataframe(dataframe)
    relevant_rows = get_relevant_customers(dataframe, question)
    columns = [
        "customer_id",
        "full_name",
        "customer_value_segment",
        "churn_risk_segment",
        "next_best_action",
        "preferred_channel",
        "nb_transactions",
        "total_balance_xof",
        "nb_complaints",
        "nb_negative_interactions",
        "nb_digital_events_30d",
        "nb_failed_digital_events_30d",
        "is_digitally_dormant",
    ]
    relevant_rows = relevant_rows[[column for column in columns if column in relevant_rows.columns]]

    return (
        "You are a grounded banking analytics assistant.\n"
        "Answer only from the provided dataset context.\n"
        "If the context is insufficient, say so explicitly.\n"
        "Keep the answer concise, business-oriented, and reference concrete fields when useful.\n\n"
        f"Portfolio summary:\n{summary}\n\n"
        f"Relevant customer rows:\n{relevant_rows.to_csv(index=False)}\n"
        f"User question: {question}"
    )


def answer_with_ollama(dataframe: pd.DataFrame, question: str) -> str:
    """Answer a question with a locally running Ollama model.

    Args:
        dataframe: Filtered Customer 360 dataset.
        question: User question.

    Returns:
        The model answer.

    Raises:
        RuntimeError: If the Ollama call fails.
    """
    payload = json.dumps(
        {
            "model": DEFAULT_OLLAMA_MODEL,
            "prompt": build_prompt(dataframe, question),
            "stream": False,
        }
    ).encode("utf-8")
    ollama_request = request.Request(
        url=f"{DEFAULT_OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(ollama_request, timeout=120) as response:
            body = json.loads(response.read().decode("utf-8"))
    except error.URLError as exc:
        raise RuntimeError(f"Ollama request failed: {exc}") from exc

    answer = body.get("response", "").strip()
    if not answer:
        raise RuntimeError("Ollama returned an empty response.")
    return answer


def answer_with_local_fallback(dataframe: pd.DataFrame, question: str) -> str:
    """Return a deterministic local answer when API access is unavailable.

    Args:
        dataframe: Filtered Customer 360 dataset.
        question: User question.

    Returns:
        A short grounded answer from local logic.
    """
    if dataframe.empty:
        return "No customers match the current filters, so there is no grounded answer to return."

    lowered_question = question.lower()

    if "healthy" in lowered_question and "churn" in lowered_question:
        candidates = get_early_churn_candidates(dataframe).head(5)
        if candidates.empty:
            return "No customers in the current filtered view match the profile of healthy customers with early churn signs."
        summary = ", ".join(
            f"{row.full_name} ({row.customer_value_segment}, {row.activity_status}, {row.churn_risk_segment})"
            for row in candidates.itertuples()
        )
        return (
            "The customers that still look commercially healthy but already show early churn signals are "
            f"{summary}. They remain valuable or active, but they also show complaints, negative interactions, "
            "disputes, or digital dormancy."
        )

    if "why is this customer" in lowered_question or "explain why" in lowered_question:
        customer_match = extract_customer_match(dataframe, question)
        if customer_match is not None and not customer_match.empty:
            return explain_customer_flags(customer_match.iloc[0])
        return (
            "To explain one customer precisely, include a `customer_id` such as `C0002` "
            "or the exact customer name in your question."
        )

    if "high-value" in lowered_question or "high value" in lowered_question:
        customers = dataframe[
            (dataframe["customer_value_segment"] == "High Value")
            & (dataframe["churn_risk_segment"].isin(["High Risk", "Medium Risk"]))
        ].sort_values("total_balance_xof", ascending=False).head(5)
        if customers.empty:
            return "No high-value at-risk customers were found in the current filtered view."
        names = ", ".join(customers["full_name"].tolist())
        return (
            f"The highest-priority high-value at-risk customers in the current view are {names}. "
            "They are flagged by the combination of `customer_value_segment` and `churn_risk_segment`."
        )

    if "loan" in lowered_question:
        count = int((dataframe["next_best_action"] == "Personal Loan Offer").sum())
        return (
            f"There are {count} customers currently tagged with `Personal Loan Offer` in the filtered view. "
            "The rule uses no active loan, sufficient income, and zero days past due."
        )

    if "digital" in lowered_question:
        dormant_count = int(dataframe["is_digitally_dormant"].fillna(False).sum())
        failed_events = int(dataframe["nb_failed_digital_events_30d"].sum())
        return (
            f"There are {dormant_count} digitally dormant customers in the current view, "
            f"with {failed_events} failed digital events in the last 30 days. "
            "This supports digital activation and service-friction analysis."
        )

    if "complaint" in lowered_question or "risk" in lowered_question:
        customer_match = extract_customer_match(dataframe, question)
        if customer_match is not None and not customer_match.empty:
            return explain_customer_flags(customer_match.iloc[0])

        high_risk = int((dataframe["churn_risk_segment"] == "High Risk").sum())
        complaints = int(dataframe["nb_complaints"].sum())
        return (
            f"The current filtered view contains {high_risk} high-risk customers and {complaints} total complaints. "
            "The churn-risk logic is driven by complaints, negative interactions, disputed transactions, and low activity."
        )

    return (
        "The local fallback can answer broad grounded questions about high-value at-risk customers, "
        "loan opportunities, digital dormancy, and complaint-driven churn signals. "
        "Start Ollama locally to enable free-form model answers."
    )


def answer_question(dataframe: pd.DataFrame, question: str) -> tuple[str, str]:
    """Answer a dashboard question with Ollama or a local fallback.

    Args:
        dataframe: Filtered Customer 360 dataset.
        question: User question.

    Returns:
        A tuple containing the answer text and the mode used.
    """
    try:
        return answer_with_ollama(dataframe, question), f"Ollama ({DEFAULT_OLLAMA_MODEL})"
    except Exception:
        return answer_with_local_fallback(dataframe, question), "Local fallback"
