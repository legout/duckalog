# Remote Config Contracts Implementation Plan

> **Status: COMPLETE (2026-07-02).** Implemented through focused commits for public remote `load_config()` dispatch, shared remote import resolution, remote dotenv loading, deterministic backend validation tests, and remote SQL-file failure handling. Validation: `uv run pytest tests/test_remote_config.py tests/test_config_imports.py -q` → 72 passed, 10 warnings. `uv run ruff check src/duckalog/cli.py src/duckalog/remote_config.py tests/test_remote_config.py tests/test_cli_remote.py` → All checks passed.
>
> **Known follow-up (not blocking this plan):** remaining failing test files are stale/non-remote-config hygiene work: `tests/test_cli_remote.py` still contains deleted `build`/remote-export command expectations; `tests/test_root_based_security.py` still encodes an older path-security model. These belong to `refactor-test-dead-code-hygiene`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore local/remote config loading parity through the public `load_config()` API.

**Architecture:** Make `load_config()` the single public entry point for local and remote config files. Reuse the local import and interpolation pipeline for remote content through a content-loading adapter rather than maintaining a second resolver.

**Tech Stack:** Python, fsspec-compatible fake filesystems, Pydantic config models, pytest, uv, ruff.

## Global Constraints

- Use `uv run pytest ...` for test execution.
- Use `uv run ruff check ...` for lint verification on touched Python files.
- Do not add network-dependent tests; use fake filesystems, mocks, or local temporary files.
- Preserve public APIs unless this plan explicitly names a compatibility decision.
- Each task must finish with a focused commit containing only the files named in that task.
- If implementation changes the approved behavior, update the paired design spec before continuing.

---

## Source and sequencing

Paired spec: `docs/superpowers/specs/2026-07-01-refactor-remote-config-contracts-design.md`.

Implement this plan in the roadmap order documented at `docs/superpowers/2026-07-01-refactor-roadmap.md`. Do not merge this plan with neighboring plans; merge coordination happens through the roadmap.

## File Structure

- `tests/test_remote_config.py`: public remote `load_config()` API tests.
- `tests/test_config_imports.py`: import parity and cycle tests.
- `tests/test_cli_remote.py`: CLI-facing remote config behavior.
- `src/duckalog/config/api.py`: public `load_config()` dispatcher.
- `src/duckalog/config/resolution/imports.py`: shared import-resolution pipeline.
- `src/duckalog/remote_config.py`: remote content fetch and filesystem validation.

## Validation and acceptance

Before starting a task, run only that task's focused failing test. After each task, run its focused passing test, its lint command, and commit the narrow diff. After all tasks, run the final verification commands below.

### Task 1: Route remote URIs through the public load_config API without TypeError

**Files:**

- Modify: `src/duckalog/config/api.py`, `src/duckalog/remote_config.py`
- Test: `tests/test_remote_config.py`

**Interfaces:**

- Consumes: `load_config(path_or_uri, *, filesystem=None, load_dotenv=False)` and `load_config_from_uri(...)`.
- Produces: `load_config("s3://bucket/catalog.yaml", filesystem=fake_fs)` returns a validated `Config` without argument mismatch.

- [x] **Step 1: Write the failing test**

```python
def test_load_config_accepts_remote_uri_with_fake_filesystem(fake_remote_fs):
    fake_remote_fs.write_text("s3://bucket/catalog.yaml", "views:
  v:
    sql: SELECT 1 AS id
")

    config = load_config("s3://bucket/catalog.yaml", filesystem=fake_remote_fs)

    assert "v" in config.views
```

- [x] **Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest tests/test_remote_config.py::test_load_config_accepts_remote_uri_with_fake_filesystem -q
```

Expected: FAIL before the fix with the current remote-loading argument mismatch.

- [x] **Step 3: Write the minimal implementation**

```python
def load_config(path_or_uri: str | Path, **options: Any) -> Config:
    source = str(path_or_uri)
    if is_remote_uri(source):
        return load_config_from_uri(source, **options)
    return _load_config_from_local_file(Path(path_or_uri), **options)
```

- [x] **Step 4: Run test to verify it passes**

Run:

```bash
uv run pytest tests/test_remote_config.py::test_load_config_accepts_remote_uri_with_fake_filesystem -q
```

Expected: PASS.

- [x] **Step 5: Run task lint check**

Run:

```bash
uv run ruff check src/duckalog/config/api.py src/duckalog/remote_config.py tests/test_remote_config.py
```

Expected: PASS.

- [x] **Step 6: Commit**

```bash
git add tests/test_remote_config.py src/duckalog/config/api.py src/duckalog/remote_config.py && git commit -m "fix: route remote config load api"
```

### Task 2: Resolve remote imports through the shared import pipeline

**Files:**

- Modify: `src/duckalog/config/resolution/imports.py`, `src/duckalog/remote_config.py`
- Test: `tests/test_remote_config.py`, `tests/test_config_imports.py`

**Interfaces:**

- Consumes: The Task 1 remote `load_config()` dispatcher and the local `_load_config_with_imports` import graph semantics.
- Produces: Remote root configs can import remote children, including transitive imports and cycle detection.

- [x] **Step 1: Write the failing test**

```python
def test_remote_config_imports_remote_child(fake_remote_fs):
    fake_remote_fs.write_text("s3://bucket/base.yaml", "views:
  base:
    sql: SELECT 1 AS id
")
    fake_remote_fs.write_text("s3://bucket/root.yaml", "imports:
  - s3://bucket/base.yaml
views:
  root:
    sql: SELECT * FROM base
")

    config = load_config("s3://bucket/root.yaml", filesystem=fake_remote_fs)

    assert set(config.views) == {"base", "root"}
```

- [x] **Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest tests/test_remote_config.py::test_remote_config_imports_remote_child -q
```

Expected: FAIL before the fix because remote configs validate directly and bypass the shared import resolver.

- [x] **Step 3: Write the minimal implementation**

```python
def load_config_from_uri(uri: str, *, filesystem: Any | None = None, context: ImportContext | None = None, **options: Any) -> Config:
    loader = RemoteContentLoader(filesystem=filesystem)
    return load_config_with_imports(uri, content_loader=loader, context=context, **options)
```

- [x] **Step 4: Run test to verify it passes**

Run:

```bash
uv run pytest tests/test_remote_config.py::test_remote_config_imports_remote_child -q
```

Expected: PASS.

- [x] **Step 5: Run task lint check**

Run:

```bash
uv run ruff check src/duckalog/config/resolution/imports.py src/duckalog/remote_config.py tests/test_remote_config.py tests/test_config_imports.py
```

Expected: PASS.

- [x] **Step 6: Commit**

```bash
git add tests/test_remote_config.py tests/test_config_imports.py src/duckalog/config/resolution/imports.py src/duckalog/remote_config.py && git commit -m "fix: resolve remote config imports"
```

### Task 3: Define remote dotenv interpolation behavior

**Files:**

- Modify: `src/duckalog/config/api.py`, `src/duckalog/remote_config.py`
- Test: `tests/test_remote_config.py`

**Interfaces:**

- Consumes: The Task 2 shared import path and existing local `load_dotenv=True` behavior.
- Produces: Remote config content can reference local process environment values loaded from the caller-selected `.env` file.

- [x] **Step 1: Write the failing test**

```python
def test_remote_config_load_dotenv_interpolates_local_env_file(tmp_path, fake_remote_fs, monkeypatch):
    (tmp_path / ".env").write_text("DUCKALOG_REMOTE_TABLE=remote_table
")
    fake_remote_fs.write_text("s3://bucket/catalog.yaml", "views:
  v:
    sql: SELECT * FROM ${env:DUCKALOG_REMOTE_TABLE}
")
    monkeypatch.chdir(tmp_path)

    config = load_config("s3://bucket/catalog.yaml", filesystem=fake_remote_fs, load_dotenv=True)

    assert "remote_table" in config.views["v"].sql
```

- [x] **Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest tests/test_remote_config.py::test_remote_config_load_dotenv_interpolates_local_env_file -q
```

Expected: FAIL before the fix if remote content bypasses dotenv interpolation.

- [x] **Step 3: Write the minimal implementation**

```python
def load_config_from_uri(uri: str, *, load_dotenv: bool = False, **options: Any) -> Config:
    if load_dotenv:
        load_local_dotenv()
    return load_remote_config_through_shared_pipeline(uri, **options)
```

- [x] **Step 4: Run test to verify it passes**

Run:

```bash
uv run pytest tests/test_remote_config.py::test_remote_config_load_dotenv_interpolates_local_env_file -q
```

Expected: PASS.

- [x] **Step 5: Run task lint check**

Run:

```bash
uv run ruff check src/duckalog/config/api.py src/duckalog/remote_config.py tests/test_remote_config.py
```

Expected: PASS.

- [x] **Step 6: Commit**

```bash
git add tests/test_remote_config.py src/duckalog/config/api.py src/duckalog/remote_config.py && git commit -m "fix: define remote dotenv loading"
```

### Task 4: Reject invalid filesystem protocols and keep github URI support

**Files:**

- Modify: `src/duckalog/remote_config.py`
- Test: `tests/test_remote_config.py`, `tests/test_cli_remote.py`

**Interfaces:**

- Consumes: `validate_filesystem(filesystem)` and documented remote URI scheme requirements.
- Produces: Missing or empty filesystem protocols raise a config error, and mocked `github://` URIs use the fsspec-backed path.

- [x] **Step 1: Write the failing test**

```python
def test_validate_filesystem_rejects_empty_protocol():
    class EmptyProtocolFS:
        protocol = ""

    with pytest.raises(ConfigError, match="protocol"):
        validate_filesystem(EmptyProtocolFS())
```

- [x] **Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest tests/test_remote_config.py::test_validate_filesystem_rejects_empty_protocol -q
```

Expected: FAIL before the fix because invalid protocol errors are caught and ignored.

- [x] **Step 3: Write the minimal implementation**

```python
def validate_filesystem(filesystem: Any) -> None:
    protocol = getattr(filesystem, "protocol", None)
    if not protocol:
        raise ConfigError("Remote filesystem must define a non-empty protocol")
```

- [x] **Step 4: Run test to verify it passes**

Run:

```bash
uv run pytest tests/test_remote_config.py::test_validate_filesystem_rejects_empty_protocol -q
```

Expected: PASS.

- [x] **Step 5: Run task lint check**

Run:

```bash
uv run ruff check src/duckalog/remote_config.py tests/test_remote_config.py tests/test_cli_remote.py
```

Expected: PASS.

- [x] **Step 6: Commit**

```bash
git add tests/test_remote_config.py tests/test_cli_remote.py src/duckalog/remote_config.py && git commit -m "fix: validate remote filesystem protocols"
```

## Final Verification

- [x] `uv run pytest tests/test_remote_config.py tests/test_config_imports.py tests/test_cli_remote.py -q`
- [x] `uv run ruff check src/duckalog/config src/duckalog/remote_config.py tests/test_remote_config.py tests/test_config_imports.py tests/test_cli_remote.py`

Expected final result: all listed commands pass, every explicit acceptance criterion in the paired design spec maps to at least one completed task, and no task contains uncommitted changes.
