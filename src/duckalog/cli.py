"""Typer-based CLI for Duckalog."""

from __future__ import annotations

# mypy: disable-error-code=assignment
import sys
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version
from pathlib import Path
from typing import Optional

from loguru import logger

import typer

from .cli_display import _display_table, _interactive_loop, _fail
from .cli_filesystem import _create_filesystem_from_options
from .cli_imports import _collect_import_graph, _print_import_tree
from .config import load_config, validate_file_accessibility, log_error, log_info
from .config_init import create_config_template, validate_generated_config
from .connection import connect_to_catalog
from .engine import build_catalog
from .errors import ConfigError, EngineError
from .sql_generation import generate_all_views_sql

app = typer.Typer(help="Duckalog CLI for building and inspecting DuckDB catalogs.")


def _configure_logging(verbose: bool) -> None:
    """Configure global logging settings for CLI commands.

    Args:
        verbose: When ``True``, set the log level to ``INFO``; otherwise use
            ``WARNING``.
    """
    # Remove default handler to avoid duplicate output
    logger.remove()

    # Add a new handler with appropriate level and format
    level = "INFO" if verbose else "WARNING"
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    )


# Shared callback for filesystem options across all commands
@app.callback()
def main_callback(
    ctx: typer.Context,
    fs_protocol: Optional[str] = typer.Option(
        None,
        "--fs-protocol",
        help="Remote filesystem protocol: s3 (AWS), gcs (Google), abfs (Azure), sftp, github. Protocol can be inferred from other options.",
    ),
    fs_key: Optional[str] = typer.Option(
        None,
        "--fs-key",
        help="API key, access key, or username for authentication (protocol-specific)",
    ),
    fs_secret: Optional[str] = typer.Option(
        None,
        "--fs-secret",
        help="Secret key, password, or token for authentication (protocol-specific)",
    ),
    fs_token: Optional[str] = typer.Option(
        None,
        "--fs-token",
        help="Authentication token for services like GitHub personal access tokens",
    ),
    fs_anon: bool = typer.Option(
        False,
        "--fs-anon",
        help="Use anonymous access (no authentication required). Useful for public S3 buckets.",
    ),
    fs_timeout: Optional[int] = typer.Option(
        None, "--fs-timeout", help="Connection timeout in seconds (default: 30)"
    ),
    aws_profile: Optional[str] = typer.Option(
        None,
        "--aws-profile",
        help="AWS profile name for S3 authentication (overrides --fs-key/--fs-secret)",
    ),
    gcs_credentials_file: Optional[str] = typer.Option(
        None,
        "--gcs-credentials-file",
        help="Path to Google Cloud service account credentials JSON file",
    ),
    azure_connection_string: Optional[str] = typer.Option(
        None,
        "--azure-connection-string",
        help="Azure storage connection string (overrides --fs-key/--fs-secret for Azure)",
    ),
    sftp_host: Optional[str] = typer.Option(
        None, "--sftp-host", help="SFTP server hostname (required for SFTP protocol)"
    ),
    sftp_port: int = typer.Option(
        22, "--sftp-port", help="SFTP server port (default: 22)"
    ),
    sftp_key_file: Optional[str] = typer.Option(
        None,
        "--sftp-key-file",
        help="Path to SSH private key file for SFTP authentication",
    ),
) -> None:
    """Shared callback that creates filesystem objects from CLI options.

    This callback applies to all commands and creates a filesystem object
    from the provided options, storing it in ctx.obj["filesystem"].
    """
    if ctx.resilient_parsing:
        return

    # Initialize context object if needed
    if ctx.obj is None:
        ctx.obj = {}

    # Create filesystem object using existing helper
    filesystem = _create_filesystem_from_options(
        protocol=fs_protocol,
        key=fs_key,
        secret=fs_secret,
        token=fs_token,
        anon=fs_anon,
        timeout=fs_timeout,
        aws_profile=aws_profile,
        gcs_credentials_file=gcs_credentials_file,
        azure_connection_string=azure_connection_string,
        sftp_host=sftp_host,
        sftp_port=sftp_port,
        sftp_key_file=sftp_key_file,
    )

    # Store filesystem in context for command access
    ctx.obj["filesystem"] = filesystem


@app.command(name="version", help="Show duckalog version.")
def version_command() -> None:
    """Show the installed duckalog package version."""

    try:
        current_version = pkg_version("duckalog")
    except PackageNotFoundError:
        current_version = "unknown"
    typer.echo(f"duckalog {current_version}")



@app.command(help="Run a catalog with smart connection management.")
def run(
    ctx: typer.Context,
    config_path: str = typer.Argument(
        ...,
        help="Path to configuration file or remote URI (e.g., s3://bucket/config.yaml)",
    ),
    db_path: Optional[str] = typer.Option(
        None,
        "--db-path",
        help="Override DuckDB database path. Supports local paths and remote URIs (s3://, gs://, gcs://, abfs://, adl://, sftp://).",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Generate SQL without executing against DuckDB."
    ),
    force_rebuild: bool = typer.Option(
        False,
        "--force-rebuild",
        help="Force full catalog rebuild instead of incremental updates.",
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Keep connection alive and enter interactive SQL prompt.",
    ),
    query_sql: Optional[str] = typer.Option(
        None,
        "--query",
        "-q",
        help="Execute a specific SQL query and exit.",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging output."
    ),
    load_dotenv: bool = typer.Option(
        True,
        "--load-dotenv/--no-load-dotenv",
        help="Enable/disable automatic .env file loading.",
    ),
) -> None:
    """CLI entry point for ``run`` command.

    This command provides smart catalog management with connection state restoration
    and incremental updates. For most use cases, prefer ``run`` over ``build``.

    Examples:
        # Run with smart connection management
        duckalog run config.yaml

        # Force full rebuild
        duckalog run config.yaml --force-rebuild

        # Interactive mode for multiple queries
        duckalog run config.yaml --interactive

        # Single query execution
        duckalog run config.yaml --query "SELECT * FROM my_view"

        # S3 with access key and secret
        duckalog run s3://my-bucket/config.yaml --fs-key AKIA... --fs-secret wJalr...

    Args:
        config_path: Path to configuration file or remote URI (e.g., s3://bucket/config.yaml).
        db_path: Optional override for DuckDB database file path.
        dry_run: If ``True``, print SQL instead of modifying database.
        force_rebuild: If ``True``, force full catalog rebuild instead of incremental updates.
        interactive: If ``True``, start interactive SQL shell.
        query_sql: Optional SQL query to execute and exit.
        verbose: If ``True``, enable more verbose logging.
        load_dotenv: If ``True``, automatically load and process .env files.
    """
    _configure_logging(verbose)

    # Get filesystem from context (created by shared callback)
    filesystem = ctx.obj.get("filesystem")

    # Validate that local files exist, but allow remote URIs
    try:
        from .remote_config import is_remote_uri

        if not is_remote_uri(config_path):
            # This is a local path, check if it exists
            local_path = Path(config_path)
            if not local_path.exists():
                _fail(f"Config file not found: {config_path}", 2)
    except ImportError:
        # Remote functionality not available, treat as local path
        local_path = Path(config_path)
        if not local_path.exists():
            _fail(f"Config file not found: {config_path}", 2)

    log_info(
        "CLI run invoked",
        config_path=config_path,
        db_path=db_path,
        dry_run=dry_run,
        force_rebuild=force_rebuild,
        interactive=interactive,
        query=query_sql,
        filesystem=filesystem is not None,
    )

    if dry_run:
        try:
            sql = build_catalog(
                str(config_path),
                db_path=db_path,
                dry_run=True,
                verbose=verbose,
                filesystem=filesystem,
                load_dotenv=load_dotenv,
            )
            if sql:
                typer.echo(sql)
            return
        except Exception as exc:
            log_error("Dry run failed", error=str(exc))
            _fail(f"Error: {exc}", 1)

    try:
        with connect_to_catalog(
            str(config_path),
            database_path=db_path,
            force_rebuild=force_rebuild,
            filesystem=filesystem,
            load_dotenv=load_dotenv,
        ) as catalog:
            conn = catalog.get_connection()

            if query_sql:
                res = conn.execute(query_sql)
                if res.description:
                    columns = [desc[0] for desc in res.description]
                    rows = res.fetchall()
                    if rows:
                        _display_table(columns, rows)
                    else:
                        typer.echo("Query executed successfully. No rows returned.")
                else:
                    typer.echo("Query executed successfully.")
            elif interactive:
                _interactive_loop(conn)
            else:
                action = "rebuilt" if force_rebuild else "updated"
                typer.echo(f"Catalog {action} successfully.")

    except ConfigError as exc:
        log_error("Run failed due to config error", error=str(exc))
        _fail(f"Config error: {exc}", 2)
    except EngineError as exc:
        log_error("Run failed due to engine error", error=str(exc))
        _fail(f"Engine error: {exc}", 3)
    except Exception as exc:  # pragma: no cover
        if verbose:
            raise
        log_error("Run failed unexpectedly", error=str(exc))
        _fail(f"Unexpected error: {exc}", 1)


@app.command(name="generate-sql", help="Validate config and emit CREATE VIEW SQL only.")
def generate_sql(
    ctx: typer.Context,
    config_path: str = typer.Argument(
        ..., help="Path to configuration file or remote URI"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Write SQL output to file instead of stdout."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging output."
    ),
) -> None:
    """CLI entry point for ``generate-sql`` command.

    Args:
        config_path: Path to configuration file or remote URI.
        output: Optional output file path. If omitted, SQL is printed to
            standard output.
        verbose: If ``True``, enable more verbose logging.
    """
    _configure_logging(verbose)

    # Get filesystem from context (created by shared callback)
    filesystem = ctx.obj.get("filesystem")

    # Validate that local files exist, but allow remote URIs
    try:
        from .remote_config import is_remote_uri

        if not is_remote_uri(config_path):
            # This is a local path, check if it exists
            local_path = Path(config_path)
            if not local_path.exists():
                _fail(f"Config file not found: {config_path}", 2)
    except ImportError:
        # Remote functionality not available, treat as local path
        local_path = Path(config_path)
        if not local_path.exists():
            _fail(f"Config file not found: {config_path}", 2)

    log_info(
        "CLI generate-sql invoked",
        config_path=config_path,
        output=str(output) if output else "stdout",
        filesystem=filesystem is not None,
    )
    try:
        config = load_config(config_path, filesystem=filesystem)
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
    ctx: typer.Context,
    config_path: str = typer.Argument(
        ..., help="Path to configuration file or remote URI"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging output."
    ),
) -> None:
    """CLI entry point for ``validate`` command.

    Args:
        config_path: Path to configuration file or remote URI.
        verbose: If ``True``, enable more verbose logging.
    """
    _configure_logging(verbose)

    # Get filesystem from context (created by shared callback)
    filesystem = ctx.obj.get("filesystem")

    # Validate that local files exist, but allow remote URIs
    try:
        from .remote_config import is_remote_uri

        if not is_remote_uri(config_path):
            # This is a local path, check if it exists
            local_path = Path(config_path)
            if not local_path.exists():
                _fail(f"Config file not found: {config_path}", 2)
    except ImportError:
        # Remote functionality not available, treat as local path
        local_path = Path(config_path)
        if not local_path.exists():
            _fail(f"Config file not found: {config_path}", 2)

    log_info(
        "CLI validate invoked",
        config_path=config_path,
        filesystem=filesystem is not None,
    )
    try:
        load_config(config_path, filesystem=filesystem)
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
    inaccessible_files = []
    if config.views:
        for view in config.views:
            if view.uri:
                typer.echo(f"{view.name}:")
                typer.echo(f"  Original: {view.uri}")
                # For file-based views, show what would be resolved
                if view.source in ("parquet", "delta"):
                    from .config import is_relative_path, resolve_relative_path

                    if is_relative_path(view.uri):
                        resolved = resolve_relative_path(view.uri, config_dir)
                        typer.echo(f"  Resolved: {resolved}")
                    else:
                        resolved = view.uri
                        typer.echo(f"  Resolved: {view.uri} (absolute path)")

                    if check_accessibility:
                        is_accessible, error_msg = validate_file_accessibility(resolved)
                        if is_accessible:
                            typer.echo("  Status: ✅ Accessible")
                        else:
                            typer.echo(f"  Status: ❌ {error_msg}")
                            inaccessible_files.append((view.name, resolved, error_msg))
                typer.echo("")
    else:
        typer.echo("No views with file paths found.")

    if check_accessibility:
        typer.echo("")
        if inaccessible_files:
            typer.echo(f"❌ Found {len(inaccessible_files)} inaccessible files:")
            for name, path, error in inaccessible_files:
                typer.echo(f"  - {name}: {error}")
            _fail("Some files are not accessible.", 3)
        else:
            typer.echo("✅ All files are accessible.")


@app.command(help="Show the import graph for a configuration file.")
def show_imports(
    ctx: typer.Context,
    config_path: str = typer.Argument(
        ..., help="Path to configuration file or remote URI"
    ),
    show_merged: bool = typer.Option(
        False,
        "--show-merged",
        help="Also display the fully merged configuration after imports are resolved.",
    ),
    output_format: str = typer.Option(
        "tree",
        "--format",
        "-f",
        help="Output format: tree or json (default: tree)",
    ),
    diagnostics: bool = typer.Option(
        False,
        "--diagnostics",
        help="Show import diagnostics (depth, duplicates, performance metrics).",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging output."
    ),
) -> None:
    """Display the import graph for a configuration file.

    This command shows which configuration files are imported and how they
    are connected, helping you understand the structure of your configuration.

    Examples:
        # Show the import tree
        duckalog show-imports config.yaml

        # Show import tree with diagnostics
        duckalog show-imports config.yaml --diagnostics

        # Show import tree with merged config
        duckalog show-imports config.yaml --show-merged

        # Export import graph as JSON
        duckalog show-imports config.yaml --format json

    Args:
        config_path: Path to configuration file or remote URI.
        show_merged: If True, also display the fully merged configuration.
        output_format: Output format (tree or json).
        diagnostics: If True, show import diagnostics (depth, duplicates, etc.).
        verbose: If True, enable more verbose logging.
    """
    from .config.resolution.imports import _is_remote_uri
    import json

    _configure_logging(verbose)

    # Get filesystem from context
    filesystem = ctx.obj.get("filesystem")

    # Validate that local files exist, but allow remote URIs
    if not _is_remote_uri(config_path):
        local_path = Path(config_path)
        if not local_path.exists():
            _fail(f"Config file not found: {config_path}", 2)

    log_info("CLI show-imports invoked", config_path=config_path)

    try:
        # Collect import graph information
        import_chain, import_graph, visited = _collect_import_graph(
            config_path, filesystem
        )

        # Output based on format
        if output_format == "json":
            output = {
                "import_chain": import_chain,
                "import_graph": import_graph,
                "total_files": len(visited),
            }
            typer.echo(json.dumps(output, indent=2))
        else:
            # Default tree format
            typer.echo("")
            typer.echo("Import Graph:")
            typer.echo("=" * 80)
            _print_import_tree(
                import_chain, import_graph, visited, show_diagnostics=diagnostics
            )

            # Optionally show merged config
            if show_merged:
                typer.echo("")
                typer.echo("Merged Configuration:")
                typer.echo("=" * 80)
                try:
                    merged_config = load_config(config_path, filesystem=filesystem)
                    # Use model_dump_json for clean JSON output
                    merged_json = merged_config.model_dump_json(indent=2)
                    typer.echo(merged_json)
                except ConfigError as exc:
                    typer.echo(f"Error loading merged config: {exc}", err=True)

    except ConfigError as exc:
        log_error("Show-imports failed due to config error", error=str(exc))
        _fail(f"Config error: {exc}", 2)
    except Exception as exc:
        if verbose:
            raise
        log_error("Show-imports failed unexpectedly", error=str(exc))
        _fail(f"Unexpected error: {exc}", 1)


@app.command(name="ui", help="Launch the local dashboard for a catalog.")
def ui(
    config_path: str = typer.Argument(
        ..., help="Path to configuration file (local or remote)."
    ),
    host: str = typer.Option(
        "127.0.0.1", "--host", help="Host to bind (default: loopback)."
    ),
    port: int = typer.Option(8787, "--port", help="Port to bind (default: 8787)."),
    row_limit: int = typer.Option(
        500, "--row-limit", help="Max rows to show in query results."
    ),
    db_path: Optional[str] = typer.Option(
        None, "--db", help="Path to DuckDB database file (optional)."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging output."
    ),
) -> None:
    """Start a local dashboard to inspect and query a Duckalog catalog.

    This command launches a web-based dashboard that allows you to:
    - Browse views defined in the catalog configuration
    - Execute SQL queries against the DuckDB database
    - View query results in real-time with streaming

    Examples:
        # Basic usage with config file
        duckalog ui config.yaml

        # Specify a custom host and port
        duckalog ui config.yaml --host 0.0.0.0 --port 8080

        # Use with an existing database file
        duckalog ui config.yaml --db catalog.duckdb
    """
    _configure_logging(verbose)

    # Check for UI dependencies
    try:
        from .dashboard import create_app
    except ImportError:
        _fail(
            "Dashboard dependencies not installed. Install with: pip install duckalog[ui]",
            2,
        )

    try:
        import uvicorn
    except ImportError:
        _fail("uvicorn is required. Install with: pip install duckalog[ui]", 2)

    # Load configuration
    try:
        config = load_config(config_path)
    except ConfigError as exc:
        _fail(f"Config error: {exc}", 2)

    # Create the dashboard app
    dashboard_app = create_app(
        config,
        config_path=config_path,
        db_path=db_path,
        row_limit=row_limit,
    )

    typer.echo(f"Starting dashboard at http://{host}:{port}")
    if host not in ("127.0.0.1", "localhost", "::1"):
        typer.echo(
            "Warning: binding to a non-loopback host may expose the dashboard to others on your network.",
            err=True,
        )
    uvicorn.run(dashboard_app, host=host, port=port, log_level="info")


@app.command(help="Execute SQL queries against a DuckDB catalog.")
def query(
    sql: str = typer.Argument(
        ...,
        help="SQL query to execute against the catalog.",
    ),
    catalog: Optional[str] = typer.Option(
        None,
        "--catalog",
        "-c",
        help="Path to DuckDB catalog file (optional, defaults to catalog.duckdb in current directory).",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging output."
    ),
) -> None:
    """Execute SQL queries against a DuckDB catalog.

    This command allows you to run ad-hoc SQL queries against an existing
    DuckDB catalog file and display results in a tabular format.

    Examples:
        # Query with implicit catalog discovery (catalog.duckdb in current directory)
        duckalog query "SELECT COUNT(*) FROM users"

        # Query with explicit catalog path
        duckalog query "SELECT * FROM users" --catalog catalog.duckdb
        duckalog query "SELECT * FROM users" -c analytics.duckdb

        # Query a remote catalog (if filesystem options are configured)
        duckalog query "SELECT name, email FROM users WHERE active = true" --catalog s3://my-bucket/catalog.duckdb

    Args:
        sql: SQL query string to execute.
        catalog: Optional path to DuckDB catalog file. If omitted, looks for
            'catalog.duckdb' in the current directory.
        verbose: If True, enable verbose logging.
    """
    import duckdb

    _configure_logging(verbose)

    # Determine catalog path
    if not catalog:
        # Try to find a default catalog in the current directory
        default_path = Path("catalog.duckdb")
        if default_path.exists():
            catalog = str(default_path)
        else:
            _fail(
                "No catalog file specified and catalog.duckdb not found in current directory. "
                "Either provide a catalog path or ensure catalog.duckdb exists.",
                2,
            )
    else:
        # Validate that the provided catalog path exists
        catalog_file = Path(catalog)
        if not catalog_file.exists():
            _fail(f"Catalog file not found: {catalog}", 2)

    log_info(
        "CLI query invoked",
        catalog_path=catalog,
        sql=sql[:100] + "..." if len(sql) > 100 else sql,
    )

    try:
        # Connect to the DuckDB catalog
        conn = duckdb.connect(str(catalog), read_only=True)

        try:
            # Execute the query
            result = conn.execute(sql)

            # Fetch results
            rows = result.fetchall()

            # Get column information
            columns = [desc[0] for desc in result.description]

            # Display results in tabular format
            if rows:
                _display_table(columns, rows)
            else:
                if columns:
                    typer.echo("Query executed successfully. No rows returned.")
                    # Show column headers for context
                    typer.echo(f"Columns: {', '.join(columns)}")
                else:
                    typer.echo("Query executed successfully. No results returned.")

        except duckdb.Error as exc:
            log_error("Query execution failed", error=str(exc))
            _fail(f"SQL error: {exc}", 3)
        finally:
            conn.close()

    except duckdb.Error as exc:
        log_error("Failed to connect to catalog", error=str(exc))
        _fail(f"Database error: {exc}", 3)
    except typer.Exit:
        # Re-raise Exit exceptions (from _fail) without modification
        raise
    except Exception as exc:
        if verbose:
            raise
        log_error("Query failed unexpectedly", error=str(exc))
        _fail(f"Unexpected error: {exc}", 1)


@app.command(help="Initialize a new Duckalog configuration file.")
def init(
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path for the configuration. Defaults to catalog.yaml or catalog.json based on format.",
    ),
    format: str = typer.Option(
        "yaml",
        "--format",
        "-f",
        help="Output format: yaml or json (default: yaml)",
    ),
    database_name: str = typer.Option(
        "analytics_catalog.duckdb",
        "--database",
        "-d",
        help="DuckDB database filename (default: analytics_catalog.duckdb)",
    ),
    project_name: str = typer.Option(
        "my_analytics_project",
        "--project",
        "-p",
        help="Project name used in comments (default: my_analytics_project)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing file without prompting",
    ),
    skip_existing: bool = typer.Option(
        False,
        "--skip-existing",
        help="Skip file creation if it already exists",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging output."
    ),
) -> None:
    """Create a new Duckalog configuration file.

    This command generates a basic, valid configuration template with
    sensible defaults and educational example content.

    Examples:
        # Create a basic YAML config
        duckalog init

        # Create a JSON config with custom filename
        duckalog init --format json --output my_config.json

        # Create with custom database and project names
        duckalog init --database sales.db --project sales_analytics

        # Force overwrite existing file
        duckalog init --force
    """
    _configure_logging(verbose)

    # Validate format
    if format not in ("yaml", "json"):
        typer.echo(f"Error: Format must be 'yaml' or 'json', got '{format}'", err=True)
        raise typer.Exit(1)

    # Determine default output path
    if not output:
        output = f"catalog.{format}"

    output_path = Path(output)

    # Check if file already exists
    if output_path.exists():
        if skip_existing:
            typer.echo(f"File {output_path} already exists, skipping.")
            return
        elif not force:
            # Prompt for confirmation
            if not typer.confirm(f"File {output_path} already exists. Overwrite?"):
                typer.echo("Operation cancelled.")
                return

    try:
        # Generate the configuration template
        content = create_config_template(
            format=format,
            output_path=str(output_path),
            database_name=database_name,
            project_name=project_name,
        )

        # Validate the generated content
        validate_generated_config(content, format=format)

        # Determine default filename for messaging
        if output == f"catalog.{format}":
            filename_msg = f"catalog.{format} (default filename)"
        else:
            filename_msg = str(output_path)

        typer.echo(f"✅ Created Duckalog configuration: {filename_msg}")
        typer.echo(f"📁 Path: {output_path.resolve()}")
        typer.echo(f"📄 Format: {format.upper()}")
        typer.echo(f"💾 Database: {database_name}")

        if verbose:
            typer.echo("\n🔧 Next steps:")
            typer.echo(f"   1. Edit {output_path} to customize views and data sources")
            typer.echo(
                f"   2. Run 'duckalog validate {output_path}' to check your configuration"
            )
            typer.echo(
                f"   3. Run 'duckalog run {output_path}' to create your catalog"
            )

    except Exception as exc:
        if verbose:
            raise
        typer.echo(f"Error creating configuration: {exc}", err=True)
        raise typer.Exit(1)


def main_entry() -> None:
    """Invoke the Typer application as the console entry point."""

    app()


__all__ = ["app", "main_entry"]
