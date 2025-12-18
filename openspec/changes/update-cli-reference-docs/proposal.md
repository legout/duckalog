# Change: Update CLI reference docs to match implementation

## Why
The current CLI reference (`docs/reference/cli.md`) is materially out of sync with the implemented Typer CLI in `src/duckalog/cli.py`:
- It documents flags and output modes that do not exist (e.g. `--format`, `--quiet`, `--color`, `--threads`, `--memory-limit`, `--filesystem`).
- It omits or misrepresents commands that do exist (e.g. `show-paths`, `validate-paths`, `init-env`).
This causes copy/paste failures and user confusion.

## What Changes
- Rewrite `docs/reference/cli.md` to reflect the current CLI surface area and help output.
- Document the shared filesystem options as application-level options (Typer callback) and clearly specify which commands actually use `ctx.obj["filesystem"]`.
- Remove all references to unsupported flags and behaviors.
- Keep the `ui` command documented only at a minimal/accurate level (detailed UI documentation is explicitly out of scope and will be rewritten separately).

## Impact
- Affected documentation:
  - `docs/reference/cli.md`
- No code changes.
- No changes to dashboard/UI docs beyond the minimal/accurate `ui` entry in the CLI reference.
