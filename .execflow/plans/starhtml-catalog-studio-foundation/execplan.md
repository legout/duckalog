# Build the StarHTML Catalog Studio foundation beside the existing dashboard

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document must be maintained in accordance with `.execflow/PLANS.md` from the repository root. It is the first concrete implementation plan derived from the completed umbrella brainstorm at `.execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md`; that brainstorm records the product direction, but this ExecPlan is self-contained and describes only the first foundation slice.

## Purpose / Big Picture

After this change, a user can start a new StarHTML-based Duckalog “Catalog Studio” without removing or changing the existing Litestar dashboard. From the command line, `duckalog studio catalog.yaml` starts an ASGI web app on the configured host and port. Visiting the app in a browser shows a redesigned Catalog Studio shell with navigation, the current catalog path, database target, total views, schema count, and placeholders for the later catalog editor, data viewer, and SQL workbench. The existing `duckalog ui` command continues to launch the current Litestar dashboard unchanged.

This first slice matters because it creates the safe parallel foundation for future Catalog Studio ExecPlans. It decides the launch surface, isolates StarHTML imports behind a new module boundary, proves that Duckalog packaging and testing can support the new UI stack, and gives later plans a stable place to add catalog exploration, editing, data browsing, and SQL execution without mixing those features into the old dashboard.

## Progress

- [x] (2026-04-30) Completed the interactive brainstorm and selected the parallel StarHTML “Catalog Studio” direction.
- [x] (2026-04-30) Read `.execflow/PLANS.md`, `.execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md`, `ARCHITECTURE.md`, `pyproject.toml`, `src/duckalog/cli.py`, `src/duckalog/dashboard/app.py`, `src/duckalog/dashboard/state.py`, and representative dashboard tests.
- [x] (2026-04-30) Ran a scout pass and saved repo-grounded context at `.execflow/plans/rebuild-duckalog-ui-starhtml/context.md`.
- [ ] Add StarHTML dependencies to the optional `ui` extra while keeping the existing Litestar dashboard dependencies available.
- [ ] Add a new `duckalog.studio` package with a StarHTML app factory and a small reusable studio context.
- [ ] Add a new `duckalog studio` CLI command that loads a config and starts the new StarHTML app with uvicorn.
- [ ] Add tests proving the app factory renders the shell, the health route works, the new CLI command wires the app, and the old `duckalog ui` command remains intact.
- [ ] Run focused validation commands and update this plan with results.

## Surprises & Discoveries

- Observation: The existing dashboard already has a reusable data boundary in `src/duckalog/dashboard/state.py` named `DashboardContext`, with `get_views()`, `get_view()`, `execute_query()`, and `get_catalog_stats()`.
  Evidence: `DashboardContext` is a dataclass that accepts a validated `Config`, `config_path`, optional `db_path`, and `row_limit`, and its tests in `tests/test_dashboard.py` already verify catalog stats, view listing, single-view lookup, and read-only query rejection.

- Observation: The bundled `src/duckalog/static/datastar.js` exists but the current layout loads Datastar from a CDN in `src/duckalog/dashboard/components/layout.py`.
  Evidence: The scout context notes that `base_layout()` hardcodes a jsDelivr Datastar URL while `src/duckalog/static/README.md` documents local bundling as future work. Catalog Studio should rely on StarHTML’s own Datastar integration rather than trying to share this old asset in the first slice.

- Observation: The current `ui` optional extra already includes web dependencies for the old dashboard.
  Evidence: `pyproject.toml` lists `litestar`, `htpy`, `datastar-py`, `uvicorn[standard]`, `python-multipart`, `msgspec`, and `sniffio` under `[project.optional-dependencies].ui`.

## Decision Log

- Decision: Keep the completed brainstorm as the umbrella architecture artifact and create smaller concrete ExecPlans one at a time.
  Rationale: The brainstorm already records the broad product direction, risks, and follow-up areas. A separate umbrella ExecPlan would mostly duplicate it. Smaller implementation ExecPlans are easier to validate and ticketize.
  Date/Author: 2026-04-30 / planning session

- Decision: The first implementation slice is a foundation/app-shell plan, not an editor, query workbench, or full dashboard replacement.
  Rationale: Catalog editing and SQL streaming are higher-risk features. The project first needs a stable StarHTML module boundary, dependency story, CLI launch surface, and test pattern before adding product behavior.
  Date/Author: 2026-04-30 / planning session

- Decision: Add a new `duckalog studio` CLI command instead of changing `duckalog ui` or adding a flag to it in this first slice.
  Rationale: A new command keeps the existing dashboard behavior stable and makes the new experience explicit. It avoids overloading `duckalog ui` with two framework stacks and gives documentation a clear name for the new product direction.
  Date/Author: 2026-04-30 / planning session

- Decision: Create a new `src/duckalog/studio/` package for StarHTML code rather than placing it under `src/duckalog/dashboard/`.
  Rationale: `dashboard` currently means the Litestar dashboard. A separate package prevents accidental coupling between two UI stacks and makes the future migration or coexistence policy easier to reason about.
  Date/Author: 2026-04-30 / planning session

## Outcomes & Retrospective

No implementation outcomes have been produced yet. At completion, update this section with the exact user-visible behavior, the tests that passed, any dependency or StarHTML API surprises, and the recommended next ExecPlan. The expected next plans are: Catalog Studio explorer, Query Workbench, Catalog Editing Safety and Forms, Expert YAML/JSON Editor, and eventual migration/deprecation policy for the old dashboard if the new Studio becomes the default.

## Context and Orientation

Duckalog is a Python library and CLI for building DuckDB catalogs from YAML or JSON configuration files. A “catalog” is the validated configuration plus the DuckDB database objects created from it, especially views. A “view” is a named SQL query from the config that Duckalog creates inside DuckDB.

The repository currently exposes three main interfaces. The Typer command-line interface lives in `src/duckalog/cli.py`. The Python API and engine live in files such as `src/duckalog/python_api.py`, `src/duckalog/connection.py`, and `src/duckalog/engine.py`. The optional web dashboard lives in `src/duckalog/dashboard/` and is currently built with Litestar, htpy, Datastar, and uvicorn.

The existing dashboard launch path is `duckalog ui` in `src/duckalog/cli.py`. That function imports `create_app` from `duckalog.dashboard`, loads the config with `load_config(config_path)`, calls `src/duckalog/dashboard/app.py:create_app()`, and starts the app with `uvicorn.run()`. The old app factory accepts a validated `Config`, the original config path, optional database path, row limit, and optional static directory. It returns a Litestar ASGI app. ASGI means “Asynchronous Server Gateway Interface”, the Python protocol that uvicorn uses to serve async web applications.

The existing dashboard state boundary is `src/duckalog/dashboard/state.py:DashboardContext`. It is useful because it hides several details from route handlers: it stores the validated `Config`, remembers `config_path`, opens a DuckDB connection lazily, computes catalog stats, lists views, gets one view, and executes read-only SQL in batches. This plan may reuse `DashboardContext` in the first slice to avoid inventing a second state model prematurely. If later editing features need write-specific behavior, a future ExecPlan should introduce a dedicated Studio editing service rather than expanding `DashboardContext` until it mixes read, query, build, and write concerns.

StarHTML is a Python-first framework that builds reactive HTML from Python functions and integrates Datastar-style signals and server-sent updates. A “signal” is reactive browser state that can be bound to HTML attributes or sent back to the server. StarHTML components are Python objects/functions that render HTML, so this project can keep UI construction in Python instead of adding a Node or Vite frontend build. The StarHTML skill used for this repository requires running `starhtml-check <file.py>` after generating StarHTML files; treat that checker as a focused static validation step for StarHTML-specific mistakes.

This first ExecPlan intentionally does not implement catalog editing, expert YAML/JSON editing, SQL execution, data browsing, or run/status streaming. It only creates the foundation those later features will use.

## Plan of Work

Start by adding StarHTML to the optional UI dependency set in `pyproject.toml`. Keep the existing Litestar, htpy, datastar-py, and uvicorn dependencies in the `ui` extra, because `duckalog ui` must keep working. Pin StarHTML narrowly enough to avoid silent pre-1.0 API breakage. Use a constraint such as `starhtml>=0.6,<0.7` unless package inspection during implementation shows a newer compatible range is required. Do not add StarUI in this foundation slice unless the implemented shell truly uses it; StarUI can be evaluated in the explorer or editor plans.

Create a new package directory `src/duckalog/studio/`. Add `src/duckalog/studio/__init__.py`, `src/duckalog/studio/app.py`, `src/duckalog/studio/state.py`, and `src/duckalog/studio/components.py`. The package name “studio” is the stable boundary for the new StarHTML UI. Keep imports from StarHTML inside this package so that the rest of Duckalog does not become coupled to StarHTML APIs.

In `src/duckalog/studio/state.py`, define a small `StudioContext` dataclass. It should accept the same core inputs as the existing dashboard context: `config: Config`, `config_path: str`, `db_path: str | None = None`, and `row_limit: int = 500` or another value passed from the CLI. For this foundation plan, it can delegate read-only summary behavior to `DashboardContext` or copy only the minimal summary logic needed for `get_catalog_stats()` and `get_views()`. Prefer the simpler option that avoids duplicating query execution code. Do not add config write methods in this plan.

In `src/duckalog/studio/components.py`, define Python functions that render the app shell and home content using StarHTML elements. The visible shell should include the name “Duckalog Catalog Studio”, navigation entries for “Overview”, “Catalog”, “Data”, and “SQL”, and clear disabled or “coming soon” states for features not implemented in this slice. The overview content should show the config path, the database path or “in-memory”, total view count, schema count, and a short explanation that this is the new StarHTML-based Studio running alongside the existing dashboard.

In `src/duckalog/studio/app.py`, define `create_app(config: Config, config_path: str, *, db_path: str | None = None, row_limit: int = 500)`. It should create a `StudioContext`, create a StarHTML ASGI app, register a `/health` route, and register the root `/` route. The `/health` route should return a simple successful response that can be tested without a browser. The `/` route should render the Catalog Studio shell. If StarHTML’s documented app creation API in the installed version differs from the examples known at planning time, adapt inside `studio/app.py` only and record the exact discovery in `Surprises & Discoveries`. The expected StarHTML pattern is to import from `starhtml`, create an app and route decorator with a function similar to `app, rt = star_app()`, then decorate route functions with `@rt("/")`.

In `src/duckalog/studio/__init__.py`, export `create_app` and `StudioContext`. This mirrors the existing dashboard package style, where `src/duckalog/dashboard/__init__.py` exports `create_app` and `DashboardContext`.

In `src/duckalog/cli.py`, add a new Typer command named `studio`. Its options should mirror the existing `ui` command where possible: positional `config_path`, `--host`, `--port`, `--row-limit`, `--db`, and `--verbose`. Use a default port that avoids colliding with the old dashboard when a developer runs both. Use `8788` for `duckalog studio` while `duckalog ui` keeps `8787`. The command should configure logging, import `create_app` from `duckalog.studio`, import uvicorn, load the config with `load_config(config_path)`, create the app, print `Starting Catalog Studio at http://{host}:{port}`, print the same non-loopback host warning used by `ui`, and run uvicorn. If StarHTML is missing, fail with a message that tells the user to install `duckalog[ui]`.

Add tests in a new file `tests/test_studio.py`. Do not modify `tests/test_dashboard.py` except if a shared test helper is extracted, and only extract if it reduces duplication without changing old dashboard behavior. The new tests should create a temporary YAML config similar to `_write_config()` in `tests/test_dashboard.py`, load it with `load_config()`, create the Studio app, and verify the root route returns status 200 with visible text such as “Duckalog Catalog Studio”, the view names or counts, and the config path. Add a health-route test. Add a CLI wiring test that patches `duckalog.studio.create_app` and `uvicorn.run`, invokes the Typer app with `CliRunner`, and verifies `studio` loads the config and starts uvicorn without calling the old dashboard factory. If StarHTML apps require a Starlette or httpx test client rather than Litestar’s `TestClient`, keep that test client usage local to `tests/test_studio.py`.

Run `starhtml-check` on any new StarHTML Python files after they exist. Run focused Python tests for the new Studio and existing dashboard. Then run a broader fast test command if time permits. Update this ExecPlan’s `Progress`, `Surprises & Discoveries`, and `Outcomes & Retrospective` with the actual commands and outcomes.

## Concrete Steps

Work from the repository root `/Users/volker/coding/libs/duckalog`.

First, inspect the currently installed or resolvable StarHTML package API before editing generated files. If the package is not installed yet, add the dependency to `pyproject.toml` first and synchronize the environment according to the project’s normal uv workflow. The implementation should prefer direct `pyproject.toml` editing for the dependency declaration, then use the project’s test runner through `uv run`.

After adding dependencies and files, validate imports with:

    uv run python - <<'PY'
    from duckalog.studio import create_app, StudioContext
    print(create_app, StudioContext)
    PY

The expected output is a printed function and class reference, with no ImportError. If this fails because StarHTML is missing from the environment, install the optional UI dependencies in the development environment and rerun. If it fails because the StarHTML API differs, fix only the new `duckalog.studio` package and record the discovery.

Run the StarHTML checker on the generated files:

    starhtml-check src/duckalog/studio/app.py
    starhtml-check src/duckalog/studio/components.py

The expected result is no ERROR findings. Warnings should be reviewed and either fixed or recorded in this plan with a rationale.

Run focused tests:

    uv run pytest tests/test_studio.py tests/test_dashboard.py -q

The expected result is that all new Studio tests pass and the existing dashboard tests still pass. If existing dashboard tests fail because the environment lacks old optional UI dependencies, install `duckalog[ui]` or the equivalent editable optional dependencies and rerun before changing code. Do not solve old dashboard failures by weakening old dashboard behavior.

Manually smoke-test the command with a temporary config. Create a minimal config at `/tmp/duckalog-studio-demo.yaml` if needed:

    cat >/tmp/duckalog-studio-demo.yaml <<'YAML'
    version: 1
    duckdb:
      database: ":memory:"
    views:
      - name: demo_view
        sql: "select 1 as id, 'studio' as label"
        description: "Demo view for Catalog Studio"
    YAML

Start the app:

    uv run duckalog studio /tmp/duckalog-studio-demo.yaml --port 8788

In another terminal or with a browser, verify:

    curl -i http://127.0.0.1:8788/health
    curl -s http://127.0.0.1:8788/ | rg "Duckalog Catalog Studio|demo_view|Total Views|Catalog"

The expected `/health` response is HTTP 200. The expected root page contains “Duckalog Catalog Studio” and enough catalog summary text to prove the loaded config is being used.

## Validation and Acceptance

Acceptance is user-visible. After the implementation, a user who has the optional UI dependencies installed can run `duckalog studio path/to/catalog.yaml`, open the printed URL, and see a StarHTML-rendered Catalog Studio shell. The shell identifies itself as “Duckalog Catalog Studio”, shows the loaded config path, shows whether the database is in-memory or file-backed, shows the total number of configured views and schemas, and includes navigation labels for future Catalog, Data, and SQL sections. The app’s `/health` endpoint returns HTTP 200. The old `duckalog ui path/to/catalog.yaml` command still imports and starts the existing dashboard path.

Automated acceptance requires these test outcomes:

    uv run pytest tests/test_studio.py -q

passes all new Studio tests, and:

    uv run pytest tests/test_dashboard.py -q

still passes, proving the old dashboard was not broken. If the full dashboard test file is too slow or flaky in the local environment, at minimum run the route and CLI-related dashboard tests that prove `create_app()` and `duckalog ui` still work, then record the reduced command and reason in `Surprises & Discoveries`.

StarHTML-specific acceptance requires:

    starhtml-check src/duckalog/studio/app.py
    starhtml-check src/duckalog/studio/components.py

returns no errors. This matters because StarHTML has reactive attribute rules that ordinary Python tests may not catch.

## Idempotence and Recovery

This plan is additive. It adds a new optional dependency, a new `duckalog.studio` package, a new CLI command, and new tests. It should not modify the old dashboard behavior. If the new Studio command fails at runtime, `duckalog ui` should remain available as the fallback.

If adding StarHTML causes dependency resolution conflicts, do not remove Litestar or htpy to make resolution pass. Instead, record the conflict in `Surprises & Discoveries`, pin StarHTML more narrowly if appropriate, or pause and revise the plan. If the StarHTML API differs from the examples, localize the adaptation to `src/duckalog/studio/app.py` and `src/duckalog/studio/components.py`; do not leak StarHTML-specific compatibility logic into `src/duckalog/cli.py`.

If the new CLI command partially starts and leaves a uvicorn process running during manual testing, stop it with Ctrl-C in the terminal where it is running. If tests create temporary files, keep them under pytest’s `tmp_path` so reruns are clean.

If implementation needs to be backed out, remove the new `src/duckalog/studio/` package, remove the `studio` command from `src/duckalog/cli.py`, remove `tests/test_studio.py`, and remove the StarHTML dependency from `pyproject.toml`. The old dashboard should then be exactly the remaining web UI.

## Artifacts and Notes

The completed brainstorm artifact is at:

    .execflow/plans/rebuild-duckalog-ui-starhtml/brainstorm.md

The scout context used to ground this foundation plan is at:

    .execflow/plans/rebuild-duckalog-ui-starhtml/context.md

The current old dashboard app factory has this stable shape:

    def create_app(
        config: "Config",
        config_path: str,
        *,
        db_path: str | None = None,
        row_limit: int = 1000,
        static_dir: str | None = None,
    ) -> Litestar:
        ...

The new Studio app factory should intentionally have a similar caller-facing shape, except it returns a StarHTML/ASGI app instead of a Litestar app:

    def create_app(
        config: "Config",
        config_path: str,
        *,
        db_path: str | None = None,
        row_limit: int = 500,
    ):
        ...

The existing `duckalog ui` command defaults to port `8787`. The new `duckalog studio` command should default to `8788` so both apps can be compared side by side during development.

## Interfaces and Dependencies

The new public module interface is `duckalog.studio`. At the end of this plan, this import must work:

    from duckalog.studio import create_app, StudioContext

`StudioContext` must be a dataclass or similarly simple object with these constructor inputs:

    config: Config
    config_path: str
    db_path: str | None = None
    row_limit: int = 500

It must expose enough read-only data for the app shell to render catalog stats and a small view summary. It must not expose save, write, patch, or expert editor methods in this foundation plan.

`create_app` in `src/duckalog/studio/app.py` must accept:

    config: Config
    config_path: str
    db_path: str | None = None
    row_limit: int = 500

and return an ASGI app suitable for `uvicorn.run()`. It must register at least `/` and `/health`.

`src/duckalog/cli.py` must expose a Typer command named `studio`. It must not change the existing command named `ui`. The command should load configs through the existing `load_config()` function. This preserves the deep configuration boundary: the UI layer receives a validated `Config` and does not need to know about YAML parsing, imports, environment interpolation, or path security.

The optional UI dependencies in `pyproject.toml` must continue to include the old dashboard dependencies and must add StarHTML. Because StarHTML is pre-1.0, use a bounded version range unless implementation evidence shows a different range is necessary. If StarUI is not used in this first shell, leave it out and evaluate it in the explorer or editor ExecPlan.

The next ExecPlan should build on this foundation by adding the first real Studio product slice. The recommended next slice is Catalog Studio Explorer: navigable catalog overview, views explorer, and view detail pages in the new StarHTML shell. The query workbench and catalog editor should remain separate plans because streaming SQL execution and config-file writes have different risks and validation needs.

## Revision Note

2026-04-30: Initial ExecPlan created from the completed StarHTML Catalog Studio brainstorm and codebase scout. The plan deliberately scopes the first implementation to a parallel app foundation, launch command, shell, and validation pattern so later ExecPlans can add explorer, query, and editor features without destabilizing the existing dashboard.
