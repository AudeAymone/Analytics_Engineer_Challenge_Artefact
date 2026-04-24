# dataBank CI - Customer 360 Analytics Challenge

## Overview

This project builds a `customer_360` analytical dataset for a retail bank using DuckDB and SQL.

The objective is to:

- consolidate customer, account, transaction, loan, card, complaint, interaction, and offer data
- create customer-level features
- derive business segments such as value, activity, digital engagement, churn risk, and next best action
- export the final model to CSV for analysis and dashboarding

## Repository Structure

| Path | Description |
|---|---|
| `databank.duckdb` | DuckDB database file containing all raw tables |
| `sql/01_create_sources.sql` | Creates source tables from the DuckDB database |
| `sql/02_customer_features.sql` | Builds customer-level aggregated features |
| `sql/03_customer_360.sql` | Builds the final `customer_360` model with derived business rules |
| `sql/04_validation_queries.sql` | Example validation and business review queries |
| `run_sql.py` | Executes the SQL pipeline and exports `outputs/customer_360.csv` |
| `app.py` | Streamlit dashboard for exploring the final dataset |
| `requirements.txt` | Python dependencies for the project virtual environment |
| `data/semantic_layer.md` | Business definitions for the model |
| `data/data_dictionary.md` | Field-by-field documentation for `customer_360` |
| `data/recommendations.md` | Business recommendations based on the model |
| `outputs/customer_360.csv` | Final exported dataset |

## Data Model

The final table is `customer_360` at `one row per customer`.

It contains three types of information:

- customer profile fields from the source `customers` table
- aggregated metrics derived from accounts, transactions, loans, cards, complaints, interactions, and offers
- business-facing derived fields such as `customer_value_segment`, `activity_status`, `churn_risk_segment`, and `next_best_action`

## Main Business Logic

The model includes rule-based segmentation:

- `customer_value_segment`: classifies customers into `High Value`, `Medium Value`, or `Low Value`
- `is_digital_engaged`: identifies whether the customer uses at least one digital channel
- `activity_status`: classifies customers based on transaction volume
- `churn_risk_segment`: flags customers with service, behavior, or dispute-related churn risk signals
- `next_best_action`: recommends the most relevant retention or commercial action

Full definitions are documented in [`data/semantic_layer.md`](data/semantic_layer.md) and [`data/data_dictionary.md`](data/data_dictionary.md).

## How To Run

### 1. Create the virtual environment

```bash
python -m venv .venv
```

### 2. Activate the virtual environment in Bash

```bash
source .venv/Scripts/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the SQL pipeline

```bash
python run_sql.py
```

This script:

- loads the Excel workbook into DuckDB
- creates `customer_features`
- creates `customer_360`
- exports the final dataset to `outputs/customer_360.csv`
- prints a few validation summaries in the console

## Dashboard

To launch the Streamlit dashboard:

```bash
streamlit run app.py
```

You can also access the deployed dashboard here:

[Customer 360 Dashboard](https://analyticsengineerchallengeartefact-4e5qq4dehxfwj3kuztvdwm.streamlit.app/)


The dashboard provides:

- high-level KPIs
- filters on churn risk and next best action
- portfolio and risk charts
- a priority customer list
- an individual customer 360 view

## Validation

Example validation queries are available in [`sql/04_validation_queries.sql`](c:\Users\audea\Downloads\Analytics engineer challenge\sql\04_validation_queries.sql:1).

They cover:

- total customer count
- churn risk distribution
- next best action distribution
- high-value at-risk customers
- personal loan opportunity candidates

## Documentation

- [`docs/semantic_layer.md`](c:\Users\audea\Downloads\Analytics engineer challenge\docs\semantic_layer.md:1): business definitions and semantic logic
- [`docs/data_dictionary.md`](c:\Users\audea\Downloads\Analytics engineer challenge\docs\data_dictionary.md:1): field dictionary for the final model
- [`docs/recommendations.md`](c:\Users\audea\Downloads\Analytics engineer challenge\docs\recommendations.md:1): business recommendations and suggested actions

## Current Output

The repository already contains an exported file at [`outputs/customer_360.csv`](c:\Users\audea\Downloads\Analytics engineer challenge\outputs\customer_360.csv:1), generated from the current model.

## Notes

- Currency amounts are expressed in `XOF`.
- The transformation logic is rule-based and intended for an analytics challenge, not a production scoring engine.

