# Business Recommendations — dataBank CI Customer 360

## 1. Executive summary

dataBank CI should use the Customer 360 model to prioritize three actions:

1. Retain high-value customers showing churn risk signals.
2. Increase product adoption through targeted card, loan, and savings offers.
3. Accelerate digital activation for customers with low mobile or internet banking usage.

## 2. Priority 1 — Retain high-value at-risk customers

Customers tagged as `High Value` and `High Risk` should be handled first.

Recommended actions:
- assign them to relationship managers
- contact them within a short delay
- review recent complaints or disputed transactions
- offer fee waivers, service recovery, or loyalty benefits

## 3. Priority 2 — Push next best actions

The `next_best_action` field helps business teams decide what to offer:

| Next best action | Business meaning |
|---|---|
| Card Offer | Active customer without card |
| Personal Loan Offer | Good income, no active loan, low delinquency |
| Digital Activation | Customer not using mobile or internet banking |
| Service Recovery | Customer with complaints or negative interactions |
| Savings / Loyalty Offer | Stable customer with no urgent risk |

## 4. Priority 3 — Improve digital engagement

Customers without mobile app, internet banking, or mobile money usage should receive digital activation campaigns.

Expected impact:
- more frequent engagement
- lower branch dependency
- better retention
- more data for personalization

## 5. Priority 4 — Use complaints as churn signals

Complaints and negative interactions should not be treated only as support issues.

They should feed the churn risk model because they reveal dissatisfaction.

## 6. Next steps

Recommended next improvements:
- add salary history
- add mobile login events
- add campaign history
- add customer satisfaction score
- improve churn scoring with historical behavior
- connect the Customer 360 table to a dashboard