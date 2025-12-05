# Change: Refine Documentation After Diátaxis Refactor

## Why

The `refactor-documentation-diataxis` change successfully introduced a Diátaxis‑aligned structure, but a few structural and source‑of‑truth questions remain:

1. **README vs docs/index duplication**  
   We want both:
   - A **high‑level intro + quickstart in `README.md`** (for GitHub and the code host).
   - A **high‑level intro + quickstart in `docs/index.md`** (for the documentation site).  
   Today they overlap without a clear duplication or reuse strategy.

2. **Architecture document placement**  
   `architecture.md` lives at the docs root but is conceptually part of the Explanation layer; the Diátaxis design expected it under `explanation/`.

3. **Top‑level navigation UX**  
   We want the **main chapters (Tutorials, How‑to, Reference, Explanation, Examples, etc.) to live in the top bar**, not only as a vertical sidebar. With MkDocs Material this means making better use of top navigation tabs.

4. **Spec/task bookkeeping**  
   The original Diátaxis change’s task list still has unchecked items (README/docs consolidation, spell/style checks) while the summary claims 100 % completion. This makes it harder to see what’s truly done vs intentionally deferred.

This follow‑up focuses on structural and UX refinement, not content rewrites.

## What Changes

### 1. README and Docs Index Strategy

- Define a **clear split of responsibilities**:
  - `README.md`:
    - Concise product overview.
    - Very short “Quickstart” (one or two minimal examples).
    - Clear pointer into the docs site for everything else.
  - `docs/index.md`:
    - Same high‑level overview.
    - **Expanded** quickstart (more narrative and links into Tutorials/How‑tos).
- Avoid divergence by:
  - Introducing a **single canonical intro + quickstart** block (either in `docs/index.md` or a shared snippet).
  - Including it in the other location via `pymdownx.snippets` or an equivalent mechanism, or documenting an explicit duplication policy.
- Document this in the spec so future changes don’t re‑introduce drift between README and docs.

### 2. Move Architecture into Explanation

- Move `docs/architecture.md` → `docs/explanation/architecture.md`.
- Update `mkdocs.yml` to reference the new path under the “Understanding” / Explanation section.
- Update any internal links (markdown and cross‑refs) to the new location.
- Treat `docs/explanation/architecture.md` as the **canonical architecture document** going forward.

### 3. Improve Top‑Level Navigation (Top Bar Tabs)

- Rework MkDocs Material configuration to emphasize **top‑bar chapters**:
  - Enable navigation tabs, for example:
    ```yaml
    theme:
      name: material
      features:
        - navigation.tabs
        - navigation.sections
    ```
  - Ensure top‑level `nav` entries correspond directly to main chapters:
    - `Home`
    - `Getting Started` (tutorials)
    - `How‑to Guides`
    - `Reference`
    - `Understanding`
    - `Examples`
    - `Legacy Guides`
    - `Security`
- Verify that:
  - These chapters appear as tabs in the top bar.
  - The left sidebar is reserved for **within‑chapter** navigation.
- Adjust section names/ordering if needed to keep the top bar clean and readable.

### 4. Align Original Diátaxis Tasks with Reality

- Update `openspec/changes/refactor-documentation-diataxis/tasks.md`:
  - Either complete and check off 7.x (README/docs consolidation) and 8.6–8.7 (spell/style checks), **or**
  - Mark them as intentionally deferred and adjust the Implementation Summary (no longer “84/84 tasks completed”).
- Add a short note in that summary clarifying that this follow‑up change addresses the remaining structural/UX items.

## Impact

- **User experience**: Clearer top‑level navigation and a more coherent entry experience for both GitHub readers (`README.md`) and docs‑site visitors.
- **Maintenance**: A documented source‑of‑truth for intro/quickstart content reduces future duplication and drift.
- **Spec hygiene**: Aligns the Diátaxis spec with actual implementation and outstanding work.

## Non‑Goals

- Rewriting tutorial/how‑to content.
- Changing technical behavior or config schema.
- Automating API docs generation (handled by a separate docstrings/mkdocstrings change).

