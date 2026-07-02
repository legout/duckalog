# CLI Boundary Simplification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make CLI help, errors, config loading, and query rendering truthful and shared.

**Architecture:** Lock the CLI contract first: filesystem options remain global Typer options. Then make import diagnostics fail loudly, centralize config loading/error mapping, share query rendering, and remove stale command-test drift.

**Tech Stack:** Python, Typer, pytest, uv, ruff.

## Global Constraints

- Use `uv run pytest ...` for test execution.
- Use `uv run ruff check ...` for lint verification on touched Python files.
- Do not add network-dependent tests; use fake filesystems, mocks, or local temporary files.
- Preserve public APIs unless this plan explicitly names a compatibility decision.
- Each task must finish with a focused commit containing only the files named in that task.
- If implementation changes the approved behavior, update the paired design spec before continuing.
---

## Source and sequencing

Paired spec: `docs/superpowers/specs/2026-07-01-refactor-cli-boundary-design.md`.

Implement this plan in the roadmap order documented at `docs/superpowers/2026-07-01-refactor-roadmap.md`. Do not merge this plan with neighboring plans; merge coordination happens through the roadmap.

## File Structure

- `tests/test_cli_filesystem.py`: global filesystem option contract.
- `tests/test_engine_cli.py`: command behavior and stale command cleanup.
- `tests/test_cli_query.py`: query rendering behavior.
- `src/duckalog/cli.py`: Typer commands and shared command helper calls.
- `src/duckalog/cli_filesystem.py`: filesystem option parsing.
- `src/duckalog/cli_imports.py`: import graph diagnostics.
- `src/duckalog/cli_display.py`: shared result rendering.

## Validation and acceptance

Before starting a task, run only that task's focused failing test. After each task, run its focused passing test, its lint command, and commit the narrow diff. After all tasks, run the final verification commands below.

### Task 1: Document and test filesystem options as global options

**Files:**
- Modify: `src/duckalog/cli.py`, `src/duckalog/cli_filesystem.py`
- Test: `tests/test_cli_filesystem.py`

**Interfaces:**
- Consumes: Typer global callback options and existing filesystem injection behavior.
- Produces: Tests and help expectations that use `duckalog --fs-protocol ... validate config.yaml`.

- [ ] **Step 1: Write the failing test**

```python
def test_filesystem_protocol_option_is_global(cli_runner, config_path):
    result = cli_runner.invoke(app, ["--fs-protocol", "file", "validate", str(config_path)])

    assert result.exit_code == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
uv run pytest tests/test_cli_filesystem.py::test_filesystem_protocol_option_is_global -q
```
Expected: FAIL before docs/tests are aligned if the suite still places filesystem options after subcommands.

- [ ] **Step 3: Write the minimal implementation**

```python
@app.callback()
def main_callback(fs_protocol: str | None = typer.Option(None, "--fs-protocol")) -> None:
    cli_state.filesystem_protocol = fs_protocol
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
uv run pytest tests/test_cli_filesystem.py::test_filesystem_protocol_option_is_global -q
```
Expected: PASS.

- [ ] **Step 5: Run task lint check**

Run:
```bash
uv run ruff check src/duckalog/cli.py src/duckalog/cli_filesystem.py tests/test_cli_filesystem.py
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/test_cli_filesystem.py src/duckalog/cli.py src/duckalog/cli_filesystem.py && git commit -m "fix: align cli filesystem option contract"
```

### Task 2: Make show-imports fail loudly for broken imports

**Files:**
- Modify: `src/duckalog/cli.py`, `src/duckalog/cli_imports.py`
- Test: `tests/test_engine_cli.py`

**Interfaces:**
- Consumes: `show_imports` command and `cli_imports.py` import graph builder.
- Produces: Missing or invalid imports cause non-zero exit with an actionable error message.

- [ ] **Step 1: Write the failing test**

```python
def test_show_imports_exits_nonzero_for_missing_import(cli_runner, tmp_path):
    config = tmp_path / "catalog.yaml"
    config.write_text("imports:
  - missing.yaml
views: {}
")

    result = cli_runner.invoke(app, ["show-imports", str(config)])

    assert result.exit_code != 0
    assert "missing.yaml" in result.output
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
uv run pytest tests/test_engine_cli.py::test_show_imports_exits_nonzero_for_missing_import -q
```
Expected: FAIL before the fix because broken imports are reported as partial success.

- [ ] **Step 3: Write the minimal implementation**

```python
def show_imports(config_path: Path) -> None:
    try:
        graph = build_import_graph(config_path)
    except ConfigError as exc:
        raise typer.Exit(code=1) from render_cli_error(exc)
    render_import_graph(graph)
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
uv run pytest tests/test_engine_cli.py::test_show_imports_exits_nonzero_for_missing_import -q
```
Expected: PASS.

- [ ] **Step 5: Run task lint check**

Run:
```bash
uv run ruff check src/duckalog/cli.py src/duckalog/cli_imports.py tests/test_engine_cli.py
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/test_engine_cli.py src/duckalog/cli.py src/duckalog/cli_imports.py && git commit -m "fix: fail cli show-imports on broken imports"
```

### Task 3: Centralize config path validation and ConfigError mapping

**Files:**
- Modify: `src/duckalog/cli.py`
- Test: `tests/test_engine_cli.py`, `tests/test_cli_filesystem.py`

**Interfaces:**
- Consumes: `run`, `generate_sql`, and `validate` command functions.
- Produces: A shared helper used by all config-loading CLI commands for path validation and user-facing errors.

- [ ] **Step 1: Write the failing test**

```python
def test_validate_and_generate_sql_share_missing_config_error(cli_runner, tmp_path):
    missing = tmp_path / "missing.yaml"

    validate_result = cli_runner.invoke(app, ["validate", str(missing)])
    sql_result = cli_runner.invoke(app, ["generate-sql", str(missing)])

    assert validate_result.exit_code != 0
    assert sql_result.exit_code != 0
    assert "missing.yaml" in validate_result.output
    assert "missing.yaml" in sql_result.output
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
uv run pytest tests/test_engine_cli.py::test_validate_and_generate_sql_share_missing_config_error -q
```
Expected: FAIL before the fix if commands diverge in missing-config error behavior.

- [ ] **Step 3: Write the minimal implementation**

```python
def load_cli_config(config_path: Path, *, filesystem: Any | None = None) -> Config:
    try:
        return load_config(config_path, filesystem=filesystem)
    except ConfigError as exc:
        raise CliConfigError(str(exc)) from exc
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
uv run pytest tests/test_engine_cli.py::test_validate_and_generate_sql_share_missing_config_error -q
```
Expected: PASS.

- [ ] **Step 5: Run task lint check**

Run:
```bash
uv run ruff check src/duckalog/cli.py tests/test_engine_cli.py tests/test_cli_filesystem.py
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/test_engine_cli.py tests/test_cli_filesystem.py src/duckalog/cli.py && git commit -m "refactor: centralize cli config loading"
```

### Task 4: Share query-result rendering across CLI query paths

**Files:**
- Modify: `src/duckalog/cli.py`, `src/duckalog/cli_display.py`
- Test: `tests/test_cli_query.py`

**Interfaces:**
- Consumes: `run --query`, `query`, interactive query execution, and `cli_display.py`.
- Produces: One renderer function used by all CLI query-result paths.

- [ ] **Step 1: Write the failing test**

```python
def test_run_query_and_query_command_render_same_table(cli_runner, config_path):
    run_result = cli_runner.invoke(app, ["run", str(config_path), "--query", "SELECT 1 AS id"])
    query_result = cli_runner.invoke(app, ["query", str(config_path), "SELECT 1 AS id"])

    assert run_result.exit_code == 0
    assert query_result.exit_code == 0
    assert normalize_table(run_result.output) == normalize_table(query_result.output)
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
uv run pytest tests/test_cli_query.py::test_run_query_and_query_command_render_same_table -q
```
Expected: FAIL before the fix if query-result rendering remains duplicated.

- [ ] **Step 3: Write the minimal implementation**

```python
def render_query_result(rows: Sequence[Mapping[str, Any]]) -> str:
    table = build_result_table(rows)
    return table.to_console_text()
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
uv run pytest tests/test_cli_query.py::test_run_query_and_query_command_render_same_table -q
```
Expected: PASS.

- [ ] **Step 5: Run task lint check**

Run:
```bash
uv run ruff check src/duckalog/cli.py src/duckalog/cli_display.py tests/test_cli_query.py
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/test_cli_query.py src/duckalog/cli.py src/duckalog/cli_display.py && git commit -m "refactor: share cli query rendering"
```

### Task 5: Remove stale build command and module-execution tests

**Files:**
- Modify: `tests/test_engine_cli.py`, `tests/test_cli_query.py`
- Test: `tests/test_engine_cli.py`, `tests/test_cli_query.py`

**Interfaces:**
- Consumes: The decision that `build` and `python -m duckalog.cli` are unsupported in this workstream.
- Produces: CLI tests invoke canonical `run` behavior or Typer runner behavior only.

- [ ] **Step 1: Write the failing test**

```python
def test_cli_suite_uses_run_for_catalog_execution(cli_runner, config_path):
    result = cli_runner.invoke(app, ["run", str(config_path)])

    assert result.exit_code == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
uv run pytest tests/test_engine_cli.py tests/test_cli_query.py -q
```
Expected: FAIL before the cleanup if stale command assertions remain active.

- [ ] **Step 3: Write the minimal implementation**

```python
SUPPORTED_CATALOG_EXECUTION_COMMAND = "run"
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
uv run pytest tests/test_engine_cli.py tests/test_cli_query.py -q
```
Expected: PASS.

- [ ] **Step 5: Run task lint check**

Run:
```bash
uv run ruff check tests/test_engine_cli.py tests/test_cli_query.py tests/test_engine_cli.py tests/test_cli_query.py
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/test_engine_cli.py tests/test_cli_query.py && git commit -m "test: remove stale cli command coverage"
```

## Final Verification

- [ ] `uv run pytest tests/test_cli_filesystem.py tests/test_engine_cli.py tests/test_cli_query.py -q`
- [ ] `uv run ruff check src/duckalog/cli.py src/duckalog/cli_filesystem.py src/duckalog/cli_imports.py src/duckalog/cli_display.py tests/test_cli_filesystem.py tests/test_engine_cli.py tests/test_cli_query.py`

Expected final result: all listed commands pass, every explicit acceptance criterion in the paired design spec maps to at least one completed task, and no task contains uncommitted changes.
