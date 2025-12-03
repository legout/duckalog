# Change: Enforce Path Security with Explicit Root Boundaries

## Why

Duckalog currently attempts to prevent dangerous path traversal via heuristics in the path resolution layer (for example, counting `../` segments and checking for “dangerous” substrings like `/etc/`). These heuristics are:

- Easy to bypass (different encodings, Windows paths, symlinks, etc.).
- Difficult to reason about and test comprehensively.
- Coupled to specific Unix filesystem conventions.

For a library that may consume configuration from semi-trusted sources, we need a clear and robust specification: all resolved file paths used for local access MUST remain under a small set of allowed roots (typically the config directory and its descendants), regardless of how many `..` segments or path encodings are used.

## What Changes

- **Define path security in terms of roots, not heuristics**
  - Specify that any local file path derived from configuration (for configs, SQL files, data files, exports, etc.) MUST resolve to a path under one of the configured “allowed roots”.
  - By default, the allowed root set includes:
    - The directory containing the primary config file.
    - Any additional explicit roots (for example, a configured `base_dir` or a project root option, if present in the config spec).

- **Replace `_is_reasonable_parent_traversal` with root-based validation**
  - Remove or deprecate the current `_is_reasonable_parent_traversal` logic that:
    - Counts occurrences of `"../"` and compares them to a magic threshold.
    - Checks resolved paths for “dangerous patterns” like `/etc/`, `/usr/`, etc.
  - Introduce a new helper that:
    - Resolves the candidate path using `Path(path).resolve()`.
    - Resolves each allowed root (config directory, and any others).
    - Uses `os.path.commonpath` or `Path.relative_to` to ensure the resolved path sits under at least one allowed root.
    - Treats any path that does not share a common path prefix with an allowed root as a security violation.

- **Clarify threat model and behavior on violation**
  - Update the config spec to make the threat model explicit:
    - Config files may be controlled by the same team, but Duckalog MUST assume they can be malformed or contain unexpected values.
    - Duckalog MUST NOT follow paths that escape configured roots to system directories or arbitrary filesystem locations.
  - Define behavior when a violation is detected:
    - Raise a `ConfigError` (or `PathResolutionError`) with a clear message including the original path and config directory.
    - Do not attempt to “fix up” or silently modify the path.

- **Improve cross-platform and encoding coverage**
  - Ensure the new logic handles:
    - Unix and Windows absolute paths.
    - Mixed separators (`/` vs `\`).
    - Symlinks (via `resolve()`).
  - Explicitly treat un-decodable or otherwise invalid paths as errors with clear messages.

## Impact

- **Specs updated**
  - `specs/config/spec.md`:
    - Add or update path resolution requirements to specify allowed roots and the “must not escape” rule.
    - Document the error behavior when a path is outside allowed roots.
  - `specs/catalog-build/spec.md`:
    - Clarify which file paths are subject to path security checks (SQL files, local data paths, exported catalogs, etc.).

- **Implementation**
  - `src/duckalog/path_resolution.py`:
    - Replace `_is_reasonable_parent_traversal` with a root-based check helper (for example, `_is_within_allowed_roots`).
    - Use `Path.resolve()` and `os.path.commonpath` / `Path.relative_to` for robust comparisons.
  - `src/duckalog/config.py` (or its successors if refactored):
    - Ensure any integration points that currently rely on `_is_reasonable_parent_traversal` now call the new helper.

- **Non-goals**
  - This change does not introduce new config options for defining extra roots beyond what the config spec already supports; if we later want a richer “allowed roots” model, we can define it in a separate change.
  - Remote URIs (for example, `s3://`, `https://`) are out of scope for this path security rule and continue to be validated by remote-config logic.

## Risks and Trade-offs

- Tighter root-based checks may reject configurations that previously “worked” by allowing paths to escape the config directory; this is an intentional hardening and should be called out in the changelog and docs.
- Cross-platform semantics (especially on Windows) require careful testing; however, using `Path.resolve()` and `commonpath` significantly reduces the likelihood of subtle bugs compared to the existing heuristic.

