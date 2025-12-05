# Implementation Tasks: Refine Documentation After Diátaxis Refactor

## 1. README and Docs Index Strategy

- [x] 1.1 Decide and document the canonical location for the intro + quickstart snippet (e.g. `docs/index.md` or a dedicated shared file).
- [x] 1.2 Refactor `README.md` to:
  - Present a concise product overview.
  - Include a minimal quickstart example.
  - Link prominently to the full documentation site.
- [x] 1.3 Refactor `docs/index.md` to:
  - Reuse the canonical intro + quickstart content (via snippet or synchronized text).
  - Provide an expanded quickstart that links into Tutorials and How‑to Guides.
- [x] 1.4 Document the duplication policy (snippet reuse vs manual sync) so future changes keep README and docs/index aligned.

## 2. Architecture Document Relocation

- [x] 2.1 Move `docs/architecture.md` to `docs/explanation/architecture.md`.
- [x] 2.2 Update `mkdocs.yml` to reference `explanation/architecture.md` under the "Understanding" / Explanation section.
- [x] 2.3 Search and update any internal links that reference the old `architecture.md` path.
- [x] 2.4 Confirm the architecture page still renders correctly and appears in the expected section of the docs.

## 3. Top‑Level Navigation (Top Bar Tabs)

- [x] 3.1 Enable MkDocs Material navigation tabs in `mkdocs.yml` (e.g. `navigation.tabs` and, if useful, `navigation.sections`).
- [x] 3.2 Ensure top‑level `nav` entries correspond to the main chapters:
  - Home
  - Getting Started
  - How‑to Guides
  - Reference
  - Understanding
  - Examples
  - Legacy Guides
  - Security
- [x] 3.3 Verify that these chapters appear in the top bar and that within‑chapter navigation appears in the left sidebar.
- [x] 3.4 Adjust ordering and naming if needed to keep the top bar concise and intuitive.

## 4. Align Original Diátaxis Tasks and Summary

- [x] 4.1 Review `openspec/changes/refactor-documentation-diataxis/tasks.md` and decide whether to:
  - Complete 7.x (README/docs consolidation) and 8.6–8.7 (spell/style checks), or
  - Explicitly mark them as deferred/out‑of‑scope.
- [x] 4.2 Update the checkboxes for those tasks to reflect the decision (completed or intentionally left unchecked).
- [x] 4.3 Update the Implementation Summary in that change to accurately report completed vs remaining tasks and reference this follow‑up change where relevant.

## 5. Validation

- [x] 5.1 Run `mkdocs build` and ensure the site builds without warnings or broken links.
- [x] 5.2 Verify that the README, docs index, and navigation behave as expected when browsing locally.
- [x] 5.3 Optionally solicit quick feedback from at least one user or maintainer on the updated top‑level navigation and entry experience.
