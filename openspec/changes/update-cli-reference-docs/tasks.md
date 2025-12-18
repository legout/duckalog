## 1. Implementation
- [ ] 1.1 Inventory current CLI commands/options from `src/duckalog/cli.py`
- [ ] 1.2 Rewrite `docs/reference/cli.md` to match the current CLI:
  - Global filesystem options (Typer callback)
  - Commands: `version`, `build`, `validate`, `generate-sql`, `show-imports`, `show-paths`, `validate-paths`, `query`, `init`, `init-env`, `ui`
- [ ] 1.3 Remove unsupported flags/claims from the CLI reference (e.g. JSON output via `--format`, color, quiet, threads/memory flags)
- [ ] 1.4 Ensure examples use only supported flags and reflect current behavior (e.g. `query` uses `--catalog/-c`)

## 2. Verification
- [ ] 2.1 Run `mkdocs build` and fix any doc build issues
- [ ] 2.2 Spot-check CLI doc accuracy by comparing against `duckalog --help` and `duckalog <cmd> --help`
