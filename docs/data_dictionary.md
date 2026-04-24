# Data Dictionary — Customer 360

## Overview

This document describes the structure and business meaning of the Customer 360 dataset.

Each row represents one customer.

---

## Table: customer_360

### Identifiers

| Column | Description |
|------|-------------|
| customer_id | Unique identifier of the customer |
| full_name | Customer full name |

---

### Customer Profile

| Column | Description |
|------|-------------|
| city | Customer city |
| district | Customer district |
| occupation | Customer occupation |
| segment | Original segmentation from source data |
| monthly_income_xof | Estimated monthly income |
| preferred_channel | Preferred banking channel |

---

### Digital Usage

| Column | Description |
|------|-------------|
| mobile_app_active | Whether the customer uses mobile app |
| internet_banking_active | Whether the customer uses internet banking |
| mobile_money_linked | Whether mobile money is linked |
| nb_digital_events | Number of synthetic digital events available for the customer |
| last_digital_event_date | Most recent synthetic digital event date |
| nb_digital_events_30d | Number of digital events in the last 30 days |
| nb_failed_digital_events_30d | Number of failed digital events in the last 30 days |
| is_digital_engaged | Derived flag indicating digital usage |
| is_digitally_dormant | Derived flag indicating no recent digital activity |

---

### Accounts & Financials

| Column | Description |
|------|-------------|
| nb_accounts | Number of accounts |
| total_balance_xof | Total balance across accounts |
| avg_balance_90d_xof | Average balance over last 90 days |
| has_salary_domiciliation | Salary deposited into account |

---

### Transactions

| Column | Description |
|------|-------------|
| nb_transactions | Number of transactions |
| total_transaction_amount_xof | Total transaction volume |
| last_transaction_date | Most recent transaction |
| nb_disputed_transactions | Number of disputed transactions |

---

### Loans

| Column | Description |
|------|-------------|
| nb_loans | Number of active loans |
| total_loan_balance_xof | Total outstanding loan balance |
| max_days_past_due | Maximum delay in repayment |

---

### Cards

| Column | Description |
|------|-------------|
| nb_cards | Number of cards |
| card_spend_90d_xof | Card spending over 90 days |
| ecommerce_enabled | Whether e-commerce is enabled |

---

### Interactions & Complaints

| Column | Description |
|------|-------------|
| nb_interactions | Number of interactions with bank |
| nb_negative_interactions | Number of negative interactions |
| nb_complaints | Number of complaints |
| nb_high_severity_complaints | High severity complaints |

---

### Offers

| Column | Description |
|------|-------------|
| nb_offers | Number of offers received |
| nb_accepted_offers | Number of accepted offers |
| total_expected_offer_value_xof | Expected value of offers |

---

## Derived Business Fields

### Customer Value Segment

| Value | Definition |
|------|------------|
| High Value | High balance or high income |
| Medium Value | Medium balance or income |
| Low Value | Other customers |

---

### Activity Status

| Value | Definition |
|------|------------|
| Active | ≥ 10 transactions |
| Low Activity | 1–9 transactions |
| Inactive | 0 transactions |

---

### Churn Risk Segment

| Value | Definition |
|------|------------|
| High Risk | Complaints, disputes, or low activity |
| Medium Risk | Some signals of disengagement |
| Low Risk | Healthy customer |

---

### Next Best Action

| Value | Meaning |
|------|---------|
| Card Offer | Customer has no card but is active |
| Personal Loan Offer | Eligible for loan |
| Digital Activation | Not using digital channels |
| Service Recovery | Complaints or negative signals |
| Savings / Loyalty Offer | Stable customer |

---

## Notes

- All monetary values are in XOF (West African CFA Franc).
- Derived fields are computed using business rules defined in the SQL model.
- The dataset is designed for analytics, dashboarding, and decision-making.
