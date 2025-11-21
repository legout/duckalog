"""Web UI module for Duckalog using Datastar and Starlette."""

from __future__ import annotations

import io
import json
import os
import tempfile
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Route
from starlette.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTasks

from .config import Config, ConfigError, load_config
from .engine import EngineError, build_catalog
from .logging_utils import log_error, log_info

# Background task functions
def _execute_query_task(config: Config, query: str, result_store: Dict[str, Any]) -> None:
    """Background task for executing DuckDB queries."""
    try:
        import duckdb
        db_path = config.duckdb.database
        conn = duckdb.connect(db_path)

        try:
            query_result = conn.execute(query)
            rows = query_result.fetchall()

            if rows:
                columns = [desc[0] for desc in query_result.description]
                data = [dict(zip(columns, row)) for row in rows]
            else:
                data = []

            result_store["status"] = "completed"
            result_store["status"] = "completed"
            result_store["success"] = True
            result_store["data"] = data
            result_store["row_count"] = len(data)

        finally:
            conn.close()

    except Exception as exc:
        result_store["status"] = "failed"
        result_store["success"] = False
        result_store["error"] = str(exc)


def _export_data_task(config: Config, query: str, format_type: str, result_store: Dict[str, Any]) -> None:
    """Background task for exporting DuckDB data."""
    try:
        import duckdb
        db_path = config.duckdb.database
        conn = duckdb.connect(db_path)

        try:
            query_result = conn.execute(query)
            rows = query_result.fetchall()

            # Always get column information, even for empty results
            columns = [desc[0] for desc in query_result.description]

            if rows:
                data = [dict(zip(columns, row)) for row in rows]
            else:
                # For empty results, create empty data but preserve column info
                data = []

            result_store["status"] = "completed"
            result_store["success"] = True
            result_store["data"] = data
            result_store["columns"] = columns  # Preserve column information

        finally:
            conn.close()

    except Exception as exc:
        result_store["status"] = "failed"
        result_store["success"] = False
        result_store["error"] = str(exc)


def _rebuild_catalog_task(config: Config, result_store: Dict[str, Any]) -> None:
    """Background task for rebuilding the catalog."""
    try:
        build_catalog(config)
        result_store["status"] = "completed"
        result_store["success"] = True
        result_store["message"] = "Catalog rebuilt successfully"
    except Exception as exc:
        result_store["status"] = "failed"
        result_store["success"] = False
        result_store["error"] = str(exc)

try:
    from datastar_py import ServerSentEventGenerator as SSE
except ImportError as exc:
    raise ImportError(
        "Datastar dependencies not found. Install with: pip install datastar datastar-python"
    ) from exc


def _validate_read_only_query(query: str) -> str:
    """Validate that query is read-only and single-statement with safe identifier handling.

    Args:
        query: SQL query to validate

    Returns:
        Original query if valid

    Raises:
        ValueError: If query contains DDL/DML or multiple statements
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    # Remove leading/trailing whitespace and normalize case
    normalized_query = query.strip()

    # Check for DDL keywords
    ddl_keywords = [
        "create",
        "drop",
        "alter",
        "truncate",
        "rename",
        "comment",
        "grant",
        "revoke",
        "commit",
        "rollback",
        "savepoint",
    ]

    # Check for DML keywords (excluding SELECT)
    dml_keywords = [
        "insert",
        "update",
        "delete",
        "merge",
        "upsert",
        "replace",
        "call",
        "explain",
        "analyze",
        "optimize",
        "vacuum",
    ]

    # Check if query starts with SELECT (case-insensitive)
    if not normalized_query.lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed for security")

    # Check for forbidden keywords
    for keyword in ddl_keywords + dml_keywords:
        if (
            f" {keyword} " in normalized_query.lower()
            or f"\n{keyword}" in normalized_query.lower()
        ):
            raise ValueError(f"Query contains forbidden keyword: {keyword.upper()}")

    # Check for multiple statements (semicolon separation)
    if ";" in normalized_query.replace("'", "").replace('"', "").replace("`", ""):
        # Count semicolons not in string literals
        semicolon_count = normalized_query.count(";")
        if semicolon_count > 1:
            raise ValueError("Multiple statements are not allowed")

    return query


def _safe_identifier(identifier: str) -> str:
    """Create a safe SQL identifier with proper quoting.

    Args:
        identifier: Table or column name to make safe

    Returns:
        Safely quoted identifier
    """
    if not identifier or not identifier.strip():
        raise ValueError("Identifier cannot be empty")

    # Check for valid identifier pattern (letters, numbers, underscores)
    import re

    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", identifier.strip()):
        raise ValueError(f"Invalid identifier: {identifier}")

    # DuckDB identifiers are case-insensitive but we'll preserve original case
    # Use double quotes for identifiers that need quoting
    if " " in identifier or identifier.lower() in [
        "select",
        "from",
        "where",
        "order",
        "group",
        "having",
    ]:
        return f'"{identifier}"'

    return identifier


def _get_admin_token() -> Optional[str]:
    """Get admin token from environment variable."""
    return os.getenv("DUCKALOG_ADMIN_TOKEN")


def _get_cors_origins() -> List[str]:
    """Get CORS origins from environment variable or use secure defaults."""
    # Check for custom CORS origins
    custom_origins = os.getenv("DUCKALOG_CORS_ORIGINS")
    if custom_origins:
        # Split comma-separated origins and strip whitespace
        return [origin.strip() for origin in custom_origins.split(",") if origin.strip()]

    # Default to secure localhost-only origins
    return [
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://localhost:9000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:9000",
        "http://127.0.0.1:5173",
    ]


def _is_mutating_method(method: str) -> bool:
    """Check if HTTP method is mutating (requires auth)."""
    return method.upper() in {"POST", "PUT", "DELETE"}


def _check_auth(request: Request) -> Optional[Response]:
    """Check authentication for mutating endpoints.

    Returns:
        None if auth is valid or not required
        JSONResponse with 401 if auth is required but invalid/missing
    """
    admin_token = _get_admin_token()

    # If no admin token is configured, allow all requests (local mode)
    if not admin_token:
        return None

    # Check if this is a mutating endpoint
    if not _is_mutating_method(request.method):
        return None

    # Check Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            {"error": "Authorization required for mutating operations"}, status_code=401
        )

    token = auth_header[7:]  # Remove "Bearer " prefix
    if token != admin_token:
        return JSONResponse({"error": "Invalid authorization token"}, status_code=401)

    return None


try:
    from datastar_py import ServerSentEventGenerator as SSE
except ImportError as exc:
    raise ImportError(
        "Datastar dependencies not found. Install with: pip install datastar datastar-python"
    ) from exc


class UIError(Exception):
    """UI-related error.

    This exception is raised for errors specific to the web UI functionality,
    such as template rendering, request handling, or response generation.
    """


class UIServer:
    """Main UI server class for Duckalog catalog dashboard.

    This class encapsulates the Starlette application and provides endpoints for
    catalog management, schema inspection, query execution, and data export.
    """

    def __init__(self, config_path: str, host: str = "127.0.0.1", port: int = 8000):
        """Initialize the UI server.

        Args:
            config_path: Path to the Duckalog configuration file.
            host: Host address to bind the server to.
            port: Port number to listen on.
        """
        self.config_path = Path(config_path)
        self.host = host
        self.port = port
        self.config: Optional[Config] = None

        # Background task result storage
        self._task_results: Dict[str, Dict[str, Any]] = {}

        # Track original config format
        self._config_format: str = "json"  # Default to JSON

        # Load configuration
        self._load_config()

        # Create Starlette app with secure CORS middleware
        routes = [
            Route("/", self._dashboard),
            Route("/api/config", self._get_config),
            Route("/api/config", self._update_config, methods=["POST"]),
            Route("/api/views", self._get_views),
            Route("/api/views", self._create_view, methods=["POST"]),
            Route("/api/views/{view_name}", self._update_view, methods=["PUT"]),
            Route("/api/views/{view_name}", self._delete_view, methods=["DELETE"]),
            Route("/api/schema/{view_name}", self._get_schema),
            Route("/api/rebuild", self._rebuild_catalog, methods=["POST"]),
            Route("/api/query", self._execute_query, methods=["POST"]),
            Route("/api/export", self._export_data, methods=["POST"]),
            Route("/api/tasks/{task_id}", self._get_task_result),
        ]

        # Get secure CORS origins (localhost-only by default, custom via env var)
        cors_origins = _get_cors_origins()

        # Create app first, then apply middleware
        self.app = Starlette(routes=routes)

        # Apply CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=False,  # Disabled by default for security
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"],
        )

    @property
    def task_results(self) -> Dict[str, Dict[str, Any]]:
        """Access task results for testing."""
        return self._task_results

    def _load_config(self) -> None:
        """Load the Duckalog configuration."""
        try:
            # Detect file format by file extension and content
            if self.config_path.exists():
                if self.config_path.suffix.lower() in ['.yaml', '.yml']:
                    self._config_format = 'yaml'
                elif self.config_path.suffix.lower() == '.json':
                    self._config_format = 'json'
                else:
                    # Try to detect by content
                    content = self.config_path.read_text().strip()
                    if content.startswith('{') or content.startswith('['):
                        self._config_format = 'json'
                    else:
                        self._config_format = 'yaml'

            self.config = load_config(str(self.config_path))
        except ConfigError as exc:
            log_error(
                "Failed to load config",
                config_path=str(self.config_path),
                error=str(exc),
            )
            raise UIError(f"Failed to load config: {exc}")

    def _get_config(self, request: Request) -> Response:
        """Get current configuration as JSON."""
        if not self.config:
            return JSONResponse({"error": "No configuration loaded"}, status_code=500)

        try:
            config_dict = self.config.model_dump(mode="json")
            return JSONResponse(config_dict)
        except Exception as exc:
            log_error("Failed to serialize config", error=str(exc))
            return JSONResponse(
                {"error": f"Failed to serialize config: {exc}"}, status_code=500
            )

    async def _update_config(self, request: Request) -> Response:
        """Update configuration with new view data."""
        if not self.config:
            return JSONResponse({"error": "No configuration loaded"}, status_code=500)

        # Check authentication for mutating endpoint
        auth_result = _check_auth(request)
        if auth_result:
            return auth_result

        try:
            # Get request body
            body = await request.json()
            if not isinstance(body, dict):
                return JSONResponse({"error": "Invalid request body"}, status_code=400)

            # Create temporary config with new view
            current_config_dict = self.config.model_dump(mode="json")

            # Handle different operations
            if "view" in body:
                # Add new view
                if "views" not in current_config_dict:
                    current_config_dict["views"] = []
                current_config_dict["views"].append(body["view"])
            elif "views" in body:
                # Replace entire views list
                current_config_dict["views"] = body["views"]

            # Validate updated config
            updated_config = Config.model_validate(current_config_dict)

            # Write back to file preserving format
            self._write_config_preserving_format(updated_config)

            return JSONResponse(
                {"success": True, "config": updated_config.model_dump(mode="json")}
            )

        except Exception as exc:
            log_error("Failed to update config", error=str(exc))
            return JSONResponse(
                {"error": f"Failed to update config: {exc}"}, status_code=500
            )

    def _write_config_preserving_format(self, config: Config) -> None:
        """Write configuration to file, preserving original format."""
        try:
            if self._config_format == 'yaml':
                # Try to preserve YAML formatting using ruamel.yaml if available
                try:
                    from ruamel.yaml import YAML
                    yaml = YAML()
                    yaml.preserve_quotes = True
                    yaml.width = 4096  # Prevent line wrapping

                    # Convert to dict for YAML serialization
                    config_dict = config.model_dump(mode='json')

                    # Write to temporary YAML file first
                    temp_path = self.config_path.with_suffix(".tmp")
                    try:
                        with open(temp_path, 'w') as f:
                            yaml.dump(config_dict, f)

                        # Atomic move
                        shutil.move(str(temp_path), str(self.config_path))
                    except Exception as exc:
                        # Clean up temp file if it exists
                        if temp_path.exists():
                            temp_path.unlink()
                        raise exc

                except ImportError:
                    # Fallback to basic YAML if ruamel.yaml not available
                    import yaml

                    config_dict = config.model_dump(mode='json')
                    config_yaml = yaml.dump(config_dict, default_flow_style=False, sort_keys=False)

                    # Use the original atomic write method
                    self._write_config_atomic(config_yaml)

            else:
                # JSON format - use existing method
                config_json = config.model_dump_json(indent=2)
                self._write_config_atomic(config_json)

        except Exception as exc:
            raise UIError(f"Failed to write config in {self._config_format} format: {exc}")

    def _write_config_atomic(self, config_data: str) -> None:
        """Atomically write configuration to file."""
        # Write to temporary file first
        temp_path = self.config_path.with_suffix(".tmp")
        try:
            temp_path.write_text(config_data)

            # Atomic move
            shutil.move(str(temp_path), str(self.config_path))
        except Exception as exc:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            raise UIError(f"Failed to write config: {exc}")

    def _get_views(self, request: Request) -> Response:
        """Get all views from configuration."""
        if not self.config:
            return JSONResponse({"error": "No configuration loaded"}, status_code=500)

        try:
            views_data = [view.model_dump(mode="json") for view in self.config.views]
            return JSONResponse({"views": views_data})
        except Exception as exc:
            log_error("Failed to get views", error=str(exc))
            return JSONResponse(
                {"error": f"Failed to get views: {exc}"}, status_code=500
            )

    async def _create_view(self, request: Request) -> Response:
        """Create a new view in configuration."""
        if not self.config:
            return JSONResponse({"error": "No configuration loaded"}, status_code=500)

        # Check authentication for mutating endpoint
        auth_result = _check_auth(request)
        if auth_result:
            return auth_result

        try:
            body = await request.json()
            if not isinstance(body, dict) or "name" not in body:
                return JSONResponse({"error": "Invalid request body"}, status_code=400)

            # Check for duplicate view name
            existing_names = {view.name for view in self.config.views}
            if body["name"] in existing_names:
                return JSONResponse(
                    {"error": f"View name '{body['name']}' already exists"},
                    status_code=400,
                )

            # Create new view (simplified - would use full ViewConfig validation)
            new_view_data = {
                "name": body["name"],
                "sql": body.get("sql"),
                "source": body.get("source"),
                "uri": body.get("uri"),
                "database": body.get("database"),
                "table": body.get("table"),
                "catalog": body.get("catalog"),
                "options": body.get("options", {}),
                "description": body.get("description"),
                "tags": body.get("tags", []),
            }

            # Add to config
            current_config_dict = self.config.model_dump(mode="json")
            if "views" not in current_config_dict:
                current_config_dict["views"] = []
            current_config_dict["views"].append(new_view_data)

            # Validate and save
            updated_config = Config.model_validate(current_config_dict)
            self._write_config_preserving_format(updated_config)
            self._load_config()  # Reload config

            return JSONResponse({"success": True, "view": new_view_data})

        except Exception as exc:
            log_error("Failed to create view", error=str(exc))
            return JSONResponse(
                {"error": f"Failed to create view: {exc}"}, status_code=500
            )

    async def _update_view(self, request: Request) -> Response:
        """Update an existing view."""
        if not self.config:
            return JSONResponse({"error": "No configuration loaded"}, status_code=500)

        # Check authentication for mutating endpoint
        auth_result = _check_auth(request)
        if auth_result:
            return auth_result

        try:
            view_name = request.path_params["view_name"]
            body = await request.json()

            # Find existing view
            existing_view = None
            for view in self.config.views:
                if view.name == view_name:
                    existing_view = view
                    break

            if not existing_view:
                return JSONResponse(
                    {"error": f"View '{view_name}' not found"}, status_code=404
                )

            # Update view data
            updated_view_data = existing_view.model_dump(mode="json")
            updated_view_data.update(body)

            # Validate updated view
            from .config import ViewConfig

            updated_view = ViewConfig.model_validate(updated_view_data)

            # Update in config
            current_config_dict = self.config.model_dump(mode="json")
            for i, view in enumerate(current_config_dict["views"]):
                if view["name"] == view_name:
                    current_config_dict["views"][i] = updated_view.model_dump(
                        mode="json"
                    )
                    break

            # Save and reload
            updated_config = Config.model_validate(current_config_dict)
            self._write_config_preserving_format(updated_config)
            self._load_config()

            return JSONResponse(
                {"success": True, "view": updated_view.model_dump(mode="json")}
            )

        except Exception as exc:
            log_error("Failed to update view", error=str(exc))
            return JSONResponse(
                {"error": f"Failed to update view: {exc}"}, status_code=500
            )

    async def _delete_view(self, request: Request) -> Response:
        """Delete a view from configuration."""
        if not self.config:
            return JSONResponse({"error": "No configuration loaded"}, status_code=500)

        # Check authentication for mutating endpoint
        auth_result = _check_auth(request)
        if auth_result:
            return auth_result

        try:
            view_name = request.path_params["view_name"]

            # Check if view exists
            existing_view_index = None
            for i, view in enumerate(self.config.views):
                if view.name == view_name:
                    existing_view_index = i
                    break

            if existing_view_index is None:
                return JSONResponse(
                    {"error": f"View '{view_name}' not found"}, status_code=404
                )

            # Remove view from config
            current_config_dict = self.config.model_dump(mode="json")
            del current_config_dict["views"][existing_view_index]

            # Save and reload
            updated_config = Config.model_validate(current_config_dict)
            self._write_config_preserving_format(updated_config)
            self._load_config()

            return JSONResponse({"success": True})

        except Exception as exc:
            log_error("Failed to delete view", error=str(exc))
            return JSONResponse(
                {"error": f"Failed to delete view: {exc}"}, status_code=500
            )

    def _get_schema(self, request: Request) -> Response:
        """Get schema information for a specific view."""
        if not self.config:
            return JSONResponse({"error": "No configuration loaded"}, status_code=500)

        try:
            view_name = request.path_params["view_name"]

            # Check if view exists
            target_view = None
            for view in self.config.views:
                if view.name == view_name:
                    target_view = view
                    break

            if not target_view:
                return JSONResponse(
                    {"error": f"View '{view_name}' not found"}, status_code=404
                )

            # Get schema from DuckDB (simplified implementation)
            import duckdb

            # Connect to database
            db_path = self.config.duckdb.database
            conn = duckdb.connect(db_path)

            try:
                # Get column info
                result = conn.execute(f"DESCRIBE {target_view.name}")
                columns = []
                for row in result.fetchall():
                    columns.append(
                        {
                            "name": row[0],
                            "type": row[1],
                            "nullable": row[2] == "YES",
                            "default": row[3],
                        }
                    )

                return JSONResponse({"view": view_name, "columns": columns})
            finally:
                conn.close()

        except Exception as exc:
            log_error("Failed to get schema", error=str(exc))
            return JSONResponse(
                {"error": f"Failed to get schema: {exc}"}, status_code=500
            )

    async def _rebuild_catalog(self, request: Request, background_tasks: BackgroundTasks) -> Response:
        """Rebuild the DuckDB catalog from current configuration."""
        if not self.config:
            return JSONResponse({"error": "No configuration loaded"}, status_code=500)

        # Check authentication for mutating endpoint
        auth_result = _check_auth(request)
        if auth_result:
            return auth_result

        try:
            # Generate task ID and create result store
            task_id = str(uuid.uuid4())
            result_store = {"task_id": task_id, "status": "pending"}
            self._task_results[task_id] = result_store

            # Add background task
            background_tasks.add_task(_rebuild_catalog_task, self.config, result_store)

            # Return task ID for client to poll results
            return JSONResponse({"task_id": task_id, "status": "pending"})

        except Exception as exc:
            log_error("Failed to rebuild catalog", error=str(exc))
            return JSONResponse({"error": f"Failed to rebuild catalog: {exc}"}, status_code=500)

    async def _execute_query(self, request: Request, background_tasks: BackgroundTasks) -> Response:
        """Execute a SQL query and return results."""
        if not self.config:
            return JSONResponse({"error": "No configuration loaded"}, status_code=500)

        try:
            body = await request.json()
            if not isinstance(body, dict) or "query" not in body:
                return JSONResponse({"error": "Invalid request body"}, status_code=400)

            query = body["query"]
            limit = body.get("limit", 100)

            # Validate query is read-only and single-statement
            try:
                validated_query = _validate_read_only_query(query)
            except ValueError as exc:
                return JSONResponse({"error": f"Invalid query: {exc}"}, status_code=400)

            # Add LIMIT clause if specified
            if limit:
                limited_query = f"{validated_query} LIMIT {limit}"
            else:
                limited_query = validated_query

            # Generate task ID and create result store
            task_id = str(uuid.uuid4())
            result_store = {"task_id": task_id, "status": "pending"}
            self._task_results[task_id] = result_store

            # Add background task
            background_tasks.add_task(_execute_query_task, self.config, limited_query, result_store)

            # Return task ID for client to poll results
            return JSONResponse({"task_id": task_id, "status": "pending"})

        except Exception as exc:
            log_error("Failed to execute query", error=str(exc))
            return JSONResponse(
                {"error": f"Failed to execute query: {exc}"}, status_code=500
            )

    async def _get_task_result(self, request: Request) -> Response:
        """Get the result of a background task."""
        try:
            task_id = request.path_params.get("task_id")
            if not task_id or task_id not in self._task_results:
                return JSONResponse({"error": "Task not found"}, status_code=404)

            result = self._task_results[task_id]

            # If task is completed and successful
            if result.get("status") == "completed" and result.get("success"):
                # Handle export tasks by generating the actual file
                if "format" in result:
                    format_type = result.get("format", "").lower()
                    data = result.get("data", [])
                    columns = result.get("columns", [])

                    if format_type == "csv":
                        return self._export_csv(data, columns)
                    elif format_type == "parquet":
                        return self._export_parquet(data, columns)
                    elif format_type == "excel":
                        return self._export_excel(data, columns)
                    else:
                        return JSONResponse({"error": f"Unsupported format: {format_type}"}, status_code=400)

                # Regular query task, return JSON response with data
                return JSONResponse(result)
            elif result.get("status") == "failed":
                return JSONResponse(result)
            else:
                # Task still pending or in progress
                return JSONResponse({"task_id": task_id, "status": result.get("status", "pending")})

        except Exception as exc:
            log_error("Failed to get task result", error=str(exc))
            return JSONResponse({"error": f"Failed to get task result: {exc}"}, status_code=500)

    async def _export_data(self, request: Request, background_tasks: BackgroundTasks) -> Response:
        """Export query results in various formats."""
        if not self.config:
            return JSONResponse({"error": "No configuration loaded"}, status_code=500)

        try:
            body = await request.json()
            if not isinstance(body, dict):
                return JSONResponse({"error": "Invalid request body"}, status_code=400)

            format_type = body.get("format", "csv").lower()
            query = body.get("query")
            view_name = body.get("view")

            # Determine what to export
            if query:
                # Validate custom query
                try:
                    export_query = _validate_read_only_query(query)
                except ValueError as exc:
                    return JSONResponse({"error": f"Invalid query: {exc}"}, status_code=400)
            elif view_name:
                # Validate view name exists and create safe identifier
                view_names = {view.name for view in self.config.views}
                if view_name not in view_names:
                    return JSONResponse({"error": f"View '{view_name}' not found"}, status_code=404)
                safe_view_name = _safe_identifier(view_name)
                export_query = f"SELECT * FROM {safe_view_name}"
            else:
                return JSONResponse(
                    {"error": "Must provide either 'query' or 'view'"}, status_code=400
                )

            # Validate format type
            if format_type not in ["csv", "parquet", "excel"]:
                return JSONResponse(
                    {"error": f"Unsupported format: {format_type}"}, status_code=400
                )

            # Generate task ID and create result store
            task_id = str(uuid.uuid4())
            result_store = {"task_id": task_id, "status": "pending", "format": format_type}
            self._task_results[task_id] = result_store

            # Add background task
            background_tasks.add_task(_export_data_task, self.config, export_query, format_type, result_store)

            # Return task ID for client to poll results
            return JSONResponse({"task_id": task_id, "status": "pending", "format": format_type})

        except Exception as exc:
            log_error("Failed to export data", error=str(exc))
            return JSONResponse(
                {"error": f"Failed to export data: {exc}"}, status_code=500
            )

    def _export_csv(self, data: List[Dict[str, Any]], columns: List[str] = None) -> Response:
        """Export data as CSV."""
        import csv

        output = io.StringIO()

        if not data:
            # For empty data, use provided columns or create empty CSV
            if columns:
                writer = csv.DictWriter(output, fieldnames=columns)
                writer.writeheader()
            else:
                # No columns available, create empty CSV
                writer = csv.writer(output)
        else:
            # Use actual data columns for consistency
            fieldnames = data[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        return Response(
            output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=export.csv"},
        )

    def _export_parquet(self, data: List[Dict[str, Any]], columns: List[str] = None) -> Response:
        """Export data as Parquet."""
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError:
            return JSONResponse(
                {"error": "PyArrow not installed for Parquet export"}, status_code=500
            )

        if not data:
            # For empty data, create schema from columns if available
            if columns:
                # Create empty table with proper schema
                schema = pa.schema([(col, pa.string()) for col in columns])
                table = pa.Table.from_pydict({col: [] for col in columns}, schema=schema)
            else:
                # No column information, create truly empty table
                table = pa.table([])
        else:
            # Convert list of dictionaries to dictionary format for PyArrow
            if isinstance(data, list) and data and isinstance(data[0], dict):
                # Convert list of dicts to dict of lists
                pydict_data = {}
                for key in data[0].keys():
                    pydict_data[key] = [row.get(key) for row in data]
                table = pa.Table.from_pydict(pydict_data)
            else:
                # Data is already in correct format
                table = pa.Table.from_pydict(data)

        # Write to buffer
        buffer = io.BytesIO()
        pq.write_table(table, buffer)

        return Response(
            buffer.getvalue(),
            media_type="application/octet-stream",
            headers={"Content-Disposition": "attachment; filename=export.parquet"},
        )

    def _export_excel(self, data: List[Dict[str, Any]], columns: List[str] = None) -> Response:
        """Export data as Excel."""
        try:
            import pandas as pd
        except ImportError:
            return JSONResponse(
                {"error": "pandas not installed for Excel export"}, status_code=500
            )

        if not data:
            # For empty data, create DataFrame with columns if available
            if columns:
                df = pd.DataFrame(columns=columns)
            else:
                df = pd.DataFrame()
        else:
            df = pd.DataFrame(data)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Export")

        return Response(
            buffer.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=export.xlsx"},
        )

    def _dashboard(self, request: Request) -> Response:
        """Render the main dashboard HTML page using Datastar."""
        if not self.config:
            return HTMLResponse(
                "<html><body><h1>Error: No configuration loaded</h1></body></html>"
            )

        try:
            # Generate dashboard HTML with Datastar integration
            dashboard_html = self._generate_datastar_dashboard()

            return HTMLResponse(dashboard_html)

        except Exception as exc:
            log_error("Failed to render dashboard", error=str(exc))
            return HTMLResponse(f"<html><body><h1>Error: {exc}</h1></body></html>")

    def _generate_datastar_dashboard(self) -> str:
        """Generate a Datastar-powered dashboard HTML."""
        if not self.config:
            return "<html><body><h1>Error: No configuration loaded</h1></body></html>"

        views_data = [
            {
                "name": view.name,
                "source": view.source or "sql",
                "description": view.description or "",
                "tags": view.tags,
            }
            for view in self.config.views
        ]

        return f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Duckalog Catalog Dashboard</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <script type="module" src="https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.0-RC.6/bundles/datastar.js"></script>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    button {{ margin: 5px; padding: 10px; cursor: pointer; }}
                    .query-section {{ margin: 20px 0; }}
                    textarea {{ width: 100%; height: 100px; margin: 10px 0; }}
                    .results {{ margin: 20px 0; }}
                    .error {{ color: red; }}
                    .success {{ color: green; }}
                    input[type="text"] {{ padding: 8px; margin: 5px 0; width: 300px; }}
                </style>
            </head>
            <body data-signals="{{{{views: {json.dumps(views_data)}, selectedView: '', query: '', queryResults: null, message: '', messageType: 'info'}}}}">
                <h1>Duckalog Catalog Dashboard</h1>
                
                <div data-signals="message">
                    <div data-show="$message" class="$messageType" style="padding: 10px; margin: 10px 0; border-radius: 4px;">
                        $message
                    </div>
                </div>
                
                <div>
                    <h2>Views ($views.length)</h2>
                    <table>
                        <tr>
                            <th>Name</th>
                            <th>Source</th>
                            <th>Description</th>
                            <th>Tags</th>
                            <th>Actions</th>
                        </tr>
                        {"<tr data-each='view in views'>"}
                            <td>$view.name</td>
                            <td>$view.source</td>
                            <td>$view.description</td>
                            <td>$view.tags.join(', ')</td>
                            <td>
                                <button data-on-click="selectedView = view.name; query = 'SELECT * FROM ' + view.name + ' LIMIT 100'; message = 'Selected view: ' + view.name; messageType = 'success'">Select</button>
                                <button data-on-click="/api/schema/$view.name">GET</button>
                                <button data-on-click="/api/views/$view.name" data-method="DELETE" data-confirm="Are you sure you want to delete this view?" data-success="message = 'View deleted successfully'; messageType = 'success'">Delete</button>
                            </td>
                        {"</tr>"}
                    </table>
                </div>
                
                <div class="query-section">
                    <h2>Query Runner</h2>
                    <textarea data-bind="query" placeholder="Enter SQL query..."></textarea>
                    <br>
                    <button data-on-click="/api/query" data-method="POST" data-body='{{"query": "$query"}}' data-success="queryResults = $response; message = 'Query executed successfully'; messageType = 'success'">Execute Query</button>
                    <button data-on-click="/api/export" data-method="POST" data-body='{{"query": "$query", "format": "csv"}}' data-download="export.csv">Export CSV</button>
                    <button data-on-click="/api/export" data-method="POST" data-body='{{"query": "$query", "format": "excel"}}' data-download="export.xlsx">Export Excel</button>
                    <button data-on-click="/api/export" data-method="POST" data-body='{{"query": "$query", "format": "parquet"}}' data-download="export.parquet">Export Parquet</button>
                </div>
                
                <div class="results">
                    <h3>Results</h3>
                    <div data-show="$queryResults">
                        <p>Returned $queryResults.count rows:</p>
                        <table data-show="$queryResults.rows.length > 0">
                            <tr>
                                {"<th data-each='col in queryResults.columns'>$col</th>"}
                            </tr>
                            {"<tr data-each='row in queryResults.rows'>"}
                                {"<td data-each='col in queryResults.columns'>$row[col]</td>"}
                            {"</tr>"}
                        </table>
                        <p data-show="$queryResults.rows.length == 0">No results returned.</p>
                    </div>
                    <div data-show="$queryResults == null">
                        No results to display. Run a query to see data.
                    </div>
                </div>
                
                <div>
                    <h2>Catalog Management</h2>
                    <button data-on-click="/api/rebuild" data-method="POST" data-success="message = 'Catalog rebuilt successfully'; messageType = 'success'">Rebuild Catalog</button>
                </div>
                
                <div>
                    <h2>Add New View</h2>
                    <div data-signals="newViewName: '', newViewSql: ''">
                        <input type="text" data-bind="newViewName" placeholder="View Name">
                        <br>
                        <textarea data-bind="newViewSql" placeholder="SQL for view..." rows="5" cols="60"></textarea>
                        <br>
                        <button data-on-click="/api/views" data-method="POST" data-body='{{"name": "$newViewName", "sql": "$newViewSql"}}' data-success="message = 'View created successfully'; messageType = 'success'; newViewName = ''; newViewSql = ''">Create View</button>
                    </div>
                </div>
            </body>
        </html>
        """

    def _generate_simple_dashboard(self) -> str:
        """Generate a simple dashboard HTML (fallback - DEPRECATED).

        This method is no longer used. All dashboard functionality now uses
        the Datastar-powered implementation in _generate_datastar_dashboard().
        This method is kept for reference only and should be removed in a future release.
        """
        if not self.config:
            return "<html><body><h1>Error: No configuration loaded</h1></body></html>"

        views_data = [
            {
                "name": view.name,
                "source": view.source or "sql",
                "description": view.description or "",
                "tags": view.tags,
            }
            for view in self.config.views
        ]

        return f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Duckalog Catalog Dashboard</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <script type="module" src="https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.0-RC.6/bundles/datastar.js"></script>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    button {{ margin: 5px; padding: 10px; cursor: pointer; }}
                    .query-section {{ margin: 20px 0; }}
                    textarea {{ width: 100%; height: 100px; margin: 10px 0; }}
                    .results {{ margin: 20px 0; }}
                    .error {{ color: red; }}
                    .success {{ color: green; }}
                </style>
            </head>
            <body>
                <h1>Duckalog Catalog Dashboard</h1>
                
                <div>
                    <h2>Views ({len(views_data)})</h2>
                    <table>
                        <tr>
                            <th>Name</th>
                            <th>Source</th>
                            <th>Description</th>
                            <th>Tags</th>
                            <th>Actions</th>
                        </tr>
                        {
            " ".join(
                [
                    f'''
                        <tr>
                            <td>{view["name"]}</td>
                            <td>{view["source"]}</td>
                            <td>{view["description"]}</td>
                            <td>{", ".join(view["tags"]) if view["tags"] else ""}</td>
                            <td>
                                <button onclick="selectView('{view["name"]}')">Select</button>
                                <button onclick="getSchema('{view["name"]}')">Schema</button>
                                <button onclick="deleteView('{view["name"]}')" style="background-color: #f44336; color: white;">Delete</button>
                            </td>
                        </tr>'''
                    for view in views_data
                ]
            )
        }
                    </table>
                </div>
                
                <div class="query-section">
                    <h2>Query Runner</h2>
                    <textarea id="query-input" placeholder="Enter SQL query..."></textarea>
                    <br>
                    <button onclick="executeQuery()">Execute Query</button>
                    <button onclick="exportData('csv')">Export CSV</button>
                    <button onclick="exportData('excel')">Export Excel</button>
                    <button onclick="exportData('parquet')">Export Parquet</button>
                </div>
                
                <div class="results">
                    <h3>Results</h3>
                    <div id="query-results">No results to display. Run a query to see data.</div>
                </div>
                
                <div>
                    <h2>Catalog Management</h2>
                    <button onclick="rebuildCatalog()">Rebuild Catalog</button>
                </div>
                
                <div>
                    <h2>Add New View</h2>
                    <input type="text" id="new-view-name" placeholder="View Name">
                    <br>
                    <textarea id="new-view-sql" placeholder="SQL for view..."></textarea>
                    <br>
                    <button onclick="createView()">Create View</button>
                </div>

                <script>
                    let selectedView = null;
                    
                    // API call functions
                    async function apiCall(url, method = 'GET', data = null) {{
                        const response = await fetch(url, {{
                            method,
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: data ? JSON.stringify(data) : undefined
                        }});
                        
                        if (!response.ok) {{
                            throw new Error(`API call failed: ${{response.statusText}}`);
                        }}
                        
                        return await response.json();
                    }}
                    
                    function selectView(viewName) {{
                        selectedView = viewName;
                        document.getElementById('query-input').value = `SELECT * FROM ${{viewName}} LIMIT 100`;
                        showMessage(`Selected view: ${{viewName}}`, 'success');
                    }}
                    
                    async function getSchema(viewName) {{
                        try {{
                            const result = await apiCall(`/api/schema/${{viewName}}`);
                            const schemaText = result.columns.map(col => 
                                `${{col.name}}: ${{col.type}} (${{col.nullable ? 'nullable' : 'not null'}})`
                            ).join('\\n');
                            alert(`Schema for ${{viewName}}:\\n${{schemaText}}`);
                        }} catch (error) {{
                            showMessage('Error getting schema: ' + error.message, 'error');
                        }}
                    }}
                    
                    async function deleteView(viewName) {{
                        if (!confirm(`Are you sure you want to delete view "${{viewName}}"?`)) return;
                        
                        try {{
                            await apiCall(`/api/views/${{viewName}}`, 'DELETE');
                            showMessage(`View "${{viewName}}" deleted successfully`, 'success');
                            location.reload(); // Reload to update the view list
                        }} catch (error) {{
                            showMessage('Error deleting view: ' + error.message, 'error');
                        }}
                    }}
                    
                    async function executeQuery() {{
                        const query = document.getElementById('query-input').value;
                        if (!query.trim()) {{
                            showMessage('Please enter a query', 'error');
                            return;
                        }}
                        
                        try {{
                            const result = await apiCall('/api/query', 'POST', {{ query }});
                            displayResults(result);
                        }} catch (error) {{
                            showMessage('Error executing query: ' + error.message, 'error');
                        }}
                    }}
                    
                    async function exportData(format) {{
                        const query = document.getElementById('query-input').value;
                        if (!query.trim()) {{
                            showMessage('Please enter a query to export', 'error');
                            return;
                        }}
                        
                        try {{
                            const response = await fetch('/api/export', {{
                                method: 'POST',
                                headers: {{ 'Content-Type': 'application/json' }},
                                body: JSON.stringify({{ query, format }})
                            }});
                            
                            if (!response.ok) {{
                                throw new Error(`Export failed: ${{response.statusText}}`);
                            }}
                            
                            // Create download link
                            const blob = await response.blob();
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = `export.${{format}}`;
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                            URL.revokeObjectURL(url);
                            
                            showMessage(`Data exported as ${{format.toUpperCase()}}`, 'success');
                        }} catch (error) {{
                            showMessage('Error exporting data: ' + error.message, 'error');
                        }}
                    }}
                    
                    async function rebuildCatalog() {{
                        if (!confirm('Rebuild the catalog? This may take a moment.')) return;
                        
                        try {{
                            const result = await apiCall('/api/rebuild', 'POST');
                            showMessage('Catalog rebuilt successfully', 'success');
                        }} catch (error) {{
                            showMessage('Error rebuilding catalog: ' + error.message, 'error');
                        }}
                    }}
                    
                    async function createView() {{
                        const name = document.getElementById('new-view-name').value;
                        const sql = document.getElementById('new-view-sql').value;
                        
                        if (!name.trim() || !sql.trim()) {{
                            showMessage('Please provide both name and SQL for the view', 'error');
                            return;
                        }}
                        
                        try {{
                            await apiCall('/api/views', 'POST', {{ name, sql }});
                            showMessage(`View "${{name}}" created successfully`, 'success');
                            document.getElementById('new-view-name').value = '';
                            document.getElementById('new-view-sql').value = '';
                            location.reload(); // Reload to update the view list
                        }} catch (error) {{
                            showMessage('Error creating view: ' + error.message, 'error');
                        }}
                    }}
                    
                    function displayResults(result) {{
                        const resultsDiv = document.getElementById('query-results');
                        
                        if (!result.rows || result.rows.length === 0) {{
                            resultsDiv.innerHTML = '<p>No results returned.</p>';
                            return;
                        }}
                        
                        let html = `<p>Returned ${{result.count}} rows:</p>`;
                        html += '<table>';
                        
                        // Header row
                        html += '<tr>';
                        result.columns.forEach(col => {{
                            html += `<th>${{col}}</th>`;
                        }});
                        html += '</tr>';
                        
                        // Data rows
                        result.rows.forEach(row => {{
                            html += '<tr>';
                            result.columns.forEach(col => {{
                                html += `<td>${{row[col] || ''}}</td>`;
                            }});
                            html += '</tr>';
                        }});
                        
                        html += '</table>';
                        resultsDiv.innerHTML = html;
                    }}
                    
                    function showMessage(message, type) {{
                        const resultsDiv = document.getElementById('query-results');
                        const className = type === 'error' ? 'error' : 'success';
                        resultsDiv.innerHTML = `<p class="${{className}}">${{message}}</p>`;
                    }}
                </script>
            </body>
        </html>
        """

    def run(self) -> None:
        """Start the UI server."""
        log_info(
            "Starting UI server",
            config_path=str(self.config_path),
            host=self.host,
            port=self.port,
        )

        import uvicorn

        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="warning",  # Reduce uvicorn logging noise
        )
