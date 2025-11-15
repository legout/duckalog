## 1. View metadata fields

- [x] 1.1 Extend the `ViewConfig` model to include optional `description` and `tags: List[str]` fields if not already present.
- [x] 1.2 Ensure config validation accepts these fields without affecting view SQL generation.
- [x] 1.3 Add tests that confirm metadata is loaded and preserved through config parsing.
