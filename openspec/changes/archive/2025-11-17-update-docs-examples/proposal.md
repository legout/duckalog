## Why

Duckalog now has a solid README, a basic MkDocs site, and API docstrings, but
the documentation remains relatively thin on context and real-world examples.
Users reading the docs may still need to open the PRD or dive into tests to
understand:

- How to structure multi-source configs (attachments + Iceberg + raw SQL).
- Common patterns for environment variables and credentials.
- How to combine CLI and Python API in typical workflows.
- How to troubleshoot common errors.

Improving the docs with richer explanations and end-to-end examples will make
the project easier to adopt and reduce the need to read the full PRD for
day-to-day usage.

## What Changes

- Extend the documentation under `docs/` to provide:
  - A more narrative quickstart with a complete example (config + CLI + Python
    usage) that mirrors a realistic workflow.
  - A richer user guide that covers multi-source configs, credentials, and
    troubleshooting tips.
  - Additional example configs for common scenarios (e.g. "only Parquet",
    "attachments only", "Iceberg catalog views").
- Keep the existing structure (README, `docs/index.md`, `docs/guides/usage.md`,
  `docs/reference/api.md`) and build on it rather than introducing a large
  reorganization.

## Impact

- Makes the docs more self-contained for everyday use; users can learn by
  example without needing to open `docs/PRD_Spec.md` for common tasks.
- Provides better guidance on composing advanced configs (attachments,
  Iceberg, env vars) and on using the CLI and Python API together.
- Improves the value of the MkDocs site as a user-facing resource.

