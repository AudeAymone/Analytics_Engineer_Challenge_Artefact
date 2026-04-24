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
6. Optional AI assistant consumption through a grounded question-answer layer.

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

The repository now includes one structured synthetic enrichment:

- `data/digital_events.csv`

This file simulates digital interaction events such as logins, transfers,
bill payments, password resets, and card-management actions across mobile
app and internet-banking channels.

It is used to derive:

- `nb_digital_events`
- `last_digital_event_date`
- `nb_digital_events_30d`
- `nb_failed_digital_events_30d`

These fields improve the credibility of the engagement view and make the
`Digital Activation` recommendation more explicit.

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

## AI Layer

The repository now includes a lightweight AI layer through `ai_assistant.py`.

Its role is to answer grounded business questions from the filtered
`customer_360` dataset inside the Streamlit dashboard.

Current design:

- the assistant builds a compact summary from the filtered portfolio
- it selects a small set of relevant customer rows
- it sends that grounded context to Ollama when a local model is available
- it falls back to local rule-based answers when no model server is available

This is not a full MCP server, but it is a practical AI interface aligned
with the optional AI objective of the brief.
