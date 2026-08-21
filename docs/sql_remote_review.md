## Review

### Correct

- **SQL view identifier quoting is consistently applied**: `src/duckalog/sql_generation.py:33-37` quotes view/schema names and `src/duckalog/sql_generation.py:72-74` quotes attached database/table identifiers; canonical quoting lives in `src/duckalog/sql_utils.py:12-52`.
- **The old duplicated `_is_remote_uri` helper is mostly consolidated in code**: only `src/duckalog/remote_config.py:70-83` defines `is_remote_uri`; config/import/sql callers import it as an alias (`src/duckalog/config/resolution/imports.py:26`, `src/duckalog/config/resolution/env.py:20`, `src/duckalog/config/loading/sql.py:44`). `ARCHITECTURE.md:224` is stale when it says four helper copies still exist.
- **`_render_view_body` is not currently a giant switch**: `src/duckalog/sql_generation.py:47-76` has a small source dispatch. The larger provider complexity is in secret/remote handling, not view SQL generation.

### Findings

#### Blocker / Critical — public remote config loading is currently broken

- **Evidence**: `src/duckalog/config/api.py:33-41` calls `load_config_from_uri(..., context=context)`, but `src/duckalog/remote_config.py:286-294` has no `context` parameter.
- **Observed result**: `uv run python` with a mocked remote fetch returned `TypeError load_config_from_uri() got an unexpected keyword argument 'context'` for `load_config('s3://bucket/config.yaml')`.
- **Rationale**: `load_config()` is the documented public entry point for remote configs (`README.md:332-359`), so this breaks CLI/API paths that delegate through `load_config()`.

#### Blocker / Critical — secret names are emitted unquoted and can inject additional SQL

- **Evidence**: `src/duckalog/sql_generation.py:242` uses `secret.name or secret.type` directly, and `src/duckalog/sql_generation.py:277` interpolates it into `CREATE SECRET` without `quote_ident`. The model only strips empties at `src/duckalog/config/models.py:85-92`; it does not constrain SQL metacharacters. Engine execution uses the generated string at `src/duckalog/engine.py:739-742`.
- **Observed result**: generating a secret named `evil (TYPE S3); DROP TABLE victims; --` produced `CREATE SECRET evil (TYPE S3); DROP TABLE victims; -- (TYPE S3, KEY_ID 'key', SECRET 'secret')`; executing it in DuckDB dropped the `victims` table.
- **Rationale**: This is a SQL injection path from configuration into executed DuckDB SQL.

#### Blocker / High — `scope` secrets generate invalid DuckDB SQL

- **Evidence**: `src/duckalog/sql_generation.py:277-280` appends `; SCOPE '...'` after the `CREATE SECRET` statement. The test expectation locks in that shape at `tests/test_sql_generation.py:253-267`.
- **Observed result**: DuckDB rejects `CREATE SECRET scoped_s3 (...); SCOPE 'prod/'` with `ParserException: syntax error at or near "SCOPE"`; `SCOPE` is not a separate post-semicolon statement.
- **Rationale**: Any configured secret with `scope` cannot be created successfully.

#### High — direct remote config loading does not resolve `imports`

- **Evidence**: `src/duckalog/remote_config.py:409-420` interpolates and validates the fetched mapping directly with `Config.model_validate`; it does not run the import-resolution path used by local configs (`src/duckalog/config/resolution/imports.py:517-540`, `src/duckalog/config/resolution/imports.py:661-680`). Remote import support is documented in `docs/examples/config-imports.md:360-390`.
- **Observed result**: `load_config_from_uri('s3://bucket/main.yaml')` on content with `imports: [s3://bucket/base.yaml]` fetched only `main.yaml` and returned only `main_view`.
- **Rationale**: Remote root configs and local configs do not have equivalent import semantics.

#### Medium — `load_dotenv` is accepted by remote loading but not honored

- **Evidence**: `src/duckalog/remote_config.py:293` exposes `load_dotenv`, but the implementation goes straight to `_interpolate_env` at `src/duckalog/remote_config.py:411-415`. Local loading performs `.env` discovery at `src/duckalog/config/resolution/imports.py:607-615`.
- **Observed result**: direct `load_config_from_uri(..., load_dotenv=True)` with `.env` in CWD failed with `ConfigError Environment variable 'REMOTE_VAR' is not set`.
- **Rationale**: The remote API advertises a parameter that currently has no behavioral effect.

#### Medium — documented GitHub remote configs are not recognized by remote detection

- **Evidence**: `README.md:396-398` and `docs/reference/cli.md:779-780` show `github://...` remote configs, but `SCHEME_REQUIREMENTS` in `src/duckalog/remote_config.py:41-52` has no `github` entry, and `is_remote_uri` only checks that table at `src/duckalog/remote_config.py:82-83`.
- **Observed result**: `is_remote_uri('github://user/repo/config.yaml')` returned `False`.
- **Rationale**: The provider matrix and documentation are out of sync.

#### Medium — filesystem validation suppresses its own protocol failure

- **Evidence**: `src/duckalog/remote_config.py:105-116` raises `RemoteConfigError` for a missing/empty `protocol`, then catches all `Exception` and passes.
- **Observed result**: a filesystem object with `open()` and `protocol=''` was accepted by `validate_filesystem()`.
- **Rationale**: The validation branch reads as protective but does not enforce the condition it detects.

#### Low — dead/placeholder provider branches remain in fsspec fetching

- **Evidence**: `src/duckalog/remote_config.py:254-271` parses the scheme and enters S3/GCS/Azure/SFTP branches that all contain only comments plus `pass`.
- **Rationale**: This is dead scaffolding that adds provider-handling surface without behavior.

#### Low — duplicated SQL option rendering logic

- **Evidence**: `src/duckalog/sql_utils.py:76-89` renders typed option values for scan calls; `src/duckalog/sql_generation.py:262-275` repeats the same bool/number/string/type-error logic for secret options with only casing/separator differences.
- **Rationale**: The duplicated type matrix can drift across generated SQL surfaces.

#### Low — duplicated database secret builders

- **Evidence**: `_build_postgres_params` (`src/duckalog/sql_generation.py:189-208`) and `_build_mysql_params` (`src/duckalog/sql_generation.py:211-230`) are structurally identical.
- **Rationale**: Provider handling is simpler than a giant switch now, but these duplicate builders still increase maintenance cost.

### Commands run

- `read` on requested files: `src/duckalog/sql_generation.py`, `src/duckalog/sql_utils.py`, `src/duckalog/sql_file_loader.py`, `src/duckalog/remote_config.py`, `ARCHITECTURE.md`, plus OpenSpec instructions.
- `read /Users/volker/coding/libs/duckalog/plan.md` and `read /Users/volker/coding/libs/duckalog/progress.md` both returned `ENOENT`.
- `grep` for remote URI helper definitions/imports across `src/duckalog`.
- `uv run pytest -q tests/test_config.py::test_load_config_delegates_to_remote_helper_for_remote_uris tests/test_remote_config.py::TestIntegrationWithLocalConfig::test_remote_config_delegation tests/test_remote_config.py::TestFilesystemParameter::test_filesystem_parameter_passed_to_load_config_from_uri` — 1 passed, 2 failed due changed mock call shape including `context=None`/`load_dotenv=True`.
- Targeted `uv run python` probes for remote `load_config()`, secret SQL execution, GitHub URI detection, `.env` behavior, filesystem validation, and remote import behavior.
- `git status --short`, `git diff --name-only`, and `git diff --cached --name-only`; no staged files were present. `uv.lock` was already modified before this report and was not touched.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Completed review-only task and wrote findings to sql_remote_review.md without editing source files."
    }
  ],
  "changedFiles": [
    "sql_remote_review.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "read requested source/docs plus plan.md/progress.md",
      "result": "passed",
      "summary": "Reviewed target files; plan.md and progress.md were absent (ENOENT)."
    },
    {
      "command": "grep remote URI helpers across src/duckalog",
      "result": "passed",
      "summary": "Confirmed a single canonical is_remote_uri definition plus import aliases."
    },
    {
      "command": "uv run pytest -q tests/test_config.py::test_load_config_delegates_to_remote_helper_for_remote_uris tests/test_remote_config.py::TestIntegrationWithLocalConfig::test_remote_config_delegation tests/test_remote_config.py::TestFilesystemParameter::test_filesystem_parameter_passed_to_load_config_from_uri",
      "result": "failed",
      "summary": "1 passed, 2 failed due mock expectations not including context/load_dotenv kwargs."
    },
    {
      "command": "uv run python targeted probes for remote loading, secret SQL, GitHub URI, dotenv, filesystem validation, remote imports",
      "result": "passed",
      "summary": "Produced evidence for the reported findings."
    },
    {
      "command": "git status --short && git diff --name-only && git diff --cached --name-only",
      "result": "passed",
      "summary": "No staged files; uv.lock was pre-existing unstaged change."
    }
  ],
  "validationOutput": [
    "load_config('s3://bucket/config.yaml') -> TypeError unexpected keyword argument 'context'",
    "DuckDB executed generated malicious secret SQL and victims table was dropped",
    "Scoped secret SQL with post-semicolon SCOPE raised DuckDB ParserException",
    "is_remote_uri('github://user/repo/config.yaml') -> False",
    "validate_filesystem accepted empty protocol",
    "remote root import probe fetched only main config and returned only main_view"
  ],
  "residualRisks": [
    "Review only; no source fixes applied.",
    "Existing unstaged uv.lock change was not inspected as part of source review."
  ],
  "noStagedFiles": true,
  "diffSummary": "Created review report only; no source files edited.",
  "reviewFindings": [
    "blocker: src/duckalog/config/api.py:33-41 and src/duckalog/remote_config.py:286-294 - remote load_config passes unsupported context kwarg",
    "blocker: src/duckalog/sql_generation.py:242,277 - unquoted secret name permits SQL injection",
    "blocker: src/duckalog/sql_generation.py:277-280 - scoped secrets generate invalid SQL",
    "high: src/duckalog/remote_config.py:409-420 - direct remote loader does not expand imports",
    "medium: src/duckalog/remote_config.py:293,411-415 - load_dotenv parameter unused",
    "medium: src/duckalog/remote_config.py:41-52 - documented github:// scheme not recognized",
    "medium: src/duckalog/remote_config.py:105-116 - filesystem protocol validation is swallowed",
    "low: src/duckalog/remote_config.py:254-271 - empty provider branches",
    "low: src/duckalog/sql_utils.py:76-89 and src/duckalog/sql_generation.py:262-275 - duplicated option rendering",
    "low: src/duckalog/sql_generation.py:189-230 - duplicated postgres/mysql builders"
  ],
  "manualNotes": "Report written to /Users/volker/coding/libs/duckalog/sql_remote_review.md as requested."
}
```
