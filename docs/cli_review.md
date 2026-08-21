## Review

### Scope and context checked

- Read `ARCHITECTURE.md` CLI guidance: it already classifies `duckalog.cli` as "shallow and wide" and calls out direct orchestration of filesystem creation, SQL generation, building, interactive mode, and display formatting (`ARCHITECTURE.md:84-89`, `ARCHITECTURE.md:238-242`).
- Attempted to read the requested `/Users/volker/coding/libs/duckalog/plan.md` and `/Users/volker/coding/libs/duckalog/progress.md`; both paths are absent in this checkout.
- Reviewed `src/duckalog/cli.py`, `src/duckalog/cli_filesystem.py`, `src/duckalog/cli_imports.py`, `src/duckalog/cli_display.py`, related CLI tests, and command behavior.

### Correct

- The CLI has already started separating concerns: filesystem construction lives in `src/duckalog/cli_filesystem.py`, import graph display in `src/duckalog/cli_imports.py`, and table/interactive display in `src/duckalog/cli_display.py` (`src/duckalog/cli.py:16-18`).
- The installed console entry point works through Typer: `pyproject.toml:86-87` points `duckalog` at `duckalog.cli:app`, and `uv run duckalog --help` showed the expected commands.
- There is targeted coverage for several CLI areas: selected CLI tests produced 31 passing tests before 8 failures exposed below.

### Fixed

- None. Review-only task; no source or test files were intentionally changed.

### Findings

| Severity | Finding | Evidence | Rationale |
|---|---|---|---|
| High | `show-imports` can report success while hiding broken imports. | `_collect_import_graph()` catches any config-load failure and records an empty child list (`src/duckalog/cli_imports.py:58-71`), and also silently skips any per-import resolution/load error (`src/duckalog/cli_imports.py:77-96`). `show_imports()` then prints the graph as success (`src/duckalog/cli.py:569-590`). A local config importing `missing.yaml` exited 0 and printed only the root file. | This makes an inspection/diagnostic command unreliable: invalid import graphs are presented as valid, and callers cannot distinguish "no imports" from "imports failed to load." |
| High | Filesystem options are global callback options, but CLI examples and tests place them after subcommands. | Options are defined on `@app.callback()` (`src/duckalog/cli.py:49-136`), not on individual commands. `run` documents an after-subcommand example (`src/duckalog/cli.py:210-211`). `uv run duckalog validate nonexistent.yaml --fs-protocol github --fs-token test` fails with `No such option: --fs-protocol`; `uv run duckalog validate --help` does not list filesystem options. | This is a user-facing interface mismatch and a maintenance trap: command bodies retrieve `ctx.obj["filesystem"]` (`src/duckalog/cli.py:226`, `src/duckalog/cli.py:335`, `src/duckalog/cli.py:393`, `src/duckalog/cli.py:559`), but users following command-level help/examples cannot supply it there. |
| High | The filesystem factory has concrete behavioral inconsistencies beyond being long. | `_create_filesystem_from_options()` is one 214-line, 12-argument function (`src/duckalog/cli_filesystem.py:21-234`). Anonymous S3 is accepted by validation (`src/duckalog/cli_filesystem.py:104-110`) but omitted from `filesystem_options` when no key/secret/profile is present (`src/duckalog/cli_filesystem.py:166-181`); the selected test failed because actual call was `filesystem('s3', timeout=30)` rather than including `anon=True`. The callback default is `None` (`src/duckalog/cli.py:77-79`) and always passes that value (`src/duckalog/cli.py:120-127`), bypassing the helper's `timeout=30` default (`src/duckalog/cli_filesystem.py:21-33`, `src/duckalog/cli_filesystem.py:161-163`). | The factory is not only a simplification candidate; its option-normalization paths already diverge from help text and tests. The ambiguous inference branches also duplicate `key and secret` for S3 before Azure (`src/duckalog/cli_filesystem.py:84-92`), making part of the Azure inference condition unreachable without an Azure-specific option. |
| Medium | Several CLI commands remain god functions that mix parsing, validation, domain work, I/O, display, and error mapping. | Function sizes from AST inspection: `run` is 157 lines (`src/duckalog/cli.py:152-308`), `show_imports` 110 lines (`src/duckalog/cli.py:503-612`), `query` 107 lines (`src/duckalog/cli.py:691-797`), `init` 119 lines (`src/duckalog/cli.py:801-919`). `run` alone validates paths, logs, dry-runs via engine, manages `connect_to_catalog`, executes optional SQL, formats output, and maps exceptions (`src/duckalog/cli.py:223-308`). | This matches the architecture concern (`ARCHITECTURE.md:84-89`) and makes behavior changes cut across command parsing, execution, and presentation in the same blocks. |
| Medium | Local-config existence validation and error mapping are repeated with small variations. | Near-identical local/remote config checks occur in `run` (`src/duckalog/cli.py:228-241`), `generate_sql` (`src/duckalog/cli.py:337-350`), `validate` (`src/duckalog/cli.py:395-408`), and a different variant in `show_imports` (`src/duckalog/cli.py:561-565`). Repeated `ConfigError` handling appears at `src/duckalog/cli.py:298-300`, `src/duckalog/cli.py:361-363`, `src/duckalog/cli.py:417-419`, `src/duckalog/cli.py:451-453`, `src/duckalog/cli.py:605-607`, `src/duckalog/cli.py:670-671`. | The duplicates already differ in behavior: some import `remote_config.is_remote_uri`, one imports the private `_is_remote_uri`, and `show_paths` only accepts local `Path` with Typer `exists=True` (`src/duckalog/cli.py:425-428`). |
| Medium | Query-result rendering is duplicated across normal run, ad-hoc query, and interactive shell paths. | `run --query` executes SQL and formats/no-row messages (`src/duckalog/cli.py:281-291`); `query` repeats execution/fetch/format/no-row handling (`src/duckalog/cli.py:756-779`); `_interactive_loop()` repeats similar rendering (`src/duckalog/cli_display.py:107-117`). | Repeated display semantics increase the chance that no-row output, column-header handling, and SQL error behavior drift between CLI surfaces. |
| Medium | `query` advertises remote catalogs but only supports local filesystem checks. | The docstring example says remote catalog usage is possible if filesystem options are configured (`src/duckalog/cli.py:719-720`), but the command has no `ctx` parameter and never reads `ctx.obj`; it validates `catalog` with `Path(catalog).exists()` (`src/duckalog/cli.py:691-705`, `src/duckalog/cli.py:744-748`) and opens it with `duckdb.connect(str(catalog), read_only=True)` (`src/duckalog/cli.py:756-758`). | This is a mixed-concern/doc drift issue: global filesystem creation exists, but this command cannot consume it, so the advertised remote path flow is not implemented in this layer. |
| Low | Dead/unused code and stale references remain in the CLI layer. | `main_entry()` is exported (`src/duckalog/cli.py:922-928`) but local grep found no references, while the package script points to `app` (`pyproject.toml:86-87`). `python -m duckalog.cli ...` returned 0 with no output because the module never invokes `app()` at import-as-main time. `_print_import_tree()` accepts `original_root_path` but never uses it (`src/duckalog/cli_imports.py:197-203`). `_traverse_imports()` accepts `base_path` but never uses it (`src/duckalog/cli_imports.py:42-43`, `src/duckalog/cli_imports.py:93`). `run` still says "prefer run over build" although no `build` command exists in `app` (`src/duckalog/cli.py:194-195`). | These are small but concrete signs of architecture drift after prior CLI changes/removals. |
| Low | `cli_imports` duplicates work and reaches into private config resolver helpers. | `_collect_import_graph()` imports `_is_remote_uri`, `_normalize_uri`, and `_resolve_import_path` from `config.resolution.imports` (`src/duckalog/cli_imports.py:31-35`). Its remote and local branches call `load_config()` identically (`src/duckalog/cli_imports.py:59-67`). | The helper is tightly coupled to private config internals and contains redundant control flow, which makes the diagnostic command sensitive to non-public resolver changes. |

### Note

- Selected CLI test run failed 8 tests. Failures included the S3 anonymous option mismatch, contradictory no-options expectations in `tests/test_cli_filesystem.py`, and subprocess tests using `python -m duckalog.cli`, which currently no-ops. These failures are evidence for the findings above, not changes made by this review.
- `uv run` attempted to update `uv.lock`; that unintended lockfile diff was reverted before writing this report.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Performed review-only inspection of requested CLI files and ARCHITECTURE.md; wrote findings report only, with no source/test changes."
    }
  ],
  "changedFiles": [
    "cli_review.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "read plan.md, progress.md, openspec/AGENTS.md, ARCHITECTURE.md",
      "result": "mixed",
      "summary": "OpenSpec and ARCHITECTURE read; requested root plan.md and progress.md were absent."
    },
    {
      "command": "nl -ba src/duckalog/cli.py src/duckalog/cli_filesystem.py src/duckalog/cli_imports.py src/duckalog/cli_display.py",
      "result": "passed",
      "summary": "Collected line-numbered evidence for reviewed files."
    },
    {
      "command": "python AST function-size inspection",
      "result": "passed",
      "summary": "Measured CLI function sizes: run 157 lines, show_imports 110, query 107, init 119, filesystem factory 214."
    },
    {
      "command": "uv run pytest tests/test_cli_filesystem.py tests/test_engine_cli.py::test_cli_show_imports_simple_config tests/test_engine_cli.py::test_cli_show_imports_with_nested_imports tests/test_engine_cli.py::test_cli_show_imports_json_format tests/test_engine_cli.py::test_cli_show_imports_nonexistent_file tests/test_cli_query.py -q",
      "result": "failed",
      "summary": "31 passed, 8 failed; failures exposed filesystem factory mismatches and python -m CLI no-op behavior."
    },
    {
      "command": "uv run duckalog validate nonexistent.yaml --fs-protocol github --fs-token test; uv run duckalog --fs-protocol github --fs-token test validate nonexistent.yaml",
      "result": "failed-as-evidence",
      "summary": "After-subcommand filesystem options are rejected; before-subcommand GitHub filesystem creation fails before config validation."
    },
    {
      "command": "uv run duckalog show-imports <config importing missing.yaml>",
      "result": "failed-as-evidence",
      "summary": "Command exited 0 and hid the missing import, confirming show-imports diagnostic issue."
    }
  ],
  "validationOutput": [
    "Selected pytest: 31 passed, 8 failed.",
    "show-imports missing import repro: exit 0 with only root file shown.",
    "git diff --cached --stat: no staged changes."
  ],
  "residualRisks": [
    "Review did not run the full test suite.",
    "Requested plan.md and progress.md were absent at the exact provided paths."
  ],
  "noStagedFiles": true,
  "diffSummary": "Created cli_review.md report only; no source or test files changed.",
  "reviewFindings": [
    "high: src/duckalog/cli_imports.py:58-96 - show-imports suppresses config/import errors and can report success for broken import graphs.",
    "high: src/duckalog/cli.py:49-136 - filesystem options are global while examples/tests use subcommand placement.",
    "high: src/duckalog/cli_filesystem.py:21-234 - overlarge filesystem factory has observed anon/timeout/inference inconsistencies.",
    "medium: src/duckalog/cli.py:152-919 - multiple command handlers remain large mixed-concern orchestration functions.",
    "medium: src/duckalog/cli.py:228-408 - repeated local/remote config validation and ConfigError mapping.",
    "medium: src/duckalog/cli.py:281-291, src/duckalog/cli.py:756-779, src/duckalog/cli_display.py:107-117 - duplicate query result rendering.",
    "low: src/duckalog/cli.py:922-928 and src/duckalog/cli_imports.py:42-43,197-203 - unused/dead CLI-layer surfaces remain."
  ],
  "manualNotes": "Report intentionally contains no fix proposal or source edits, per task instruction."
}
```
