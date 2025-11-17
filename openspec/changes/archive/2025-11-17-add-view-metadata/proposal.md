## Why

The PRD specifies optional `description` and `tags` fields on views, which are useful for documentation, discovery, and tooling, but this metadata behavior is not yet captured in the config spec.

Explicitly specifying how view metadata is represented and preserved makes it easier for downstream tools (e.g., docs generation) to rely on it.

## What Changes

- Extend the `config` capability spec to include optional `description` and `tags` fields on view definitions.
- Define expectations around how these fields are validated and preserved, even if they do not directly affect generated SQL.

## Impact

- Encourages consistent use of view metadata across configs.
- Enables future tooling (e.g. documentation generators) to rely on structured metadata without breaking existing configs.
- Keeps metadata concerns clearly separated from SQL generation and engine behavior.

