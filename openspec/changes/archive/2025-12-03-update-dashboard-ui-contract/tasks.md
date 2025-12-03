## 1. Spec alignment
- [x] 1.1 Review `specs/dashboard-ui/spec.md` for all CLI-related requirements and scenarios
- [x] 1.2 Add a `## MODIFIED Requirements` section clarifying that Python API launch is required and CLI launch is optional
- [x] 1.3 Update the CLI launch scenario to explicitly apply only when the `duckalog ui` command is available

## 2. Documentation updates
- [x] 2.1 Update `docs/guides/ui-dashboard.md` to present the Python API as the primary supported entry point
- [x] 2.2 Mark the `duckalog ui` example as optional/experimental or note that it may not be available in all builds
- [x] 2.3 Ensure docs no longer imply that `duckalog ui` is universally available today

## 3. Validation
- [x] 3.1 Run `openspec validate update-dashboard-ui-contract --strict`
- [x] 3.2 Manually confirm that specs, docs, and current behavior are aligned
