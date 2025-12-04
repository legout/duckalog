# Design: Remote Config Imports

## Goals
- Extend the existing `imports` mechanism to support remote configuration files.
- Reuse the remote loading infrastructure so authentication, timeouts, and logging are handled consistently.
- Keep semantics aligned with local imports: same merge strategy, uniqueness rules, and cycle detection.

## High-Level Approach

1. **Recognize remote import paths**
   - Treat any `imports` entry whose value is recognized by `is_remote_uri()` as a remote import.
   - For remote imports, skip local path resolution and path-security checks that are specific to the filesystem; rely on remote-config security instead.

2. **Fetch + parse, then merge**
   - For a remote import URI:
     - Use `fetch_remote_content()` (or `load_config_from_uri`) to retrieve and parse the remote config into a dictionary or `Config` instance.
     - Apply the same environment-variable interpolation used for local configs.
     - Feed the resulting structure into the same deep-merge and uniqueness-validation pipeline defined by `add-config-imports`.

3. **Cycles and caching**
   - Maintain the same import context data structure used for local imports (visited set, import stack, cache).
   - Use a normalized representation of the remote URI as the key in `visited` / cache so that cycles involving remote files are detected.

4. **Error handling and logging**
   - On fetch or parse failure, raise a configuration error with:
     - The remote URI.
     - The attempted operation (e.g. fetch, parse, validate).
     - The underlying exception chained via `raise ... from exc`.
   - Log remote import operations at INFO/DEBUG level using existing logging utilities, without leaking sensitive credentials.

## Out of Scope
- New URI schemes or storage backends beyond those already supported by the remote loader.
- Any changes to the core merge semantics or uniqueness rules.
- Advanced import syntaxes (selective imports, overrides, globbing), which are covered by separate changes.
