-- Builds customer-level aggregated features from the raw source tables.
--
-- The output table has one row per customer and combines profile fields from
-- `customers` with summarized account, transaction, loan, card, complaint,
-- interaction, and offer metrics.

CREATE OR REPLACE TABLE customer_features AS
WITH account_features AS (
    -- Aggregates account ownership, balances, and salary domiciliation flags.
    SELECT
        customer_id,
        COUNT(*) AS nb_accounts,
        SUM(current_balance_xof) AS total_balance_xof,
        AVG(avg_balance_90d_xof) AS avg_balance_90d_xof,
        MAX(CASE WHEN salary_domiciled_flag THEN 1 ELSE 0 END) AS has_salary_domiciliation
    FROM accounts
    GROUP BY customer_id
),

transaction_features AS (
    -- Aggregates transaction activity, recency, disputes, inflows, and outflows.
    SELECT
        customer_id,
        COUNT(*) AS nb_transactions,
        SUM(amount_xof) AS total_transaction_amount_xof,
        MAX(txn_datetime) AS last_transaction_date,
        SUM(CASE WHEN is_disputed THEN 1 ELSE 0 END) AS nb_disputed_transactions,
        SUM(CASE WHEN direction = 'OUT' THEN amount_xof ELSE 0 END) AS total_outflow_xof,
        SUM(CASE WHEN direction = 'IN' THEN amount_xof ELSE 0 END) AS total_inflow_xof
    FROM transactions
    GROUP BY customer_id
),

loan_features AS (
    -- Aggregates loan exposure and delinquency indicators.
    SELECT
        customer_id,
        COUNT(*) AS nb_loans,
        SUM(outstanding_balance_xof) AS total_loan_balance_xof,
        MAX(days_past_due) AS max_days_past_due
    FROM loans
    GROUP BY customer_id
),

card_features AS (
    -- Aggregates card ownership, recent spend, and e-commerce capability.
    SELECT
        customer_id,
        COUNT(*) AS nb_cards,
        SUM(monthly_spend_90d_xof) AS card_spend_90d_xof,
        MAX(CASE WHEN ecommerce_enabled THEN 1 ELSE 0 END) AS ecommerce_enabled
    FROM cards
    GROUP BY customer_id
),

complaint_features AS (
    -- Aggregates complaint volume and severity signals.
    SELECT
        customer_id,
        COUNT(*) AS nb_complaints,
        SUM(CASE WHEN severity = 'High' THEN 1 ELSE 0 END) AS nb_high_severity_complaints,
        MAX(opened_date) AS last_complaint_date
    FROM complaints
    GROUP BY customer_id
),

interaction_features AS (
    -- Aggregates customer interaction volume and negative sentiment.
    SELECT
        customer_id,
        COUNT(*) AS nb_interactions,
        SUM(CASE WHEN sentiment = 'Negative' THEN 1 ELSE 0 END) AS nb_negative_interactions
    FROM interactions
    GROUP BY customer_id
),

offer_features AS (
    -- Aggregates outbound commercial offers and accepted offers.
    SELECT
        customer_id,
        COUNT(*) AS nb_offers,
        SUM(CASE WHEN accepted_flag THEN 1 ELSE 0 END) AS nb_accepted_offers,
        SUM(expected_value_xof) AS total_expected_offer_value_xof
    FROM offers
    GROUP BY customer_id
)

-- Combines customer profile fields with all aggregated feature sets.
SELECT
    c.customer_id,
    c.full_name,
    c.city,
    c.district,
    c.occupation,
    c.segment,
    c.monthly_income_xof,
    c.preferred_channel,
    c.mobile_app_active,
    c.internet_banking_active,
    c.mobile_money_linked,
    c.risk_band,
    c.marketing_opt_in,

    COALESCE(a.nb_accounts, 0) AS nb_accounts,
    COALESCE(a.total_balance_xof, 0) AS total_balance_xof,
    COALESCE(a.avg_balance_90d_xof, 0) AS avg_balance_90d_xof,
    COALESCE(a.has_salary_domiciliation, 0) AS has_salary_domiciliation,

    COALESCE(t.nb_transactions, 0) AS nb_transactions,
    COALESCE(t.total_transaction_amount_xof, 0) AS total_transaction_amount_xof,
    t.last_transaction_date,
    COALESCE(t.nb_disputed_transactions, 0) AS nb_disputed_transactions,

    COALESCE(l.nb_loans, 0) AS nb_loans,
    COALESCE(l.total_loan_balance_xof, 0) AS total_loan_balance_xof,
    COALESCE(l.max_days_past_due, 0) AS max_days_past_due,

    COALESCE(cd.nb_cards, 0) AS nb_cards,
    COALESCE(cd.card_spend_90d_xof, 0) AS card_spend_90d_xof,
    COALESCE(cd.ecommerce_enabled, 0) AS ecommerce_enabled,

    COALESCE(cp.nb_complaints, 0) AS nb_complaints,
    COALESCE(cp.nb_high_severity_complaints, 0) AS nb_high_severity_complaints,

    COALESCE(i.nb_interactions, 0) AS nb_interactions,
    COALESCE(i.nb_negative_interactions, 0) AS nb_negative_interactions,

    COALESCE(o.nb_offers, 0) AS nb_offers,
    COALESCE(o.nb_accepted_offers, 0) AS nb_accepted_offers,
    COALESCE(o.total_expected_offer_value_xof, 0) AS total_expected_offer_value_xof

FROM customers c
LEFT JOIN account_features a USING (customer_id)
LEFT JOIN transaction_features t USING (customer_id)
LEFT JOIN loan_features l USING (customer_id)
LEFT JOIN card_features cd USING (customer_id)
LEFT JOIN complaint_features cp USING (customer_id)
LEFT JOIN interaction_features i USING (customer_id)
LEFT JOIN offer_features o USING (customer_id);
