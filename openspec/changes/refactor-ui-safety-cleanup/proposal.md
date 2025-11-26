# Change: Refactor UI safety and cleanup

## Why
Beyond the config decode crash, the UI has additional robustness gaps and over-complexity: query validation is brittle, background task results can leak memory, config writing logic is over-engineered, and missing static assets fail silently. Addressing these will make the UI safer and simpler.

## What Changes
- Harden query validation to correctly detect multi-statements/DDL without naive string checks.
- Cap/clean background task result storage to avoid unbounded growth.
- Simplify config write helpers (one atomic writer) and keep yaml/json handling minimal.
- Log a warning when static assets are missing instead of silently skipping.

## Impact
- Affected capability: ui
- Code: `src/duckalog/ui.py` (query validation, task store, config writing, static mount logging)
