# Semantic Layer - Customer 360

## Purpose

The semantic layer translates the `customer_360` model into business language.
It defines the main entities, the derived indicators, and the decision rules used by business teams to interpret the data consistently.

## Core Entities

### Customer
A unique individual identified by `customer_id`.

### Account
A banking account linked to a customer. Accounts contribute to balance and salary domiciliation metrics.

### Transaction
A financial movement associated with a customer. Transactions are used to measure activity, inflows, outflows, and disputes.

### Loan
A credit product linked to a customer. Loans contribute to exposure and delinquency indicators.

### Card
A payment card linked to a customer. Cards contribute to card ownership and card spend metrics.

### Interaction
A customer contact with the bank across service or relationship channels. Interactions are used to derive engagement and negative sentiment signals.

### Complaint
A formal issue reported by the customer. Complaints are part of the churn-risk logic.

### Offer
A commercial proposal sent to the customer. Offers are used to track commercial activity and acceptance.

## Grain Of The Model

The `customer_360` table is at `one row per customer`.

Each row combines:

- customer profile attributes from `customers`
- aggregated account, transaction, loan, card, complaint, interaction, and offer features
- business-facing derived segments and recommended actions

## Key Base Metrics

The semantic layer relies on the following aggregated metrics from `customer_features`:

| Field | Definition |
|---|---|
| `nb_accounts` | Number of accounts held by the customer |
| `total_balance_xof` | Sum of current account balances |
| `avg_balance_90d_xof` | Average account balance over the last 90 days |
| `has_salary_domiciliation` | Flag indicating at least one salary-domiciled account |
| `nb_transactions` | Total number of transactions |
| `total_transaction_amount_xof` | Sum of all transaction amounts |
| `last_transaction_date` | Most recent transaction date |
| `nb_disputed_transactions` | Count of disputed transactions |
| `nb_loans` | Number of loans |
| `total_loan_balance_xof` | Sum of outstanding loan balances |
| `max_days_past_due` | Maximum number of days past due across loans |
| `nb_cards` | Number of cards |
| `card_spend_90d_xof` | Total card spend over 90 days |
| `ecommerce_enabled` | Flag indicating at least one e-commerce-enabled card |
| `nb_complaints` | Total number of complaints |
| `nb_high_severity_complaints` | Number of high-severity complaints |
| `nb_interactions` | Total number of customer interactions |
| `nb_negative_interactions` | Number of interactions with negative sentiment |
| `nb_offers` | Total number of offers sent |
| `nb_accepted_offers` | Number of accepted offers |
| `total_expected_offer_value_xof` | Sum of expected offer value |

## Derived Business Definitions

### Activity Status

The field `activity_status` classifies customers based on transaction volume:

| Segment | Rule |
|---|---|
| `Active` | `nb_transactions >= 10` |
| `Low Activity` | `nb_transactions BETWEEN 1 AND 9` |
| `Inactive` | `nb_transactions = 0` |

### Customer Value Segment

The field `customer_value_segment` classifies customers using balance and income:

| Segment | Rule |
|---|---|
| `High Value` | `total_balance_xof >= 5000000 OR monthly_income_xof >= 1500000` |
| `Medium Value` | `total_balance_xof >= 1000000 OR monthly_income_xof >= 500000` |
| `Low Value` | all remaining customers |

### Digital Engagement

The field `is_digital_engaged` is `TRUE` when the customer uses at least one digital channel:

```text
mobile_app_active = TRUE
OR internet_banking_active = TRUE
OR mobile_money_linked = TRUE
```

### Churn Risk Segment

The field `churn_risk_segment` is a rule-based risk classification:

| Segment | Rule |
|---|---|
| `High Risk` | `nb_high_severity_complaints > 0 OR nb_negative_interactions >= 2 OR nb_disputed_transactions > 0 OR nb_transactions < 3` |
| `Medium Risk` | `nb_complaints > 0 OR nb_negative_interactions = 1 OR nb_transactions BETWEEN 3 AND 9` |
| `Low Risk` | all remaining customers |

## Next Best Action Logic

The field `next_best_action` provides a simple commercial or retention recommendation:

| Next best action | Rule | Business meaning |
|---|---|---|
| `Card Offer` | `nb_cards = 0 AND nb_transactions >= 5` | Customer is active but does not yet hold a card |
| `Personal Loan Offer` | `nb_loans = 0 AND monthly_income_xof >= 500000 AND max_days_past_due = 0` | Customer may qualify for a loan and shows no delinquency |
| `Digital Activation` | `is_digital_engaged = FALSE` | Customer should be encouraged to adopt digital channels |
| `Service Recovery` | `nb_complaints > 0` | Customer may require service follow-up before sales activation |
| `Savings / Loyalty Offer` | fallback rule | Stable customer with no more urgent need detected |

## Example Business Audiences

### Relationship Managers
Use the model to identify high-value customers with elevated churn risk.

### Marketing Teams
Use `next_best_action` and product ownership gaps to target campaigns.

### Customer Service Teams
Use complaint and negative interaction indicators as early warning signals.

### Management
Use the model as a common customer health and opportunity view across teams.

## Notes And Limitations

- This semantic layer is rule-based, not predictive.
- Thresholds are business assumptions and should be validated against historical outcomes.
- The model currently focuses on customer-level aggregation rather than account-level behavioral sequences.
- Some derived fields depend on source data quality, especially complaints, sentiment, and delinquency fields.
