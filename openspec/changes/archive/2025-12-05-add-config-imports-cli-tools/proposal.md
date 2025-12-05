# Proposal: Add CLI Tooling for Config Imports

## Why
With `add-config-imports` (and its follow-ups), Duckalog configs can become composed from many
files. Users and operators will benefit from CLI tooling that can:

- Visualize the import graph (which files import which others).
- Show the fully merged configuration for debugging.
- Detect cycles or problematic patterns before running a full build.

Without such tools, troubleshooting import-related issues may require manual inspection of many
files and ad-hoc scripts.

## What Changes
This change proposes to add CLI commands that expose import-related information, such as:

1. **Import graph visualization**
   - A command (for example, `duckalog show-imports`) that displays the import tree/graph for a
     given root config file.

2. **Merged config preview**
   - A mode to output the fully merged configuration (or a summary of it) without building a
     catalog, to aid debugging and reviews.

3. **Validation helpers**
   - Optional flags or subcommands to highlight duplicate names, deep import chains, and other
     potential issues discovered during import processing.

## Out of Scope
- Any changes to the underlying import semantics or merge behavior.
- Adding new configuration fields; this change focuses only on CLI behavior and diagnostics.

## Impact
- **Debuggability**: Users can quickly understand how a complex, imported configuration is
  composed and where conflicts arise.
- **Operational clarity**: CI pipelines and operational tooling can use CLI commands to validate
  and visualize configs prior to catalog builds.
