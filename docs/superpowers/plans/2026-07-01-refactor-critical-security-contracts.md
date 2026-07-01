# Critical Security Contracts Implementation Plan

> **Status: COMPLETE (2026-07-01).** All three tasks implemented and committed: `9d8f826` (quote secret identifiers), `bc21d97` (scoped secret rendering), `6f4d253` (attachment path boundaries). Acceptance tests green: `tests/test_sql_security.py` (26 passed), `tests/test_path_security.py` (21 passed).
>
> **Known follow-up (not blocking this plan):** the pre-existing `tests/test_root_based_security.py` suite (from `ecdb4dc`, an older path-security model) now has 7 failures because it asserts the superseded path contract. Resolution is deferred to `refactor-test-dead-code-hygiene` (roadmap #6).

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden DuckDB secret SQL generation and attachment path security.

**Architecture:** Implement security fixes with one regression-focused task per contract: secret identifiers, scoped secrets, and attachment path boundaries. Each task starts with a failing test, repairs the owning module, and commits a narrow diff.

**Tech Stack:** Python, DuckDB, Pydantic, pytest, uv, ruff.

## Global Constraints

- Use `uv run pytest ...` for test execution.
- Use `uv run ruff check ...` for lint verification on touched Python files.
- Do not add network-dependent tests; use fake filesystems, mocks, or local temporary files.
- Preserve public APIs unless this plan explicitly names a compatibility decision.
- Each task must finish with a focused commit containing only the files named in that task.
- If implementation changes the approved behavior, update the paired design spec before continuing.

---

## Source and sequencing

Paired spec: `docs/superpowers/specs/2026-07-01-refactor-critical-security-contracts-design.md`.

Implement this plan in the roadmap order documented at `docs/superpowers/2026-07-01-refactor-roadmap.md`. Do not merge this plan with neighboring plans; merge coordination happens through the roadmap.

## File Structure

- `tests/test_sql_security.py`: SQL injection and path traversal regression tests.
- `tests/test_sql_generation.py`: scoped secret SQL regression tests.
- `src/duckalog/sql_generation.py`: `CREATE SECRET` rendering and identifier quoting.
- `src/duckalog/config/validators.py`: attachment path validation hook.
- `src/duckalog/config/security/path.py`: shared local-root boundary helpers.
- `src/duckalog/sql_utils.py`: existing SQL literal/identifier helpers.

## Validation and acceptance

Before starting a task, run only that task's focused failing test. After each task, run its focused passing test, its lint command, and commit the narrow diff. After all tasks, run the final verification commands below.

### Task 1: Quote DuckDB secret identifiers

**Files:**

- Modify: `src/duckalog/sql_generation.py`
- Test: `tests/test_sql_security.py`
- Test: `tests/test_sql_generation.py` (existing expectations must be updated to match quoted identifiers)

**Interfaces:**

- Consumes: `generate_secret_sql(secret: SecretConfig) -> str` and the existing SQL quoting helper from `src/duckalog/sql_utils.py`.
- Produces: A generated `CREATE SECRET` statement whose secret name is quoted as a DuckDB identifier before execution.

- [x] **Step 1: Write the failing test**

```python
def test_secret_name_is_quoted_before_execution(duckdb_connection):
    duckdb_connection.execute("CREATE TABLE keep_me(id INTEGER)")
    secret = SecretConfig(
        type="s3",
        name='safe_name"; DROP TABLE keep_me; --',
        key_id="key",
        secret="secret",
    )

    sql = generate_secret_sql(secret)
    duckdb_connection.execute(sql)

    assert duckdb_connection.execute("SELECT count(*) FROM keep_me").fetchone() == (0,)
```

- [x] **Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest tests/test_sql_security.py::TestSecretSQLInjectionPrevention::test_secret_name_is_quoted_before_execution -q
```

Expected: FAIL before the fix because the generated secret name is not safely quoted.

- [x] **Step 3: Write the minimal implementation**

```python
def generate_secret_sql(secret: SecretConfig) -> str:
    secret_name = quote_ident(secret.name or secret.type)
    params = _build_secret_params(secret)
    return f"CREATE SECRET {secret_name} (" + ", ".join(params) + ");"
```

- [x] **Step 4: Run test to verify it passes**

Run:

```bash
uv run pytest tests/test_sql_security.py::TestSecretSQLInjectionPrevention::test_secret_name_is_quoted_before_execution -q
```

Expected: PASS.

- [x] **Step 5: Run task lint check**

Run:

```bash
uv run ruff check src/duckalog/sql_generation.py tests/test_sql_security.py tests/test_sql_generation.py
```

Expected: PASS.

- [x] **Step 6: Commit**

```bash
git add tests/test_sql_security.py tests/test_sql_generation.py src/duckalog/sql_generation.py && git commit -m "fix: quote duckdb secret identifiers"
```

### Task 2: Render scoped secrets as valid DuckDB SQL

**Files:**

- Modify: `src/duckalog/sql_generation.py`
- Test: `tests/test_sql_generation.py`

**Interfaces:**

- Consumes: `SecretConfig.scope` and `generate_secret_sql(secret: SecretConfig) -> str` from Task 1.
- Produces: `SCOPE` rendered inside the parenthesized `CREATE SECRET` option list.

- [x] **Step 1: Write the failing test**

```python
def test_scoped_secret_scope_is_inside_create_secret_options():
    secret = SecretConfig(type="http", name="scoped_http", scope="https://example.com")

    sql = generate_secret_sql(secret)

    assert "SCOPE 'https://example.com'" in sql
    assert sql.index("SCOPE") < sql.rindex(")")
```

- [x] **Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest tests/test_sql_generation.py::test_scoped_secret_scope_is_inside_create_secret_options -q
```

Expected: FAIL before the fix because `SCOPE` is appended after the statement terminator.

- [x] **Step 3: Write the minimal implementation**

```python
def _build_secret_params(secret: SecretConfig) -> list[str]:
    params = _build_provider_params(secret)
    if secret.scope:
        params.append(f"SCOPE {quote_literal(secret.scope)}")
    return params
```

- [x] **Step 4: Run test to verify it passes**

Run:

```bash
uv run pytest tests/test_sql_generation.py::test_scoped_secret_scope_is_inside_create_secret_options -q
```

Expected: PASS.

- [x] **Step 5: Run task lint check**

Run:

```bash
uv run ruff check src/duckalog/sql_generation.py tests/test_sql_generation.py
```

Expected: PASS.

- [x] **Step 6: Commit**

```bash
git add tests/test_sql_generation.py src/duckalog/sql_generation.py && git commit -m "fix: render scoped duckdb secrets"
```

### Task 3: Validate attachment paths against the local root boundary

**Files:**

- Modify: `src/duckalog/config/validators.py`, `src/duckalog/config/security/path.py`
- Test: `tests/test_sql_security.py`

**Interfaces:**

- Consumes: Existing view URI path-boundary validation behavior in `src/duckalog/config/security/path.py`.
- Produces: DuckDB, SQLite, and nested Duckalog attachment paths rejected when local traversal escapes the config root.

- [x] **Step 1: Write the failing test**

```python
def test_attachment_paths_cannot_escape_config_root(tmp_path):
    config_path = tmp_path / "catalog.yaml"
    config_path.write_text(
        "attachments:
"
        "  duckdb:
"
        "    escaped:
"
        "      path: ../outside.duckdb
"
    )

    with pytest.raises(ConfigError, match="outside the allowed root"):
        load_config(config_path)
```

- [x] **Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest tests/test_sql_security.py::test_attachment_paths_cannot_escape_config_root -q
```

Expected: FAIL before the fix because attachment paths are resolved without the same root-boundary check as view URIs.

- [x] **Step 3: Write the minimal implementation**

```python
def validate_local_attachment_path(path: str, *, config_dir: Path) -> Path:
    resolved = resolve_relative_path(path, base_dir=config_dir)
    ensure_path_within_root(resolved, root=config_dir)
    return resolved
```

- [x] **Step 4: Run test to verify it passes**

Run:

```bash
uv run pytest tests/test_sql_security.py::test_attachment_paths_cannot_escape_config_root -q
```

Expected: PASS.

- [x] **Step 5: Run task lint check**

Run:

```bash
uv run ruff check src/duckalog/config/validators.py src/duckalog/config/security/path.py tests/test_sql_security.py
```

Expected: PASS.

- [x] **Step 6: Commit**

```bash
git add tests/test_sql_security.py src/duckalog/config/validators.py src/duckalog/config/security/path.py && git commit -m "fix: validate attachment path boundaries"
```

## Final Verification

- [x] `uv run pytest tests/test_sql_security.py tests/test_sql_generation.py -q`
- [x] `uv run ruff check src/duckalog/sql_generation.py src/duckalog/config tests/test_sql_security.py tests/test_sql_generation.py`

Expected final result: all listed commands pass, every explicit acceptance criterion in the paired design spec maps to at least one completed task, and no task contains uncommitted changes.
