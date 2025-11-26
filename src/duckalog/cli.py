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
from .path_resolution import validate_file_accessibility
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


@app.command(name="version", help="Show duckalog version.")
def version_command() -> None:
    """Show the installed duckalog package version."""

    try:
        current_version = pkg_version("duckalog")
    except PackageNotFoundError:
        current_version = "unknown"
    typer.echo(f"duckalog {current_version}")


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


@app.command(help="Show resolved paths for a configuration file.")
def show_paths(
    config_path: Path = typer.Argument(
        ..., exists=True, file_okay=True, dir_okay=False
    ),
    check_accessibility: bool = typer.Option(
        False, "--check", "-c", help="Check if files are accessible."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging output."
    ),
) -> None:
    """Show how paths in a configuration are resolved.

    This command displays the original paths from the configuration file
    and their resolved absolute paths.

    Args:
        config_path: Path to the configuration file.
        check_accessibility: If True, check if resolved file paths are accessible.
        verbose: If True, enable more verbose logging.
    """
    _configure_logging(verbose)
    log_info("CLI show-paths invoked", config_path=str(config_path))

    try:
        config = load_config(str(config_path))
    except ConfigError as exc:
        log_error("Show-paths failed due to config error", error=str(exc))
        _fail(f"Config error: {exc}", 2)

    config_dir = config_path.resolve().parent
    typer.echo(f"Configuration: {config_path}")
    typer.echo(f"Config directory: {config_dir}")
    typer.echo("")

    # Show view paths
    typer.echo("View Paths:")
    typer.echo("-" * 80)
    if config.views:
        for view in config.views:
            if view.uri:
                typer.echo(f"{view.name}:")
                typer.echo(f"  Original: {view.uri}")
                # For file-based views, show what would be resolved
                if view.source in ("parquet", "delta"):
                    from .path_resolution import resolve_relative_path, is_relative_path

                    if is_relative_path(view.uri):
                        resolved = resolve_relative_path(view.uri, config_dir)
                        typer.echo(f"  Resolved: {resolved}")
                    else:
                        typer.echo(f"  Resolved: {view.uri} (absolute path)")

                    if check_accessibility:
                        is_accessible, error_msg = validate_file_accessibility(resolved)
                        if is_accessible:
                            typer.echo(f"  Status: ✅ Accessible")
                        else:
                            typer.echo(f"  Status: ❌ {error_msg}")
                typer.echo("")
    else:
        typer.echo("No views with file paths found.")


@app.command(help="Validate config and check path accessibility.")
def validate_paths(
    config_path: Path = typer.Argument(
        ..., exists=True, file_okay=True, dir_okay=False
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging output."
    ),
) -> None:
    """Validate configuration and check path accessibility.

    This command validates the configuration file and checks if all file
    paths are accessible.

    Args:
        config_path: Path to the configuration file.
        verbose: If True, enable more verbose logging.
    """
    _configure_logging(verbose)
    log_info("CLI validate-paths invoked", config_path=str(config_path))

    try:
        config = load_config(str(config_path))
        typer.echo("✅ Configuration is valid.")
    except ConfigError as exc:
        log_error("Validate-paths failed due to config error", error=str(exc))
        _fail(f"Config error: {exc}", 2)

    config_dir = config_path.resolve().parent
    inaccessible_files = []

    # Check accessibility of view files
    typer.echo("")
    typer.echo("Checking file accessibility...")
    typer.echo("-" * 50)

    if config.views:
        for view in config.views:
            if view.uri and view.source in ("parquet", "delta"):
                from .path_resolution import resolve_relative_path, is_relative_path

                path_to_check = view.uri
                if is_relative_path(view.uri):
                    path_to_check = resolve_relative_path(view.uri, config_dir)

                is_accessible, error_msg = validate_file_accessibility(path_to_check)
                if is_accessible:
                    typer.echo(f"✅ {view.name}: {path_to_check}")
                else:
                    typer.echo(f"❌ {view.name}: {error_msg}")
                    inaccessible_files.append((view.name, path_to_check, error_msg))

    # Summary
    typer.echo("")
    if inaccessible_files:
        typer.echo(f"❌ Found {len(inaccessible_files)} inaccessible files:")
        for name, path, error in inaccessible_files:
            typer.echo(f"  - {name}: {error}")
        _fail("Some files are not accessible.", 3)
    else:
        typer.echo("✅ All files are accessible.")


@app.command(help="Start the web UI for catalog management.")
def ui(
    config_path: Path = typer.Argument(
        ..., exists=True, file_okay=True, dir_okay=False
    ),
    host: str = typer.Option(
        "127.0.0.1", "--host", help="Host address to bind the server to."
    ),
    port: int = typer.Option(8000, "--port", help="Port number to listen on."),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging output."
    ),
) -> None:
    """CLI entry point for the ``ui`` command.

    This command starts a web-based UI for managing DuckDB catalogs.

    Args:
        config_path: Path to the configuration file.
        host: Host address to bind the server to.
        port: Port number to listen on.
        verbose: If ``True``, enable more verbose logging.
    """
    _configure_logging(verbose)
    log_info(
        "CLI ui invoked",
        config_path=str(config_path),
        host=host,
        port=port,
    )

    # Ensure Path object even if Click/Typer handed us a string
    if not isinstance(config_path, Path):
        config_path = Path(config_path)

    forbidden_exts = {".duckdb", ".db", ".sqlite", ".sqlite3", ".mdb"}
    suffix = config_path.suffix.lower()
    if suffix in forbidden_exts:
        _fail(
            "UI expects a Duckalog YAML/JSON config file (e.g., catalog.yaml), "
            f"not a database file like '{config_path.name}'.",
            2,
        )

    try:
        # Import UI module with error handling
        try:
            from .ui import UIServer
        except ImportError as exc:
            _fail(
                f"UI dependencies not found. Install with: pip install duckalog[ui] - {exc}",
                4,
            )

        # Create and run UI server
        ui_server = UIServer(str(config_path), host=host, port=port)
        ui_server.run()

    except Exception as exc:  # pragma: no cover - unexpected failures
        if verbose:
            raise
        log_error("UI failed unexpectedly", error=str(exc))
        _fail(f"Unexpected error: {exc}", 1)


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
