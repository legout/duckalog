## 1. Spec updates
- [ ] 1.1 Review existing path resolution and security requirements in `specs/config/spec.md`
- [ ] 1.2 Identify all places where relative→absolute resolution is described (SQL files, view URIs, attachments)
- [ ] 1.3 Add requirements defining “allowed roots” and the rule that resolved paths MUST stay under at least one allowed root
- [ ] 1.4 Specify error behavior and messaging when a path is outside allowed roots

## 2. Root-based validation design
- [ ] 2.1 Decide how allowed roots are determined (config directory plus any existing config options)
- [ ] 2.2 Design a helper API for root-based path checks (for example, `_is_within_allowed_roots(path, allowed_roots)` or similar)
- [ ] 2.3 Document the behavior for invalid or undecodable paths

## 3. Implementation in path resolution
- [ ] 3.1 Implement the new root-based helper in `path_resolution.py` using `Path.resolve()` and `commonpath` / `relative_to`
- [ ] 3.2 Replace uses of `_is_reasonable_parent_traversal` with the new helper
- [ ] 3.3 Remove or deprecate `_is_reasonable_parent_traversal` and related magic-number thresholds
- [ ] 3.4 Ensure any normalization helpers (`normalize_path_for_sql`, etc.) continue to work with the new checks

## 4. Testing
- [ ] 4.1 Add tests for Unix-style paths that stay within allowed roots
- [ ] 4.2 Add tests for Unix-style paths that attempt to escape via `..` and must be rejected
- [ ] 4.3 Add tests for Windows-style paths (drive letters, UNC paths) both valid and invalid
- [ ] 4.4 Add tests for paths involving symlinks to ensure resolution behaves as expected

## 5. Documentation and communication
- [ ] 5.1 Update documentation to describe the root-based path security model and its rationale
- [ ] 5.2 Add changelog entries highlighting that some previously-accepted paths may now be rejected for safety

