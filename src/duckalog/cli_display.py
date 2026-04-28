"""CLI display helpers for Duckalog.

Extracted from cli.py to keep the command definitions separate from
table rendering and the interactive SQL loop.
"""

from __future__ import annotations

from typing import Any

import typer


def _display_table(columns: list[str], rows: list[tuple]) -> None:
    """Display query results in a simple tabular format.

    Args:
        columns: List of column names.
        rows: List of rows, where each row is a tuple of values.
    """
    if not columns or not rows:
        return

    # Convert all values to strings for consistent display
    str_columns = [str(col) for col in columns]
    str_rows = [[str(cell) for cell in row] for row in rows]

    # Calculate column widths
    col_widths = []
    for i, col in enumerate(str_columns):
        # Start with column header width
        max_width = len(col)
        # Check all rows in this column
        for row in str_rows:
            if i < len(row):
                max_width = max(max_width, len(str(row[i])))
        col_widths.append(max_width)

    # Create horizontal separator line
    separator = "+" + "+".join("-" * (width + 2) for width in col_widths) + "+"

    # Print header
    typer.echo(separator)
    header_row = (
        "|"
        + "|".join(f" {col:<{col_widths[i]}} " for i, col in enumerate(str_columns))
        + "|"
    )
    typer.echo(header_row)
    typer.echo(separator)

    # Print data rows
    for row in str_rows:
        # Pad row with empty strings if it has fewer columns than headers
        padded_row = row + [""] * (len(str_columns) - len(row))
        data_row = (
            "|"
            + "|".join(
                f" {padded_row[i]:<{col_widths[i]}} " for i in range(len(str_columns))
            )
            + "|"
        )
        typer.echo(data_row)

    typer.echo(separator)


def _interactive_loop(conn: Any) -> None:
    """Run an interactive SQL shell for the catalog."""
    import duckdb

    typer.echo("Duckalog Interactive SQL Shell")
    typer.echo("Type '.help' for help, '.quit' to exit.")

    while True:
        try:
            sql = typer.prompt("duckalog> ", prompt_suffix="").strip()
            if not sql:
                continue

            if sql.lower() in (".quit", ".exit", "exit", "quit"):
                break

            if sql.lower() == ".help":
                typer.echo("\nCommands:")
                typer.echo("  .quit, .exit  - Exit the shell")
                typer.echo("  .tables       - List all tables")
                typer.echo("  .views        - List all views")
                typer.echo("  .help         - Show this help")
                typer.echo("  <SQL>         - Execute SQL query\n")
                continue

            if sql.lower() == ".tables":
                res = conn.execute(
                    "SELECT table_name, table_schema FROM duckdb_tables()"
                ).fetchall()
                _display_table(["table_name", "table_schema"], res)
                continue

            if sql.lower() == ".views":
                res = conn.execute(
                    "SELECT view_name, schema_name FROM duckdb_views()"
                ).fetchall()
                _display_table(["view_name", "schema_name"], res)
                continue

            # Execute SQL
            res = conn.execute(sql)
            if res.description:
                columns = [desc[0] for desc in res.description]
                rows = res.fetchall()
                if rows:
                    _display_table(columns, rows)
                else:
                    typer.echo("Query executed successfully. No rows returned.")
            else:
                typer.echo("Query executed successfully.")

        except EOFError:
            break
        except duckdb.Error as e:
            typer.echo(f"SQL Error: {e}", err=True)
        except Exception as e:
            typer.echo(f"Error: {e}", err=True)


def _fail(message: str, code: int) -> None:
    """Print an error message and exit with the given code.

    Args:
        message: Message to write to stderr.
        code: Process exit code.
    """

    typer.echo(message, err=True)
    raise typer.Exit(code)
