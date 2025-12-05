# Proposal: Extend Config Imports with Advanced Options

## Why
The core `add-config-imports` change provides a simple, robust mechanism for importing and merging
configuration files. As projects grow, teams may want more control over **which** sections are
imported, **how** conflicts are resolved, and **which files** are included via patterns. Without
advanced options, catalogs might accumulate many small import files or require boilerplate to
express common patterns.

## What Changes
This change proposes advanced options on top of the core imports feature:

1. **Selective imports**
   - Allow users to specify imports per section (e.g. `views`, `duckdb`, `attachments`) instead of
     importing entire files wholesale.

2. **Import override behavior**
   - Provide a way to mark an import as non-overriding or explicitly overriding, to control how
     imported values interact with the main config or later imports.

3. **Glob and exclude patterns**
   - Allow pattern-based imports so that multiple files (e.g. all view fragments in a directory)
     can be included with a single entry, with optional excludes.

## Out of Scope
- Introducing any new storage backends or remote schemes (covered by remote-import changes).
- Changing the default deep-merge semantics defined by `add-config-imports`.
- Modifying CLI behavior beyond what is necessary to expose these options.

## Impact
- **Flexibility**: Teams can organize configuration files more naturally (e.g. one view per file)
  without verbose import lists.
- **Control**: Override semantics can be made explicit where configuration layers are complex
  (base → environment → local overrides).
- **Maintainability**: Examples and documentation can illustrate common import patterns without
  introducing workarounds or external pre-processing steps.
