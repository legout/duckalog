# Brainstorm: I wanna rebuild/refactor the duckalog ui to use the starhtml framework (https://starhtml.com/ and https://github.com/banditburai/starHTML)

date: 2026-04-30
status: complete

## Problem Statement

Duckalog currently has a dashboard UI built with Litestar controllers, htpy-rendered HTML components, Tailwind/Basecoat styling, Datastar attributes, and a sizable hand-written JavaScript initialization block. The opportunity is not to directly replace that existing UI, but to create a new StarHTML-based dashboard from scratch: a redesigned, Python-first “Catalog Studio” for catalog browsing, catalog editing, data viewing, SQL editing/execution, and catalog run/status workflows.

From the user-facing perspective, the new UI should feel like a richer workspace rather than a direct port of the current dashboard: users should be able to inspect catalogs, edit entries/settings through structured forms, use an expert YAML/JSON editor mode when needed, explore data, and run SQL queries safely.

## Stakeholders

- Duckalog users who need a reliable local/web dashboard for catalog inspection, editing, data exploration, query execution, and catalog runs.
- Power users who want expert YAML/JSON editing without losing validation and safety.
- Duckalog maintainers who want a cleaner Python-first UI architecture with less bespoke JavaScript and fewer stringly Datastar patterns.
- Future contributors who need an approachable dashboard architecture with clear component, route, state, and editor conventions.

## Constraints

### Hard constraints

- Do not implement code during brainstorming.
- The existing dashboard should not be directly replaced as the initial move; the StarHTML UI should be created alongside it.
- The new UI should cover the full product surface over time: catalog viewer/editor, data viewer, SQL editor/executor, and run/status workflows.
- Catalog editing must account for write-path safety: validation, explicit save behavior, and likely preview/diff/backup handling.
- The dashboard must remain compatible with Duckalog's Python packaging and CLI workflow.
- Any StarHTML plan must account for project dependency/runtime constraints and current dashboard entry points.

### Soft constraints

- Prefer a bold redesign rather than a feature-for-feature visual port.
- Prefer Python-first reactive components over hand-written JavaScript.
- Prefer avoiding a frontend build pipeline unless there is a strong reason.
- Prefer staged delivery so the existing dashboard remains usable while the StarHTML UI matures.
- Prefer form/menu-based editing for normal users, with expert YAML/JSON editing for advanced users.

## Ideas Explored

### Approach A: Parallel StarHTML “Catalog Studio”

- Description: Add a new StarHTML app beside the existing dashboard, with a redesigned app shell and staged build-out. The new UI becomes a separate Catalog Studio experience covering catalog/view exploration, structured form editing, expert YAML/JSON editing, query/data workbench, and run/status. The existing dashboard remains stable until the new UI proves itself.
- Pros: Matches the user's desired direction; enables a fresh UX rather than a port; limits risk by keeping the existing dashboard available; creates room for StarHTML-native architecture and interaction patterns; supports staged validation of editor safety and SSE/query flows.
- Cons: Requires maintaining two dashboard experiences during the transition; needs clear CLI/routing/product boundaries; larger overall scope than a refactor; documentation will need to distinguish old vs new UI.
- Risks: Scope creep into a broad dashboard product; write-path/editor complexity; StarHTML maturity/API instability; uncertainty around packaging/static asset behavior and routing integration.

### Approach B: Feature-parity clone first

- Description: Recreate the current dashboard in StarHTML before adding the new editor and redesign capabilities. This treats StarHTML adoption as a framework migration first, then a product redesign.
- Pros: Lower product ambiguity; easier to compare behavior against the existing dashboard; safer for preserving current functionality; useful if maintainers want a measurable parity gate.
- Cons: Delays the desired Catalog Studio experience; may produce a temporary UI that is intentionally not the final design; can spend effort cloning limitations that should be redesigned.
- Risks: Momentum stalls before reaching the editor/workbench vision; the project inherits old UX decisions instead of using StarHTML to simplify the product.

### Approach C: Isolated StarHTML prototype first

- Description: Build an external or internal prototype/spike that validates StarHTML routing, signals, SSE streaming, form editing, expert editor integration, and packaging assumptions before integrating into Duckalog's CLI/package surface.
- Pros: Lowest integration risk; good for learning StarHTML quickly; can test the riskiest pieces before committing product structure; avoids disturbing current code.
- Cons: Delays product integration; prototype code may be discarded; users do not benefit until a later phase.
- Risks: Prototype diverges from real Duckalog constraints; false confidence if it does not exercise actual config models, DuckDB state, and packaging paths.

## Trade-offs Identified

- Fresh product direction vs parity safety: Catalog Studio gets to the desired experience faster, while parity cloning is easier to verify against current behavior.
- Clean StarHTML-native end-state vs incremental risk control: building from scratch enables cleaner architecture, but keeping it parallel is necessary to avoid destabilizing the existing UI.
- Editing power vs safety: form/menu editing is approachable, while expert YAML/JSON editing is powerful but needs validation, preview, and backup protections.
- Reduced JavaScript vs framework maturity risk: StarHTML can remove custom JS and manual Datastar wiring, but it is young/pre-1.0 and needs careful dependency/runtime assessment.
- Broad scope vs staged delivery: the desired UI includes many surfaces, so planning should define milestones that produce useful, testable slices.

## Risks and Unknowns

- Whether StarHTML's app/routing model fits Duckalog's CLI-created dashboard app factory cleanly.
- Whether the new app should be launched via a new command, a CLI flag, a route prefix, or an internal app factory exposed separately.
- Whether StarHTML can be mounted inside or run beside Litestar cleanly if shared serving is desired.
- Whether StarUI components are mature and sufficient for Duckalog's tables, forms, editor shell, buttons/cards/dialogs, and data workbench.
- How to integrate a full-featured YAML/JSON expert editor without introducing an unwanted frontend build system.
- How to preserve comments/formatting when editing YAML/JSON catalog files, if that is a requirement.
- How validation, preview diff, backup, and save/rollback should work for config writes.
- Whether existing tests and docs assume Litestar-specific dashboard behavior.
- How StarHTML serves or bundles Datastar/static assets in packaged Duckalog deployments.
- Whether StarHTML's Python version/dependency constraints match Duckalog's supported environments.

## Open Questions

- What launch surface should the new UI use: new command, `duckalog ui --starhtml`, route prefix, or app factory only?
- What should be the first milestone slice inside Catalog Studio: app shell + catalog explorer, editor safety foundation, or query/data workbench?
- Should expert YAML/JSON editing preserve original formatting/comments, or is normalized output acceptable?
- What validation layer should be authoritative for form edits and expert editor saves?
- Should the new UI initially be documented as experimental/beta?
- What is the minimum acceptable feature set before the new UI is shown to users?

## Chosen Direction

Build a new StarHTML-based UI from scratch as a parallel “Catalog Studio” experience. Do not directly replace the existing dashboard initially. The new UI should rethink the dashboard experience and visual design, covering catalog viewer/editor, data viewer, and SQL editor/executor. Catalog editing should be form/menu-based for normal users, with an expert mode providing a full-featured YAML or JSON editor.

## Decisions Made

- Decision: Use `rebuild-duckalog-ui-starhtml` as the topic slug.
  Rationale: It is lowercase, kebab-case, under 40 characters, and captures the dashboard StarHTML migration topic.
- Decision: Start with external research context before convergence.
  Rationale: The topic depends on a young external framework and current API/maturity trade-offs.
- Decision: Build a new StarHTML UI from scratch rather than directly replacing the existing dashboard.
  Rationale: The user wants a redesigned experience and does not want the current dashboard removed as the first move.
- Decision: Target the full dashboard/product surface rather than only one vertical slice.
  Rationale: The user wants catalog viewer/editor, data viewer, and SQL editor/executor in the new UI.
- Decision: Include both structured editing and expert editing.
  Rationale: Normal users need form/menu-based editing, while advanced users need direct YAML/JSON control.
- Decision: Recommend the parallel StarHTML “Catalog Studio” approach.
  Rationale: It best balances the desired fresh experience with migration safety by keeping the existing dashboard stable while the new UI matures.

## Key Assumptions

- The existing dashboard is the code under `src/duckalog/dashboard/`, currently using Litestar route controllers, htpy components, and manual Datastar/JavaScript behavior.
- StarHTML's main appeal is Python-first reactive UI over Datastar, not merely changing HTML component syntax.
- The new Catalog Studio can coexist with the current dashboard during development and early adoption.
- The plan can sequence the broad product vision into staged, testable milestones.
- Config editing is in scope and will require explicit safety design rather than being treated as ordinary UI state.

## Success Criteria

- A later ExecPlan can define a safe parallel implementation path with explicit scope, non-goals, validation steps, and rollback/escape options.
- The new StarHTML UI has a coherent app shell and visual direction distinct from a direct port of the existing dashboard.
- Users can browse catalogs/views, inspect data, execute SQL, and eventually edit catalog entries/settings through structured forms.
- Expert users can edit YAML/JSON with validation and clear save semantics.
- The existing dashboard remains usable while the new UI is developed and evaluated.
- Manual JavaScript and stringly Datastar patterns are reduced in favor of StarHTML-native components, signals, and SSE patterns.
- The final dashboard architecture is understandable, testable, and packaging-friendly.

## Next Resume Point

- No further brainstorm work is required. Proceed to planning the parallel StarHTML “Catalog Studio” ExecPlan, with special attention to CLI launch surface, editor safety, milestone sequencing, dependency/runtime constraints, and validation strategy.
