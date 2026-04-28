"""CLI import-graph helpers for Duckalog.

Extracted from cli.py to keep the command definitions separate from
import-graph collection, diagnostics, and tree printing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import typer


def _collect_import_graph(
    config_path: str,
    filesystem: Optional[Any] = None,
) -> tuple[list[str], dict[str, list[str]], set[str]]:
    """Collect import graph information from a config file.

    Args:
        config_path: Path to the configuration file.
        filesystem: Optional filesystem object for remote file access.

    Returns:
        A tuple of (import_chain, import_graph, visited) where:
        - import_chain: The chain of files from root to current
        - import_graph: Dict mapping file paths to their imported files
        - visited: Set of visited file paths (normalized)
    """
    from .config.resolution.imports import (
        _is_remote_uri,
        _normalize_uri,
        _resolve_import_path,
    )
    from .config import load_config

    import_chain = []
    import_graph: dict[str, list[str]] = {}
    visited = set()

    def _traverse_imports(current_path: str, base_path: str) -> None:
        """Recursively traverse import graph."""
        # Normalize and resolve the current path
        if _is_remote_uri(current_path):
            normalized_current = _normalize_uri(current_path)
        else:
            normalized_current = _normalize_uri(str(Path(current_path).resolve()))

        # Avoid infinite loops and duplicate processing
        if normalized_current in visited:
            return
        visited.add(normalized_current)

        # Use normalized path for the chain to ensure consistency
        import_chain.append(normalized_current)

        # Load the config to get its imports
        try:
            if _is_remote_uri(current_path):
                config = load_config(
                    current_path, filesystem=filesystem, load_sql_files=False
                )
            else:
                config = load_config(
                    current_path, filesystem=filesystem, load_sql_files=False
                )
        except Exception:
            # If we can't load the config, skip it
            import_graph[normalized_current] = []
            return

        # Get imports and resolve them to normalized paths
        imports = config.imports if config.imports else []
        resolved_imports = []

        # Recursively process each import
        for import_path in imports:
            try:
                resolved_import = _resolve_import_path(import_path, current_path)

                # Normalize the resolved import for consistency
                if _is_remote_uri(resolved_import):
                    normalized_import = _normalize_uri(resolved_import)
                else:
                    normalized_import = _normalize_uri(
                        str(Path(resolved_import).resolve())
                    )

                resolved_imports.append(normalized_import)

                # Recurse into the imported file
                _traverse_imports(resolved_import, current_path)
            except Exception:
                # Skip imports that can't be resolved
                continue

        import_graph[normalized_current] = resolved_imports

    # Start traversal from the root config path
    if _is_remote_uri(config_path):
        abs_config_path = config_path
    else:
        abs_config_path = str(Path(config_path).resolve())

    _traverse_imports(abs_config_path, abs_config_path)

    return import_chain, import_graph, visited


def _compute_import_diagnostics(import_graph: dict[str, list[str]]) -> dict[str, Any]:
    """Compute diagnostics for the import graph.

    Args:
        import_graph: Dict mapping file paths to their imported files.

    Returns:
        Dictionary containing diagnostic information:
        - max_depth: Maximum import depth
        - total_files: Total number of files in the graph
        - files_with_imports: Count of files that have imports
        - remote_imports: Count of remote URI imports
        - local_imports: Count of local file imports
        - duplicate_imports: List of files imported multiple times
    """
    if not import_graph:
        return {
            "max_depth": 0,
            "total_files": 0,
            "files_with_imports": 0,
            "remote_imports": 0,
            "local_imports": 0,
            "duplicate_imports": [],
        }

    # Build parent-child relationships
    children_map = {parent: children for parent, children in import_graph.items()}

    # Find the root (file that is not imported by any other file)
    all_imported = set()
    for children in import_graph.values():
        all_imported.update(children)

    roots = [f for f in import_graph.keys() if f not in all_imported]

    # Compute maximum depth
    max_depth = 0
    for root in roots:
        depths = {}

        def compute_depth(node: str, depth: int = 0) -> None:
            """Recursively compute depth."""
            if node in depths and depths[node] <= depth:
                return
            depths[node] = depth

            children = children_map.get(node, [])
            for child in children:
                compute_depth(child, depth + 1)

        compute_depth(root)
        max_depth = max(max_depth, max(depths.values()) if depths else 0)

    # Count file types
    remote_imports = sum(
        1 for children in import_graph.values() for child in children if "://" in child
    )

    local_imports = sum(
        1
        for children in import_graph.values()
        for child in children
        if "://" not in child
    )

    # Find duplicate imports
    all_imports = []
    for children in import_graph.values():
        all_imports.extend(children)

    import_counts = {}
    for imp in all_imports:
        import_counts[imp] = import_counts.get(imp, 0) + 1

    duplicate_imports = [imp for imp, count in import_counts.items() if count > 1]

    return {
        "max_depth": max_depth,
        "total_files": len(import_graph),
        "files_with_imports": sum(1 for children in import_graph.values() if children),
        "remote_imports": remote_imports,
        "local_imports": local_imports,
        "duplicate_imports": duplicate_imports,
    }


def _print_import_tree(
    import_chain: list[str],
    import_graph: dict[str, list[str]],
    visited: set[str],
    show_diagnostics: bool = False,
    original_root_path: Optional[str] = None,
) -> None:
    """Print the import graph as a tree structure.

    Args:
        import_chain: The chain of files from root to current.
        import_graph: Dict mapping file paths to their imported files.
        visited: Set of visited file paths.
        show_diagnostics: If True, also print diagnostic information.
        original_root_path: The original root path (for display purposes).
    """
    if not import_chain:
        typer.echo("No imports found.")
        return

    # Track which files have been printed
    printed = set()

    # Create a path display helper that shows relative paths when possible
    def _get_display_path(path: str) -> str:
        """Get a user-friendly display path."""
        # For remote URIs, show as-is
        if "://" in path:
            return path

        # For local files, try to show relative to current directory
        try:
            p = Path(path).resolve()

            # Try to make it relative to current directory
            try:
                relative = p.relative_to(Path.cwd())
                return str(relative)
            except ValueError:
                # Not under current dir, show as absolute
                return str(p)
        except Exception:
            # If anything fails, just return the path
            return path

    def _print_node(path: str, prefix: str = "", is_last: bool = True) -> None:
        """Print a node in the tree."""
        display_path = _get_display_path(path)

        # Determine if this is a remote URI
        is_remote = "://" in str(display_path)
        path_type = " [REMOTE]" if is_remote else ""

        if is_last:
            typer.echo(f"{prefix}└── {display_path}{path_type}")
            new_prefix = prefix + "    "
        else:
            typer.echo(f"{prefix}├── {display_path}{path_type}")
            new_prefix = prefix + "│   "

        printed.add(path)

        # Get and sort children
        children = sorted(import_graph.get(path, []))

        # Print children
        for i, child in enumerate(children):
            is_child_last = i == len(children) - 1
            if child not in printed:
                _print_node(child, new_prefix, is_child_last)

    # Start printing from the root
    root = import_chain[0]
    root_display = _get_display_path(root)
    typer.echo(f"{root_display}")
    children = sorted(import_graph.get(root, []))

    for i, child in enumerate(children):
        is_last = i == len(children) - 1
        _print_node(child, "", is_last)

    # Print diagnostics
    if show_diagnostics:
        diagnostics = _compute_import_diagnostics(import_graph)
        typer.echo("")
        typer.echo("Import Diagnostics:")
        typer.echo("-" * 80)
        typer.echo(f"  Total files: {diagnostics['total_files']}")
        typer.echo(f"  Maximum import depth: {diagnostics['max_depth']}")
        typer.echo(f"  Files with imports: {diagnostics['files_with_imports']}")
        typer.echo(f"  Remote imports: {diagnostics['remote_imports']}")
        typer.echo(f"  Local imports: {diagnostics['local_imports']}")
        if diagnostics["duplicate_imports"]:
            typer.echo(
                f"  Duplicate imports: {', '.join(diagnostics['duplicate_imports'])}"
            )
    else:
        total_files = len(visited) if visited else len(import_chain)
        typer.echo("")
        typer.echo(f"Total files in import graph: {total_files}")
