# Add the Catalog Studio Expert YAML/JSON Editor

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document must be maintained in accordance with `.execflow/PLANS.md` from the repository root. It builds on the completed umbrella brainstorm at `.execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md` and on these prerequisite ExecPlans: `.execflow/plans/starhtml-catalog-studio-foundation/execplan.md`, `.execflow/plans/catalog-studio-explorer/execplan.md`, `.execflow/plans/catalog-studio-query-workbench/execplan.md`, and `.execflow/plans/catalog-studio-editing-safety/execplan.md`. If any prerequisite is not implemented yet, implement it first. This Expert Editor plan assumes the editing safety service exists and exposes raw-load, validate, diff-preview, safe-save, backup, atomic-write, and reload-verification operations.

## Purpose / Big Picture

After this change, a user can open Catalog Studio’s expert editor, view the raw YAML or JSON configuration text, edit it in a large textarea, validate the proposed text, preview the exact diff, and save only through the editing safety service. Saving creates a backup, writes atomically, reloads the config, and reports success or errors clearly. The editor preserves raw text because it saves the user’s proposed text rather than regenerating YAML from the loaded `Config` object.

This feature gives power users the direct YAML/JSON control requested in the brainstorm while still respecting the safety boundary created by the previous plan. It is not the form/menu editor. It is the expert mode that future structured editing can coexist with.

## Progress

- [x] (2026-04-30) Completed the umbrella brainstorm and selected form/menu editing plus expert YAML/JSON editing as part of the Catalog Studio vision.
- [x] (2026-04-30) Created the prerequisite foundation, explorer, query workbench, and editing safety ExecPlans.
- [x] (2026-04-30) Read the editing safety ExecPlan, query workbench plan, StarHTML skill guidance, and current dashboard textarea patterns.
- [x] (2026-04-30) Ran a scout pass for expert editor planning; scout reported that `src/duckalog/studio/` is still a prerequisite-created package and that this plan should build on the editing safety service APIs.
- [ ] Confirm the editing safety service exists and exposes `load_editable_config`, `validate_config_text`, `preview_config_diff`, and `save_config_text_safely` or equivalent operations.
- [ ] Add an expert editor page component with raw config textarea, status panel, validation result panel, diff preview panel, and guarded save controls.
- [ ] Add StarHTML routes for `GET /config/expert`, `POST /config/expert/validate`, `POST /config/expert/preview`, and `POST /config/expert/save` or adapt to existing safety endpoints if they were already added.
- [ ] Wire the editor routes to the editing safety service only; do not parse or write files inline in route handlers.
- [ ] Add tests for page rendering, validation success/failure, diff preview, save success, invalid-save blocking, remote/read-only behavior, raw text preservation, and old dashboard preservation.
- [ ] Run `starhtml-check`, Studio tests, editing safety tests, and existing dashboard tests, then update this plan with results.

## Surprises & Discoveries

- Observation: The only existing editor-like UI pattern in the old dashboard is the SQL textarea.
  Evidence: `src/duckalog/dashboard/routes/query.py` renders a `textarea` with `id="sql-input"` and Datastar binding for query input. The expert config editor should use the same conceptual pattern but with StarHTML signals and safety-service routes.

- Observation: The expert editor must not serialize the loaded `Config` object back to YAML.
  Evidence: The editing safety scout identified `src/duckalog/config/loading/sql.py:process_sql_file_references()` as inlining `sql_file` and `sql_template` into `sql`, which would destroy original references if the editor saved a normalized model dump.

- Observation: The editing safety service is the mandatory boundary for writes.
  Evidence: The previous ExecPlan defines service operations for raw loading, validation, diff preview, backup, atomic save, and reload verification. This plan must consume that boundary rather than duplicating file-write policy in StarHTML route code.

## Decision Log

- Decision: Implement Expert YAML/JSON Editor before the structured form editor.
  Rationale: Expert mode directly exercises the editing safety service with raw proposed text. It avoids the schema-specific complexity of generating form-driven patches while still delivering the requested full YAML/JSON editing capability.
  Date/Author: 2026-04-30 / planning session

- Decision: Use a plain textarea first, not a full browser code-editor dependency.
  Rationale: A textarea requires no frontend build pipeline or new dependency and is enough to validate the editing workflow. A richer editor such as CodeMirror or Monaco can be evaluated later if the textarea proves inadequate.
  Date/Author: 2026-04-30 / planning session

- Decision: Save is disabled or rejected until validation and diff preview have succeeded for the current text.
  Rationale: The user should not accidentally write invalid text or skip review. The safety service still validates on save, but the UI should guide users through validate-preview-save.
  Date/Author: 2026-04-30 / planning session

- Decision: Remote configs remain read-only in Expert Editor.
  Rationale: The editing safety foundation deliberately treats remote configs as read-only because remote atomic writes and authentication are separate concerns.
  Date/Author: 2026-04-30 / planning session

## Outcomes & Retrospective

No implementation outcomes have been produced yet. At completion, update this section with the exact route names, UX flow, tests and `starhtml-check` output, any StarHTML signal/SSE discoveries, and whether a richer editor dependency should be considered in a later plan.

## Context and Orientation

Catalog Studio is the new StarHTML-based UI for Duckalog. Duckalog config files are YAML or JSON files that define DuckDB settings, views, attachments, secrets, imports, and related catalog metadata. The normal Duckalog loader turns raw text into a validated `Config` object, but that load process may resolve imports, interpolate environment variables, resolve paths, and inline SQL file references. That is correct for execution, but dangerous for editing because it can lose comments, formatting, `${env:VAR}` references, `imports`, and `sql_file` authoring intent.

The previous editing safety plan creates a pure Python service under `src/duckalog/studio/editing.py` or a similar module. This Expert Editor must call that service. Expected operations are equivalent to `load_editable_config(path)`, `validate_config_text(text, format, base_path)`, `preview_config_diff(original_text, proposed_text, path)`, and `save_config_text_safely(path, proposed_text)`. If implementation chose different names, use the implemented names and update this ExecPlan’s `Surprises & Discoveries`.

StarHTML is a Python-first framework over Datastar. A signal is browser state that can be bound to a textarea or button and sent to the server. The StarHTML skill requires snake_case signal names, no f-strings in reactive attributes, positional content arguments before keyword attributes, and `starhtml-check` after generating StarHTML files. This plan’s UI should use signals such as `config_text`, `is_validating`, `is_previewing`, `is_saving`, `validation_ok`, `has_preview`, and `last_saved_at`. Do not treat signals as Python data containers.

This plan should extend the Studio app created by earlier plans. It should not add a second CLI command or a second editing service. It should not implement structured field-level forms; those belong to a later Structured Catalog Form Editor plan.

## Plan of Work

Begin by verifying all prerequisites. The Studio package must exist, the read-only explorer and query workbench tests should pass, and the editing safety service tests should pass. If `src/duckalog/studio/editing.py` or equivalent does not exist, stop and implement `.execflow/plans/catalog-studio-editing-safety/execplan.md` first.

Add expert editor components in `src/duckalog/studio/components.py` or a feature-specific module such as `src/duckalog/studio/editor_components.py` if the Studio package has already grown. Prefer a component boundary that hides UI sequencing from the route handlers. A good top-level component is `expert_editor_page(draft, validation=None, diff=None, save_result=None)`. It should render the Studio shell content for the current config path, detected format, read-only status, and raw text.

The editor page should include a large textarea with a stable id such as `config-text-editor`. Bind it to a StarHTML signal named `config_text`. Show the file path, format, and a warning that this is expert mode. Add buttons for “Validate”, “Preview diff”, “Save changes”, and “Reload from disk”. The save button should be visually disabled until validation and preview are successful for the current text, if the StarHTML signal model makes that practical. Regardless of UI state, the save route must revalidate server-side before writing.

Add a validation result panel. On success, it should show that the proposed config is valid and summarize useful facts from the parsed config, such as view count and schema count. On failure, it should show a list of parse or validation errors with field locations when available. Do not expose raw Python tracebacks to users.

Add a diff preview panel. It should show the unified diff returned by the editing safety service in a preformatted block. It should handle “no changes” clearly. The diff labels should identify current and proposed versions of the file.

Add a save result panel. On success, it should show the saved file path, backup path, and reload verification status. On failure, it should show why no write happened or, if a restore was needed, where the backup is. Avoid saying “saved” unless reload verification succeeded.

Add or update Studio routes in `src/duckalog/studio/app.py`. Use `GET /config/expert` for the page. Use StarHTML SSE endpoints such as `POST /config/expert/validate`, `POST /config/expert/preview`, and `POST /config/expert/save` if the framework supports streaming patches. If the editing safety plan already added `POST /config/validate`, `POST /config/preview`, and `POST /config/save`, either reuse them or wrap them with expert-specific routes; do not duplicate validation/write logic. Route handlers should extract `config_text` from the request or signal parameter and then call the editing service.

Implement request parsing according to the actual StarHTML API. The StarHTML skill notes that Datastar/StarHTML POST handlers receive JSON by default and that handlers can accept signal parameters. Prefer the idiom from the implemented query workbench if it already has StarHTML SSE request parsing. Always reset `is_validating`, `is_previewing`, and `is_saving` signals to false at the end of SSE handlers.

Protect against stale saves. The simplest acceptable protection is to include the original text or an original checksum from the page load in the save request and have the save route compare it to the current file on disk before writing. If the file changed since the editor loaded, reject the save and ask the user to reload. This prevents overwriting external edits. Use a standard-library hash such as SHA-256 in the editing service or route layer. Do not rely only on timestamps.

Update navigation so a “Config” or “Expert Editor” entry leads to `/config/expert`. If the shell already has disabled editor placeholders, replace only the expert placeholder with an active link. Keep structured form editing marked as coming soon.

Add tests. Direct UI route tests should verify that `GET /config/expert` renders the raw text, format, and controls. Validation endpoint tests should submit valid and invalid YAML/JSON and assert that no file is written. Preview endpoint tests should assert that the diff contains expected changed lines and that no file is written. Save endpoint tests should assert that valid proposed text writes via the safety service, creates a backup, and preserves comments when present in the proposed text. Save endpoint tests should assert invalid proposed text does not write. Add a stale-save test if checksum protection is implemented. Add read-only/remote tests if the Studio app can be created with a remote config path.

Run `starhtml-check` on changed Studio files containing StarHTML components or reactive attributes. Run all Studio tests including editing safety tests, then run `tests/test_dashboard.py` to prove the existing dashboard remains intact.

## Concrete Steps

Work from the repository root `/Users/volker/coding/libs/duckalog`.

First verify prerequisites:

    uv run python - <<'PY'
    from duckalog.studio import create_app, StudioContext
    from duckalog.studio import editing
    print(create_app, StudioContext, editing)
    PY

Then run tests from prior Studio plans:

    uv run pytest tests/test_studio.py tests/test_studio_editing.py -q

If prior feature tests are split, include them:

    uv run pytest tests/test_studio.py tests/test_studio_explorer.py tests/test_studio_query.py tests/test_studio_editing.py -q

If any prerequisite fails because it is unimplemented, stop and implement that prerequisite plan first.

Inspect the implemented editing service API and any existing config endpoints:

    rg -n "load_editable_config|validate_config_text|preview_config_diff|save_config_text_safely|config/validate|config/preview|config/save|config_text" src/duckalog/studio tests

Add the expert editor page and routes. After the first implementation, run a smoke import:

    uv run python - <<'PY'
    from pathlib import Path
    from duckalog.config import load_config
    from duckalog.studio import create_app

    path = Path('/tmp/duckalog-expert-editor.yaml')
    path.write_text('''# expert editor smoke
    version: 1
    duckdb:
      database: ":memory:"
    views:
      - name: demo
        sql: "select 1 as id"
    ''')
    app = create_app(load_config(str(path), load_sql_files=False), config_path=str(path))
    print(app)
    PY

Run StarHTML checks on changed UI files:

    starhtml-check src/duckalog/studio/app.py
    starhtml-check src/duckalog/studio/components.py

If expert editor components live in a new file, check that file too:

    starhtml-check src/duckalog/studio/editor_components.py

Run focused tests:

    uv run pytest tests/test_studio_expert_editor.py -q

Then run all Studio tests:

    uv run pytest tests/test_studio.py tests/test_studio_editing.py tests/test_studio_expert_editor.py -q

If explorer/query tests are split, include them too:

    uv run pytest tests/test_studio.py tests/test_studio_explorer.py tests/test_studio_query.py tests/test_studio_editing.py tests/test_studio_expert_editor.py -q

Run old dashboard tests:

    uv run pytest tests/test_dashboard.py -q

Manually smoke-test the editor with a temporary local config:

    cat >/tmp/duckalog-expert-editor.yaml <<'YAML'
    # keep this comment
    version: 1
    duckdb:
      database: ":memory:"
    views:
      - name: demo
        sql: "select 1 as id"
        description: "Expert editor demo"
    YAML

Start Studio:

    uv run duckalog studio /tmp/duckalog-expert-editor.yaml --port 8788

In another terminal, verify the page exists:

    curl -s http://127.0.0.1:8788/config/expert | rg "Expert|config-text-editor|Validate|Preview diff|Save changes|keep this comment"

Endpoint curl commands depend on the StarHTML request format used by implementation. Add the working validate, preview, and save curl examples to this plan during implementation once the exact payload is known.

## Validation and Acceptance

Acceptance is user-visible. A local-config Studio session has an Expert Editor page. The page displays the raw config text including comments. The user can edit the text, validate it, see structured validation success or errors, preview a unified diff, and save only when the proposed text validates. A successful save reports the backup path and reload verification. Invalid text does not write. If the file changed on disk since the editor loaded, save is rejected and the user is told to reload. Remote configs are displayed as read-only or rejected from editing according to the safety service behavior.

Automated tests must prove the same behavior. They must verify raw text appears in the page, validation and preview do not write to disk, save writes exact proposed text, save creates a backup, comments and `sql_file` references in proposed text are preserved, invalid saves are blocked, and stale-save protection works if implemented. Tests should assert that route handlers call the editing safety service or exercise equivalent behavior through it; they should not accept inline `Path.write_text()` in route handlers.

StarHTML validation requires `starhtml-check` on every changed Studio UI file with no ERROR findings. Existing dashboard tests must still pass.

## Idempotence and Recovery

Loading the Expert Editor and running validate or preview is read-only. Those operations must be safe to repeat. Save operations are safe in the sense that each successful save creates a new backup and writes atomically through the safety service. Tests should use temporary paths and clean up through pytest fixtures.

If a save fails validation, do not create a backup and do not write. If a save fails after backup creation, follow the editing safety service recovery behavior and surface its result. If stale-save protection detects an external change, reject the save and preserve both the current file and the user’s proposed text in the browser state so the user can copy or reapply it after reload.

If StarHTML SSE route testing is difficult because the test client buffers events, keep service tests strong and add route tests for page render plus representative endpoint response text. Record the limitation in `Surprises & Discoveries`.

If this implementation must be backed out, remove the expert editor routes, components, navigation link, and tests. Keep the editing safety service intact because it is the foundation for both expert and structured editors.

## Artifacts and Notes

The umbrella brainstorm is:

    .execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md

Prerequisite ExecPlans are:

    .execflow/plans/starhtml-catalog-studio-foundation/execplan.md
    .execflow/plans/catalog-studio-explorer/execplan.md
    .execflow/plans/catalog-studio-query-workbench/execplan.md
    .execflow/plans/catalog-studio-editing-safety/execplan.md

Relevant existing references are:

    src/duckalog/dashboard/routes/query.py  # old textarea pattern
    src/duckalog/config/loading/sql.py      # SQL file inlining risk
    src/duckalog/studio/editing.py          # expected safety service after prerequisite plan

The Expert Editor should avoid new frontend dependencies in this plan. A future enhancement may add CodeMirror, Monaco, or a StarHTML-compatible editor component, but only after this plain-textarea workflow proves the backend safety and route flow.

## Interfaces and Dependencies

At the end of this plan, the Studio app should expose these routes or equivalent names documented in tests:

    GET /config/expert
    POST /config/expert/validate
    POST /config/expert/preview
    POST /config/expert/save

If the editing safety plan already exposed generic safety endpoints, this plan may reuse them and only add `GET /config/expert`, but tests must still cover the Expert Editor user flow.

The expert editor UI should use stable element ids for tests and patches:

    config-text-editor
    config-validation-panel
    config-diff-panel
    config-save-panel
    config-save-button

The implementation should use only existing dependencies plus StarHTML from the foundation plan. Do not add a browser code editor dependency in this plan. Do not add a round-trip YAML parser in this plan. Do not bypass `src/duckalog/studio/editing.py` or equivalent safety service for validation, preview, or save.

The next ExecPlan should be Structured Catalog Form Editor. It should generate proposed raw text or structured patches, then use this same safety service and preview/save flow rather than writing directly.

## Revision Note

2026-04-30: Initial Catalog Studio Expert Editor ExecPlan created. It provides the raw YAML/JSON editing UI on top of the editing safety service and deliberately avoids structured form editing and new frontend editor dependencies.
