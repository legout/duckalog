# Test and Dead-Code Hygiene Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove stale abstractions, stale docs/tests, and duplicated fixtures after contract repairs.

**Architecture:** Run this after the behavior plans. Inventory candidates with code-aware searches, remove or justify dead code in narrow commits, refresh docs, consolidate fixtures, and improve obvious typing drift without changing behavior.

**Tech Stack:** Python AST tools, pytest, ruff, mypy, uv, Markdown docs.

## Global Constraints

- Use `uv run pytest ...` for test execution.
- Use `uv run ruff check ...` for lint verification on touched Python files.
- Do not add network-dependent tests; use fake filesystems, mocks, or local temporary files.
- Preserve public APIs unless this plan explicitly names a compatibility decision.
- Each task must finish with a focused commit containing only the files named in that task.
- If implementation changes the approved behavior, update the paired design spec before continuing.

---

## Source and sequencing

Paired spec: `docs/superpowers/specs/2026-07-01-refactor-test-dead-code-hygiene-design.md`.

Implement this plan in the roadmap order documented at `docs/superpowers/2026-07-01-refactor-roadmap.md`. Do not merge this plan with neighboring plans; merge coordination happens through the roadmap.

## File Structure

- `src/duckalog/`: stale abstractions and obvious annotation drift.
- `tests/test_config.py`: duplicated config YAML fixtures.
- `tests/test_config_imports.py`: duplicated import YAML fixtures.
- `tests/conftest.py`: shared test factory helpers when reuse crosses files.
- `tests/test_remote_config.py`: stale `mock.patch` target referencing the removed `duckalog.config._load_config_from_local_file` re-export.
- `ARCHITECTURE.md`: stale boundary and file references.
- `docs/`: stale command and architecture references outside behavior plans.

## Validation and acceptance

Before starting a task, run only that task's focused failing test. After each task, run its focused passing test, its lint command, and commit the narrow diff. After all tasks, run the final verification commands below.

### Task 1: Inventory and remove uncalled internal abstractions

**Files:**

- Modify: `src/duckalog/`
- Test: `tests/`

**Interfaces:**

- Consumes: Completed security, remote config, catalog runtime, and CLI plans.
- Produces: Each reviewed dead-code candidate is either removed or documented with a live caller/test.

- [ ] **Step 1: Write the failing test**

```python
def test_default_env_processor_is_not_part_of_public_api():
    import duckalog.config as config

    assert not hasattr(config, "DefaultEnvProcessor")
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest tests -q
```

Expected: FAIL only for candidates whose tests or public imports prove the removal decision needs adjustment.

- [ ] **Step 3: Write the minimal implementation**

```python
# Remove internal classes and parameters only after grep and import checks show no supported caller remains.
```

Also fix the stale mock target in `tests/test_remote_config.py`. The helper is no longer re-exported from `duckalog.config` (it lives in `duckalog.config.api`), so the existing `patch("duckalog.config._load_config_from_local_file")` target is dead and silently patches nothing. Rewrite the test to patch the real location or to exercise behavior through `load_config()`:

```python
with patch("duckalog.config.api._load_config_from_local_file") as mock_load:
    mock_config = Mock()
    mock_load.return_value = mock_config

    from duckalog.config import load_config

    config = load_config(config_path, filesystem=None)
    mock_load.assert_called_once()
    assert config == mock_config
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
uv run pytest tests/test_remote_config.py -q
```

Expected: PASS, with the patched mock actually intercepting the local load path.

- [ ] **Step 5: Run task lint check**

Run:

```bash
uv run ruff check src/duckalog/ tests/
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/duckalog tests && git commit -m "refactor: remove unused internal abstractions"
```

### Task 2: Refresh stale architecture and command references

**Files:**

- Modify: `ARCHITECTURE.md`, `docs/`
- Test: `ARCHITECTURE.md`

**Interfaces:**

- Consumes: The final command/runtime decisions from the CLI and catalog runtime plans.
- Produces: Docs describe current files and current commands, without references to removed modules or commands.

- [ ] **Step 1: Write the failing test**

```python
def test_architecture_doc_no_longer_mentions_removed_build_command():
    text = Path("ARCHITECTURE.md").read_text()

    assert "duckalog build" not in text
    assert "duckalog run" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
uv run python - <<'PY'
from pathlib import Path
text = Path("ARCHITECTURE.md").read_text()
assert "duckalog build" not in text
PY
```

Expected: FAIL before stale command references are removed.

- [ ] **Step 3: Write the minimal implementation**

```python
# Update docs to name the current command surface: `duckalog run`, `duckalog validate`, `duckalog generate-sql`, and `duckalog show-imports`.
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
uv run python - <<'PY'
from pathlib import Path
text = Path("ARCHITECTURE.md").read_text()
assert "duckalog build" not in text
PY
```

Expected: PASS.

- [ ] **Step 5: Run task lint check**

Run:

```bash
uv run ruff check ARCHITECTURE.md docs/ ARCHITECTURE.md
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add ARCHITECTURE.md docs && git commit -m "docs: refresh architecture references"
```

### Task 3: Consolidate duplicated config test fixtures

**Files:**

- Modify: `tests/test_config.py`, `tests/test_config_imports.py`, `tests/conftest.py`
- Test: `tests/test_config.py`, `tests/test_config_imports.py`

**Interfaces:**

- Consumes: Stable config behavior from the security and remote config plans.
- Produces: Shared factory helpers for repeated config YAML patterns without reducing assertions.

- [ ] **Step 1: Write the failing test**

```python
def write_config(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(body)
    return path
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest tests/test_config.py tests/test_config_imports.py -q
```

Expected: PASS before and after fixture consolidation; any failure means the helper changed test semantics.

- [ ] **Step 3: Write the minimal implementation**

```python
def simple_view_config(sql: str = "SELECT 1 AS id") -> str:
    return "views:
  v:
    sql: " + sql + "
"
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
uv run pytest tests/test_config.py tests/test_config_imports.py -q
```

Expected: PASS.

- [ ] **Step 5: Run task lint check**

Run:

```bash
uv run ruff check tests/test_config.py tests/test_config_imports.py tests/conftest.py tests/test_config.py tests/test_config_imports.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/test_config.py tests/test_config_imports.py tests/conftest.py && git commit -m "test: consolidate config fixtures"
```

### Task 4: Reduce obvious mypy drift in touched modules

**Files:**

- Modify: `src/duckalog/`
- Test: `src/duckalog/`

**Interfaces:**

- Consumes: The final touched-module set from earlier hygiene tasks.
- Produces: Fewer mypy errors on touched modules without large unrelated typing rewrites.

- [ ] **Step 1: Write the failing test**

```python
def test_public_imports_remain_available_after_typing_cleanup():
    from duckalog.config import load_config
    from duckalog.python_api import connect_to_catalog

    assert callable(load_config)
    assert callable(connect_to_catalog)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest tests -q
```

Expected: PASS before typing cleanup; failures reveal accidental behavior changes.

- [ ] **Step 3: Write the minimal implementation**

```python
def normalize_path(path: str | Path) -> Path:
    return path if isinstance(path, Path) else Path(path)
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
uv run mypy src/duckalog/config src/duckalog/engine.py src/duckalog/cli.py
```

Expected: PASS.

- [ ] **Step 5: Run task lint check**

Run:

```bash
uv run ruff check src/duckalog/ src/duckalog/
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/duckalog tests && git commit -m "refactor: reduce touched-module typing drift"
```

### Task 5: Verify cleanup did not duplicate earlier behavior/removal-plan scope

**Files:**

- Modify: `docs/superpowers/2026-07-01-refactor-roadmap.md`, `docs/superpowers/specs/2026-07-01-refactor-test-dead-code-hygiene-design.md`
- Test: `docs/superpowers/`

**Interfaces:**

- Consumes: CLI behavior plans already owning their specific repairs.
- Produces: The hygiene docs reference earlier behavior/removal decisions instead of duplicating their tasks.

- [ ] **Step 1: Write the failing test**

```python
def test_hygiene_plan_does_not_reintroduce_removed_test_scope():
    text = Path("docs/superpowers/plans/2026-07-01-refactor-test-dead-code-hygiene.md").read_text()

    assert "Verify cleanup did not duplicate earlier behavior/removal-plan scope" in text
    assert "Replace broad exception-swallowing tests" not in text
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
uv run python - <<'PY'
from pathlib import Path
text = Path("docs/superpowers/plans/2026-07-01-refactor-test-dead-code-hygiene.md").read_text()
forbidden = "Replace broad exception-swallowing tests"
assert "Replace broad exception-swallowing tests" not in text
PY
```

Expected: FAIL before the Superpowers docs are de-duplicated.

- [ ] **Step 3: Write the minimal implementation**

```python
# Roadmap owns sequencing. Behavior/removal plans own behavior-specific repairs. Hygiene owns final stale-reference cleanup only.
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
uv run python - <<'PY'
from pathlib import Path
text = Path("docs/superpowers/plans/2026-07-01-refactor-test-dead-code-hygiene.md").read_text()
forbidden = "Replace broad exception-swallowing tests"
assert "Replace broad exception-swallowing tests" not in text
PY
```

Expected: PASS.

- [ ] **Step 5: Run task lint check**

Run:

```bash
uv run ruff check docs/superpowers/2026-07-01-refactor-roadmap.md docs/superpowers/specs/2026-07-01-refactor-test-dead-code-hygiene-design.md docs/superpowers/
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add docs/superpowers && git commit -m "docs: de-duplicate superpowers cleanup scope"
```

## Final Verification

- [ ] `uv run pytest tests -q`
- [ ] `uv run ruff check src/duckalog tests`
- [ ] `uv run mypy src/duckalog/config src/duckalog/engine.py src/duckalog/cli.py`

Expected final result: all listed commands pass, every explicit acceptance criterion in the paired design spec maps to at least one completed task, and no task contains uncommitted changes.
