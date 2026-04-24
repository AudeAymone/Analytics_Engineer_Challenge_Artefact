"""Build and export the Customer 360 dataset.

This script runs the SQL pipeline that creates the source tables,
derives customer-level features, builds the final `customer_360` table,
exports the result to CSV, and prints a few validation queries.
"""

from pathlib import Path

import duckdb

DB_PATH = "databank.duckdb"
OUTPUT_PATH = Path("outputs/customer_360.csv")
SQL_FILES = [
    "sql/01_create_sources.sql",
    "sql/02_customer_features.sql",
    "sql/03_customer_360.sql",
]
VALIDATION_QUERIES = [
    ("Total customers", "SELECT COUNT(*) FROM customer_360"),
    (
        "Churn distribution",
        """
        SELECT churn_risk_segment, COUNT(*)
        FROM customer_360
        GROUP BY churn_risk_segment
        """,
    ),
    (
        "Next best actions",
        """
        SELECT next_best_action, COUNT(*)
        FROM customer_360
        GROUP BY next_best_action
        """,
    ),
]


def connect_database(database_path: str) -> duckdb.DuckDBPyConnection:
    """Return a connection to the local DuckDB database.

    Args:
        database_path: Path to the DuckDB database file.

    Returns:
        An active DuckDB connection.
    """
    return duckdb.connect(database_path)


def execute_sql_files(
    connection: duckdb.DuckDBPyConnection,
    sql_files: list[str],
) -> None:
    """Run the SQL files in order.

    Args:
        connection: Active DuckDB connection.
        sql_files: Ordered list of SQL file paths to execute.
    """
    for file_path in sql_files:
        print(f"Running {file_path}...")
        with open(file_path, "r", encoding="utf-8") as sql_file:
            connection.execute(sql_file.read())


def export_customer_360(
    connection: duckdb.DuckDBPyConnection,
    output_path: Path,
) -> None:
    """Export the final customer_360 table to CSV.

    Args:
        connection: Active DuckDB connection.
        output_path: Destination path for the exported CSV file.
    """
    output_path.parent.mkdir(exist_ok=True)
    connection.execute(
        f"""
        COPY customer_360
        TO '{output_path.as_posix()}'
        WITH (HEADER, DELIMITER ',');
        """
    )


def print_validation_queries(connection: duckdb.DuckDBPyConnection) -> None:
    """Run and print the validation queries.

    Args:
        connection: Active DuckDB connection.
    """
    print("\n--- VALIDATION ---")

    for name, query in VALIDATION_QUERIES:
        print(f"\n{name}")
        result = connection.execute(query).fetchall()
        for row in result:
            print(row)


def main() -> None:
    """Execute the full Customer 360 SQL pipeline."""
    connection = connect_database(DB_PATH)

    execute_sql_files(connection, SQL_FILES)
    export_customer_360(connection, OUTPUT_PATH)

    print(f"Done. {OUTPUT_PATH.name} created in {OUTPUT_PATH.parent}/")
    print_validation_queries(connection)


if __name__ == "__main__":
    main()
