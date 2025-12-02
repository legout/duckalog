# Change: Clarify and Align Python Version Support

## Why

There is currently drift between:

- Project metadata and tooling (for example, `pyproject.toml` `requires-python`).
- Documentation (`project.md`, README, and other docs referencing 3.9–3.12).
- Typing style and code (now using PEP 604 unions and built-in generics, with a minimum target of Python 3.12+ implied by `modernize-python-typing`).

This can confuse users and contributors:

- Users on Python 3.9–3.11 may see docs implying support but be blocked by packaging metadata or hit syntax errors.
- Contributors may be unsure whether they can rely on Python 3.12+ features in new code.

We need a single, explicit statement of supported Python versions, and we need metadata, specs, and docs to match that statement.

## What Changes

- **Decide and document the minimum supported Python version**
  - Adopt Python 3.12+ as the minimum supported version, consistent with:
    - The `modernize-python-typing` change (PEP 604 unions, built-in generics).
    - Current code that uses these features without compatibility shims.

- **Align packaging metadata**
  - Update `pyproject.toml`:
    - Set `requires-python = ">=3.12"`.
    - Update Trove classifiers to only include supported versions (for example, 3.12, 3.13).

- **Align specs and documentation**
  - Update:
    - `openspec/project.md` (Tech Stack section) to reflect Python 3.12+.
    - `specs/package-metadata/spec.md` and `specs/docs/spec.md` to state the supported versions and rationale.
    - README and any other user-facing docs that currently mention 3.9–3.12.

- **Clarify contributor guidance**
  - Ensure contribution guidelines (including any references in specs) explicitly allow and encourage:
    - PEP 604 unions (`str | int`).
    - Built-in generics (`list[int]`, `dict[str, Any]`).
    - Other Python 3.12+ idioms that the project wants to rely on.

## Impact

- **Specs updated**
  - `specs/package-metadata/spec.md`:
    - Explicit supported version range (>=3.12).
    - Classifier expectations for releases.
  - `specs/docs/spec.md`:
    - Documentation and examples updated to mention Python 3.12+.

- **Implementation**
  - `pyproject.toml` metadata updated to match the decision.
  - CI configuration updated to run tests on supported Python versions (for example, 3.12 and 3.13).

- **Non-goals**
  - No attempt is made to restore support for Python 3.9–3.11; this is a forward-looking clarification.

## Risks and Trade-offs

- Some users on older Python versions will no longer be able to run Duckalog without upgrading their environment. Given the use of modern typing conventions and the project’s target audience, this is an acceptable trade-off for simplicity and clarity.

