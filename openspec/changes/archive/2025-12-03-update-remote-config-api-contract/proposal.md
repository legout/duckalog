# Change: Clarify Remote Config API Contract and Helpers

## Why

Duckalog supports loading configs both from local files and remote URIs (for example, S3/HTTP), but the responsibilities between:

- `load_config`
- `_load_config_from_local_file`
- `load_config_from_uri`

are not clearly specified. Historical tests and reviews expect:

- A patchable `_load_config_from_local_file(path, filesystem)` helper used for local loading.
- A top-level `load_config_from_uri` symbol imported from `duckalog.config`.

The current implementation inlines parts of this behavior, making it harder to test, mock, and reason about remote vs local behavior, especially around the `filesystem` parameter. We need a clear contract in the specs and a matching implementation.

## What Changes

- **Define clear responsibilities for config loaders**
  - `load_config(path_or_uri, *, filesystem=None, ...)`:
    - Public entrypoint for all config loading.
    - Determines if `path_or_uri` is local or remote, then delegates.
  - `_load_config_from_local_file(path, *, filesystem=None, ...)`:
    - Internal helper responsible for local file reading, env interpolation, path resolution, and validation.
    - Treats `filesystem` as an optional abstraction for local I/O when supplied (for example, fsspec-like objects in tests).
  - `load_config_from_uri(uri, *, filesystem, ...)`:
    - Public helper for remote URIs.
    - Owns URI parsing, remote fetch, and any caching/temporary-file behavior.
    - Requires a `filesystem` or equivalent remote access mechanism where appropriate.

- **Specify dispatch rules**
  - Update the config spec to state that:
    - If `path_or_uri` is recognized as a remote URI (for example, has a scheme like `s3://`, `http://`, `https://`), `load_config` MUST delegate to `load_config_from_uri`.
    - Otherwise, `load_config` MUST delegate to `_load_config_from_local_file`.
  - The detection of “remote URI” vs “local path” should be defined in terms of the existing path/URI detection logic from the path-resolution spec.

- **Define filesystem parameter semantics**
  - Document what is expected of the `filesystem` object (for example, an fsspec-like API with `.open`, `.exists`, etc.).
  - Clarify that:
    - For local files, `filesystem` is optional and default path-based file I/O is used when it is `None`.
    - For remote URIs, `filesystem` may be required depending on protocol (or a suitable default may be used).
  - Specify error behavior when an invalid `filesystem` is provided or required capabilities are missing.

- **Export and test `load_config_from_uri`**
  - Ensure `duckalog.config` exposes `load_config_from_uri` at module level so tests and callers can patch or call it directly.
  - Update specs and tests to rely on this exported symbol rather than re-importing internal modules.

## Impact

- **Specs updated**
  - `specs/config/spec.md`:
    - New or updated section describing:
      - `load_config`, `_load_config_from_local_file`, and `load_config_from_uri`.
      - Their inputs, outputs, and behavior.
      - Dispatch rules and filesystem semantics.

- **Implementation**
  - `src/duckalog/config.py`:
    - Introduce `_load_config_from_local_file` as a dedicated helper (if not already present).
    - Export `load_config_from_uri` from the module.
    - Update `load_config` to act as a thin router between local and remote loaders.
  - `src/duckalog/remote_config.py`:
    - Ensure it implements the behavior required by the spec for `load_config_from_uri`.

- **Non-goals**
  - No new protocols or remote backends are added.
  - No change to the high-level `load_config` signature beyond clarifying semantics and tightening behavior.

## Risks and Trade-offs

- Tighter validation around `filesystem` may surface misuses that previously went unnoticed in tests; this is desirable for correctness.
- Ensuring all call sites use `load_config` or `load_config_from_uri` consistently may require editing a few internal modules, but will make behavior more predictable.

