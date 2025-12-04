## 1. Selective Imports
- [ ] 1.1 Design and implement syntax for section-specific imports (for example, `imports.views`, `imports.duckdb`, or an equivalent)
- [ ] 1.2 Extend the import loader to apply selective imports only to the targeted sections.
- [ ] 1.3 Add validation to ensure that selective imports do not conflict with global imports in unexpected ways.

## 2. Import Override Semantics
- [ ] 2.1 Introduce an optional `override` flag (or equivalent) that can be attached to import entries.
- [ ] 2.2 Define how `override=false` behaves relative to main-file values and other imports (e.g. imports that only fill in missing fields).
- [ ] 2.3 Add tests that cover combinations of overriding and non-overriding imports.

## 3. Glob and Exclude Patterns
- [ ] 3.1 Define a syntax for glob-based imports, such as `imports: ["./views/*.yaml"]` or a nested form.
- [ ] 3.2 Support exclude patterns so that certain files can be omitted (for example, `"!./views/legacy.yaml"`).
- [ ] 3.3 Implement pattern resolution using standard library helpers and ensure platform compatibility.
- [ ] 3.4 Add tests to cover multiple overlapping patterns and edge cases.

## 4. Documentation and Examples
- [ ] 4.1 Update configuration documentation to describe selective imports, override flags, and glob patterns.
- [ ] 4.2 Add at least one example catalog that demonstrates these advanced options in a realistic scenario.
- [ ] 4.3 Ensure the examples library and migration guides reference these features as optional, advanced patterns.
