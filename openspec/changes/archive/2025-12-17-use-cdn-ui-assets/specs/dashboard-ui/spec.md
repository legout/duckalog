## MODIFIED Requirements

### Requirement: Offline Asset Bundling
All UI assets SHALL be available offline with no CDN dependency in the production configuration, while development and preview configurations MAY temporarily load Tailwind CSS, Basecoat CSS, and Datastar JS from CDNs until bundling is implemented.

#### Scenario: Offline production load
- **WHEN** the dashboard is opened without internet access in its production configuration
- **THEN** all CSS/JS (Datastar runtime and component library styles) are served locally and the UI functions fully.

#### Scenario: Prebuilt CSS
- **WHEN** the package is installed for production use
- **THEN** a precompiled `static/tailwind.css` (including component-library styles) is present; no Node build step runs at user install time.

#### Scenario: CDN development mode
- **WHEN** the dashboard is run in a development or preview configuration without a build pipeline
- **THEN** Tailwind, Basecoat, and Datastar assets MAY be fetched from documented CDNs
- **AND** documentation clearly calls out the online requirement and the future plan to bundle assets for offline use.
