# Design: Shared CLI Filesystem Options

## Goals

- Declare filesystem-related CLI options once and reuse them across commands.
- Construct filesystem objects in a single place with consistent defaults and validation.

## High-level approach

- Use either:
  - A Typer `@app.callback` that declares filesystem options and populates `ctx.obj["filesystem"]`, or
  - A decorator that wraps command functions and injects a `filesystem` argument.

The exact approach will be chosen based on how well it fits the current `cli.py` structure, but the design goal is to remove duplicated option lists from individual commands.

## Behavior

- CLI options for filesystem configuration (protocol, credentials, endpoints, etc.) remain the same for users.
- The helper:
  - Normalizes options into a consistent representation.
  - Constructs a filesystem object using existing utility functions.
  - Makes that filesystem available to commands without repeated boilerplate.

## Testing

- Add tests (or extend existing CLI tests) to verify:
  - `duckalog build`, `duckalog generate-sql`, and `duckalog validate` accept the same filesystem-related flags as before.
  - Filesystem creation behavior is identical before and after the refactor.

