# Customer 360 Analytics for dataBank CI

Customer 360 analytics project for dataBank CI using DuckDB, SQL, and Streamlit to build customer features, churn-risk segments, and next-best-action recommendations.

## Overview

This repository builds a customer-level analytical model from a banking dataset stored in Excel.

The project:

- loads raw banking data into DuckDB
- aggregates customer-level features across accounts, transactions, loans, cards, complaints, interactions, and offers
- creates a final `customer_360` model
- exports the result as a CSV file
- provides a Streamlit dashboard for business exploration
- documents the semantic layer, field definitions, and business recommendations

## Repository Structure

| Path | Description |
|---|---|
| `data/starter_dataset.xlsx` | Source workbook used to create the raw tables |
| `sql/01_create_sources.sql` | Loads each Excel sheet into DuckDB source tables |
| `sql/02_customer_features.sql` | Builds aggregated customer-level features |
| `sql/03_customer_360.sql` | Builds the final Customer 360 model |
| `sql/04_validation_queries.sql` | Validation and business review queries |
| `run_sql.py` | Runs the SQL pipeline and exports the final CSV |
| `app.py` | Streamlit dashboard for the final dataset |
| `requirements.txt` | Python dependencies |
| `docs/semantic_layer.md` | Business definitions and semantic rules |
| `docs/data_dictionary.md` | Field-by-field dictionary for `customer_360` |
| `docs/recommendations.md` | Business recommendations based on the model |
| `docs/architecture_and_assumptions.md` | Architecture choices, assumptions, limitations, and next steps |
| `docs/modeling_diagram.md` | Logical modeling diagram of the pipeline |
| `outputs/customer_360.csv` | Final exported dataset |

## Data Model

The final table is `customer_360`, with `one row per customer`.

It combines:

- customer profile attributes
- product ownership and balance indicators
- transaction behavior and dispute signals
- loan exposure and delinquency metrics
- card usage metrics
- complaint and interaction signals
- commercial offer metrics
- derived business segments and recommended actions

## Core Derived Fields

The final model includes five main business-facing fields:

- `customer_value_segment`
- `is_digital_engaged`
- `activity_status`
- `churn_risk_segment`
- `next_best_action`

These rules are documented in [docs/semantic_layer.md](docs/semantic_layer.md) and detailed field definitions are available in [docs/data_dictionary.md](docs/data_dictionary.md).

## Setup

### 1. Create a virtual environment

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

## Run the Pipeline

```bash
python run_sql.py
```

The script:

- connects to the local DuckDB database
- executes the SQL models in order
- exports `customer_360` to `outputs/customer_360.csv`
- prints validation summaries in the console

## Launch the Dashboard

```bash
streamlit run app.py
```

You can also access the deployed dashboard here:

[Customer 360 Dashboard](https://analyticsengineerchallengeartefact-4e5qq4dehxfwj3kuztvdwm.streamlit.app/)

The dashboard includes:

- portfolio KPIs
- engagement and channel-usage views
- churn-risk and next-best-action filters
- customer segment distributions
- risk analysis charts
- priority customer views
- an individual customer 360 drill-down

## Validation

Example validation queries are available in [sql/04_validation_queries.sql](sql/04_validation_queries.sql).

They help review:

- total customer volume
- churn risk distribution
- next-best-action distribution
- high-value at-risk customers
- personal-loan opportunity candidates

## Documentation

- [docs/semantic_layer.md](docs/semantic_layer.md)
- [docs/data_dictionary.md](docs/data_dictionary.md)
- [docs/recommendations.md](docs/recommendations.md)
- [docs/architecture_and_assumptions.md](docs/architecture_and_assumptions.md)
- [docs/modeling_diagram.md](docs/modeling_diagram.md)

## Notes

- All monetary amounts are expressed in `XOF`.
- The model is rule-based and designed for analytics and business review.
- The Bash activation command above is intended for Git Bash or a similar Bash shell on Windows.
