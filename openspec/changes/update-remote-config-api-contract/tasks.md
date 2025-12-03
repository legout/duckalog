## 1. Spec updates
- [x] 1.1 Review current config loading behavior in `specs/config/spec.md`
- [x] 1.2 Add a subsection documenting `load_config`, `_load_config_from_local_file`, and `load_config_from_uri`
- [x] 1.3 Define dispatch rules for local vs remote paths and URIs
- [x] 1.4 Document expected `filesystem` interface and error semantics

## 2. Implementation alignment
- [x] 2.1 Introduce `_load_config_from_local_file` helper in `config.py` (if missing)
- [x] 2.2 Export `load_config_from_uri` from `duckalog.config`
- [x] 2.3 Update `load_config` to route to `_load_config_from_local_file` or `load_config_from_uri` per spec
- [x] 2.4 Ensure remote config behavior in `remote_config.py` aligns with the spec

## 3. Testing
- [x] 3.1 Add tests that patch `_load_config_from_local_file` to verify delegation for local paths
- [x] 3.2 Add tests that patch `load_config_from_uri` to verify delegation for remote URIs
- [x] 3.3 Add tests for `filesystem` validation: valid objects, missing methods, and `None`
- [x] 3.4 Run existing remote-config and attachment hierarchy tests to ensure behavior is preserved or clarified

