## Why

When serving the documentation with mkdocs, several warning messages appear indicating broken links:

```
WARNING -  Doc file 'examples/index.md' contains a link 'docs/reference/api.md', but the target 'examples/docs/reference/api.md' is not found among documentation files.
WARNING -  Doc file 'examples/index.md' contains a link 'docs/guides/usage.md', but the target 'examples/docs/guides/usage.md' is not found among documentation files.
WARNING -  Doc file 'examples/index.md' contains a link 'docs/PRD_Spec.md', but the target 'examples/docs/PRD_Spec.md' is not found among documentation files.
```

These warnings indicate that the relative paths in the documentation links are incorrect. Since the `examples/index.md` file is located at `docs/examples/index.md`, links to other files in the `docs/` directory should use relative paths without the `docs/` prefix.

## What Changes

- Fix broken relative paths in `docs/examples/index.md`:
  - Change `docs/reference/api.md` to `../reference/api.md`
  - Change `docs/guides/usage.md` to `../guides/usage.md` 
  - Change `docs/PRD_Spec.md` to `../PRD_Spec.md`
- Verify all links resolve correctly when serving the documentation
- Ensure mkdocs builds without link warnings

## Impact

- Affected capabilities: `docs` (documentation site capability)
- Affected code: `docs/examples/index.md` file
- Users will see clean documentation builds without link warnings
- Documentation navigation will work correctly