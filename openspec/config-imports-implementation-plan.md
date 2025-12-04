# Config Imports – Implementation Plan

This document outlines a complete, multi‑phase implementation plan for config imports in Duckalog.
It is aligned with the following OpenSpec changes:

- `add-config-imports` (core local imports)
- `extend-config-imports-remote` (remote imports)
- `extend-config-imports-advanced-options` (advanced options: selective imports, overrides, globs)
- `add-config-imports-cli-tools` (CLI tooling for imports)

Implementation should be incremental: land and stabilize **Phase 1** first, then build on top.

---

## Phase 1 – Core Local Imports (`add-config-imports`)

**Goal:** Support `imports` for local files with deep merge, uniqueness validation, and security,
keeping behavior simple and robust.

### 1. Config Model & Validation

- Add `imports: list[str] = Field(default_factory=list)` to `Config` in `src/duckalog/config/models.py`.
- Update the `Config` docstring to mention `imports` as an optional list of additional config files.
- Keep `_validate_uniqueness` focused on the final merged `Config`; do **not** add import‑specific
  logic here (imports are resolved before validation).

### 2. Import Context & Data Structures

- Introduce an internal import context (in `src/duckalog/config/loader.py` or a small helper):
  - `visited_paths: set[str]` – normalized absolute paths of already loaded config files.
  - `import_stack: list[str]` – current chain of imports (for error messages).
  - `config_cache: dict[str, dict]` – cache of parsed/merged config dicts keyed by absolute path.
- Decide on caching granularity:
  - Recommended: cache merged **dicts** (post‑imports) per file, then validate only once at the top.

### 3. Import Path Resolution & Env Interpolation (Local Only)

- Extend the local‑file path in the loader (either `config/__init__.py` or `config/loader.py`) to:
  - Treat the current config file path (`config_path: Path`) as the base for resolving imports.
  - For each `imports` entry:
    - Apply env interpolation (`${env:VAR}`) to the string value.
    - Resolve relative paths against `config_path.parent`.
    - Leave absolute paths unchanged.
    - Apply existing path‑security helpers (`validate_path_security`) to ensure imports remain
      within allowed roots (e.g., config directory).
- Ensure env interpolation happens before path resolution to match the spec.

### 4. Recursive Import Loading & Merging

- Implement a recursive loader, e.g.:
  - `_load_config_tree(path: str, context: ImportContext, filesystem: Optional[Any]) -> dict`
- Steps inside `_load_config_tree`:
  1. Normalize and resolve `path` to an absolute local filesystem path.
  2. Cycle detection:
     - If `path` is in `context.import_stack`, raise a circular‑import `ConfigError`
       including the full chain in the message.
     - If `path` is already in `visited_paths`, return a deep copy of the cached dict.
  3. Read the file (YAML/JSON) into a dict, handling filesystem abstractions if provided.
  4. Apply env interpolation to the entire dict using the same mechanism as existing config loading.
  5. Extract `imports` from this dict (if present, defaulting to empty list).
  6. For each import path in order:
     - Recursively call `_load_config_tree` to get an imported dict.
     - Deep‑merge imported dict into a working dict using the merge helper (see below).
  7. After processing all imports, deep‑merge the **local file’s own contents** on top so the main
     file can override imported values.
  8. Store the merged dict in `config_cache[path]`, add `path` to `visited_paths`, and return it.

### 5. Deep‑Merge Helper

- Implement `deep_merge(base: dict, override: dict) -> dict`:
  - If both values are dicts → recurse.
  - If both are lists → concatenate `base + override`.
  - Otherwise → override (scalar last‑wins).
- Keep this helper domain‑agnostic (no special cases for views or attachments).

### 6. Integration with `load_config` Pipeline

- For **local paths** in the config loading code:
  - Replace the old “parse + validate” flow with:
    1. `merged_dict = _load_config_tree(path, context, filesystem)`
    2. `config = Config.model_validate(merged_dict)`
  - Keep **remote URI** handling unchanged in this phase (still delegated to existing
    `load_config_from_uri` logic).

### 7. Uniqueness & Semantic Validation

- Rely on the existing `Config` validators:
  - Duplicate view names (by `(db_schema, name)`).
  - Duplicate semantic model names.
  - Duplicate Iceberg catalog names and attachment aliases.
  - Semantic model base view / join references.
- Verify that these validators behave correctly on **merged** dictionaries – no extra work should
  be needed if imports are resolved before validation.

### 8. Error Handling & Logging

- Error handling:
  - For missing import file, parse errors, or invalid structure:
    - Raise `ConfigError` including the resolved path and a short description.
    - Include import chain context where helpful (e.g., “while importing X from Y”).
- Logging:
  - `log_info` when starting to load a config and after imports are fully merged.
  - `log_debug` per import (file path, depth) to help debug complex trees.

### 9. Tests (Phase 1)

- Add tests (e.g. `tests/test_config_imports.py` or extend `tests/test_config.py`) for:
  - Basic imports from multiple local files.
  - Deep‑merge semantics:
    - Scalars: last‑wins.
    - Lists: concatenation.
    - Dicts: recursive merge.
  - Duplicate views/semantic models/attachments across imports → `ConfigError`.
  - Missing import file → clear error.
  - Direct and indirect circular imports → clear error with chain info.
  - Config with no `imports` or `imports: []` behaves identically to prior behavior.
- Add at least one end‑to‑end test:
  - `main.yaml` imports `settings.yaml` and `views.yaml`, then assert the final `Config` has the
    expected DuckDB settings and views.

### 10. Documentation (Phase 1)

- Update config documentation to:
  - Introduce `imports` syntax for local files.
  - Document merge rules and uniqueness behavior.
  - Provide a minimal example (base + environment override).

---

## Phase 2 – Remote Imports (`extend-config-imports-remote`)

**Goal:** Allow `imports` entries that are remote URIs (S3/HTTP/etc.), reusing remote loading
infrastructure and keeping semantics consistent with local imports.

### 1. Remote Import Detection

- In `_load_config_tree` (or equivalent), when encountering an import path:
  - Use `is_remote_uri(path)` to distinguish local vs remote imports.
  - For remote imports:
    - Skip local filesystem path‑security checks.
    - Defer to existing remote config helpers for scheme validation and auth guidance.

### 2. Fetch & Parse Remote Configs

- Implement remote import resolution using one of:
  - **Option A:** Call `load_config_from_uri` and obtain a `Config`, then convert to a dict via
    `model_dump()` for merging.
  - **Option B:** Use `fetch_remote_content` to fetch raw content, then parse YAML/JSON and feed it
    into the same interpolation + merge pipeline as local configs.
- Apply env interpolation to the parsed dict just like local configs.

### 3. Integration with Merge & Cycle Detection

- Use the normalized URI string as the key in:
  - `visited_paths` (for cycle detection).
  - `config_cache` (for caching parsed remote configs).
- Ensure cycles that involve remote configs (e.g., remote imports local, local imports remote)
  are detected and reported.
- Once parsed into dicts, treat remote configs identically to local ones in the merge logic.

### 4. Security & Error Handling

- Security:
  - Reuse existing scheme validation and dependency checks in `remote_config`.
  - Ensure remote imports do not bypass any security assumptions already in place.
- Error handling:
  - On fetch/parse/validation error, raise a config error (typically `ConfigError` surfaced through
    `load_config`) that:
    - Includes the failing URI.
    - Identifies the failed step (fetch vs parse vs validate).
    - Preserves the underlying exception via `raise ... from exc`.

### 5. Tests (Phase 2)

- Add unit tests that mock remote behavior:
  - Monkeypatch `fetch_remote_content` or `load_config_from_uri` to return known config payloads.
  - Test mixed local + remote imports and confirm merged result.
  - Test failure modes:
    - Non‑existent object.
    - Invalid YAML/JSON.
    - Unsupported scheme.
- Add an integration‑style test:
  - Simulate remote imports via a fake filesystem or HTTP fixture, then verify the final config.

### 6. Documentation (Phase 2)

- Extend the imports docs section with:
  - Remote `imports` examples (S3, HTTP).
  - Notes on authentication, timeouts, and security, referencing the existing remote config docs.

---

## Phase 3 – Advanced Import Options (`extend-config-imports-advanced-options`)

**Goal:** Add advanced import options—section‑specific imports, override flags, and glob patterns—
on top of the core semantics from Phases 1–2.

### 1. Finalize YAML Syntax

- Decide on and document concrete shapes before coding. Example candidates:

**Section‑specific imports**
```yaml
imports:
  files:
    - ./base.yaml
  views:
    - ./views/users.yaml
    - ./views/products.yaml
  duckdb:
    - ./config/duckdb-settings.yaml
```

**Override semantics**
```yaml
imports:
  - path: ./base.yaml
  - path: ./env.yaml
    override: false
```

**Glob patterns**
```yaml
imports:
  files:
    - ./views/*.yaml
    - "!./views/legacy.yaml"
```

- Update the OpenSpec design/spec to match the chosen syntax exactly before implementation.

### 2. Parsing Advanced Imports

- Extend import parsing to normalize both:
  - Simple list form from Phase 1 (`imports: ["./a.yaml", "./b.yaml"]`).
  - Structured forms with sections, `path`, `override`, and patterns.
- Normalize to internal “import entries”, each with:
  - `path: str`
  - `sections: Optional[set[str]]` (None → all sections).
  - `override: bool` (default `True`).
  - `is_pattern: bool` or similar, if the path originated from a glob.

### 3. Section‑Specific Imports Behavior

- Adjust merging so that for entries with `sections`:
  - Only the specified top‑level keys (e.g. `views`, `duckdb`) are merged from the imported dict.
  - Other sections in the imported dict are ignored.
- Define and document precedence/interaction between:
  - Global imports (no `sections`).
  - Section‑specific imports.
  - Local config content.

### 4. Override Semantics

- Extend deep‑merge behavior to support `override=False`:
  - For dicts:
    - `override=True`: same as Phase 1 semantics (last‑wins per key).
    - `override=False`: only fill missing keys; do not overwrite existing ones.
  - For lists:
    - Decide and document whether `override=False` changes behavior (e.g. still concatenate, or
      skip list merging for those imports).
- Ensure that override semantics are applied consistently for both core and section‑specific imports.

### 5. Glob & Exclude Patterns

- Before processing each import entry:
  - If `path` is a pattern:
    - Expand to a deterministic list of matching files using `glob` / `fnmatch`.
    - Apply exclude patterns after expansion (e.g. entries prefixed with `!`).
  - Sort the final list of matched paths to keep behavior stable across platforms.
- Treat each resolved file as a standard import entry (respecting `sections` and `override`).

### 6. Tests (Phase 3)

- Section‑specific imports:
  - Only targeted sections change; others remain as in the base config.
  - Mixed global + section‑specific imports with clear expectations documented.
- Override behavior:
  - Examples where `override=False` preserves main values while filling gaps.
  - Mixed imports with `override=True` and `override=False`.
- Glob patterns:
  - Patterns that match multiple files with includes and excludes.
  - Confirm deterministic ordering and expected merged results.

### 7. Documentation (Phase 3)

- Add an “Advanced imports” section to the docs:
  - Explain selective imports, override flags, and glob patterns.
  - Provide realistic examples (e.g. one view per file, environment layering).

---

## Phase 4 – CLI Tooling (`add-config-imports-cli-tools`)

**Goal:** Add CLI commands to inspect and debug imported configurations without building a catalog.

### 1. CLI Command Design

- Add subcommands to `duckalog` CLI, for example:
  - `duckalog show-imports <config>` – visualize import graph/tree.
  - `duckalog preview-config <config> [--section SECTION]` – show merged config or portions of it.
- Ensure these commands:
  - Use the same import resolution and merge logic as `load_config`.
  - Do **not** execute DuckDB or build catalogs.

### 2. Import Graph Visualization

- Implement a helper that:
  - Loads the root config and resolves imports using the same context structure.
  - Collects edges: `parent -> child` for each import.
  - Produces a tree/graph representation (e.g. indented text):
    ```text
    config/catalog.yaml
    ├── config/settings.yaml
    ├── views/users.yaml
    └── views/products.yaml
    ```
- Mark remote URIs and cycles (e.g. `[remote]`, `[cycle]`) where applicable.

### 3. Merged Config Preview

- Implement a command or option that:
  - Loads and merges the config (like Phase 1/2 code).
  - Dumps the resulting `Config` to YAML/JSON (using `model_dump`).
  - Optionally supports `--section views` or similar to focus on specific sections.
- Respect existing guidance for secrets:
  - Decide whether to redact known secret fields or clearly document that this command is for
    development use only.

### 4. Diagnostics (Optional but Planned)

- Use the same traversal to compute:
  - Maximum import depth.
  - Total number of imports.
  - Locations of duplicate names (if validation errors are detected).
- Expose these via:
  - Flags (e.g. `--summary`) or
  - Additional subcommands (e.g. `duckalog check-imports`).

### 5. Tests (Phase 4)

- CLI tests:
  - Simple config with a few imports; assert `show-imports` output contains expected file names.
  - Config with a cycle; assert the CLI reports the issue instead of hanging.
  - `preview-config` output matches the configuration used by `load_config` (at least for core sections).
- Use temporary files in `tmp_path` and CLI runner patterns to simulate real invocation.

### 6. Documentation (Phase 4)

- Update CLI docs to:
  - Describe `show-imports` and `preview-config`.
  - Show typical usage scenarios (debugging import issues, verifying merged configs in CI).
  - Link back to the config imports documentation for context.

---

## Cross‑Cutting Concerns

- **Backward compatibility**
  - Configs without `imports` must behave exactly as before across all phases.
  - Any new fields or behaviors are purely additive and optional.

- **Incremental rollout**
  - Each phase corresponds to an OpenSpec change; implement, test, and ship each independently.
  - After Phase 1 is stable, progressively enable Phases 2–4 as needed.

- **Performance**
  - Import caching and depth/file limits can be introduced in Phase 2 or 3:
    - Cache parsed/merged configs by path/URI.
    - Optionally enforce max depth and max file count for safety.
  - Add performance tests or benchmarks once correctness is established.

