# Refactor: Consolidate CLI Filesystem Options

## Why

The CLI currently exposes filesystem-related options (protocol, credentials, endpoints, etc.) across multiple commands (`build`, `generate-sql`, `validate`, and possibly others). In several places this leads to:

- Repeated option declarations with the same defaults and help text.
- Duplicated logic for constructing a filesystem object from those options.
- A higher chance that behavior diverges between commands over time.

To improve maintainability and consistency, we want a single, well-defined way for CLI commands to receive filesystem options and construct a filesystem object, while keeping the command-line interface unchanged for users.

## What Changes

- **Introduce a shared filesystem options helper**
  - Define a small helper or Typer callback that:
    - Declares filesystem-related options once (protocol, key, secret, endpoint, region, etc.).
    - Constructs a filesystem object (or `None`) from those options.
    - Stores the constructed filesystem in `typer.Context` (for example, `ctx.obj["filesystem"]`) or passes it into commands via a wrapper.

- **Update CLI commands to use the shared helper**
  - Refactor `build`, `generate-sql`, `validate`, and any other relevant commands to:
    - Remove duplicated filesystem option parameters from their signatures (if they are now captured by the shared helper).
    - Retrieve the filesystem object from `ctx.obj` or the helper’s return value.
  - Ensure command-line flags remain the same (no breaking changes to the CLI surface).

- **Clarify CLI expectations in specs**
  - Update the CLI-related sections in the catalog-build or Python API specs to describe:
    - That filesystem options are shared across commands.
    - That they are parsed and validated in one place.

## Impact

- **Specs updated**
  - `specs/catalog-build/spec.md` and/or `specs/python-api/spec.md`:
    - Add a short description of shared CLI filesystem option handling and its rationale.

- **Implementation**
  - `src/duckalog/cli.py`:
    - New helper and refactored command functions.

- **Non-goals**
  - No new filesystem capabilities or options are added.
  - No change to existing CLI flags or their semantics; the refactor is internal to option declaration and wiring.

## Risks and Trade-offs

- If not done carefully, there is a risk of changing the order or grouping of help text in `--help` output; this is acceptable as long as flags and behavior remain the same.

