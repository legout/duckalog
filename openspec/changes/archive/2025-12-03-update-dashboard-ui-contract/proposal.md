# Change: Update Dashboard UI Contract to Match Current Behavior

## Why

The `dashboard-ui` spec and docs currently state that users can launch the dashboard via the CLI command `duckalog ui ...` and via a Python API. In the current codebase:

- The **Python API** entry point (`duckalog.dashboard.run_dashboard`) is implemented and covered by tests.
- The **CLI `ui` command code exists but is commented out**, so `duckalog ui` is not available to users.

This creates a gap between specification, documentation, and actual behavior. Given that the project is intentionally deferring full UI work for now, we should update the spec and docs so they:

- Require the Python API for launching the dashboard.
- Treat the CLI command as optional/experimental rather than mandatory.

## What Changes

- **Clarify launch requirements in the `dashboard-ui` spec**
  - Modify the `Local Dashboard Launch` requirement so that:
    - The **Python API** launch is REQUIRED.
    - The CLI `duckalog ui ...` command is OPTIONAL: implementations MAY provide it, but the spec no longer requires it for conformance.
  - Update the CLI scenario to explicitly apply only when the `duckalog ui` command is available in a given installation.

- **Align UI docs with current behavior**
  - Update `docs/guides/ui-dashboard.md` so that:
    - The Python API (`run_dashboard`) is presented as the primary, supported entry point.
    - The CLI `duckalog ui` example is marked as optional/experimental, or clearly called out as not available in all builds.

- **Document relationship to archived change**
  - Note that this change refines the behavior originally described in archived change `2025-12-02-add-dashboard-starui`, and explains that the CLI integration is deferred until a future dedicated change re-enables it.

## Impact

- **Specs updated**
  - `specs/dashboard-ui/spec.md`:
    - `Local Dashboard Launch` requirement modified to require Python API and soften CLI requirement.
  - `specs/docs/spec.md`:
    - Updated to reflect that docs must not promise a CLI command that is currently disabled.

- **Implementation**
  - No immediate code changes to CLI behavior; the change brings specs/docs in line with the present implementation instead of changing runtime behavior.

- **Non-goals**
  - This change does not re-enable or implement the `duckalog ui` CLI command.
  - This change does not alter the underlying dashboard behavior, routes, or tests.

## Relation to Previous Changes

- Refines the expectations set by archived change `2025-12-02-add-dashboard-starui`.
- Makes room for a future change (e.g. `restore-dashboard-cli-command`) that can reintroduce and fully test `duckalog ui` when the project is ready to ship the dashboard CLI again.

