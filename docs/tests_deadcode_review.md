# Duckalog tests/dead-code/duplication review

Scope inspected: all 27 files under `tests/` (13,297 test lines by `wc -l`), `src/duckalog/`, and `ARCHITECTURE.md`. The requested `plan.md` and `progress.md` were not present in the repository root at review time.

## Review

- Correct: `uv run ruff check src tests` exits 0, so the current tree has no Ruff-reported unused imports or standard lint violations in `src/` or `tests/`.
- Correct: The dead-code modules called out in `ARCHITECTURE.md` as `src/duckalog/config/loading/base.py`, `file.py`, and `remote.py` are no longer present; `src/duckalog/config/loading/` contains only `__init__.py` and `sql.py`.
- Correct: Most assertion-less tests identified by AST are still meaningful because they assert via `pytest.raises(...)`, mock assertions, or nested async assertions; I did not count those alone as failures.
- Blocker: `tests/test_cli_filesystem.py:249` invokes `[sys.executable, "-m", "duckalog.cli", "build", "--help"]`, but `src/duckalog/cli.py:922` only defines `main_entry()` and has no `if __name__ == "__main__"` call. Running `uv run pytest tests/test_cli_filesystem.py::TestCLIFileSystem::test_cli_help_text_includes_filesystem_options -q` fails because `result.stdout == ""` at `tests/test_cli_filesystem.py:257`. This is a high-severity stale/inert CLI test path; it verifies neither the installed console script nor the Typer app.
- Blocker: The same CLI filesystem test file still references an obsolete `build` command at `tests/test_cli_filesystem.py:249` and `tests/test_cli_filesystem.py:291-300`, while the Typer commands in `src/duckalog/cli.py` are `run`, `generate-sql`, `validate`, `show-paths`, `show-imports`, `ui`, `query`, `init`, and `version` (`src/duckalog/cli.py:140`, `src/duckalog/cli.py:152`, `src/duckalog/cli.py:312`, `src/duckalog/cli.py:375`, `src/duckalog/cli.py:425`, `src/duckalog/cli.py:503`, `src/duckalog/cli.py:616`, `src/duckalog/cli.py:691`, `src/duckalog/cli.py:801`). Severity is high because these tests can fail for the wrong reason or pass without covering a real command.
- Blocker: Several dashboard CLI tests swallow all outcomes. `tests/test_dashboard.py:747-767`, `tests/test_dashboard.py:772-790`, `tests/test_dashboard.py:795-813`, `tests/test_dashboard.py:819-837`, `tests/test_dashboard.py:843-861`, `tests/test_dashboard.py:869-886`, `tests/test_dashboard.py:894-910`, and `tests/test_dashboard.py:919-954` call `duckalog.cli.ui(...)` and then `pass` on `SystemExit` and broad `Exception`. These tests can pass when the dashboard cannot load config, cannot import dependencies, or cannot start. Severity is high because the test names claim option validation but the assertions accept any exception.
- Medium: `tests/test_performance_benchmarks.py:96-106` and `tests/test_performance_benchmarks.py:110-127` benchmark env interpolation and SQL file loading without validating result shape or a threshold; `tests/test_performance_benchmarks.py:130-134` repeats `load_config()` under `@pytest.mark.limit_memory` but has no explicit assertion if the marker is not active. Rationale: these are useful measurements, but as tests they mainly prove no exception under the current plugin setup.
- Medium: `tests/test_config.py` is a 2,620-line mixed schema/loader suite. The semantic-model validation cases at `tests/test_config.py:1337-1595` repeatedly write a full YAML config to disk and call `load_config()` for model-level validation failures. This makes small schema validations depend on file I/O, env interpolation, import resolution, and loader exception wrapping. Severity is medium because the integration path is valuable, but the repeated pattern increases test bloat and makes failures less localized.
- Medium: Duplicated test fixture/config construction is widespread. Exact repeated blocks detected include the semantic-model base YAML repeated 11 times in `tests/test_config.py:742-752`, `tests/test_config.py:1162-1172`, `tests/test_config.py:1364-1374`, `tests/test_config.py:1391-1401`, `tests/test_config.py:1416-1426`, `tests/test_config.py:1440-1450`, `tests/test_config.py:1467-1477`, and `tests/test_config.py:1492-1502`; the simple `show-imports` catalog YAML repeats in `tests/test_engine_cli.py:511-524`, `tests/test_engine_cli.py:574-587`, `tests/test_engine_cli.py:598-611`, and `tests/test_engine_cli.py:628-641`; identical `_write()` helpers exist at `tests/test_config.py:16-18` and `tests/test_config_imports.py:20-22`. Rationale: this duplication is test bloat and increases maintenance cost when config schema defaults change.
- Medium: Production CLI shape appears hard to test cleanly. `src/duckalog/cli.py:616-686` loads config, imports UI dependencies, constructs the app, emits warnings, and calls `uvicorn.run(...)` in one command function. The corresponding tests at `tests/test_dashboard.py:747-954` use broad exception swallowing rather than deterministic assertions, which is evidence that the command boundary is difficult to exercise without starting a server.
- Medium: Production CLI contains duplicated local-config existence validation in three command functions: `src/duckalog/cli.py:222-241` (`run`), `src/duckalog/cli.py:331-350` (`generate_sql`), and `src/duckalog/cli.py:389-408` (`validate`). Rationale: exact duplicate control flow means a future remote/local path behavior change has at least three sites to keep consistent.
- Medium: Production SQL option rendering logic is duplicated. `_build_postgres_params()` and `_build_mysql_params()` repeat the same connection-string/host/port/database/user/password construction at `src/duckalog/sql_generation.py:189-208` and `src/duckalog/sql_generation.py:211-230`; `generate_secret_sql()` repeats type rendering at `src/duckalog/sql_generation.py:264-276` that also exists in `src/duckalog/sql_utils.py:73-88`. Rationale: duplicate rendering paths can diverge in quoting/type support.
- Medium: `DefaultEnvProcessor` is a dead exported abstraction. It is defined at `src/duckalog/config/resolution/env.py:311-349` and exported at `src/duckalog/config/resolution/env.py:352-361`, but a repository grep for `DefaultEnvProcessor(` matches only the class definition. The actual import loader directly calls `_load_dotenv_files_for_config()` at `src/duckalog/config/resolution/imports.py:613` and `_interpolate_env()` at `src/duckalog/config/resolution/imports.py:479` and `src/duckalog/config/resolution/imports.py:651`. Rationale: the protocol/implementation exists in production code but is not used by production execution paths.
- Low: `BenchmarkResult` and `RegressionDetector` are production classes used only by their test file. They are defined at `src/duckalog/performance.py:83-121`; grep matches outside that file only `tests/test_performance_regression.py:1-35` and an execplan note. Rationale: they are not exported from `src/duckalog/__init__.py` and do not affect runtime catalog loading, so this is an isolated test-only abstraction rather than an active runtime bug.
- Note: `ARCHITECTURE.md:164-167` is stale for `config.loading.base`, `config.loading.file`, and `config.loading.remote`; those files are absent from `src/duckalog/config/loading/`. The architecture document still correctly identifies broader shallow/duplicate areas such as `duckalog.config.validators`, `duckalog.cli`, and `duckalog.sql_generation.generate_secret_sql`.
- Note: Repository status before writing this report showed `M uv.lock`; final status after writing the report showed untracked review reports including `tests_deadcode_review.md` and no staged files. I did not inspect or modify `uv.lock`.

## Commands run

- `git status --short` — showed pre-existing `M uv.lock` before report generation.
- `wc -l tests/*.py src/duckalog/**/*.py src/duckalog/*.py | sort -n` — counted test/source file sizes.
- Python AST inventory over `tests/` — read all test files and counted tests, fixtures, assertion-less top-level test functions.
- Python AST inventory over `src/duckalog` and `tests/` — listed definitions and possible unreferenced symbols.
- `uv run ruff check src tests` — passed with exit 0 (`[]`).
- `uv run pytest tests/test_cli_filesystem.py::TestCLIFileSystem::test_cli_help_text_includes_filesystem_options -q` — failed as evidence for the stale CLI subprocess test.
- Python exact-block duplication detector over `src/duckalog` — found the cited CLI and SQL-generation duplicate blocks.
- Python exact-block duplication detector over `tests` — found the cited repeated YAML/helper blocks.
- `git diff --cached --quiet; echo EXIT:$?` — returned `EXIT:0`, confirming no staged files.
- Final `git status --short` — showed `M uv.lock` plus untracked review reports including `tests_deadcode_review.md`.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Reviewed tests/dead-code/duplication only; no production or test fixes were made. Findings are written to /Users/volker/coding/libs/duckalog/tests_deadcode_review.md with file:line evidence."
    }
  ],
  "changedFiles": [
    "tests_deadcode_review.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "git status --short",
      "result": "passed",
      "summary": "Showed pre-existing modified uv.lock before report generation."
    },
    {
      "command": "wc -l tests/*.py src/duckalog/**/*.py src/duckalog/*.py | sort -n",
      "result": "passed",
      "summary": "Counted test/source line sizes for scope assessment."
    },
    {
      "command": "python AST inventory over tests/",
      "result": "passed",
      "summary": "Read all test files and counted tests, fixtures, and assertion patterns."
    },
    {
      "command": "uv run ruff check src tests",
      "result": "passed",
      "summary": "No Ruff lint/unused-import findings; output was []."
    },
    {
      "command": "uv run pytest tests/test_cli_filesystem.py::TestCLIFileSystem::test_cli_help_text_includes_filesystem_options -q",
      "result": "failed",
      "summary": "Confirmed stale CLI subprocess test fails with empty stdout."
    },
    {
      "command": "python duplicate block detectors over src/duckalog and tests",
      "result": "passed",
      "summary": "Found cited exact duplicate blocks."
    },
    {
      "command": "git diff --cached --quiet; echo EXIT:$?",
      "result": "passed",
      "summary": "Returned EXIT:0, confirming no staged files."
    },
    {
      "command": "git status --short",
      "result": "passed",
      "summary": "Final status showed M uv.lock plus untracked review report files including tests_deadcode_review.md."
    }
  ],
  "validationOutput": [
    "ruff: [] with exit 0",
    "pytest targeted failure: AssertionError because '--fs-protocol' not in empty stdout"
  ],
  "residualRisks": [
    "Full test suite was not run; this was a static/cross-cutting review plus one targeted failing test for evidence.",
    "uv.lock was already modified before this report was written and was left untouched."
  ],
  "noStagedFiles": true,
  "diffSummary": "Added review report only; no source or test files were changed.",
  "reviewFindings": [
    "blocker: tests/test_cli_filesystem.py:249 - stale python -m duckalog.cli build invocation does not exercise current CLI and targeted test fails",
    "blocker: tests/test_dashboard.py:747-954 - multiple UI CLI tests swallow SystemExit and broad Exception, allowing false positives",
    "medium: tests/test_config.py:1337-1595 - repeated integration-style YAML/load_config validation cases create test bloat",
    "medium: src/duckalog/config/resolution/env.py:311 - DefaultEnvProcessor is exported but not used by production paths"
  ],
  "manualNotes": "plan.md and progress.md were requested but not present. Report writing is the only file write performed for the required output path."
}
```
