## 1. Implementation
- [x] 1.1 Update `docs/reference/config-schema.md` to match `src/duckalog/config/models.py`
- [x] 1.2 Update secrets documentation to reflect implemented shape:
  - Move `secrets:` examples to `duckdb: { secrets: [...] }`
  - Remove `secrets_ref` from all examples and diagrams
- [x] 1.3 Update affected docs pages containing invalid secrets/schema examples:
  - `docs/examples/duckdb-secrets.md`
  - `docs/guides/usage.md` (secret-related sections only)
  - `docs/SECURITY.md` (secret-related examples only)
  - `docs/explanation/architecture.md` (schema references/diagrams)
- [x] 1.4 Remove references to unimplemented config fields from schema docs (e.g. `views[].materialized`)

## 2. Verification
- [x] 2.1 Run `mkdocs build` and fix any build issues
- [x] 2.2 Spot-check that updated examples match to current config model fields (no `secrets_ref`, no top-level `secrets`)