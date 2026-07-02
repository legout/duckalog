# Duckalog Refactoring Superpowers Roadmap

This roadmap coordinates the remaining focused Superpowers design specs and implementation plans without merging them into one oversized plan.

## Dependency order

1. `specs/2026-07-01-refactor-critical-security-contracts-design.md` and `plans/2026-07-01-refactor-critical-security-contracts.md`
   - Fixes security-critical SQL and path contracts first.
2. `specs/2026-07-01-refactor-remote-config-contracts-design.md` and `plans/2026-07-01-refactor-remote-config-contracts.md`
   - Restores public remote config loading before runtime and CLI work depend on it.
3. `specs/2026-07-01-refactor-catalog-runtime-boundary-design.md` and `plans/2026-07-01-refactor-catalog-runtime-boundary.md`
   - Unifies engine, Python API, and CLI runtime state after remote config behavior is stable.
4. `specs/2026-07-01-refactor-cli-boundary-design.md` and `plans/2026-07-01-refactor-cli-boundary.md`
   - Repairs user-facing CLI contracts after config/runtime behavior is stable.
5. `specs/2026-07-01-refactor-test-dead-code-hygiene-design.md` and `plans/2026-07-01-refactor-test-dead-code-hygiene.md`
   - Runs last so cleanup does not delete or consolidate code that active behavior plans still need.

## Merge decision

Keep the remaining spec/plan pairs separate. They touch different review domains and can be implemented with separate Superpowers execution checkpoints. Removed workstreams are intentionally omitted from this roadmap.

- CLI `build` and `python -m duckalog.cli` test drift belongs to the CLI boundary plan; the hygiene plan cleans up remaining stale references that are outside that plan.
- Shared test fixture cleanup belongs to the final hygiene plan after behavior-specific tests exist.
