"""Import resolution extracted from the legacy loader with DI hooks."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union

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
from ..loading.sql import load_sql_files_from_config
from ..validators import validate_path_security
from .env import EnvCache, DefaultEnvProcessor, _load_dotenv_files_for_config
from .base import ImportContext, ImportResolver


@dataclass
class RequestContext:
    """Context for request-scoped caching and state management."""

    env_cache: EnvCache = field(default_factory=EnvCache)
    import_context: ImportContext = field(default_factory=ImportContext)
    max_cache_size: int = 1000  # Maximum number of configs to cache

    def clear(self) -> None:
        self.env_cache.clear()
        self.import_context.visited_files.clear()
        self.import_context.import_stack.clear()
        self.import_context.config_cache.clear()
        self.import_context.import_chain.clear()

    def _enforce_cache_limit(self) -> None:
        """Enforce cache size limit to prevent memory issues with large config trees."""
        if len(self.import_context.config_cache) > self.max_cache_size:
            # Remove oldest entries (simple FIFO strategy)
            oldest_keys = list(self.import_context.config_cache.keys())[
                : len(self.import_context.config_cache) - self.max_cache_size
            ]
            for key in oldest_keys:
                del self.import_context.config_cache[key]
            log_debug(
                "Cache size limit enforced",
                removed_count=len(oldest_keys),
                current_size=len(self.import_context.config_cache),
                max_size=self.max_cache_size,
            )


@contextmanager
def request_cache_scope(context: Optional[RequestContext] = None):
    ctx = context or RequestContext()
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
                excluded_files.update(matches)
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
                            resolved_files.append(resolved_pattern)
                    else:
                        raise ImportFileNotFoundError(
                            f"No files match pattern: {pattern}"
                        )
                else:
                    resolved_files.extend(sorted(matches))
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

    log_debug(
        "Expanded glob patterns",
        input_patterns=patterns,
        resolved_files=final_result,
    )

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
            else:
                raise ConfigError(
                    f"Invalid import format: expected string or ImportEntry, got {type(item)}"
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
                elif isinstance(item, ImportEntry):
                    override = item.override
                    normalized.append((item.path, override, section_name))
                else:
                    raise ConfigError(
                        f"Invalid import format in {section_name}: expected string or ImportEntry, got {type(item)}"
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


def _merge_config_with_override(
    base: Any,
    override: Any,
    override_mode: bool = True,
) -> Any:
    from ..models import Config

    base_dict = base.model_dump(mode="json")
    override_dict = override.model_dump(mode="json")

    log_debug("Deep merge base keys", keys=list(base_dict.keys()))
    log_debug("Deep merge override keys", keys=list(override_dict.keys()))

    override_imports = override_dict.get("imports", [])
    base_dict = base_dict.copy()
    base_dict.pop("imports", None)
    override_dict = override_dict.copy()
    override_dict.pop("imports", None)

    log_debug("After removing imports - base_dict keys", keys=list(base_dict.keys()))
    log_debug(
        "After removing imports - override_dict keys", keys=list(override_dict.keys())
    )

    if override_mode:
        merged_dict = _deep_merge_dict(base_dict, override_dict)
    else:
        merged_dict = base_dict.copy()
        for key, value in override_dict.items():
            if key not in merged_dict or merged_dict[key] is None:
                merged_dict[key] = value

    merged_dict["imports"] = override_imports

    log_debug("Deep merge result keys", keys=list(merged_dict.keys()))

    try:
        result = Config(**merged_dict)
        log_debug("Config created successfully", views=len(result.views))
        return result
    except ValueError as e:
        if "Duplicate view name" in str(e):
            import re

            match = re.search(r"Duplicate view name\(s\) found: (.+)", str(e))
            if match:
                duplicates = match.group(1)
                raise DuplicateNameError(
                    f"Duplicate view name(s) found: {duplicates}",
                    name_type="view",
                    duplicate_names=[d.strip() for d in duplicates.split(",")],
                ) from e
        elif "Duplicate Iceberg catalog name" in str(e):
            raise DuplicateNameError(str(e), name_type="iceberg_catalog") from e
        elif "Duplicate semantic model name" in str(e):
            raise DuplicateNameError(str(e), name_type="semantic_model") from e
        elif "Duplicate attachment alias" in str(e):
            raise DuplicateNameError(str(e), name_type="attachment") from e
        log_debug("Failed to create Config", error=str(e))
        log_debug("merged_dict details", merged_dict=str(merged_dict))
        raise
    except Exception as e:
        log_debug("Failed to create Config", error=str(e))
        log_debug("merged_dict details", merged_dict=str(merged_dict))
        raise


def _merge_section_specific(
    imported_config: Any,
    base_config: Any,
    section_name: str,
    override_mode: bool = True,
) -> Any:
    from ..models import Config

    imported_dict = imported_config.model_dump(mode="json")
    base_dict = base_config.model_dump(mode="json")

    log_debug(
        "Merging section-specific imports",
        section=section_name,
        override_mode=override_mode,
    )

    if section_name not in imported_dict:
        log_debug("Section not found in imported config", section=section_name)
        return base_config

    imported_section = imported_dict.get(section_name)
    imported_dict.pop("imports", None)
    base_dict.pop("imports", None)
    merged_dict = base_dict.copy()

    if section_name in merged_dict:
        base_section = merged_dict[section_name]

        if override_mode:
            if isinstance(base_section, dict) and isinstance(imported_section, dict):
                merged_dict[section_name] = _deep_merge_dict(
                    base_section, imported_section
                )
            elif isinstance(base_section, list) and isinstance(imported_section, list):
                merged_dict[section_name] = base_section + imported_section
            else:
                merged_dict[section_name] = imported_section
        else:
            if isinstance(base_section, dict) and isinstance(imported_section, dict):
                for key, value in imported_section.items():
                    if key not in base_section or base_section[key] is None:
                        merged_dict[section_name][key] = value
            elif isinstance(base_section, list) and isinstance(imported_section, list):
                for item in imported_section:
                    if item not in base_section:
                        merged_dict[section_name].append(item)
            else:
                if base_section is None:
                    merged_dict[section_name] = imported_section
    else:
        merged_dict[section_name] = imported_section

    merged_dict["imports"] = base_dict.get("imports", [])

    try:
        result = Config(**merged_dict)
        log_debug("Section merged successfully", section=section_name)
        return result
    except ValueError as e:
        if "Duplicate view name" in str(e):
            import re

            match = re.search(r"Duplicate view name\(s\) found: (.+)", str(e))
            if match:
                duplicates = match.group(1)
                raise DuplicateNameError(
                    f"Duplicate view name(s) found: {duplicates}",
                    name_type="view",
                    duplicate_names=[d.strip() for d in duplicates.split(",")],
                ) from e
        elif "Duplicate Iceberg catalog name" in str(e):
            raise DuplicateNameError(str(e), name_type="iceberg_catalog") from e
        elif "Duplicate semantic model name" in str(e):
            raise DuplicateNameError(str(e), name_type="semantic_model") from e
        elif "Duplicate attachment alias" in str(e):
            raise DuplicateNameError(str(e), name_type="attachment") from e
        log_debug("Failed to create Config", error=str(e))
        log_debug("merged_dict details", merged_dict=str(merged_dict))
        raise
    except Exception as e:
        log_debug("Failed to create Config", error=str(e))
        log_debug("merged_dict details", merged_dict=str(merged_dict))
        raise


def _validate_unique_names(config: Any, context: ImportContext) -> None:
    view_names: dict[tuple[Optional[str], str], int] = {}
    duplicates = []
    for view in config.views:
        key = (view.db_schema, view.name)
        if key in view_names:
            schema_part = f"{view.db_schema}." if view.db_schema else ""
            duplicates.append(f"{schema_part}{view.name}")
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
    for catalog in config.iceberg_catalogs:
        if catalog.name in catalog_names:
            duplicates.append(catalog.name)
        else:
            catalog_names[catalog.name] = 1

    if duplicates:
        raise DuplicateNameError(
            f"Duplicate Iceberg catalog name(s) found: {', '.join(sorted(set(duplicates)))}",
            name_type="iceberg_catalog",
            duplicate_names=sorted(set(duplicates)),
        )

    semantic_model_names: dict[str, int] = {}
    duplicates = []
    for semantic_model in config.semantic_models:
        if semantic_model.name in semantic_model_names:
            duplicates.append(semantic_model.name)
        else:
            semantic_model_names[semantic_model.name] = 1

    if duplicates:
        raise DuplicateNameError(
            f"Duplicate semantic model name(s) found: {', '.join(sorted(set(duplicates)))}",
            name_type="semantic_model",
            duplicate_names=sorted(set(duplicates)),
        )

    attachment_aliases: dict[str, int] = {}
    duplicates = []
    for attachment in config.attachments.duckdb:
        if attachment.alias in attachment_aliases:
            duplicates.append(f"duckdb.{attachment.alias}")
        else:
            attachment_aliases[attachment.alias] = 1

    for attachment in config.attachments.sqlite:
        if attachment.alias in attachment_aliases:
            duplicates.append(f"sqlite.{attachment.alias}")
        else:
            attachment_aliases[attachment.alias] = 1

    for attachment in config.attachments.postgres:
        if attachment.alias in attachment_aliases:
            duplicates.append(f"postgres.{attachment.alias}")
        else:
            attachment_aliases[attachment.alias] = 1

    for attachment in config.attachments.duckalog:
        if attachment.alias in attachment_aliases:
            duplicates.append(f"duckalog.{attachment.alias}")
        else:
            attachment_aliases[attachment.alias] = 1

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
) -> Any:
    try:
        resolved_path = _resolve_import_path(import_path, base_path)
    except Exception as exc:
        raise ImportFileNotFoundError(
            f"Failed to resolve import path '{import_path}' from '{base_path}': {exc}",
            import_path=import_path,
            cause=exc,
        ) from exc

    log_debug("Resolving import", import_path=import_path, resolved_path=resolved_path)

    normalized_path = _normalize_uri(resolved_path)

    if normalized_path in import_context.visited_files:
        if normalized_path in import_context.import_stack:
            chain = " -> ".join(
                _normalize_uri(p) for p in import_context.import_stack + [resolved_path]
            )
            raise CircularImportError(
                f"Circular import detected in import chain: {chain}",
                import_chain=import_context.import_stack + [resolved_path],
            )
        else:
            log_debug(
                "Using cached config for already-loaded import", path=resolved_path
            )
            return import_context.config_cache.get(resolved_path)

    import_context.import_stack.append(resolved_path)
    import_context.visited_files.add(normalized_path)

    try:
        if _is_remote_uri(resolved_path):
            try:
                from duckalog.remote_config import load_config_from_uri

                imported_config = load_config_from_uri(
                    uri=resolved_path,
                    load_sql_files=load_sql_files,
                    sql_file_loader=sql_file_loader,
                    resolve_paths=False,
                    filesystem=filesystem,
                )
            except Exception as exc:
                raise ImportValidationError(
                    f"Failed to load remote config '{resolved_path}': {exc}",
                    import_path=resolved_path,
                    cause=exc,
                ) from exc
        else:
            config_path = Path(resolved_path)

            exists = False
            if filesystem is not None:
                exists = filesystem.exists(resolved_path)
            else:
                exists = config_path.exists()

            if not exists:
                raise ImportFileNotFoundError(
                    f"Imported file not found: {resolved_path}",
                    import_path=resolved_path,
                )

            try:
                if filesystem is not None:
                    if not hasattr(filesystem, "open") or not hasattr(
                        filesystem, "exists"
                    ):
                        raise ImportError(
                            "filesystem object must provide 'open' and 'exists' methods"
                        )
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
            if suffix in {".yaml", ".yml"}:
                parsed = yaml.safe_load(raw_text)
            elif suffix == ".json":
                parsed = json.loads(raw_text)
            else:
                raise ImportValidationError(
                    f"Imported file must use .yaml, .yml, or .json extension: {resolved_path}",
                    import_path=resolved_path,
                )

            if parsed is None:
                raise ImportValidationError(
                    f"Imported file is empty: {resolved_path}",
                    import_path=resolved_path,
                )
            if not isinstance(parsed, dict):
                raise ImportValidationError(
                    f"Imported file must define a mapping at the top level: {resolved_path}",
                    import_path=resolved_path,
                )

            interpolated = _interpolate_env(parsed)

            from ..models import Config

            try:
                imported_config = Config.model_validate(interpolated)
            except Exception as exc:
                raise ImportValidationError(
                    f"Imported config validation failed: {exc}",
                    import_path=resolved_path,
                    cause=exc,
                ) from exc

            if load_sql_files:
                imported_config = load_sql_files_from_config(
                    imported_config, config_path, sql_file_loader
                )

        import_context.config_cache[resolved_path] = imported_config
        import_context.config_cache[normalized_path] = imported_config

        # Enforce cache size limit to prevent memory issues
        import_context._enforce_cache_limit(log_debug)

        if imported_config.imports:
            try:
                import_count = len(imported_config.imports)  # type: ignore[arg-type]
            except TypeError:
                import_count = 1

            log_debug(
                "Processing nested imports",
                path=resolved_path,
                import_count=import_count,
            )

            try:
                import_items = list(imported_config.imports)  # type: ignore[arg-type]
            except TypeError:
                import_items = [imported_config.imports]  # type: ignore[arg-type]

            for import_item in import_items:
                try:
                    nested_import_path = import_item.path  # type: ignore[attr-defined]
                except AttributeError:
                    nested_import_path = str(import_item)

                nested_config = _resolve_and_load_import(
                    import_path=nested_import_path,
                    base_path=resolved_path,
                    filesystem=filesystem,
                    resolve_paths=resolve_paths,
                    load_sql_files=load_sql_files,
                    sql_file_loader=sql_file_loader,
                    import_context=import_context,
                )
                imported_config = _merge_config_with_override(
                    nested_config, imported_config, True
                )

        # Update cache with fully merged config
        import_context.config_cache[resolved_path] = imported_config
        import_context.config_cache[normalized_path] = imported_config
        import_context._enforce_cache_limit(log_debug)

        return imported_config

    finally:
        import_context.import_stack.pop()


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
) -> Any:
    if import_context is None:
        import_context = ImportContext()
    env_cache = env_cache or EnvCache()

    config_path = Path(file_path)
    resolved_path = str(config_path.resolve())

    log_debug("Loading config with imports", path=resolved_path)

    normalized_path = _normalize_uri(resolved_path)

    if resolved_path in import_context.config_cache:
        log_debug("Using cached config", path=resolved_path)
        return import_context.config_cache[resolved_path]
    if normalized_path in import_context.config_cache:
        log_debug("Using cached config (via normalized path)", path=resolved_path)
        return import_context.config_cache[normalized_path]

    import_context.visited_files.add(normalized_path)
    import_context.import_stack.append(resolved_path)

    try:
        env_file_patterns = [".env"]
        try:
            raw_config_path = Path(file_path)
            if raw_config_path.exists():
                with open(raw_config_path, "r") as f:
                    raw_config = yaml.safe_load(f)
                    if (
                        raw_config
                        and isinstance(raw_config, dict)
                        and "env_files" in raw_config
                    ):
                        custom_patterns = raw_config["env_files"]
                        if isinstance(custom_patterns, list) and custom_patterns:
                            env_file_patterns = custom_patterns
                            log_debug(
                                "Using custom .env file patterns",
                                patterns=env_file_patterns,
                            )
        except Exception:
            log_debug("Failed to read custom .env patterns, using defaults")
            pass

        if load_dotenv:
            _load_dotenv_files_for_config(
                file_path, env_file_patterns, cache=env_cache, filesystem=filesystem
            )

        try:
            if filesystem is not None:
                if not hasattr(filesystem, "open") or not hasattr(filesystem, "exists"):
                    raise ConfigError(
                        "filesystem object must provide 'open' and 'exists' methods"
                    )
                if not filesystem.exists(resolved_path):
                    raise ConfigError(f"Config file not found: {file_path}")
                with filesystem.open(resolved_path, "r") as f:
                    raw_text = f.read()
            else:
                if not config_path.exists():
                    raise ConfigError(f"Config file not found: {file_path}")
                raw_text = config_path.read_text()
        except OSError as exc:
            if isinstance(exc, ConfigError):
                raise
            raise ConfigError(
                f"Failed to read config file '{file_path}': {exc}"
            ) from exc

        if format == "yaml":
            parsed = yaml.safe_load(raw_text)
        elif format == "json":
            parsed = json.loads(raw_text)
        else:
            raise ConfigError("Config files must use .yaml, .yml, or .json extensions")

        if parsed is None:
            raise ConfigError("Config file is empty")
        if not isinstance(parsed, dict):
            raise ConfigError("Config file must define a mapping at the top level")

        interpolated = _interpolate_env(parsed)

        from ..models import Config

        try:
            config = Config.model_validate(interpolated)
        except Exception as exc:
            log_debug(
                "Validation failed interpolated keys", keys=list(interpolated.keys())
            )
            if "views" in interpolated:
                log_debug("views value", views=interpolated["views"])
            else:
                log_debug("views missing from interpolated dict")
            raise ConfigError(f"Configuration validation failed: {exc}") from exc

        import_context.config_cache[resolved_path] = config
        import_context.config_cache[normalized_path] = config

        if config.imports:
            if isinstance(config.imports, list):
                import_count = len(config.imports)  # type: ignore[arg-type]
            else:
                try:
                    import_count = sum(
                        len(field_value) if field_value else 0  # type: ignore[arg-type]
                        for field_value in config.imports
                        if field_value is not None
                    )
                except TypeError:
                    import_count = 1
            log_debug("Processing imports", import_count=import_count)

            normalized_imports = _normalize_imports_for_processing(
                config.imports,
                base_path=resolved_path,
                filesystem=filesystem,
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

            for import_path, override in global_imports:
                expanded_paths = _expand_glob_patterns(
                    [import_path],
                    base_path=resolved_path,
                    filesystem=filesystem,
                )

                for expanded_path in expanded_paths:
                    imported_config = _resolve_and_load_import(
                        import_path=expanded_path,
                        base_path=resolved_path,
                        filesystem=filesystem,
                        resolve_paths=resolve_paths,
                        load_sql_files=load_sql_files,
                        sql_file_loader=sql_file_loader,
                        import_context=import_context,
                    )
                    config = _merge_config_with_override(
                        config, imported_config, override_mode=override
                    )

            for section_name, imports_list in section_imports.items():
                for import_path, override in imports_list:
                    expanded_paths = _expand_glob_patterns(
                        [import_path],
                        base_path=resolved_path,
                        filesystem=filesystem,
                    )

                    for expanded_path in expanded_paths:
                        imported_config = _resolve_and_load_import(
                            import_path=expanded_path,
                            base_path=resolved_path,
                            filesystem=filesystem,
                            resolve_paths=resolve_paths,
                            load_sql_files=load_sql_files,
                            sql_file_loader=sql_file_loader,
                            import_context=import_context,
                        )

                        config = _merge_section_specific(
                            imported_config,
                            config,
                            section_name,
                            override_mode=override,
                        )

        # Update cache with fully merged config
        import_context.config_cache[resolved_path] = config
        import_context.config_cache[normalized_path] = config

        _validate_unique_names(config, import_context)

        if resolve_paths:
            config = _resolve_paths_in_config(config, config_path)

        if load_sql_files:
            config = load_sql_files_from_config(
                config, config_path, sql_file_loader, filesystem=filesystem
            )

        log_debug(
            "Config loaded with imports", path=resolved_path, views=len(config.views)
        )
        return config

    finally:
        import_context.import_stack.pop()


class DefaultImportResolver(ImportResolver):
    """ImportResolver implementation that wraps the helper functions."""

    def __init__(self, context: Optional[RequestContext] = None):
        self.context = context or RequestContext()

    def resolve(
        self, config_data: dict[str, Any], context: ImportContext
    ) -> dict[str, Any]:
        base_path = (
            config_data.get("file_path") if isinstance(config_data, dict) else None
        )
        if not base_path:
            raise ConfigError(
                "config_data must include 'file_path' for import resolution"
            )
        raw_content = (
            config_data.get("content") if isinstance(config_data, dict) else None
        )
        format_hint = (
            config_data.get("format", "yaml")
            if isinstance(config_data, dict)
            else "yaml"
        )
        filesystem = (
            config_data.get("filesystem") if isinstance(config_data, dict) else None
        )
        resolve_paths = (
            config_data.get("resolve_paths", True)
            if isinstance(config_data, dict)
            else True
        )
        load_sql_files = (
            config_data.get("load_sql_files", True)
            if isinstance(config_data, dict)
            else True
        )
        sql_loader = (
            config_data.get("sql_file_loader")
            if isinstance(config_data, dict)
            else None
        )
        load_dotenv = (
            config_data.get("load_dotenv", True)
            if isinstance(config_data, dict)
            else True
        )

        return _load_config_with_imports(
            file_path=str(base_path),
            content=raw_content,
            format=format_hint,
            filesystem=filesystem,
            resolve_paths=resolve_paths,
            load_sql_files=load_sql_files,
            sql_file_loader=sql_loader,
            import_context=context,
            load_dotenv=load_dotenv,
            env_cache=self.context.env_cache,
        )


__all__ = [
    "DefaultImportResolver",
    "RequestContext",
    "request_cache_scope",
    "_load_config_with_imports",
]
