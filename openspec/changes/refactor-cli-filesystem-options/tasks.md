## 1. Spec updates
- [ ] 1.1 Update CLI-related sections in `specs/catalog-build/spec.md` or `specs/python-api/spec.md` to mention shared filesystem options handling

## 2. Helper design and implementation
- [ ] 2.1 Design a shared filesystem options helper or Typer callback signature
- [ ] 2.2 Implement the helper in `cli.py` (or a small helper module)
- [ ] 2.3 Ensure the helper constructs a filesystem object (or `None`) consistently

## 3. Command refactors
- [ ] 3.1 Refactor `build` command to use the shared helper
- [ ] 3.2 Refactor `generate-sql` command to use the shared helper
- [ ] 3.3 Refactor `validate` command (and any other commands using filesystem options) to use the shared helper
- [ ] 3.4 Verify that CLI flags remain unchanged and behavior is consistent

