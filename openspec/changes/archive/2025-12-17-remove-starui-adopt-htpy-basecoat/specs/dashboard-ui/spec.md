## MODIFIED Requirements

### Requirement: Litestar + Datastar Application Stack
The dashboard SHALL run on Litestar with Datastar for reactive updates and a typed HTML helper (htpy) for type-safe HTML composition.

#### Scenario: Application initialization
- **GIVEN** the UI extras are installed
- **WHEN** `create_app(context)` is called
- **THEN** a Litestar application is returned with registered routes, middleware, and dependency injection wired for `DashboardContext`.

#### Scenario: Static file serving
- **GIVEN** the app is running
- **WHEN** a request is made to `/static/*`
- **THEN** assets (prebuilt CSS/JS/fonts) are served from the packaged `duckalog/static/` directory without requiring internet access.

#### Scenario: Dependency injection
- **GIVEN** a route declares `DashboardContext`
- **WHEN** the handler executes
- **THEN** Litestar injects the shared context instance for use in the handler.

### Requirement: Type-Safe HTML Generation
The dashboard SHALL generate HTML via htpy (or equivalent typed helpers) with Datastar attributes for reactivity.

#### Scenario: Component rendering
- **WHEN** a page is rendered
- **THEN** HTML is produced by Python functions with type hints
- **AND** Datastar attributes (`data-bind`, `data-on`, `data-signal`) are present where interactivity is required.

#### Scenario: Composition
- **WHEN** building complex layouts
- **THEN** smaller typed components are composed without raw string templates.

### Requirement: Component and Styling Priority (Basecoatui First)
The dashboard SHALL prefer basecoatui components for UI and styling; it SHALL use Tailwind utility classes and simple htpy components when basecoatui does not provide the needed element or pattern; starui MUST NOT be a runtime dependency. All chosen components MUST be shipped for offline use.

#### Scenario: Basecoatui by default
- **WHEN** implementing a UI element that exists in basecoatui
- **THEN** the basecoatui variant is used (including its CSS/JS) and bundled in `static/`.

#### Scenario: Custom htpy components when needed
- **WHEN** basecoatui lacks the needed pattern or accessibility baseline
- **THEN** a small htpy-based component is created and styled with Basecoat/Tailwind classes
- **AND** its styles and behavior are bundled in `static/`.

#### Scenario: Tailwind fallback only
- **WHEN** no basecoatui component fits the need
- **THEN** Tailwind utility classes are used to compose the UI with htpy
- **AND** the compiled Tailwind CSS is shipped in `static/tailwind.css` with no CDN requirement for production.
