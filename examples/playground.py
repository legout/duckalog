# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "duckalog==0.2.0",
#     "duckdb==1.4.2",
#     "polars==1.35.2",
#     "pyarrow==22.0.0",
# ]
# ///

import marimo

__generated_with = "0.18.0"
app = marimo.App(width="full", auto_download=["html"], sql_output="polars")


@app.cell
def _():
    import duckdb
    import marimo as mo
    from duckalog import load_config, build_catalog
    return duckdb, mo


@app.cell
def _(duckdb):
    con = duckdb.connect("simple_parquet/analytics_catalog.duckdb")
    return (con,)


@app.cell
def _():
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT * FROM '/Users/volker/coding/libs/duckalog/examples/simple_parquet/data/users.parquet'
        """,
        engine=con
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
