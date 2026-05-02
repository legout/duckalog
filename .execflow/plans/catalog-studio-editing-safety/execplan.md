# Add the Catalog Studio editing safety foundation

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document must be maintained in accordance with `.execflow/PLANS.md` from the repository root. It builds on the completed umbrella brainstorm at `.execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md`, the prerequisite foundation plan at `.execflow/plans/starhtml-catalog-studio-foundation/execplan.md`, the prerequisite explorer plan at `.execflow/plans/catalog-studio-explorer/execplan.md`, and the prerequisite query workbench plan at `.execflow/plans/catalog-studio-query-workbench/execplan.md`. If those plans have not been implemented yet, implement them first. This plan creates the safe write model for later structured form editing and expert YAML/JSON editing; it does not add those full editors yet.

## Purpose / Big Picture

After this change, Duckalog Catalog Studio has a backend safety layer for editing local catalog configuration files. A user-facing editor is not complete yet, but the Studio code can load the raw config text, parse proposed YAML or JSON text, validate it with Duckalog’s existing `Config` model, preview a diff, create a backup, write changes atomically, and reload the saved file to prove it is still valid. Remote configs are treated as read-only and local file writes are blocked unless they pass explicit path and format checks.

This matters because catalog editing is the first feature that can damage user files. The earlier Studio plans are read-only. This plan creates a deep, testable safety boundary before any form editor or expert editor is allowed to save changes. Later UI plans should call this service instead of implementing their own ad hoc parsing, validation, backup, and write logic.

## Progress

- [x] (2026-04-30) Completed the umbrella brainstorm and selected form/menu editing plus expert YAML/JSON editing as part of the Catalog Studio vision.
- [x] (2026-04-30) Created the prerequisite foundation, explorer, and query workbench ExecPlans.
- [x] (2026-04-30) Read existing config loading, import resolution, config initialization, path-security, and query/explorer planning context.
- [x] (2026-04-30) Ran a scout pass for editing safety and saved its output in `code_context.md`.
- [ ] Confirm the Studio foundation and read-only product slices are implemented before adding write-safety endpoints.
- [ ] Add a local-only config editing service that can read raw config text without resolving imports or inlining SQL files.
- [ ] Add proposed-text parsing and validation using Duckalog’s existing `Config` model with `load_sql_files=False` semantics where needed.
- [ ] Add diff preview generation for original text versus proposed text and for original validated structure versus proposed validated structure.
- [ ] Add backup creation and atomic save helpers with reload verification.
- [ ] Add minimal Studio endpoints for validate, preview, and save that expose the safety service without building a full editor UI.
- [ ] Add tests for raw load, validation errors, remote read-only behavior, path safety, backup creation, atomic save, reload verification, and no old dashboard regression.
- [ ] Run focused tests and update this plan with results.

## Surprises & Discoveries

- Observation: Duckalog’s config system is currently a read-only pipeline.
  Evidence: `src/duckalog/config/api.py:load_config()` delegates to local or remote loaders and returns a validated `Config`. No save or write-back API exists in `src/duckalog/config/`.

- Observation: Existing YAML loading is not format-preserving.
  Evidence: `src/duckalog/config/resolution/imports.py` parses YAML with `yaml.safe_load(raw_text)`. `src/duckalog/config_init.py:_format_as_yaml()` uses `yaml.dump()`. This destroys comments and may normalize formatting.

- Observation: SQL file references are inlined during normal loading.
  Evidence: `src/duckalog/config/loading/sql.py:process_sql_file_references()` and `load_sql_files_from_config()` replace `sql_file` or `sql_template` fields with inline `sql` content using `model_copy(update={"sql": sql_content, "sql_file": None})`. An editor that serializes a loaded `Config` would lose original SQL file references.

- Observation: Existing write patterns are unsafe for config editing.
  Evidence: `src/duckalog/config_init.py:_write_config_file()` uses `Path.write_text(content, encoding="utf-8")`. `src/duckalog/cli.py` also writes generated SQL directly with `out_path.write_text(sql)`. There is no existing atomic config save or backup helper.

- Observation: Documentation already promises atomic, format-preserving config updates in some places, but the current code does not implement that capability.
  Evidence: `README.md` and dashboard docs mention atomic config updates, while the scout found no matching write-back implementation. This plan should build the missing safety foundation rather than relying on documentation claims.

## Decision Log

- Decision: Create an editing safety foundation before creating any visible form editor or expert editor.
  Rationale: The first write-capable feature must centralize validation, diffing, backups, atomic writes, and reload verification. Without this boundary, future UI code would spread file-safety policy across route handlers and components.
  Date/Author: 2026-04-30 / planning session

- Decision: Support local config files only in the first editing-safety implementation.
  Rationale: Remote configs involve S3/GCS/ABFS/HTTP write semantics, authentication, and no universal atomic replace operation. Treating remote configs as read-only is simpler and safer for the first write foundation.
  Date/Author: 2026-04-30 / planning session

- Decision: Preserve raw user text for editing and saving rather than serializing the loaded `Config` model back to YAML.
  Rationale: Normal loading resolves imports, interpolates environment variables, resolves paths, and inlines SQL file references. Serializing the loaded model would lose comments, formatting, import shape, env references, and SQL file references. The safety layer should validate proposed raw text, then save that proposed raw text if approved.
  Date/Author: 2026-04-30 / planning session

- Decision: Use the existing `Config` validation model as the authoritative structure gate.
  Rationale: `Config.model_validate()` and `load_config()` already encode Duckalog’s schema and cross-field validation. The editor safety layer should not invent a parallel schema.
  Date/Author: 2026-04-30 / planning session

- Decision: Do not promise full comment-preserving structured rewrites in this plan.
  Rationale: Preserving comments while programmatically editing YAML requires a round-trip YAML library such as `ruamel.yaml` and a separate design decision. This plan saves raw proposed text, which preserves comments if the user or later expert editor keeps them, but it does not implement comment-aware transformations.
  Date/Author: 2026-04-30 / planning session

## Outcomes & Retrospective

No implementation outcomes have been produced yet. At completion, update this section with the exact service module, endpoint names, backup naming scheme, test commands, validation results, and any decision about YAML round-trip libraries. The expected next plan after this one is Structured Catalog Form Editor, unless implementation reveals that Expert YAML/JSON Editor should come first to exercise the safety layer with less schema-specific UI.

## Context and Orientation

Duckalog loads configuration files through `src/duckalog/config/api.py:load_config()`. A configuration file may be YAML or JSON. Loading is not just parsing text: Duckalog can resolve imports, interpolate environment variables, validate paths, load SQL files, and return a Pydantic `Config` object from `src/duckalog/config/models.py`. Pydantic is a validation library; it turns Python dictionaries into typed models and raises detailed validation errors when data is invalid.

Catalog Studio editing must distinguish two forms of config data. The first is raw text: exactly what is stored in the user’s local `.yaml`, `.yml`, or `.json` file. Raw text may include comments, `${env:VAR}` references, imports, SQL file references, and user formatting. The second is the validated model: the `Config` object produced after Duckalog loads and normalizes the file. The editor must save raw text, not a dumped version of the normalized model, because the normalized model may have lost important authoring information.

The current normal load path is `load_config(path)` to `_load_config_from_local_file()` to `_load_config_with_imports()`. Local YAML is parsed with `yaml.safe_load()`. JSON is parsed with `json.loads()`. SQL file references are later loaded and replaced with inline SQL by `src/duckalog/config/loading/sql.py`. This is correct for building catalogs, but dangerous as a basis for editing because it can turn `sql_file:` into `sql:` and remove the original external file reference.

The existing path-security helpers live in `src/duckalog/config/security/path.py`. They are read-oriented, but this plan should reuse the same concept: a local config file is safe to edit only if the target path is a normal local file inside an allowed root. The default allowed root should be the directory containing the loaded config file. Remote URIs such as `s3://...`, `gs://...`, `abfs://...`, `https://...`, and `http://...` should be read-only in this plan.

The new Catalog Studio code lives in `src/duckalog/studio/`, created by the foundation plan. This editing safety plan should add a service module under that package, such as `src/duckalog/studio/editing.py` or `src/duckalog/studio/config_editing.py`. The service should be independent of StarHTML components so it can be tested directly. Minimal Studio endpoints may be added to exercise the service, but full form fields and full YAML/JSON editor UI are deliberately deferred.

## Plan of Work

Begin by verifying that the previous Studio plans have been implemented. `from duckalog.studio import create_app, StudioContext` must succeed, and the Studio tests for foundation, explorer, and query workbench should pass. If they do not, stop and implement those earlier plans first.

Create a new module `src/duckalog/studio/editing.py`. Define a small set of plain Python dataclasses to describe editing operations. Use names such as `ConfigDraft`, `ValidationResult`, `DiffPreview`, and `SaveResult` only if they hide useful state; avoid shallow wrappers around strings. At minimum, the service should expose functions or a class that can read raw text from a local config path, detect the format from the file extension, parse proposed text as YAML or JSON, validate it as a Duckalog config, generate a diff preview, create a backup, atomically write the proposed text, and reload the saved file.

Implement local-path safety first. Add a helper such as `ensure_local_editable_config_path(path: str | Path) -> Path`. It should reject remote URIs using the existing remote detection helper from `duckalog.remote_config` if available. It should resolve the path, require that the file exists, require a supported suffix `.yaml`, `.yml`, or `.json`, require that it is a regular file, and ensure it is inside the allowed root. For this first plan the allowed root can be the target file’s parent directory after resolution, but the helper should accept an optional `allowed_roots` parameter so a future Studio command can pass a stricter project root if needed.

Implement raw loading. Add `load_editable_config(path)` or equivalent that returns the raw text, detected format, file path, and current validated config. It should read the text with UTF-8. For validation, prefer using `load_config(path, load_sql_files=False)` or a parsing path that avoids SQL file inlining when the goal is preserving authoring structure. If using `load_config(..., load_sql_files=False)` still resolves imports or environment variables, document that behavior and keep raw text as the thing being saved. The returned object should make it clear whether the file is local and editable.

Implement proposed-text validation. Add `validate_config_text(text, format, base_path)` or equivalent. It should parse YAML with `yaml.safe_load()` and JSON with `json.loads()`, handle empty YAML files as invalid, then call `Config.model_validate(parsed_data)` for structural validation. It should return a result object with `ok`, parsed config if valid, and a list of human-readable error messages if invalid. Do not throw raw Pydantic tracebacks into the UI layer; preserve detailed field locations but present them in a stable structure tests can assert against.

Handle imports and SQL file references explicitly. In this plan, validating a proposed raw file should validate the proposed file as the root config, but saving should only write the root file. It should not rewrite imported files or external SQL files. If the proposed root config contains `imports`, the validation path should still be capable of using Duckalog’s existing import resolver for full validation when the proposed text is written to a temporary file. The implementation may validate in two phases: first parse the raw text with `Config.model_validate()` for syntax and top-level structure, then write it to a temporary sibling file and call `load_config(temp_path, load_sql_files=False)` for import/env/path behavior if needed. If this two-phase behavior is implemented, document it in the service docstring and tests.

Implement diff preview. Provide both a unified text diff and, if simple enough, a structured summary. Use Python’s standard `difflib.unified_diff()` for text diff to avoid a new dependency. The diff should compare original raw text to proposed raw text and label paths clearly, for example `catalog.yaml (current)` and `catalog.yaml (proposed)`. A structured summary can be minimal in this plan: count added, removed, and changed lines, and optionally compare top-level sections if both texts parse. Do not add a third-party diff library unless this plan is revised.

Implement backup creation. Before saving, copy the original file to a timestamped sibling backup such as `catalog.yaml.bak.20260430T153000Z`. Use `shutil.copy2()` so file metadata is preserved where possible. After creating the backup, verify that the backup exists and can be read. If the original file is invalid before save, still back it up before writing a proposed valid file.

Implement atomic save. Write proposed text to a temporary file in the same directory as the target, using a name that includes the process id or a random token. Flush and close the temporary file. Then replace the target with `os.replace(temp_path, target_path)`. Writing in the same directory matters because atomic replace generally only works reliably within the same filesystem. If any step fails, remove the temporary file and leave the original target in place when possible.

Implement reload verification. After atomic replacement, call `load_config(target_path, load_sql_files=False)` or the service’s chosen validation load path. If reload fails, restore the backup with another atomic replace if possible, return a failure result that names the backup path, and leave clear evidence for the user. If reload succeeds, return a save result containing the target path, backup path, parsed config summary, and diff summary.

Add minimal Studio endpoints only after the service is testable. For example, add `GET /config/edit` to show a simple safety page with the raw config text in a `<pre>` or readonly textarea, `POST /config/validate` to validate proposed text and return a StarHTML/Datastar patch with validation results, `POST /config/preview` to return a diff preview, and `POST /config/save` to save proposed text. If this is too much UI for the foundation, expose only validation/preview/save endpoints and keep the visible page minimal. The endpoints should call the service and must not implement parsing or file writes inline.

Add tests. Create `tests/test_studio_editing.py` or extend Studio tests if they are still small. Direct service tests are mandatory and more important than UI route tests. Cover YAML and JSON validation, invalid syntax, invalid schema, remote path rejection, unsupported extension rejection, diff preview, backup creation, atomic save, reload verification, restore-on-reload-failure if implemented, and preservation of raw comments when proposed text includes them. Also test that a config with `sql_file` remains textually a `sql_file` after saving unchanged raw text; this guards against accidental serialization of the loaded model. Add route tests for validate/preview/save only after the service tests pass.

Run focused tests and old dashboard tests. Run `starhtml-check` on any changed Studio files that contain StarHTML components or reactive attributes. The service module itself does not need `starhtml-check` if it contains no StarHTML elements.

## Concrete Steps

Work from the repository root `/Users/volker/coding/libs/duckalog`.

First verify prerequisites:

    uv run python - <<'PY'
    from duckalog.studio import create_app, StudioContext
    print(create_app, StudioContext)
    PY

Then run the current Studio tests from prior plans:

    uv run pytest tests/test_studio.py -q

If query or explorer tests live in split files, include them:

    uv run pytest tests/test_studio.py tests/test_studio_explorer.py tests/test_studio_query.py -q

If these fail because prior plans are not implemented, stop and complete those plans first.

Inspect existing config writing and loading code before editing:

    rg -n "def load_config|safe_load|json.loads|load_sql_files|sql_file|write_text|os.replace|backup" src/duckalog/config src/duckalog/config_init.py src/duckalog/cli.py

Add `src/duckalog/studio/editing.py` and direct tests. A quick manual validation script after the service exists should look like this, adjusted to the actual function names chosen:

    uv run python - <<'PY'
    from pathlib import Path
    from duckalog.studio.editing import load_editable_config, validate_config_text, preview_config_diff

    path = Path('/tmp/duckalog-editing-safety.yaml')
    path.write_text('''# keep this comment
    version: 1
    duckdb:
      database: ":memory:"
    views:
      - name: demo
        sql: "select 1 as id"
    ''')

    draft = load_editable_config(path)
    assert '# keep this comment' in draft.text
    result = validate_config_text(draft.text, draft.format, base_path=path)
    assert result.ok, result.errors
    diff = preview_config_diff(draft.text, draft.text.replace('demo', 'demo_renamed'), path)
    print(diff.text)
    assert 'demo_renamed' in diff.text
    print('editing safety service ok')
    PY

Add backup and save tests before adding UI endpoints. A manual save smoke test should look like this, adjusted to actual API names:

    uv run python - <<'PY'
    from pathlib import Path
    from duckalog.config import load_config
    from duckalog.studio.editing import save_config_text_safely

    path = Path('/tmp/duckalog-editing-save.yaml')
    original = '''# original comment
    version: 1
    duckdb:
      database: ":memory:"
    views:
      - name: demo
        sql: "select 1 as id"
    '''
    proposed = original.replace('demo', 'demo_saved')
    path.write_text(original)
    result = save_config_text_safely(path, proposed)
    print(result)
    assert path.read_text() == proposed
    assert result.backup_path.exists()
    assert '# original comment' in path.read_text()
    loaded = load_config(str(path), load_sql_files=False)
    assert loaded.views[0].name == 'demo_saved'
    print('safe save ok')
    PY

Run focused tests:

    uv run pytest tests/test_studio_editing.py -q

Run all Studio tests:

    uv run pytest tests/test_studio.py tests/test_studio_editing.py -q

If prior plans split tests by feature, include all Studio files:

    uv run pytest tests/test_studio.py tests/test_studio_explorer.py tests/test_studio_query.py tests/test_studio_editing.py -q

Run the existing dashboard tests to prove old UI behavior remains intact:

    uv run pytest tests/test_dashboard.py -q

Run StarHTML checks only on changed Studio UI files. If this plan adds or changes StarHTML components in `app.py` or `components.py`, run:

    starhtml-check src/duckalog/studio/app.py
    starhtml-check src/duckalog/studio/components.py

No `starhtml-check` is needed for `src/duckalog/studio/editing.py` if it is pure Python service code.

## Validation and Acceptance

Acceptance is primarily service behavior, because this plan is the safety foundation rather than the final editor UI. A local YAML config with comments can be loaded as raw text, validated, diffed, backed up, saved atomically, and reloaded. The saved file contains the exact proposed text, not a regenerated YAML dump. A local JSON config receives the same safety treatment. Invalid YAML, invalid JSON, invalid Duckalog schema, unsupported file extensions, and remote URIs return structured errors and do not write files. A backup file is created before every successful save. If reload verification fails, the service either restores the backup or returns a failure result that clearly names the backup and target paths.

Automated tests must prove raw-text preservation, validation, diff preview, backup creation, atomic save behavior, reload verification, remote read-only rejection, unsupported suffix rejection, and SQL-file-reference preservation when saving unchanged raw text. Tests should assert that a config containing a YAML comment still contains that comment after saving proposed text that includes it. Tests should assert that a config containing `sql_file:` is not converted to `sql:` by the save service.

If minimal Studio endpoints are added, route tests must prove that validation and preview do not write to disk, and that save writes only after validation succeeds. The old dashboard tests must still pass.

## Idempotence and Recovery

The service should be safe to call repeatedly. Validation and diff preview must never write files. Save creates a new timestamped backup each time and writes through a temporary file in the same directory as the target. Tests should use `tmp_path` so reruns do not pollute the repository.

If a save fails before `os.replace()`, delete the temporary file and leave the original target untouched. If a save fails after replacement but before reload verification succeeds, restore from the backup if possible. If restore also fails, return a result that names both target and backup and tells the user manual recovery is needed.

If a proposed edit is invalid, do not create a backup and do not write a temp file. If the target path is remote or outside the allowed root, return an error before reading or writing.

If implementation must be backed out, remove `src/duckalog/studio/editing.py`, remove any editing endpoints or components from the Studio app, and remove `tests/test_studio_editing.py`. The foundation, explorer, and query workbench should continue to function.

## Artifacts and Notes

The umbrella brainstorm is:

    .execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md

Prerequisite ExecPlans are:

    .execflow/plans/starhtml-catalog-studio-foundation/execplan.md
    .execflow/plans/catalog-studio-explorer/execplan.md
    .execflow/plans/catalog-studio-query-workbench/execplan.md

The scout context for this plan was written to:

    code_context.md

Relevant existing code references are:

    src/duckalog/config/api.py:load_config
    src/duckalog/config/resolution/imports.py:_load_config_with_imports
    src/duckalog/config/loading/sql.py:load_sql_files_from_config
    src/duckalog/config/loading/sql.py:process_sql_file_references
    src/duckalog/config/models.py:Config
    src/duckalog/config/models.py:ViewConfig
    src/duckalog/config/security/path.py:validate_path_security
    src/duckalog/config_init.py:_write_config_file
    src/duckalog/remote_config.py:is_remote_uri

A safe atomic write pattern for the implementation is:

    write proposed text to a temporary file in the same directory
    flush and close the temporary file
    call os.replace(temp_path, target_path)
    reload and validate target_path
    clean up temporary file on failure

Use `difflib.unified_diff()` for the first diff preview. Avoid third-party dependencies in this plan.

## Interfaces and Dependencies

At the end of this plan, the Studio editing service should provide a stable local API equivalent to these operations, even if exact class names differ:

    load_editable_config(path) -> draft with path, format, text, and validated config summary
    validate_config_text(text, format, base_path) -> validation result
    preview_config_diff(original_text, proposed_text, path) -> diff preview
    save_config_text_safely(path, proposed_text) -> save result with backup path and reload status

The service should depend on existing project dependencies only: `pyyaml`, `pydantic`, standard-library `json`, `difflib`, `tempfile`, `shutil`, `os`, `datetime`, and `pathlib`. Do not add a round-trip YAML dependency in this plan. If comment-aware structured rewrites become necessary, create a later plan that evaluates `ruamel.yaml` or another round-trip parser explicitly.

If minimal routes are added, the Studio app may expose these endpoints:

    GET /config/edit
    POST /config/validate
    POST /config/preview
    POST /config/save

These routes are intentionally safety endpoints, not the final structured form editor or expert editor. They must call the editing service and must not contain file-write logic inline.

The next ExecPlan should be Structured Catalog Form Editor or Expert YAML/JSON Editor. Structured Form Editor should use this safety service to validate and save generated proposed text. Expert YAML/JSON Editor should use this safety service to validate, preview, and save raw user-edited text.

## Revision Note

2026-04-30: Initial Catalog Studio Editing Safety ExecPlan created. It establishes local-only raw-text validation, diff preview, backup, atomic save, and reload verification before any visible config editing UI is implemented.
