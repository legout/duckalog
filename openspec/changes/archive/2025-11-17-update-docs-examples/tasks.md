## 1. Improve documentation depth and examples

- [x] 1.1 Expand `docs/index.md` to include a short, narrative quickstart that
      walks through a realistic use case end-to-end (config creation, CLI
      build, Python usage).
- [x] 1.2 Extend `docs/guides/usage.md` with:
      - A section on common configuration patterns (Parquet-only, attachments
        only, Iceberg-only).
      - A short troubleshooting section for typical errors (invalid config,
        missing env vars, missing attachments/catalogs).
- [x] 1.3 Add at least one additional example config under `docs/` (or a
      dedicated `docs/examples/` folder) that demonstrates a multi-source
      setup, and link to it from the user guide.
- [x] 1.4 Ensure the README remains consistent with the updated docs (links,
      examples, and terminology) and adjust references as needed.
- [x] 1.5 Validate that `mkdocs build` succeeds and that the navigation still
      exposes quickstart, user guide, and API reference as expected.

