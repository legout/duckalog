# Design: Dashboard UI Contract Update

## Goals

- Remove the spec/docs gap around the `duckalog ui` CLI command.
- Keep the Python API (`run_dashboard`) as the required way to launch the dashboard.
- Treat the CLI command as an optional feature that can be restored in a future change.

## Spec adjustments

### Dashboard launch requirement

Current `Requirement: Local Dashboard Launch` in `specs/dashboard-ui/spec.md` implies that both:

- CLI launch (`duckalog ui catalog.yaml`), and
- Python API launch

are mandatory. We will:

- Clarify that:
  - The **Python API launch** MUST be provided.
  - The **CLI `duckalog ui` command** MAY be provided; if present, it MUST behave as described in the CLI scenario.
- Update the CLI scenario’s wording to explicitly state that it applies only in installations where `duckalog ui` is enabled.

### Docs requirement

The docs spec will be adjusted so that:

- The dashboard guide MUST document the Python API launch.
- The dashboard guide MAY document `duckalog ui`, but must clearly indicate that it is optional/experimental and not guaranteed to be available in every installation.

## Behavior after this change

- Current behavior (Python API only, CLI command commented out) will fully satisfy the updated `dashboard-ui` spec.
- Users reading the docs will not be misled into expecting a `duckalog ui` command that is not wired up yet.
- A future change can re-enable `duckalog ui`, add CLI tests, and then tighten the spec again if desired.

