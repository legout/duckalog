## 1. Import Graph Command
- [x] 1.1 Design the UX for an import visualization command (e.g. `duckalog show-imports <config>`).
- [x] 1.2 Implement the command to load the root config, resolve imports (without building a catalog), and print the import tree/graph.
- [x] 1.3 Add tests that verify correct output for simple and nested import setups, including cycles.

## 2. Merged Config Preview
- [x] 2.1 Add a CLI option or subcommand to output the fully merged config (or selected sections) after imports are resolved.
- [x] 2.2 Ensure sensitive values continue to be handled according to existing logging/printing guidelines.
- [x] 2.3 Add tests that confirm the preview matches the configuration that would be used for a build.

## 3. Import Diagnostics
- [x] 3.1 Optionally extend the CLI to highlight duplicate names, deep import chains, or potential performance issues.
- [x] 3.2 Provide clear, human-readable output suitable for CI logs.

## 4. Documentation
- [x] 4.1 Update CLI documentation to describe the new commands/options and show example invocations.
- [x] 4.2 Add a short troubleshooting section that explains how to use these tools when import-related errors occur.
