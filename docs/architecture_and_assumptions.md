# Architecture And Assumptions

## Objective

The goal of this project is to build a reusable Customer 360 foundation for dataBank CI.

The model is designed to help business teams answer three practical questions:

- which customers show early churn-risk signals
- which customers should receive the next best offer
- which customers need digital activation or service recovery

## Architecture Overview

The repository follows a simple analytics flow:

1. Raw source ingestion from the Excel workbook into DuckDB tables.
2. Customer-level feature aggregation in `customer_features`.
3. Business-rule enrichment in `customer_360`.
4. CSV export for downstream consumption.
5. Dashboard consumption through Streamlit.

## Modeling Choice

The project uses a hybrid customer-centric analytical model.

It is not a full star schema and not a formal Data Vault implementation.
Instead, it follows a pragmatic layered approach:

- raw source tables preserve the starter entities
- `customer_features` acts as an analytical feature layer
- `customer_360` acts as the business-facing semantic consumption layer

This design was chosen because it fits the scope of the challenge:

- it is easy to understand and review quickly
- it supports one-row-per-customer analytics directly
- it keeps the SQL simple enough for rapid iteration
- it is sufficient for dashboarding and decision support

## Semantic Layer Mapping

Business language is mapped to physical fields through derived rules in `customer_360`.

Examples:

- `Active customer` maps to `nb_transactions >= 10`
- `Digitally engaged customer` maps to mobile app, internet banking, or mobile money usage
- `High-value customer` maps to balance and income thresholds
- `At-risk customer` maps to complaints, negative interactions, disputes, and low activity
- `Cross-sell eligible customer` maps to product gaps and rule-based next-best-action logic

## Assumptions

The following assumptions were made in the current implementation:

- the provided Excel workbook is the main trusted source for the challenge
- each `customer_id` uniquely identifies one customer
- transaction count is a sufficient proxy for customer activity in the absence of richer behavioral history
- current balance and declared income are acceptable proxies for customer value
- complaints, negative interactions, and disputed transactions are valid early churn indicators
- rule-based segmentation is acceptable for this challenge even without historical outcome labels

## Missing Data And Potential Enrichment

The starter dataset is sufficient to build a baseline Customer 360, but several data points are still missing for a more credible production-grade view.

Examples of useful enrichment:

- salary payment history over time
- digital login frequency and recency
- campaign delivery and campaign response history
- customer satisfaction or NPS signals
- branch visit history
- product closure events
- repayment history by installment
- complaint text or call-center notes for unstructured analysis

No additional synthetic data was materially added in the current repository.
Instead, the project documents recommended enrichments and uses rule-based logic on the available dataset.

## Business KPIs Covered

The current model supports the following KPI families:

- active vs inactive customers
- number of products per customer
- balance depth
- transaction activity
- digital adoption
- complaint intensity
- delinquency flags
- offer volume and offer acceptance
- next-best-action distribution

## Limitations

The current version has a few important limitations:

- it is rule-based rather than predictive
- it does not include time-series behavior modeling
- it does not track historical snapshots of customer state
- it does not include a formal ontology or inference engine
- it does not expose the dataset through MCP or another AI tool layer
- some dashboard areas are lighter than the brief’s ideal target, especially deeper engagement analytics

## Next Steps

The most valuable next improvements would be:

1. Add richer engagement data such as recency, frequency, and digital event history.
2. Add a modeling snapshot or history layer to compare customer evolution over time.
3. Add a formal modeling diagram and, if needed, evolve the structure toward a star schema.
4. Introduce inferred business classes such as `High-Value At-Risk Customer`.
5. Add unstructured service data for complaint theme analysis.
6. Expose the modeled data to an assistant through MCP or a lightweight API layer.
