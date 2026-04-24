-- Builds the final Customer 360 model from customer-level features.
--
-- The output adds business-facing segmentation and action fields to
-- `customer_features` so the dataset can be used directly by analytics,
-- marketing, and retention teams.

CREATE OR REPLACE TABLE customer_360 AS
SELECT
    *,

    -- Classifies customers by financial value using balances and income.
    CASE
        WHEN total_balance_xof >= 5000000 OR monthly_income_xof >= 1500000 THEN 'High Value'
        WHEN total_balance_xof >= 1000000 OR monthly_income_xof >= 500000 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS customer_value_segment,

    -- Flags whether the customer uses at least one digital channel or recent digital event.
    CASE
        WHEN mobile_app_active = TRUE
          OR internet_banking_active = TRUE
          OR mobile_money_linked = TRUE
          OR nb_digital_events_30d > 0
        THEN TRUE
        ELSE FALSE
    END AS is_digital_engaged,

    -- Flags customers who have little or no recent digital activity.
    CASE
        WHEN COALESCE(nb_digital_events_30d, 0) = 0 THEN TRUE
        ELSE FALSE
    END AS is_digitally_dormant,

    -- Classifies customers based on transaction activity volume.
    CASE
        WHEN nb_transactions >= 10 THEN 'Active'
        WHEN nb_transactions BETWEEN 1 AND 9 THEN 'Low Activity'
        ELSE 'Inactive'
    END AS activity_status,

    -- Assigns a rule-based churn risk segment from service and behavior signals.
    CASE
        WHEN nb_high_severity_complaints > 0
          OR nb_negative_interactions >= 2
          OR nb_disputed_transactions > 0
          OR nb_transactions < 3
        THEN 'High Risk'

        WHEN nb_complaints > 0
          OR nb_negative_interactions = 1
          OR nb_transactions BETWEEN 3 AND 9
        THEN 'Medium Risk'

        ELSE 'Low Risk'
    END AS churn_risk_segment,

    -- Recommends the next best commercial or retention action.
    CASE
        WHEN nb_cards = 0 AND nb_transactions >= 5 THEN 'Card Offer'
        WHEN nb_loans = 0
          AND monthly_income_xof >= 500000
          AND max_days_past_due = 0
        THEN 'Personal Loan Offer'
        WHEN is_digitally_dormant = TRUE THEN 'Digital Activation'
        WHEN nb_complaints > 0 THEN 'Service Recovery'
        ELSE 'Savings / Loyalty Offer'
    END AS next_best_action

FROM customer_features;
