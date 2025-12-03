# Design: Remote Config Loader Contract

## Goals

- Make remote vs local config loading explicit and testable.
- Preserve a simple public API (`load_config`) while providing clear helper functions for advanced use cases.
- Reduce ambiguity and duplication between `config.py` and `remote_config.py`.

## Function roles

### `load_config(path_or_uri, *, filesystem=None, ...)`

- Public, user-facing entrypoint for loading a Duckalog config.
- Responsibilities:
  - Determine whether `path_or_uri` is local or remote.
  - Delegate to the appropriate helper:
    - `_load_config_from_local_file` for local paths.
    - `load_config_from_uri` for remote URIs.
  - Apply any global options (for example, toggles for path resolution) consistently.

### `_load_config_from_local_file(path, *, filesystem=None, ...)`

- Internal helper that owns local file reading and validation.
- Responsibilities:
  - Resolve the given path to an absolute path.
  - Read YAML/JSON from local disk or from the provided `filesystem` (if non-`None`).
  - Perform environment interpolation, path resolution, and Pydantic validation.
- Exposed only for tests and internal callers via a private name and not documented as a stable public API.

### `load_config_from_uri(uri, *, filesystem, ...)`

- Public helper for remote URIs.
- Responsibilities:
  - Parse and validate the URI scheme (for example, `s3://`, `http://`, `https://`).
  - Use the provided `filesystem` or a suitable default for network/file I/O.
  - Apply the same interpolation, path resolution, and validation pipeline as local configs once the data is retrieved.
- Exported from `duckalog.config` so tests can patch or call it directly.

## Remote vs local detection

- We reuse the URI detection logic from the path/URI spec:
  - If `path_or_uri` matches a `<scheme>://` pattern, it is considered remote.
  - Otherwise, it is treated as a local path.
- This logic lives in a shared helper, so both the config loading and path-resolution layers agree on what counts as a remote URI.

## Filesystem semantics

- The expected `filesystem` interface is intentionally simple:
  - For local files:
    - Either use default path-based I/O, or
    - Use `filesystem.open(path, mode)` and related methods if an fsspec-like object is provided.
  - For remote URIs:
    - Expect `filesystem` to understand the given scheme and provide `.open` / `.exists` as needed.
- On mismatches (for example, missing methods), `load_config` or `load_config_from_uri` raise a clear error describing the required interface.

## Testing strategy

- Use monkeypatching to:
  - Replace `_load_config_from_local_file` and assert that `load_config` delegates correctly for local paths.
  - Replace `load_config_from_uri` and assert that `load_config` delegates correctly for remote URIs.
- Use in-memory or dummy filesystem implementations to test behavior without real network or disk access.

