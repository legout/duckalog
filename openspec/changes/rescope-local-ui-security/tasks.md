## 1. Scope alignment
- [x] Clarify that `/api/query` stays, but must be read-only/single-statement (coordinate with `harden-ui-readonly-config`)
- [x] Set admin token auth as opt-in and applied only to mutating endpoints when configured
- [x] Allow exports from views or read-only queries (reject DDL/DML/multi-statement)
- [x] Keep API surface unchanged (no forced removal of endpoints) and avoid mandated service-layer splits

## 2. Specs and validation
- [x] Update web-ui spec deltas to reflect scoped security/convenience balance
- [x] Cross-check with `harden-ui-readonly-config`, `fix-export-formats`, and `bundle-datastar-assets` to avoid duplication
- [x] Validate with `openspec validate rescope-local-ui-security --strict`
