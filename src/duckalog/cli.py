"""Typer-based CLI for Duckalog."""

from __future__ import annotations

# mypy: disable-error-code=assignment
import logging
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version
from pathlib import Path
from typing import Optional

import typer

from .config import ConfigError, load_config
from .engine import EngineError, build_catalog
from .logging_utils import log_error, log_info
from .sql_generation import generate_all_views_sql

app = typer.Typer(help="Duckalog CLI for building and inspecting DuckDB catalogs.")


def _configure_logging(verbose: bool) -> None:
    """Configure global logging settings for CLI commands.

    Args:
        verbose: When ``True``, set the log level to ``INFO``; otherwise use
            ``WARNING``.
    """

    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(message)s")


@app.callback(invoke_without_command=True)
def main_callback(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show duckalog version and exit.",
        is_eager=True,
    ),
) -> None:
    """Handle global CLI options such as --version."""

    if version:
        try:
            current_version = pkg_version("duckalog")
        except PackageNotFoundError:
            current_version = "unknown"
        typer.echo(f"duckalog {current_version}")
        raise typer.Exit()


@app.command(help="Build or update a DuckDB catalog from a config file.")
def build(
    config_path: Path = typer.Argument(
        ..., exists=True, file_okay=True, dir_okay=False
    ),
    db_path: Optional[Path] = typer.Option(
        None, "--db-path", help="Override DuckDB database path."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Generate SQL without executing against DuckDB."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging output."
    ),
) -> None:
    """CLI entry point for the ``build`` command.

    This command loads a configuration file and applies it to a DuckDB
    catalog, or prints the generated SQL when ``--dry-run`` is used.

    Args:
        config_path: Path to the configuration file.
        db_path: Optional override for the DuckDB database file path.
        dry_run: If ``True``, print SQL instead of modifying the database.
        verbose: If ``True``, enable more verbose logging.
    """
    _configure_logging(verbose)
    log_info(
        "CLI build invoked",
        config_path=str(config_path),
        db_path=str(db_path) if db_path else None,
        dry_run=dry_run,
    )
    try:
        sql = build_catalog(
            str(config_path),
            db_path=str(db_path) if db_path else None,
            dry_run=dry_run,
            verbose=verbose,
        )
    except ConfigError as exc:
        log_error("Build failed due to config error", error=str(exc))
        _fail(f"Config error: {exc}", 2)
    except EngineError as exc:
        log_error("Build failed due to engine error", error=str(exc))
        _fail(f"Engine error: {exc}", 3)
    except Exception as exc:  # pragma: no cover - unexpected failures
        if verbose:
            raise
        log_error("Build failed unexpectedly", error=str(exc))
        _fail(f"Unexpected error: {exc}", 1)

    if dry_run and sql:
        typer.echo(sql)
    elif not dry_run:
        typer.echo("Catalog build completed.")


@app.command(name="generate-sql", help="Validate config and emit CREATE VIEW SQL only.")
def generate_sql(
    config_path: Path = typer.Argument(
        ..., exists=True, file_okay=True, dir_okay=False
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Write SQL output to file instead of stdout."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging output."
    ),
) -> None:
    """CLI entry point for the ``generate-sql`` command.

    Args:
        config_path: Path to the configuration file.
        output: Optional output file path. If omitted, SQL is printed to
            standard output.
        verbose: If ``True``, enable more verbose logging.
    """
    _configure_logging(verbose)
    log_info(
        "CLI generate-sql invoked",
        config_path=str(config_path),
        output=str(output) if output else "stdout",
    )
    try:
        config = load_config(str(config_path))
        sql = generate_all_views_sql(config)
    except ConfigError as exc:
        log_error("Generate-sql failed due to config error", error=str(exc))
        _fail(f"Config error: {exc}", 2)

    if output:
        out_path = Path(output)
        out_path.write_text(sql)
        if verbose:
            typer.echo(f"Wrote SQL to {out_path}")
    else:
        typer.echo(sql)


@app.command(help="Validate a config file and report success or failure.")
def validate(
    config_path: Path = typer.Argument(
        ..., exists=True, file_okay=True, dir_okay=False
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging output."
    ),
) -> None:
    """CLI entry point for the ``validate`` command.

    Args:
        config_path: Path to the configuration file.
        verbose: If ``True``, enable more verbose logging.
    """
    _configure_logging(verbose)
    log_info("CLI validate invoked", config_path=str(config_path))
    try:
        load_config(str(config_path))
    except ConfigError as exc:
        log_error("Validate failed due to config error", error=str(exc))
        _fail(f"Config error: {exc}", 2)

    typer.echo("Config is valid.")


def _fail(message: str, code: int) -> None:
    """Print an error message and exit with the given code.

    Args:
        message: Message to write to stderr.
        code: Process exit code.
    """

    typer.echo(message, err=True)
    raise typer.Exit(code)


def main_entry() -> None:
    """Invoke the Typer application as the console entry point."""

    app()


__all__ = ["app", "main_entry"]
