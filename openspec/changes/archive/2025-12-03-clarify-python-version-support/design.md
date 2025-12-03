# Design: Python Version Support Policy

## Goals

- Provide a clear, enforceable policy for which Python versions Duckalog supports.
- Align metadata, docs, and code-style expectations with that policy.

## Chosen policy

- Minimum supported Python version: **3.12**.
- Rationale:
  - Code already uses Python 3.12+ typing features (PEP 604 unions, built-in generics).
  - Project conventions explicitly prefer these patterns.
  - Supporting older Python versions would require shims and/or more complex typing patterns, which is not a priority for this library.

## Enforcement points

- **Packaging (`pyproject.toml`)**
  - `requires-python = ">=3.12"`.
  - Trove classifiers: include 3.12 and any newer versions tested in CI.

- **CI**
  - Run tests on at least the minimum supported version and one newer version (for example, 3.12 and 3.13).

- **Specs and docs**
  - Tech Stack sections reflect 3.12+.
  - Examples and instructions do not mention older versions as supported.

## Developer experience

- Contributors can:
  - Use PEP 604 unions and built-in generics everywhere.
  - Avoid backported or compatibility-bridging code for older versions.

If future needs arise to support additional Python versions, they will be handled via a new spec change that revisits this policy.

