# Add Catalog Studio attachments and secrets form editing

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document must be maintained in accordance with `.execflow/PLANS.md` from the repository root. It builds on the completed umbrella brainstorm at `.execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md` and on the full Catalog Studio editing chain through `.execflow/plans/catalog-studio-view-lifecycle/execplan.md`. If the Studio foundation, explorer, query workbench, editing safety service, expert editor, structured form editor, and view lifecycle flows have not been implemented yet, implement them first. This plan adds structured forms for attachments and secrets, with special care for sensitive values.

## Purpose / Big Picture

After this change, a Catalog Studio user can edit database attachments and DuckDB secrets through structured forms. They can add, edit, duplicate, and delete DuckDB, SQLite, Postgres, and Duckalog attachments. They can add, edit, duplicate, and delete DuckDB secrets for providers such as S3, Azure, GCS, HTTP, Postgres, and MySQL. Every change generates proposed raw config text, validates the full config, previews a redacted diff, and saves only through the editing safety service.

This is the first Catalog Studio editor for sensitive and connection-oriented config. It completes a major part of catalog setup beyond views while preserving safety, redaction, and raw-text handling.

## Progress

- [x] (2026-04-30) Created prerequisite ExecPlans through Catalog Studio View Lifecycle.
- [x] (2026-04-30) Read attachment and secret model definitions, SQL generation code, engine attachment setup, redaction utilities, and predecessor editing plans.
- [x] (2026-04-30) Ran a scout pass and saved context at `.execflow/plans/catalog-studio-attachments-secrets-editor/context.md`.
- [ ] Confirm the full predecessor chain is implemented and tests pass.
- [ ] Add pure helper functions that build proposed raw text for attachment add/edit/duplicate/delete operations.
- [ ] Add pure helper functions that build proposed raw text for secret add/edit/duplicate/delete operations.
- [ ] Add redacted diff-preview handling for secret and password fields.
- [ ] Add StarHTML components and routes for attachments list/forms and secrets list/forms.
- [ ] Route all validate, preview, and save actions through the editing safety service.
- [ ] Add tests for provider-specific secret validation, attachment validation, redaction, save backups, `sql_file` preservation in unrelated sections, and old dashboard preservation.
- [ ] Run `starhtml-check`, Studio tests, editing tests, and existing dashboard tests, then update this plan with results.

## Surprises & Discoveries

- Observation: Attachments and secrets live in different parts of the config tree.
  Evidence: `AttachmentsConfig` is the top-level `config.attachments` field with `duckdb`, `sqlite`, `postgres`, and `duckalog` lists. Secrets live under `config.duckdb.secrets`.

- Observation: Secrets have provider-specific required fields.
  Evidence: `SecretConfig._validate_secret_fields()` requires different fields for S3, Azure, GCS, HTTP, Postgres, and MySQL depending on provider and connection-string use.

- Observation: Attachment aliases must be unique across all attachment types.
  Evidence: `Config._validate_uniqueness()` checks alias uniqueness across `attachments.duckdb`, `attachments.sqlite`, `attachments.postgres`, and `attachments.duckalog`.

- Observation: Diffs can expose credentials if raw unified diffs are shown directly.
  Evidence: Secret fields include names such as `secret`, `password`, `client_secret`, `service_account_key`, `json_key`, `bearer_token`, and `connection_string`; Postgres attachments include `password`. Existing logging redaction helpers in `src/duckalog/config/validators.py` redact based on sensitive key names, but diff preview needs its own redacted presentation.

## Decision Log

- Decision: Implement attachments and secrets in one plan but keep helper modules separated by concern.
  Rationale: Both use the same form-to-proposed-text and safety-service pipeline, but secret redaction and provider-specific validation are complex enough to deserve distinct helpers/components.
  Date/Author: 2026-04-30 / planning session

- Decision: Redacted preview is mandatory for secrets and passwords.
  Rationale: The safety service’s raw diff is useful for exact file changes but can reveal credentials. UI previews for this plan must use a redacted diff by default, with no accidental logging of sensitive values.
  Date/Author: 2026-04-30 / planning session

- Decision: Secret forms preserve existing sensitive values unless the user explicitly replaces them.
  Rationale: Editing a non-sensitive field should not blank or expose a stored secret. Placeholder values such as `********` must not be saved literally unless the user intentionally enters them as real values.
  Date/Author: 2026-04-30 / planning session

- Decision: Do not test live database or cloud connections in this plan.
  Rationale: This plan edits and validates config shape. Runtime connectivity belongs to engine integration and environment-specific testing, not the form editor.
  Date/Author: 2026-04-30 / planning session

- Decision: Use the existing raw-text dictionary transformation pattern and avoid `Config.model_dump()`.
  Rationale: Previous plans established that normal loading can inline SQL files and normalize authoring details. This editor must preserve unrelated raw sections and only change targeted attachment/secret sections.
  Date/Author: 2026-04-30 / planning session

## Outcomes & Retrospective

No implementation outcomes have been produced yet. At completion, update this section with exact routes, helper names, redaction behavior, validation coverage, and test results.

## Context and Orientation

Duckalog attachments connect a catalog to other databases. `DuckDBAttachment` has `alias`, `path`, and `read_only`. `SQLiteAttachment` has `alias` and `path`. `PostgresAttachment` has `alias`, `host`, `port`, `database`, `user`, `password`, optional `sslmode`, and options. `DuckalogAttachment` has `alias`, `config_path`, optional `database`, and `read_only`. The engine turns these into DuckDB `ATTACH DATABASE` statements in `src/duckalog/engine.py:_setup_attachments()` and related child-catalog state logic.

DuckDB secrets configure credentials for remote storage and databases. `SecretConfig` lives under `duckdb.secrets` and supports types `s3`, `azure`, `gcs`, `http`, `postgres`, and `mysql`. Secret fields include multiple sensitive values. `src/duckalog/sql_generation.py:generate_secret_sql()` renders `CREATE SECRET` SQL and provider-specific helper functions render the right parameters.

The editing safety service is the only file-write boundary. The structured form editor and view lifecycle plans establish helper modules that parse raw config text into dictionaries, modify targeted sections, serialize proposed YAML or JSON, validate the proposed text, preview a diff, and call `save_config_text_safely()` only on save. This plan must follow that same pattern.

Secrets create an extra UI security requirement. The raw config file may contain literal credentials or environment-variable references such as `${env:PG_PASSWORD}`. The editor must not display literal credentials in overview lists or diff previews unless the raw expert editor is being used intentionally. For structured forms, sensitive inputs should show placeholders and preserve original values when left unchanged.

## Plan of Work

Begin by verifying prerequisites. The Studio package must contain the editing safety service, form editing helpers, and view lifecycle helpers. Their tests must pass. If not, stop and implement prerequisite plans first.

Add pure helper functions for attachments, for example in `src/duckalog/studio/attachment_editing.py`. The helpers should parse the current editable draft text into a plain dictionary, modify the relevant `attachments.<type>` list, serialize proposed text to the same format, and validate via the editing safety service. Required operations are add, edit, duplicate, and delete. Use stable attachment identity as `(type, alias)`. Editing an alias is effectively a rename and must validate cross-type alias uniqueness.

Add pure helper functions for secrets, for example in `src/duckalog/studio/secret_editing.py`. The helpers should modify `duckdb.secrets`, using identity `(type, name or type)` or a stable list index if duplicate anonymous secrets are otherwise ambiguous. Prefer requiring a name in the structured UI for new secrets even though the model allows `name` to default to the type; this reduces ambiguity. Required operations are add, edit, duplicate, and delete.

Implement form normalization for attachments. DuckDB attachment forms should support alias, path, and read_only. SQLite forms should support alias and path. Postgres forms should support alias, host, port, database, user, password, sslmode, and options as a JSON textarea. Duckalog attachment forms should support alias, config_path, database, and read_only. Empty optional fields should be omitted or serialized as null according to conventions from earlier form helpers.

Implement form normalization for secrets. The UI should start with a secret type selector. For S3, support provider, name, persistent, scope, key_id, secret, region, endpoint, and options. For Azure, support connection_string, tenant_id, account_name, client_id, client_secret or secret, persistent, scope, and options. For GCS, support service_account_key, json_key, or key_id plus secret. For HTTP, support bearer_token. For Postgres and MySQL secrets, support connection_string or host, port, database, user/key_id, password/secret. Let `SecretConfig.model_validate()` be the final authority for required-field combinations.

Implement redaction helpers for structured editor output. Add a function that redacts sensitive keys in dictionaries and another function that creates a redacted unified diff for UI preview. Sensitive key names should include at least `password`, `secret`, `token`, `key`, `pwd`, `connection_string`, `service_account_key`, `json_key`, and `bearer_token`. Reuse or mirror `src/duckalog/config/validators.py:_redact_value()` but do not import private helpers if project conventions discourage it; if importing is acceptable, wrap it in a Studio-local helper. Tests must prove redaction.

For secret edit forms, preserve existing sensitive values. When rendering a secret with an existing sensitive value, show a placeholder such as `********` and include server-side metadata or hidden state sufficient to distinguish “unchanged” from “replace with empty”. In the POST handler/helper, if the placeholder is submitted unchanged, keep the original raw dictionary value. If the user clears a required sensitive field, validation should fail unless the selected provider no longer requires it.

Add StarHTML components. Add attachment list and secret list pages under the config area. Lists should show safe summaries: type, alias/name, host/path/scope where non-sensitive, and badges for read_only/persistent/provider. Do not show literal passwords, secrets, tokens, connection strings, service account keys, or JSON keys in lists. Add forms for each attachment and secret type. Add validation, preview, and save panels consistent with the structured form editor.

Add routes. Recommended attachment routes are `GET /catalog/forms/attachments`, `GET /catalog/forms/attachments/{type}/add`, `GET /catalog/forms/attachments/{type}/{alias}/edit`, `GET /catalog/forms/attachments/{type}/{alias}/duplicate`, `GET /catalog/forms/attachments/{type}/{alias}/delete`, and POST endpoints for validate/preview/save grouped by operation. Recommended secret routes are `GET /catalog/forms/secrets`, `GET /catalog/forms/secrets/add`, `GET /catalog/forms/secrets/{identity}/edit`, `GET /catalog/forms/secrets/{identity}/duplicate`, `GET /catalog/forms/secrets/{identity}/delete`, and POST endpoints for validate/preview/save. If the existing Studio route conventions differ, follow them and update tests.

Every POST route should call helper functions to generate proposed text, call `validate_config_text()` or preview functions, and call `save_config_text_safely()` only for save. Route handlers must not write files directly and must not log raw submitted secret values.

Add tests. Helper tests should cover all attachment types and representative secret types. Required tests include duplicate attachment alias rejection across types, Postgres attachment required fields, S3 secret required key_id/secret for config provider, credential_chain S3 not requiring key_id/secret, HTTP bearer token requirement, Postgres/MySQL connection-string versus field-based validation, secret placeholder preservation, redacted diff output, backup creation on save, and no direct writes during validate/preview. Route tests should prove pages render without exposing sensitive values.

Run `starhtml-check` on changed Studio UI files, all Studio editing tests, and old dashboard tests.

## Concrete Steps

Work from the repository root `/Users/volker/coding/libs/duckalog`.

Verify prerequisites:

    uv run python - <<'PY'
    from duckalog.studio import create_app, StudioContext
    from duckalog.studio import editing, form_editing, view_lifecycle
    print(create_app, StudioContext, editing, form_editing, view_lifecycle)
    PY

Run prerequisite tests:

    uv run pytest tests/test_studio_editing.py tests/test_studio_expert_editor.py tests/test_studio_form_editor.py tests/test_studio_view_lifecycle.py -q

Inspect relevant model and SQL generation code:

    rg -n "class SecretConfig|class AttachmentsConfig|class DuckDBAttachment|class SQLiteAttachment|class PostgresAttachment|class DuckalogAttachment|def generate_secret_sql|def _setup_attachments|_redact_value" src/duckalog

After adding helper functions, run a direct smoke test. Adjust names to match implementation:

    uv run python - <<'PY'
    from pathlib import Path
    from duckalog.studio.editing import load_editable_config, validate_config_text
    from duckalog.studio.attachment_editing import build_proposed_add_attachment_text
    from duckalog.studio.secret_editing import build_proposed_add_secret_text, redact_config_diff

    path = Path('/tmp/duckalog-attachments-secrets.yaml')
    path.write_text('''version: 1
    duckdb:
      database: ":memory:"
      secrets: []
    views:
      - name: demo
        sql: "select 1 as id"
    attachments:
      duckdb: []
      sqlite: []
      postgres: []
      duckalog: []
    ''')
    draft = load_editable_config(path)
    proposed_attachment = build_proposed_add_attachment_text(draft, 'duckdb', {'alias': 'ref', 'path': './ref.duckdb', 'read_only': True})
    assert validate_config_text(proposed_attachment, draft.format, base_path=path).ok
    proposed_secret = build_proposed_add_secret_text(draft, {'type': 's3', 'name': 'prod_s3', 'key_id': 'AKIA...', 'secret': 'super-secret'})
    assert validate_config_text(proposed_secret, draft.format, base_path=path).ok
    redacted = redact_config_diff(draft.text, proposed_secret, path)
    assert 'super-secret' not in redacted
    print('attachments/secrets helpers ok')
    PY

Run StarHTML checks after adding UI:

    starhtml-check src/duckalog/studio/app.py
    starhtml-check src/duckalog/studio/components.py

If UI is split, also run:

    starhtml-check src/duckalog/studio/attachment_components.py
    starhtml-check src/duckalog/studio/secret_components.py

Run focused tests:

    uv run pytest tests/test_studio_attachments_secrets_editor.py -q

Run all Studio editing tests:

    uv run pytest tests/test_studio_editing.py tests/test_studio_expert_editor.py tests/test_studio_form_editor.py tests/test_studio_view_lifecycle.py tests/test_studio_attachments_secrets_editor.py -q

Run old dashboard tests:

    uv run pytest tests/test_dashboard.py -q

Manual smoke test:

    cat >/tmp/duckalog-attachments-secrets.yaml <<'YAML'
    version: 1
    duckdb:
      database: ":memory:"
      secrets:
        - type: s3
          name: demo_s3
          key_id: "${env:AWS_ACCESS_KEY_ID}"
          secret: "${env:AWS_SECRET_ACCESS_KEY}"
    views:
      - name: demo
        sql: "select 1 as id"
    attachments:
      duckdb:
        - alias: ref
          path: ./ref.duckdb
          read_only: true
    YAML

Start Studio:

    uv run duckalog studio /tmp/duckalog-attachments-secrets.yaml --port 8788

Verify pages exist and do not reveal raw secret values:

    curl -s http://127.0.0.1:8788/catalog/forms/attachments | rg "Attachments|ref|duckdb"
    curl -s http://127.0.0.1:8788/catalog/forms/secrets | rg "Secrets|demo_s3|s3"
    curl -s http://127.0.0.1:8788/catalog/forms/secrets | rg -v "AWS_SECRET_ACCESS_KEY"

During implementation, add working validate, preview, and save curl examples once the StarHTML request format is known.

## Validation and Acceptance

Acceptance is user-visible. A user can list attachments and secrets, add/edit/duplicate/delete supported attachment types, and add/edit/duplicate/delete supported secret types. Validation errors are provider-specific and understandable. Preview diffs shown in the structured UI redact sensitive values. Successful saves create backups and reload valid config. Validate and preview do not write files. Old dashboard behavior remains unchanged.

Automated tests must prove attachment alias uniqueness, provider-specific secret validation, sensitive placeholder preservation, redacted diff behavior, no raw secret leakage in list pages, backup creation on save, and route handlers using the safety service. Tests must confirm that unrelated sections such as views and `sql_file` references are preserved when attachments or secrets are edited.

StarHTML validation requires `starhtml-check` on every changed Studio UI file with no ERROR findings.

## Idempotence and Recovery

GET routes and validate/preview POST routes must never write. Save routes go through the editing safety service, so each successful save creates a backup and writes atomically. If stale-save protection exists from earlier editors, use it here too.

If a secret edit form leaves a sensitive placeholder unchanged, preserve the original value. If the user clears a required secret value, validation should fail and no write should happen. If a preview diff would expose sensitive values, show only the redacted preview in the structured UI; Expert Editor remains the deliberate raw-text mode.

If implementation must be backed out, remove attachments/secrets helpers, components, routes, navigation links, and tests. Keep view lifecycle, form editor, expert editor, and editing safety service intact.

## Artifacts and Notes

Prerequisite ExecPlans include:

    .execflow/plans/catalog-studio-editing-safety/execplan.md
    .execflow/plans/catalog-studio-expert-editor/execplan.md
    .execflow/plans/catalog-studio-form-editor/execplan.md
    .execflow/plans/catalog-studio-view-lifecycle/execplan.md

Scout context for this plan is:

    .execflow/plans/catalog-studio-attachments-secrets-editor/context.md

Relevant code references are:

    src/duckalog/config/models.py:SecretConfig
    src/duckalog/config/models.py:AttachmentsConfig
    src/duckalog/config/models.py:DuckDBAttachment
    src/duckalog/config/models.py:SQLiteAttachment
    src/duckalog/config/models.py:PostgresAttachment
    src/duckalog/config/models.py:DuckalogAttachment
    src/duckalog/sql_generation.py:generate_secret_sql
    src/duckalog/engine.py:_setup_attachments
    src/duckalog/config/validators.py:_redact_value

Future plans can add live connection testing, attachment dependency analysis, secret import/export helpers, semantic model forms, and Iceberg catalog editing. Those are out of scope here.

## Interfaces and Dependencies

At the end of this plan, helper operations equivalent to these should exist:

    build_proposed_add_attachment_text(draft, attachment_type, values) -> str
    build_proposed_edit_attachment_text(draft, attachment_type, alias, values) -> str
    build_proposed_duplicate_attachment_text(draft, attachment_type, alias, new_alias) -> str
    build_proposed_delete_attachment_text(draft, attachment_type, alias) -> str
    build_proposed_add_secret_text(draft, values) -> str
    build_proposed_edit_secret_text(draft, identity, values) -> str
    build_proposed_duplicate_secret_text(draft, identity, new_name) -> str
    build_proposed_delete_secret_text(draft, identity) -> str
    redact_config_diff(original_text, proposed_text, path) -> str

The Studio app should expose list, add, edit, duplicate, delete, validate, preview, and save routes for attachments and secrets. Exact route names may follow the conventions established by previous Studio editors, but tests must document them.

Use existing dependencies only. Do not add a secrets manager, live credential tester, or round-trip YAML parser in this plan. Do not write files directly outside the editing safety service.

The next ExecPlan should likely cover semantic model form editing or Iceberg catalog editing, because attachments/secrets plus views cover most catalog construction inputs.

## Revision Note

2026-04-30: Initial Catalog Studio Attachments and Secrets Editor ExecPlan created. It extends structured editing to connection and credential configuration while requiring redacted previews and safety-service saves.
