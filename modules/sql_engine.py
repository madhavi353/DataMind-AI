
import duckdb
import sqlglot
from sqlglot import exp


def execute_query(df, query):
    """
    Execute a read-only SQL query against
    the uploaded Pandas DataFrame.
    """

    if not query or not query.strip():
        raise ValueError("Please enter a SQL query.")

    # Parse the SQL statement
    statements = sqlglot.parse(
        query,
        read="duckdb"
    )

    statements = [
        statement for statement in statements
        if statement is not None
    ]

    # Allow only one SQL statement
    if len(statements) != 1:
        raise ValueError(
            "Only one SQL statement is allowed."
        )

    statement = statements[0]

    # Allow only SELECT queries
    if not isinstance(statement, exp.Select):
        raise ValueError(
            "Only SELECT queries are permitted."
        )

    # Check referenced tables
    tables = list(statement.find_all(exp.Table))

    if not tables:
        raise ValueError(
            "Your query must use the uploaded_data table."
        )

    for table in tables:

        if (
            not isinstance(table.this, exp.Identifier)
            or table.name.lower() != "uploaded_data"
        ):
            raise ValueError(
                "You can query only the uploaded_data table."
            )

    # Connect to an in-memory DuckDB database
    connection = duckdb.connect(
        database=":memory:"
    )

    connection.execute(
        "SET enable_external_access = false"
    )

    try:

        # Register Pandas DataFrame as SQL table
        connection.register(
            "uploaded_data",
            df
        )

        # Execute SQL query
        result = connection.execute(
            query
        ).fetchdf()

        return result

    finally:
        connection.close()
