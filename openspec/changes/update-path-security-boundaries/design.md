# Design: Root-Based Path Security

## Goals

- Ensure that any path derived from configuration and used for local file access cannot escape a well-defined set of directories.
- Replace heuristic-based checks (for example, counting `../` or scanning for `/etc/`) with clear, composable, and testable invariants.
- Provide cross-platform behavior (Unix + Windows) that is easy to reason about.

## Allowed roots model

We define the concept of **allowed roots**:

- At minimum, the directory containing the main configuration file is an allowed root.
- If the config spec already supports additional root-like options (for example, a `base_dir` or an explicit project root), these can be added to the allowed roots set.

The invariant is:

> Any local path resolved from configuration MUST result in an absolute path that is located under at least one allowed root.

This is independent of how many `..` segments appear or how the path is encoded.

## Root-based check algorithm

Pseudocode for the core helper:

```python
from pathlib import Path
import os

def is_within_allowed_roots(candidate: str, allowed_roots: list[Path]) -> bool:
    candidate_path = Path(candidate).resolve()
    root_paths = [root.resolve() for root in allowed_roots]

    for root in root_paths:
        try:
            common = Path(os.path.commonpath([candidate_path, root]))
        except ValueError:
            # Different drives on Windows, cannot be within this root
            continue

        if common == root:
            return True

    return False
```

Integration points:

- Whenever a relative path is resolved to an absolute path for local access (for example, SQL files, data paths, export targets), we call `is_within_allowed_roots` with:
  - `candidate` = resolved absolute path.
  - `allowed_roots` = list including the config directory and any additional roots derived from config.
- If the helper returns `False`, we raise a configuration-level error.

## Error handling

When a candidate path is outside all allowed roots:

- Raise a `ConfigError` or `PathResolutionError` with fields:
  - `original_path` (the raw value from config).
  - `resolved_path` (the result of `Path(...).resolve()`, if available).
  - Optionally, the list of allowed roots.
- Error messages should guide users towards placing files under the config directory (or other configured roots) rather than using absolute system paths.

If `Path(candidate).resolve()` itself fails (for example, due to invalid characters):

- Treat this as a configuration error with a clear message indicating that the path is invalid.

## Cross-platform considerations

- `Path.resolve()` and `os.path.commonpath` already handle most platform differences.
- On Windows:
  - `commonpath` raises `ValueError` when paths are on different drives; we treat that as “not within this root”.
  - UNC paths are handled by `Path` and `commonpath`.
- We rely on these primitives rather than re-implementing OS-specific logic.

## Relationship to existing behavior

- The existing `_is_reasonable_parent_traversal`:
  - Counts `../` occurrences and compares them to a threshold.
  - Scans for “dangerous patterns” like `/etc/` in the resolved path string.
  - Is easily bypassed (encoded `..`, different separators, symlinks, etc.).
- The new design:
  - Eliminates magic numbers and pattern checks.
  - Expresses security in terms of a clear invariant: “path must be under config dir (or other allowed roots)”.
  - Is easier to test thoroughly with a small matrix of path and root combinations.

