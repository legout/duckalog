"""Import resolution extracted from the legacy loader with DI hooks."""

from __future__ import annotations

import concurrent.futures
import json
import os
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union, TYPE_CHECKING
import threading

if TYPE_CHECKING:
    from ..models import Config

import yaml

from duckalog.errors import (
    CircularImportError,
    ConfigError,
    DuplicateNameError,
    ImportError,
    ImportFileNotFoundError,
    ImportValidationError,
    PathResolutionError,
)
from .env import _interpolate_env
from ..validators import (
    log_debug,
    log_info,
    _resolve_path_core,
    _resolve_paths_in_config,
)
from ..loading.sql import load_sql_files_from_config, process_sql_file_references
from ..validators import validate_path_security
from ..security.path import path_resolution_context
from .env import EnvCache, DefaultEnvProcessor, _load_dotenv_files_for_config
from ...performance import PerformanceMetrics

from .base import ImportContext, ImportResolver


@dataclass
class RequestContext:
    """Context for request-scoped caching and state management."""

    env_cache: EnvCache = field(default_factory=EnvCache)
    metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    import_context: ImportContext = field(init=False)
    max_cache_size: int = 1000  # Maximum number of configs to cache

    def __post_init__(self):
        self.import_context = ImportContext(
            metrics=self.metrics, max_cache_size=self.max_cache_size
        )

    def clear(self) -> None:
        self.env_cache.clear()
        with self.import_context._lock:
            self.import_context.visited_files.clear()
            self.import_context.import_stack.clear()
            self.import_context.config_cache.clear()
            self.import_context.import_chain.clear()

    def _enforce_cache_limit(self) -> None:
        """Enforce cache size limit to prevent memory issues with large config trees."""
        self.import_context._enforce_cache_limit()


@contextmanager
def request_cache_scope(context: Optional[RequestContext] = None):
    ctx = context or RequestContext()
    with path_resolution_context():
        try:
            yield ctx
        finally:
            ctx.clear()


def _normalize_uri(uri: str) -> str:
    if not _is_remote_uri(uri):
        return uri

    from urllib.parse import urlparse

    parsed = urlparse(uri)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc
    if netloc:
        if "@" in netloc:
            auth, host = netloc.rsplit("@", 1)
        else:
            auth, host = "", netloc
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"
        netloc = f"{auth}@{host}" if auth else host
    path = parsed.path.rstrip("/") if parsed.path != "/" else "/"
    query = f"?{parsed.query}" if parsed.query else ""
    fragment = f"#{parsed.fragment}" if parsed.fragment else ""
    return f"{scheme}://{netloc}{path}{query}{fragment}"


def _is_remote_uri(path: str) -> bool:
    try:
        from duckalog.remote_config import is_remote_uri as check_remote_uri

        return check_remote_uri(path)
    except ImportError:
        remote_schemes = [
            "http://",
            "https://",
            "s3://",
            "gcs://",
            "az://",
            "abfs://",
            "sftp://",
        ]
        return any(path.startswith(scheme) for scheme in remote_schemes)


def _normalize_path(path: str) -> str:
    """Normalize path for consistent comparison, handling macOS /var symlink."""
    if _is_remote_uri(path):
        return _normalize_uri(path)
    return str(Path(path).resolve())


def _expand_glob_patterns(
    patterns: list[str],
    base_path: str,
    filesystem: Optional[Any] = None,
) -> list[str]:
    import glob as glob_module

    resolved_files: list[str] = []
    excluded_files: set[str] = set()

    for pattern in patterns:
        if pattern.startswith("!"):
            exclude_pattern = pattern[1:]
            if not _is_remote_uri(exclude_pattern):
                exclude_pattern = str(Path(base_path).parent / exclude_pattern)
            if _is_remote_uri(exclude_pattern):
                continue

            try:
                if filesystem is not None and hasattr(filesystem, "glob"):
                    matches = filesystem.glob(exclude_pattern)
                else:
                    matches = glob_module.glob(exclude_pattern, recursive=True)
                excluded_files.update(_normalize_path(m) for m in matches)
            except Exception:
                continue
            continue

        if not _is_remote_uri(pattern):
            resolved_pattern = str(Path(base_path).parent / pattern)
        else:
            if "*" in pattern or "?" in pattern:
                raise ImportError(
                    f"Glob patterns are not supported for remote URIs: {pattern}"
                )
            resolved_pattern = pattern

        if _is_remote_uri(resolved_pattern):
            resolved_files.append(resolved_pattern)
        else:
            try:
                if filesystem is not None and hasattr(filesystem, "glob"):
                    matches = filesystem.glob(resolved_pattern)
                else:
                    matches = glob_module.glob(resolved_pattern, recursive=True)

                if not matches:
                    if "*" not in resolved_pattern and "?" not in resolved_pattern:
                        exists = False
                        if filesystem is not None:
                            exists = filesystem.exists(resolved_pattern)
                        else:
                            exists = Path(resolved_pattern).exists()

                        if exists:
                            resolved_files.append(_normalize_path(resolved_pattern))
                        else:
                            raise ImportFileNotFoundError(
                                f"Imported file not found: {pattern}",
                                import_path=pattern,
                            )
                    else:
                        raise ImportFileNotFoundError(
                            f"No files match pattern: {pattern}",
                            import_path=pattern,
                        )
                else:
                    resolved_files.extend(sorted(_normalize_path(m) for m in matches))
            except Exception as exc:
                if isinstance(exc, ImportFileNotFoundError):
                    raise
                raise ImportError(
                    f"Failed to expand glob pattern '{pattern}': {exc}"
                ) from exc

    result = [f for f in resolved_files if f not in excluded_files]
    seen: set[str] = set()
    final_result: list[str] = []
    for f in result:
        if f not in seen:
            seen.add(f)
            final_result.append(f)

    return final_result


def _resolve_import_path(import_path: str, base_path: str) -> str:
    if _is_remote_uri(import_path):
        return import_path

    if Path(import_path).is_absolute():
        return import_path

    base_dir = Path(base_path).parent
    try:
        resolved_path = _resolve_path_core(import_path, base_dir, check_exists=True)
        return str(resolved_path)
    except ValueError as exc:
        raise PathResolutionError(
            f"Failed to resolve import path: {import_path}",
            f"Resolved path does not exist: {exc}",
        ) from exc


def _normalize_imports_for_processing(
    imports: Union[list[str], Any],
    base_path: str,
    filesystem: Optional[Any] = None,
) -> list[tuple[str, bool, Optional[str]]]:
    from ..models import ImportEntry

    if isinstance(imports, list):
        normalized = []
        for item in imports:
            if isinstance(item, str):
                normalized.append((item, True, None))
            elif isinstance(item, ImportEntry):
                normalized.append((item.path, item.override, None))
            elif isinstance(item, dict):
                path = item.get("path")
                override = item.get("override", True)
                if path:
                    normalized.append((path, override, None))
            else:
                raise ConfigError(
                    f"Invalid import format: expected string or ImportEntry, got {type(item)}"
                )
        return normalized

    if isinstance(imports, dict):
        normalized = []
        for section_name, field_value in imports.items():
            if field_value is None:
                continue
            if not isinstance(field_value, list):
                field_value = [field_value]

            for item in field_value:
                if isinstance(item, str):
                    normalized.append((item, True, section_name))
                elif isinstance(item, dict):
                    path = item.get("path")
                    override = item.get("override", True)
                    if path:
                        normalized.append((path, override, section_name))
                elif hasattr(item, "path"):
                    normalized.append(
                        (item.path, getattr(item, "override", True), section_name)
                    )
        return normalized

    if hasattr(imports, "model_fields"):
        normalized = []
        for field_name, field_value in imports:
            if field_value is None:
                continue
            section_name = field_name
            for item in field_value:
                if isinstance(item, str):
                    normalized.append((item, True, section_name))
                elif hasattr(item, "path"):
                    normalized.append(
                        (item.path, getattr(item, "override", True), section_name)
                    )
        return normalized

    return [(str(path), True, None) for path in imports]


def _deep_merge_dict(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, override_value in override.items():
        if key not in result:
            result[key] = override_value
        else:
            base_value = result[key]
            if isinstance(base_value, dict) and isinstance(override_value, dict):
                result[key] = _deep_merge_dict(base_value, override_value)
            elif isinstance(base_value, list) and isinstance(override_value, list):
                result[key] = base_value + override_value
            else:
                result[key] = override_value
    return result


def _merge_config_dicts(
    base: dict[str, Any],
    override: dict[str, Any],
    override_mode: bool = True,
) -> dict[str, Any]:
    """Merge two config dictionaries with override control.

    In Duckalog's convention, the second argument (override) wins over the first (base).
    """
    override_imports = override.get("imports", [])
    base_dict = {k: v for k, v in base.items() if k != "imports"}
    override_dict = {k: v for k, v in override.items() if k != "imports"}

    if override_mode:
        merged_dict = _deep_merge_dict(base_dict, override_dict)
    else:
        # Non-overriding merge: fill in missing fields recursively
        # We want base_dict to win over override_dict
        merged_dict = _deep_merge_dict(override_dict, base_dict)

    merged_dict["imports"] = override_imports
    return merged_dict


def _merge_section_specific_dicts(
    target_dict: dict[str, Any],
    source_dict: dict[str, Any],
    section_name: str,
    override_mode: bool = True,
) -> dict[str, Any]:
    """Merge only a specific section from source_dict into target_dict."""
    if section_name not in source_dict:
        return target_dict

    source_section = source_dict.get(section_name)
    result = target_dict.copy()

    if section_name in result:
        target_section = result[section_name]

        if override_mode:
            if isinstance(target_section, dict) and isinstance(source_section, dict):
                result[section_name] = _deep_merge_dict(target_section, source_section)
            elif isinstance(target_section, list) and isinstance(source_section, list):
                result[section_name] = target_section + source_section
            else:
                result[section_name] = source_section
        else:
            if isinstance(target_section, dict) and isinstance(source_section, dict):
                for key, value in source_section.items():
                    if key not in target_section or target_section[key] is None:
                        if not isinstance(result[section_name], dict):
                            result[section_name] = {}
                        else:
                            result[section_name] = result[section_name].copy()
                        result[section_name][key] = value
            elif isinstance(target_section, list) and isinstance(source_section, list):
                for item in source_section:
                    if item not in target_section:
                        result[section_name].append(item)
            else:
                if target_section is None:
                    result[section_name] = source_section
    else:
        result[section_name] = source_section

    return result


def _validate_unique_names(config: Any, context: ImportContext) -> None:
    view_names: dict[tuple[Optional[str], str], int] = {}
    duplicates = []

    views = config.views if hasattr(config, "views") else config.get("views", [])
    for view in views:
        name = view.name if hasattr(view, "name") else view.get("name")
        db_schema = (
            view.db_schema if hasattr(view, "db_schema") else view.get("db_schema")
        )
        key = (db_schema, name)
        if key in view_names:
            schema_part = f"{db_schema}." if db_schema else ""
            duplicates.append(f"{schema_part}{name}")
        else:
            view_names[key] = 1

    if duplicates:
        raise DuplicateNameError(
            f"Duplicate view name(s) found: {', '.join(sorted(set(duplicates)))}",
            name_type="view",
            duplicate_names=sorted(set(duplicates)),
        )

    catalog_names: dict[str, int] = {}
    duplicates = []
    iceberg_catalogs = (
        config.iceberg_catalogs
        if hasattr(config, "iceberg_catalogs")
        else config.get("iceberg_catalogs", [])
    )
    for catalog in iceberg_catalogs:
        name = catalog.name if hasattr(catalog, "name") else catalog.get("name")
        if name in catalog_names:
            duplicates.append(name)
        else:
            catalog_names[name] = 1

    if duplicates:
        raise DuplicateNameError(
            f"Duplicate Iceberg catalog name(s) found: {', '.join(sorted(set(duplicates)))}",
            name_type="iceberg_catalog",
            duplicate_names=sorted(set(duplicates)),
        )

    semantic_model_names: dict[str, int] = {}
    duplicates = []
    semantic_models = (
        config.semantic_models
        if hasattr(config, "semantic_models")
        else config.get("semantic_models", [])
    )
    for sm in semantic_models:
        name = sm.name if hasattr(sm, "name") else sm.get("name")
        if name in semantic_model_names:
            duplicates.append(name)
        else:
            semantic_model_names[name] = 1

    if duplicates:
        raise DuplicateNameError(
            f"Duplicate semantic model name(s) found: {', '.join(sorted(set(duplicates)))}",
            name_type="semantic_model",
            duplicate_names=sorted(set(duplicates)),
        )

    attachment_aliases: dict[str, int] = {}
    duplicates = []
    attachments = (
        config.attachments
        if hasattr(config, "attachments")
        else config.get("attachments", {})
    )
    if hasattr(attachments, "duckdb"):
        duckdb_attachments = attachments.duckdb
        sqlite_attachments = attachments.sqlite
        postgres_attachments = attachments.postgres
        duckalog_attachments = attachments.duckalog
    else:
        duckdb_attachments = attachments.get("duckdb", [])
        sqlite_attachments = attachments.get("sqlite", [])
        postgres_attachments = attachments.get("postgres", [])
        duckalog_attachments = attachments.get("duckalog", [])

    for attachment in duckdb_attachments:
        alias = (
            attachment.alias
            if hasattr(attachment, "alias")
            else attachment.get("alias")
        )
        if alias in attachment_aliases:
            duplicates.append(f"duckdb.{alias}")
        else:
            attachment_aliases[alias] = 1

    for attachment in sqlite_attachments:
        alias = (
            attachment.alias
            if hasattr(attachment, "alias")
            else attachment.get("alias")
        )
        if alias in attachment_aliases:
            duplicates.append(f"sqlite.{alias}")
        else:
            attachment_aliases[alias] = 1

    for attachment in postgres_attachments:
        alias = (
            attachment.alias
            if hasattr(attachment, "alias")
            else attachment.get("alias")
        )
        if alias in attachment_aliases:
            duplicates.append(f"postgres.{alias}")
        else:
            attachment_aliases[alias] = 1

    for attachment in duckalog_attachments:
        alias = (
            attachment.alias
            if hasattr(attachment, "alias")
            else attachment.get("alias")
        )
        if alias in attachment_aliases:
            duplicates.append(f"duckalog.{alias}")
        else:
            attachment_aliases[alias] = 1

    if duplicates:
        raise DuplicateNameError(
            f"Duplicate attachment alias(es) found: {', '.join(sorted(set(duplicates)))}",
            name_type="attachment",
            duplicate_names=sorted(set(duplicates)),
        )


def _resolve_and_load_import(
    import_path: str,
    base_path: str,
    filesystem: Optional[Any],
    resolve_paths: bool,
    load_sql_files: bool,
    sql_file_loader: Optional[Any],
    import_context: ImportContext,
    current_stack: Optional[list[str]] = None,
) -> dict[str, Any]:
    if current_stack is None:
        current_stack = []

    try:
        metrics = import_context.metrics
        with (
            metrics.timer("path_resolution", path=import_path)
            if metrics
            else nullcontext()
        ):
            resolved_path = _resolve_import_path(import_path, base_path)
    except Exception as exc:
        raise ImportFileNotFoundError(
            f"Failed to resolve import path '{import_path}' from '{base_path}': {exc}",
            import_path=import_path,
            cause=exc,
        ) from exc

    normalized_path = _normalize_path(resolved_path)

    if normalized_path in current_stack:
        chain = " -> ".join(_normalize_uri(p) for p in current_stack + [resolved_path])
        raise CircularImportError(
            f"Circular import detected in import chain: {chain}",
            import_chain=current_stack + [resolved_path],
        )

    with import_context._lock:
        if normalized_path in import_context.visited_files:
            return {}
        import_context.visited_files.add(normalized_path)

    new_stack = current_stack + [resolved_path]

    try:
        if _is_remote_uri(resolved_path):
            from duckalog.remote_config import load_config_from_uri

            try:
                imported_config = load_config_from_uri(
                    uri=resolved_path,
                    load_sql_files=load_sql_files,
                    sql_file_loader=sql_file_loader,
                    resolve_paths=False,
                    filesystem=filesystem,
                )
                imported_dict = imported_config.model_dump(mode="json")
            except Exception as exc:
                raise ImportValidationError(
                    f"Failed to load remote config '{resolved_path}': {exc}",
                    import_path=resolved_path,
                    cause=exc,
                ) from exc
        else:
            config_path = Path(resolved_path)
            if not config_path.exists():
                raise ImportFileNotFoundError(
                    f"Imported file not found: {resolved_path}",
                    import_path=resolved_path,
                )

            try:
                with (
                    metrics.timer("file_io", path=resolved_path)
                    if metrics
                    else nullcontext()
                ):
                    if filesystem is not None:
                        with filesystem.open(resolved_path, "r") as f:
                            raw_text = f.read()
                    else:
                        raw_text = config_path.read_text()
            except OSError as exc:
                raise ImportValidationError(
                    f"Failed to read imported file '{resolved_path}': {exc}",
                    import_path=resolved_path,
                    cause=exc,
                ) from exc

            suffix = config_path.suffix.lower()
            with (
                metrics.timer("parsing", path=resolved_path)
                if metrics
                else nullcontext()
            ):
                if suffix in {".yaml", ".yml"}:
                    parsed = yaml.safe_load(raw_text)
                elif suffix == ".json":
                    parsed = json.loads(raw_text)
                else:
                    raise ImportValidationError(
                        f"Imported file must use .yaml, .yml, or .json extension: {resolved_path}",
                        import_path=resolved_path,
                    )

            if parsed is None or not isinstance(parsed, dict):
                raise ImportValidationError(
                    f"Imported file must define a mapping at the top level: {resolved_path}",
                    import_path=resolved_path,
                )

            with (
                metrics.timer("env_interpolation", path=resolved_path)
                if metrics
                else nullcontext()
            ):
                interpolated = _interpolate_env(parsed)
            imported_dict = interpolated

            if load_sql_files and "views" in imported_dict:
                from ..models import ViewConfig

                views_data = imported_dict.get("views", [])
                if isinstance(views_data, list):
                    views = []
                    for v_data in views_data:
                        try:
                            if isinstance(v_data, dict):
                                views.append(ViewConfig.model_validate(v_data))
                        except Exception:
                            pass
                    if views:
                        with (
                            metrics.timer("sql_processing", path=resolved_path)
                            if metrics
                            else nullcontext()
                        ):
                            updated_views, _ = process_sql_file_references(
                                views=views,
                                sql_file_loader=sql_file_loader,
                                config_file_path=str(resolved_path),
                                log_info_func=log_info,
                                log_debug_func=log_debug,
                                filesystem=filesystem,
                            )
                        imported_dict["views"] = [
                            v.model_dump(mode="json") for v in updated_views
                        ]

        with import_context._lock:
            import_context.config_cache[resolved_path] = imported_dict
            import_context.config_cache[normalized_path] = imported_dict
            import_context._enforce_cache_limit()

        raw_imports = imported_dict.get("imports", [])
        if raw_imports:
            normalized_nested = _normalize_imports_for_processing(
                raw_imports, base_path=resolved_path, filesystem=filesystem
            )
            for nested_path, nested_override, _ in normalized_nested:
                nested_imported_dict = _resolve_and_load_import(
                    import_path=nested_path,
                    base_path=resolved_path,
                    filesystem=filesystem,
                    resolve_paths=resolve_paths,
                    load_sql_files=load_sql_files,
                    sql_file_loader=sql_file_loader,
                    import_context=import_context,
                    current_stack=new_stack,
                )
                with (
                    metrics.timer("merge", path=nested_path)
                    if metrics
                    else nullcontext()
                ):
                    imported_dict = _merge_config_dicts(
                        nested_imported_dict, imported_dict, nested_override
                    )

        with import_context._lock:
            import_context.config_cache[resolved_path] = imported_dict
            import_context.config_cache[normalized_path] = imported_dict
        return imported_dict
    except Exception:
        raise


def _load_config_with_imports(
    file_path: str,
    content: Optional[str] = None,
    format: str = "yaml",
    filesystem: Optional[Any] = None,
    resolve_paths: bool = True,
    load_sql_files: bool = True,
    sql_file_loader: Optional[Any] = None,
    import_context: Optional[ImportContext] = None,
    load_dotenv: bool = True,
    env_cache: Optional[EnvCache] = None,
    current_stack: Optional[list[str]] = None,
) -> Any:
    if import_context is None:
        import_context = ImportContext()
    metrics = import_context.metrics
    env_cache = env_cache or EnvCache()
    if current_stack is None:
        current_stack = []

    config_path = Path(file_path)
    resolved_path = str(config_path.resolve())
    normalized_path = _normalize_path(resolved_path)

    with import_context._lock:
        if resolved_path in import_context.config_cache:
            cached = import_context.config_cache[resolved_path]
            from ..models import Config

            if isinstance(cached, Config):
                return cached
        import_context.visited_files.add(normalized_path)

    if normalized_path in current_stack:
        chain = " -> ".join(_normalize_uri(p) for p in current_stack + [resolved_path])
        raise CircularImportError(
            f"Circular import detected in import chain: {chain}",
            import_chain=current_stack + [resolved_path],
        )

    new_stack = current_stack + [resolved_path]

    try:
        env_file_patterns = [".env"]
        try:
            if Path(file_path).exists():
                with open(file_path, "r") as f:
                    raw_config = yaml.safe_load(f)
                    if (
                        raw_config
                        and isinstance(raw_config, dict)
                        and "env_files" in raw_config
                    ):
                        env_file_patterns = raw_config["env_files"]
        except Exception:
            pass

        if load_dotenv:
            with (
                metrics.timer("dotenv_loading", path=file_path)
                if metrics
                else nullcontext()
            ):
                _load_dotenv_files_for_config(
                    file_path, env_file_patterns, cache=env_cache, filesystem=filesystem
                )

        try:
            with (
                metrics.timer("file_io", path=resolved_path)
                if metrics
                else nullcontext()
            ):
                if filesystem is not None:
                    with filesystem.open(resolved_path, "r") as f:
                        raw_text = f.read()
                else:
                    raw_text = config_path.read_text()
        except OSError as exc:
            raise ConfigError(
                f"Failed to read config file '{file_path}': {exc}"
            ) from exc

        with metrics.timer("parsing", path=resolved_path) if metrics else nullcontext():
            if format == "yaml":
                parsed = yaml.safe_load(raw_text)
            elif format == "json":
                parsed = json.loads(raw_text)
            else:
                raise ConfigError(
                    "Config files must use .yaml, .yml, or .json extensions"
                )

        if parsed is None or not isinstance(parsed, dict):
            raise ConfigError("Config file must define a mapping at the top level")

        with (
            metrics.timer("env_interpolation", path=resolved_path)
            if metrics
            else nullcontext()
        ):
            config_dict = _interpolate_env(parsed)

        with import_context._lock:
            import_context.config_cache[resolved_path] = config_dict
            import_context.config_cache[normalized_path] = config_dict

        loader_settings_data = config_dict.get("loader_settings", {})
        concurrency_enabled = loader_settings_data.get("concurrency_enabled", True)
        max_threads = loader_settings_data.get("max_threads", None)

        raw_imports = config_dict.get("imports", [])
        if raw_imports:
            normalized_imports = _normalize_imports_for_processing(
                raw_imports, base_path=resolved_path, filesystem=filesystem
            )

            global_imports = []
            section_imports: dict[str, list[tuple[str, bool]]] = {}
            for path, override, section in normalized_imports:
                if section is None:
                    global_imports.append((path, override))
                else:
                    if section not in section_imports:
                        section_imports[section] = []
                    section_imports[section].append((path, override))

            if global_imports:
                all_patterns = [p for p, _ in global_imports]
                exclude_patterns = [p for p in all_patterns if p.startswith("!")]

                ordered_paths = []
                seen_p = set()
                for p, override in global_imports:
                    if p.startswith("!"):
                        continue
                    expanded = _expand_glob_patterns(
                        [p] + exclude_patterns,
                        base_path=resolved_path,
                        filesystem=filesystem,
                    )
                    for exp_p in expanded:
                        if exp_p not in seen_p:
                            ordered_paths.append((exp_p, override))
                            seen_p.add(exp_p)

                path_to_result = {}
                if concurrency_enabled and len(ordered_paths) > 1:
                    with concurrent.futures.ThreadPoolExecutor(
                        max_workers=max_threads
                    ) as executor:
                        fut_to_p = {
                            executor.submit(
                                _resolve_and_load_import,
                                p,
                                resolved_path,
                                filesystem,
                                resolve_paths,
                                load_sql_files,
                                sql_file_loader,
                                import_context,
                                new_stack,
                            ): p
                            for p, _ in ordered_paths
                        }
                        for fut in concurrent.futures.as_completed(fut_to_p):
                            path_to_result[fut_to_p[fut]] = fut.result()
                else:
                    for p, _ in ordered_paths:
                        path_to_result[p] = _resolve_and_load_import(
                            p,
                            resolved_path,
                            filesystem,
                            resolve_paths,
                            load_sql_files,
                            sql_file_loader,
                            import_context,
                            new_stack,
                        )

                merged_imports_dict = {}
                for p, override in ordered_paths:
                    merged_imports_dict = _merge_config_dicts(
                        merged_imports_dict, path_to_result[p], override
                    )

                config_dict = _merge_config_dicts(
                    merged_imports_dict, config_dict, True
                )

            for section_name, imports_list in section_imports.items():
                all_patterns = [p for p, _ in imports_list]
                exclude_patterns = [p for p in all_patterns if p.startswith("!")]

                ordered_paths = []
                seen_p = set()
                for p, override in imports_list:
                    if p.startswith("!"):
                        continue
                    expanded = _expand_glob_patterns(
                        [p] + exclude_patterns,
                        base_path=resolved_path,
                        filesystem=filesystem,
                    )
                    for exp_p in expanded:
                        if exp_p not in seen_p:
                            ordered_paths.append((exp_p, override))
                            seen_p.add(exp_p)

                path_to_result = {}
                if concurrency_enabled and len(ordered_paths) > 1:
                    with concurrent.futures.ThreadPoolExecutor(
                        max_workers=max_threads
                    ) as executor:
                        fut_to_p = {
                            executor.submit(
                                _resolve_and_load_import,
                                p,
                                resolved_path,
                                filesystem,
                                resolve_paths,
                                load_sql_files,
                                sql_file_loader,
                                import_context,
                                new_stack,
                            ): p
                            for p, _ in ordered_paths
                        }
                        for fut in concurrent.futures.as_completed(fut_to_p):
                            path_to_result[fut_to_p[fut]] = fut.result()
                else:
                    for p, _ in ordered_paths:
                        path_to_result[p] = _resolve_and_load_import(
                            p,
                            resolved_path,
                            filesystem,
                            resolve_paths,
                            load_sql_files,
                            sql_file_loader,
                            import_context,
                            new_stack,
                        )

                merged_section = {}
                for p, override in ordered_paths:
                    merged_section = _merge_config_dicts(
                        merged_section, path_to_result[p], override
                    )

                temp_merged_config = _merge_config_dicts(
                    merged_section, config_dict, True
                )
                if section_name in temp_merged_config:
                    config_dict[section_name] = temp_merged_config[section_name]

        from ..models import Config

        try:
            with (
                metrics.timer("validation", path=resolved_path)
                if metrics
                else nullcontext()
            ):
                config = Config.model_validate(config_dict)
        except Exception as e:
            error_str = str(e)
            if "Duplicate view name" in error_str:
                import re

                match = re.search(r"Duplicate view name\(s\) found: (.+)", error_str)
                if match:
                    duplicates = match.group(1)
                    raise DuplicateNameError(
                        f"Duplicate view name(s) found: {duplicates}",
                        name_type="view",
                        duplicate_names=[d.strip() for d in duplicates.split(",")],
                    ) from e
                raise DuplicateNameError(error_str, name_type="view") from e
            elif "Duplicate Iceberg catalog name" in error_str:
                raise DuplicateNameError(error_str, name_type="iceberg_catalog") from e
            elif "Duplicate semantic model name" in error_str:
                raise DuplicateNameError(error_str, name_type="semantic_model") from e
            elif "Duplicate attachment alias" in error_str:
                raise DuplicateNameError(error_str, name_type="attachment") from e
            raise ConfigError(f"Configuration validation failed: {e}") from e

        with import_context._lock:
            import_context.config_cache[resolved_path] = config
            import_context.config_cache[normalized_path] = config

        with (
            metrics.timer("unique_name_validation", path=resolved_path)
            if metrics
            else nullcontext()
        ):
            _validate_unique_names(config, import_context)
        if resolve_paths:
            with (
                metrics.timer("path_resolution", path=resolved_path)
                if metrics
                else nullcontext()
            ):
                config = _resolve_paths_in_config(config, config_path)
        if load_sql_files:
            with (
                metrics.timer("sql_loading", path=resolved_path)
                if metrics
                else nullcontext()
            ):
                config = load_sql_files_from_config(
                    config, config_path, sql_file_loader, filesystem=filesystem
                )
        return config
    finally:
        pass


class DefaultImportResolver(ImportResolver):
    def __init__(self, context: Optional[RequestContext] = None):
        self.context = context or RequestContext()

    def resolve(
        self, config_data: dict[str, Any], context: ImportContext
    ) -> dict[str, Any]:
        base_path = config_data.get("file_path")
        if not base_path:
            raise ConfigError("config_data must include 'file_path'")
        return _load_config_with_imports(
            file_path=str(base_path),
            content=config_data.get("content"),
            format=config_data.get("format", "yaml"),
            filesystem=config_data.get("filesystem"),
            resolve_paths=config_data.get("resolve_paths", True),
            load_sql_files=config_data.get("load_sql_files", True),
            sql_file_loader=config_data.get("sql_file_loader"),
            import_context=context,
            load_dotenv=config_data.get("load_dotenv", True),
            env_cache=self.context.env_cache,
        )


__all__ = [
    "DefaultImportResolver",
    "RequestContext",
    "request_cache_scope",
    "_load_config_with_imports",
]
