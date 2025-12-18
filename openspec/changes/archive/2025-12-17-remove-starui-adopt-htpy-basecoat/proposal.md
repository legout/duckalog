# Change: Remove starui; standardize on htpy + basecoatui components + Tailwind

## Why
Starui is not used in the current implementation and adds dependency/complexity. We already render HTML with htpy and should use basecoatui components first with Tailwind utility classes as fallback. Simplifying the stack aligns code with reality and reduces install size.

## What Changes
- Remove starui from the tech stack and specs.
- Keep htpy for HTML generation; prioritize basecoatui components when available.
- Use Tailwind utility classes as fallback when basecoatui lacks needed components.
- Update specs and docs to reflect the basecoatui-first component approach.
- Adjust optional deps to drop starui (not present in current implementation).

## Component Strategy
- **First Choice**: Use basecoatui components (buttons, cards, dialogs, selects, tabs, toast, etc.)
- **Second Choice**: Custom htpy components styled with Tailwind utility classes
- **Never**: StarUI (not in stack)
- **Offline Requirement**: Bundle basecoat CSS/JS in static/ for production

## Impact
- Specs: `dashboard-ui` - updated to emphasize basecoatui-first
- Code: component references (cleanup only - starui not present)
- Dependencies: remove `starui` from `[project.optional-dependencies].ui` when added (not currently present)
