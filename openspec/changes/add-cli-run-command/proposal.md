# Change: Add CLI Run Command for Config-Driven Workflow

## Why
The current CLI only supports full catalog builds via the `build` command. Users need a primary entry point that handles the config-driven workflow with smart connection management and incremental updates.

## What Changes
- Add new `run` command as the primary CLI entry point
- Update existing `build` command to be explicit full rebuild
- Add Python API function for smart catalog connection
- Update help text and documentation to reflect new workflow
- Add deprecation warnings for direct `build_catalog` function usage

## Impact
- Affected specs: cli
- Affected code: src/duckalog/cli.py, src/duckalog/python_api.py
- User experience: `duckalog run config.yaml` becomes default behavior