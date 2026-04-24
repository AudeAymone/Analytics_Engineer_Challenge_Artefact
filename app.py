"""Render the Customer 360 Streamlit dashboard.

The dashboard reads the exported `customer_360.csv` dataset and exposes
portfolio, risk, actionability, and individual customer views for
business users.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from ai_assistant import answer_question

DATA_PATH = "outputs/customer_360.csv"


def configure_page() -> None:
    """Configure the Streamlit page metadata."""
    st.set_page_config(page_title="dataBank CI Customer 360", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load the exported Customer 360 dataset.

    Returns:
        The Customer 360 dataset as a pandas DataFrame.
    """
    dataframe = pd.read_csv(DATA_PATH)
    dataframe["last_transaction_date"] = pd.to_datetime(
        dataframe["last_transaction_date"],
        errors="coerce",
    )
    dataframe["digital_engagement_label"] = dataframe["is_digital_engaged"].map(
        {True: "Digitally Engaged", False: "Not Digitally Engaged"},
    )
    dataframe["digital_engagement_label"] = dataframe[
        "digital_engagement_label"
    ].fillna("Unknown")
    return dataframe


def render_kpis(dataframe: pd.DataFrame) -> None:
    """Display the top-level portfolio KPIs.

    Args:
        dataframe: Full Customer 360 dataset.
    """
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Customers", len(dataframe))
    col2.metric("Total Balance XOF", f"{dataframe['total_balance_xof'].sum():,.0f}")
    col3.metric(
        "Avg Products / Customer",
        f"{(dataframe['nb_accounts'] + dataframe['nb_cards'] + dataframe['nb_loans']).mean():.2f}",
    )
    col4.metric(
        "High Risk Customers",
        len(dataframe[dataframe["churn_risk_segment"] == "High Risk"]),
    )


def render_filters(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Render sidebar filters and return the filtered dataset.

    Args:
        dataframe: Full Customer 360 dataset.

    Returns:
        Filtered Customer 360 dataset.
    """
    st.sidebar.header("Filters")

    risk_options = dataframe["churn_risk_segment"].dropna().unique()
    action_options = dataframe["next_best_action"].dropna().unique()

    risk_filter = st.sidebar.multiselect(
        "Churn Risk",
        options=risk_options,
        default=risk_options,
    )

    action_filter = st.sidebar.multiselect(
        "Next Best Action",
        options=action_options,
        default=action_options,
    )

    return dataframe[
        dataframe["churn_risk_segment"].isin(risk_filter)
        & dataframe["next_best_action"].isin(action_filter)
    ]


def render_portfolio_view(dataframe: pd.DataFrame) -> None:
    """Render the portfolio distribution charts.

    Args:
        dataframe: Filtered Customer 360 dataset.
    """
    st.header("1. Portfolio View")
    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            dataframe,
            x="customer_value_segment",
            title="Customers by Value Segment",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(
            dataframe,
            x="activity_status",
            title="Customers by Activity Status",
        )
        st.plotly_chart(fig, use_container_width=True)


def render_engagement_view(dataframe: pd.DataFrame) -> None:
    """Render engagement and channel-usage charts.

    Args:
        dataframe: Filtered Customer 360 dataset.
    """
    st.header("2. Engagement View")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            dataframe,
            x="preferred_channel",
            color="digital_engagement_label",
            barmode="group",
            title="Preferred Channel Mix",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(
            dataframe,
            x="digital_engagement_label",
            title="Digital Engagement Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        recency_df = (
            dataframe.dropna(subset=["last_transaction_date"])
            .assign(
                transaction_month=lambda df: df["last_transaction_date"].dt.to_period("M").astype(str)
            )
            .groupby("transaction_month", as_index=False)
            .size()
            .rename(columns={"size": "customer_count"})
        )

        fig = px.bar(
            recency_df,
            x="transaction_month",
            y="customer_count",
            title="Most Recent Transaction Month",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(
            dataframe,
            x="nb_transactions",
            y="nb_interactions",
            color="digital_engagement_label",
            size="nb_complaints",
            hover_data=["customer_id", "full_name", "preferred_channel"],
            title="Transactions vs Service Interactions",
        )
        st.plotly_chart(fig, use_container_width=True)


def render_risk_view(dataframe: pd.DataFrame) -> None:
    """Render churn-risk charts.

    Args:
        dataframe: Filtered Customer 360 dataset.
    """
    st.header("3. Retention / Risk Signals")
    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            dataframe,
            x="churn_risk_segment",
            title="Customers by Churn Risk",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(
            dataframe,
            x="nb_transactions",
            y="total_balance_xof",
            color="churn_risk_segment",
            hover_data=["customer_id", "full_name", "next_best_action"],
            title="Balance vs Transaction Activity",
        )
        st.plotly_chart(fig, use_container_width=True)


def render_next_best_action(dataframe: pd.DataFrame) -> None:
    """Render the next-best-action distribution chart.

    Args:
        dataframe: Filtered Customer 360 dataset.
    """
    st.header("4. Cross-sell / Upsell Opportunities")
    fig = px.histogram(
        dataframe,
        x="next_best_action",
        title="Next Best Action Distribution",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_priority_customers(dataframe: pd.DataFrame) -> None:
    """Render the high-priority customer table.

    Args:
        dataframe: Filtered Customer 360 dataset.
    """
    st.header("5. Priority Customers")

    priority_df = dataframe[
        (dataframe["customer_value_segment"] == "High Value")
        & (dataframe["churn_risk_segment"].isin(["High Risk", "Medium Risk"]))
    ].sort_values("total_balance_xof", ascending=False)

    st.dataframe(
        priority_df[
            [
                "customer_id",
                "full_name",
                "city",
                "total_balance_xof",
                "monthly_income_xof",
                "nb_transactions",
                "nb_complaints",
                "churn_risk_segment",
                "next_best_action",
            ]
        ],
        use_container_width=True,
    )


def render_customer_detail(dataframe: pd.DataFrame) -> None:
    """Render the individual customer view.

    Args:
        dataframe: Filtered Customer 360 dataset.
    """
    st.header("6. Individual Customer 360")

    customer = st.selectbox(
        "Select customer",
        dataframe["customer_id"].astype(str) + " - " + dataframe["full_name"].astype(str),
    )

    selected_id = customer.split(" - ")[0]
    customer_df = dataframe[dataframe["customer_id"].astype(str) == selected_id]

    if customer_df.empty:
        return

    customer_record = customer_df.iloc[0]
    col1, col2, col3 = st.columns(3)

    col1.metric("Value Segment", customer_record["customer_value_segment"])
    col2.metric("Churn Risk", customer_record["churn_risk_segment"])
    col3.metric("Next Best Action", customer_record["next_best_action"])

    st.write("### Customer Details")
    st.dataframe(customer_df.T, use_container_width=True)


def render_ai_assistant(dataframe: pd.DataFrame) -> None:
    """Render the grounded AI assistant section.

    Args:
        dataframe: Filtered Customer 360 dataset.
    """
    st.header("7. AI Assistant")
    st.write(
        "Ask a grounded business question about the filtered Customer 360 view. "
        "If Ollama is running locally, the dashboard uses it. "
        "Otherwise it falls back to local rule-based answers."
    )
    st.write("Suggested questions:")
    st.markdown(
        "- Which customers look healthy today but show early signs of churn?\n"
        "- Which customers should the bank prioritize for a personal loan offer?\n"
        "- Which customers should the bank prioritize for a card offer?\n"
        "- Why is this customer flagged as at-risk?\n"
        "- Why is this customer flagged as cross-sell eligible?\n"
        "- What additional data would most improve the quality of the Customer 360 recommendations?"
    )

    question = st.text_area(
        "Ask a question",
        value="Which customers look healthy today but show early signs of churn?",
        height=120,
    )

    if st.button("Ask the assistant", use_container_width=True):
        with st.spinner("Generating grounded answer..."):
            answer, mode = answer_question(dataframe, question)
        st.caption(f"Answer mode: {mode}")
        st.write(answer)


def main() -> None:
    """Run the Streamlit dashboard."""
    configure_page()
    dataframe = load_data()

    st.title("dataBank CI - Customer 360 Dashboard")
    render_kpis(dataframe)
    st.divider()

    filtered_df = render_filters(dataframe)
    render_portfolio_view(filtered_df)
    render_engagement_view(filtered_df)
    render_risk_view(filtered_df)
    render_next_best_action(filtered_df)
    render_priority_customers(filtered_df)
    render_customer_detail(filtered_df)
    render_ai_assistant(filtered_df)


if __name__ == "__main__":
    main()
