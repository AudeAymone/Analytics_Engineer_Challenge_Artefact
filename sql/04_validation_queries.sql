-- Validation query set for the final Customer 360 table.
--
-- These checks help confirm row counts, segment distributions, and a few
-- high-priority business slices after the model has been built.

-- Returns the total number of customers in the final model.
SELECT COUNT(*) AS total_customers
FROM customer_360;

-- Shows the distribution of customers across churn risk segments.
SELECT
    churn_risk_segment,
    COUNT(*) AS nb_customers
FROM customer_360
GROUP BY churn_risk_segment
ORDER BY nb_customers DESC;

-- Shows the distribution of recommended next best actions.
SELECT
    next_best_action,
    COUNT(*) AS nb_customers
FROM customer_360
GROUP BY next_best_action
ORDER BY nb_customers DESC;

-- Lists high-value customers with medium or high churn risk.
SELECT
    customer_id,
    full_name,
    city,
    total_balance_xof,
    monthly_income_xof,
    nb_transactions,
    nb_complaints,
    churn_risk_segment,
    next_best_action
FROM customer_360
WHERE customer_value_segment = 'High Value'
  AND churn_risk_segment IN ('High Risk', 'Medium Risk')
ORDER BY total_balance_xof DESC
LIMIT 20;

-- Lists top personal-loan cross-sell candidates.
SELECT
    customer_id,
    full_name,
    monthly_income_xof,
    total_balance_xof,
    nb_loans,
    max_days_past_due,
    next_best_action
FROM customer_360
WHERE next_best_action = 'Personal Loan Offer'
ORDER BY monthly_income_xof DESC
LIMIT 20;
