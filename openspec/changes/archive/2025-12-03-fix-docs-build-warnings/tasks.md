## 1. Implementation
- [x] 1.1 Classify each warned-about documentation file as "keep and include in nav" vs "remove or archive", and document the decision
- [x] 1.2 Update `specs/docs/spec.md` to clarify navigation and API-doc quality requirements for core guides, examples, and API reference pages
- [x] 1.3 Update `mkdocs.yml` navigation to include all kept pages (Security, path guides, examples, API reference) without introducing new warnings
- [x] 1.4 Fix broken relative links in `docs/examples/duckdb-secrets.md` and audit similar links in related docs
- [x] 1.5 Add or refine type annotations in `src/duckalog/python_api.py` and `src/duckalog/config/loader.py` to eliminate mkdocstrings/Griffe warnings
- [x] 1.6 Run `mkdocs build` and `openspec validate fix-docs-build-warnings --strict` to confirm warnings are resolved

