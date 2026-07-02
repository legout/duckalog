# Catalog Runtime Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Unify catalog runtime state across engine, Python API, and CLI connection paths.

**Architecture:** Add hierarchical catalog tests first, then extract a shared runtime helper that both `CatalogBuilder` and `CatalogConnection` use. Keep remote-output classification independent from optional fsspec imports and make stale API branches explicit.

**Tech Stack:** Python, DuckDB, Typer, pytest, uv, ruff.

## Global Constraints

- Use `uv run pytest ...` for test execution.
- Use `uv run ruff check ...` for lint verification on touched Python files.
- Do not add network-dependent tests; use fake filesystems, mocks, or local temporary files.
- Preserve public APIs unless this plan explicitly names a compatibility decision.
- Each task must finish with a focused commit containing only the files named in that task.
- If implementation changes the approved behavior, update the paired design spec before continuing.
---

## Source and sequencing

Paired spec: `docs/superpowers/specs/2026-07-01-refactor-catalog-runtime-boundary-design.md`.

Implement this plan in the roadmap order documented at `docs/superpowers/2026-07-01-refactor-roadmap.md`. Do not merge this plan with neighboring plans; merge coordination happens through the roadmap.

## File Structure

- `tests/test_connection_api.py`: Python API hierarchical catalog regression tests.
- `tests/test_engine_hierarchical.py`: shared runtime/build-path tests.
- `tests/test_engine_remote_export.py`: remote output classification tests.
- `src/duckalog/engine.py`: shared runtime helper and builder integration.
- `src/duckalog/connection.py`: connection integration.
- `src/duckalog/python_api.py`: public connection API wrapper.

## Validation and acceptance

Before starting a task, run only that task's focused failing test. After each task, run its focused passing test, its lint command, and commit the narrow diff. After all tasks, run the final verification commands below.

### Task 1: Prove hierarchical catalogs through connect_to_catalog

**Files:**
- Modify: `tests/test_connection_api.py`, `src/duckalog/connection.py`, `src/duckalog/engine.py`
- Test: `tests/test_connection_api.py`

**Interfaces:**
- Consumes: `duckalog.python_api.connect_to_catalog(path, force_rebuild=True)` and nested `attachments.duckalog` config semantics.
- Produces: A connection returned by `connect_to_catalog()` can query a parent view that selects from an attached child Duckalog catalog.

- [ ] **Step 1: Write the failing test**

```python
def test_connect_to_catalog_can_query_parent_view_from_child_duckalog_attachment(tmp_path):
    child = tmp_path / "child.yaml"
    child.write_text("views:
  child_view:
    sql: SELECT 1 AS id
")
    parent = tmp_path / "parent.yaml"
    parent.write_text(f"attachments:
  duckalog:
    child:
      config_path: {child}
views:
  parent_view:
    sql: SELECT * FROM child.child_view
")

    conn = connect_to_catalog(parent, force_rebuild=True)

    assert conn.execute("SELECT id FROM parent_view").fetchone() == (1,)
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
uv run pytest tests/test_connection_api.py::test_connect_to_catalog_can_query_parent_view_from_child_duckalog_attachment -q
```
Expected: FAIL before the fix because the connection path does not build nested Duckalog attachment state.

- [ ] **Step 3: Write the minimal implementation**

```python
def prepare_catalog_runtime(config: Config, *, connection: duckdb.DuckDBPyConnection) -> CatalogRuntimeState:
    attachments = build_attachment_dependencies(config)
    apply_settings(connection, config.settings)
    create_attachments(connection, attachments)
    create_views(connection, config.views)
    return CatalogRuntimeState(connection=connection, attachments=attachments)
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
uv run pytest tests/test_connection_api.py::test_connect_to_catalog_can_query_parent_view_from_child_duckalog_attachment -q
```
Expected: PASS.

- [ ] **Step 5: Run task lint check**

Run:
```bash
uv run ruff check tests/test_connection_api.py src/duckalog/connection.py src/duckalog/engine.py tests/test_connection_api.py
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/test_connection_api.py src/duckalog/connection.py src/duckalog/engine.py && git commit -m "fix: share catalog runtime for connections"
```

### Task 2: Use the same runtime state from CLI run

**Files:**
- Modify: `tests/test_engine_hierarchical.py`, `src/duckalog/engine.py`
- Test: `tests/test_engine_hierarchical.py`

**Interfaces:**
- Consumes: `prepare_catalog_runtime(...)` from Task 1 and the CLI `run` engine path.
- Produces: `duckalog run` behavior matches `connect_to_catalog()` for nested Duckalog attachments.

- [ ] **Step 1: Write the failing test**

```python
def test_cli_run_uses_shared_runtime_for_child_duckalog_attachment(cli_runner, tmp_path):
    child = tmp_path / "child.yaml"
    child.write_text("views:
  child_view:
    sql: SELECT 1 AS id
")
    parent = tmp_path / "parent.yaml"
    parent.write_text(f"attachments:
  duckalog:
    child:
      config_path: {child}
views:
  parent_view:
    sql: SELECT * FROM child.child_view
")

    result = cli_runner.invoke(app, ["run", str(parent), "--query", "SELECT id FROM parent_view"])

    assert result.exit_code == 0
    assert "1" in result.output
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
uv run pytest tests/test_engine_hierarchical.py::test_cli_run_uses_shared_runtime_for_child_duckalog_attachment -q
```
Expected: FAIL before the fix if the CLI build path diverges from the connection runtime path.

- [ ] **Step 3: Write the minimal implementation**

```python
class CatalogBuilder:
    def build(self) -> CatalogBuildResult:
        runtime = prepare_catalog_runtime(self.config, connection=self.connection)
        return CatalogBuildResult(connection=runtime.connection, attachments=runtime.attachments)
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
uv run pytest tests/test_engine_hierarchical.py::test_cli_run_uses_shared_runtime_for_child_duckalog_attachment -q
```
Expected: PASS.

- [ ] **Step 5: Run task lint check**

Run:
```bash
uv run ruff check tests/test_engine_hierarchical.py src/duckalog/engine.py tests/test_engine_hierarchical.py
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/test_engine_hierarchical.py src/duckalog/engine.py && git commit -m "fix: use shared runtime from cli run"
```

### Task 3: Classify remote output before optional fsspec imports

**Files:**
- Modify: `src/duckalog/engine.py`
- Test: `tests/test_engine_remote_export.py`

**Interfaces:**
- Consumes: Existing remote URI detection and remote export error handling.
- Produces: `s3://...` output targets raise the intended optional-dependency error when fsspec is unavailable.

- [ ] **Step 1: Write the failing test**

```python
def test_remote_output_without_fsspec_reports_optional_dependency(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "fsspec", None)
    config = make_catalog_config(output="s3://bucket/catalog.duckdb")

    with pytest.raises(ConfigError, match="fsspec"):
        build_catalog(config)
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
uv run pytest tests/test_engine_remote_export.py::test_remote_output_without_fsspec_reports_optional_dependency -q
```
Expected: FAIL before the fix because DuckDB attempts to open the remote URI as a local file.

- [ ] **Step 3: Write the minimal implementation**

```python
def classify_output_uri(uri: str) -> OutputTarget:
    if is_remote_uri(uri):
        require_fsspec_for_remote_output(uri)
        return OutputTarget.remote(uri)
    return OutputTarget.local(Path(uri))
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
uv run pytest tests/test_engine_remote_export.py::test_remote_output_without_fsspec_reports_optional_dependency -q
```
Expected: PASS.

- [ ] **Step 5: Run task lint check**

Run:
```bash
uv run ruff check src/duckalog/engine.py tests/test_engine_remote_export.py
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/test_engine_remote_export.py src/duckalog/engine.py && git commit -m "fix: classify remote catalog output"
```

### Task 4: Preserve include_secrets and remove unsupported use_connection drift

**Files:**
- Modify: `src/duckalog/engine.py`, `src/duckalog/python_api.py`
- Test: `tests/test_connection_api.py`

**Interfaces:**
- Consumes: `build_catalog(include_secrets=False)` documented behavior and the Task 1 shared runtime helper.
- Produces: `include_secrets=False` remains covered, and no supported branch bypasses remote-output/runtime setup through `use_connection`.

- [ ] **Step 1: Write the failing test**

```python
def test_build_catalog_include_secrets_false_excludes_secret_sql(tmp_path):
    config = make_config_with_secret_and_view(tmp_path)

    result = build_catalog(config, include_secrets=False, dry_run=True)

    assert "CREATE SECRET" not in result.sql
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
uv run pytest tests/test_connection_api.py::test_build_catalog_include_secrets_false_excludes_secret_sql -q
```
Expected: FAIL before the fix if the parameter is ignored or the stale branch bypasses the shared runtime.

- [ ] **Step 3: Write the minimal implementation**

```python
def build_catalog(config: Config, *, include_secrets: bool = True, dry_run: bool = False) -> CatalogBuildResult:
    sql = generate_catalog_sql(config, include_secrets=include_secrets)
    if dry_run:
        return CatalogBuildResult(sql=sql)
    return execute_catalog_sql(config, sql=sql)
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
uv run pytest tests/test_connection_api.py::test_build_catalog_include_secrets_false_excludes_secret_sql -q
```
Expected: PASS.

- [ ] **Step 5: Run task lint check**

Run:
```bash
uv run ruff check src/duckalog/engine.py src/duckalog/python_api.py tests/test_connection_api.py
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/test_connection_api.py src/duckalog/engine.py src/duckalog/python_api.py && git commit -m "fix: settle catalog runtime api drift"
```

## Final Verification

- [ ] `uv run pytest tests/test_connection_api.py tests/test_engine_hierarchical.py tests/test_engine_remote_export.py -q`
- [ ] `uv run ruff check src/duckalog/engine.py src/duckalog/connection.py src/duckalog/python_api.py tests/test_connection_api.py tests/test_engine_hierarchical.py tests/test_engine_remote_export.py`

Expected final result: all listed commands pass, every explicit acceptance criterion in the paired design spec maps to at least one completed task, and no task contains uncommitted changes.
