# Modeling Diagram

## Logical Model

The Customer 360 pipeline follows a layered analytical design:

- raw business entities are loaded from the Excel workbook
- customer-level features are aggregated in `customer_features`
- business-friendly segments and actions are derived in `customer_360`

## Mermaid Diagram

```mermaid
flowchart LR
    A[starter_dataset.xlsx] --> B[customers]
    A --> C[accounts]
    A --> D[transactions]
    A --> E[loans]
    A --> F[cards]
    A --> G[branches]
    A --> H[channels]
    A --> I[interactions]
    A --> J[complaints]
    A --> K[offers]

    B --> L[customer_features]
    C --> L
    D --> L
    E --> L
    F --> L
    I --> L
    J --> L
    K --> L

    L --> M[customer_360]
    M --> N[outputs/customer_360.csv]
    M --> O[Streamlit Dashboard]
```

## Modeling Notes

### Raw Layer

The raw layer mirrors the business entities delivered in the starter workbook.

### Feature Layer

`customer_features` aggregates customer metrics across products, transactions, service, and offers.

### Consumption Layer

`customer_360` adds the business-facing semantic layer:

- customer value segment
- digital engagement flag
- activity status
- churn-risk segment
- next best action

## Join Logic

The model uses `customer_id` as the primary integration key.

All feature aggregates are grouped by `customer_id` and then left-joined back to `customers`, ensuring one final row per customer.
