# Migrate Duckalog documentation to Zensical and refresh the content system

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document must be maintained according to `.execflow/PLANS.md`. A future implementer should be able to start from this single file, the current repository tree, and no prior conversation.

## Purpose / Big Picture

After this work, Duckalog will have a comprehensive documentation site built with Zensical, a modern static site generator from the creators of Material for MkDocs. Users will be able to open the documentation and find a clear learning path, task-focused guides, accurate reference pages, explanations, examples, dashboard docs, security guidance, and migration notes. Maintainers will be able to run one documented Zensical build command, rely on a single anti-duplication policy for shared README/docs content, and convert the existing broad docs tree into a coherent site without guessing which page is canonical.

The visible outcome is a Zensical-powered static site generated from `docs/` into `site/`, with `zensical.toml` replacing `mkdocs.yml` as the canonical site configuration, CI running a Zensical build, and refreshed Markdown pages that preserve existing useful content while removing or redirecting stale legacy duplicates.

## Progress

- [x] (2026-04-29) Created the required brainstorm at `.execflow/plans/duckalog-docs-zensical-framework/brainstorm.md` and recorded the user-selected direction: full Zensical migration plus content refresh.
- [x] (2026-04-29) Read `.execflow/PLANS.md`, `.execflow/AGENTS.md`, `mkdocs.yml`, `pyproject.toml`, `README.md`, `docs/index.md`, `docs/documentation-duplication-policy.md`, `.github/workflows/tests.yml`, and current Zensical documentation for setup, navigation, extensions, repository integration, customization, Markdown authoring, and mkdocstrings support.
- [x] (2026-04-29) Updated `ARCHITECTURE.md` to include the current documentation layer, MkDocs build flow, snippet policy, and documentation complexity risks.
- [x] (2026-04-29) Drafted this ExecPlan at `.execflow/plans/duckalog-docs-zensical-framework/execplan.md`.
- [ ] Add Zensical to the project development toolchain and create a first `zensical.toml` that can build the existing docs with minimal content changes.
- [ ] Audit and consolidate the documentation information architecture, especially legacy guide pages and duplicated path-resolution pages.
- [ ] Refresh the user-facing learning path, examples, how-to guides, and docs landing pages for current Duckalog behavior.
- [ ] Refresh the reference, API, dashboard, architecture, security, and migration docs, including mkdocstrings rendering under Zensical.
- [ ] Switch CI and maintainer documentation from MkDocs to Zensical, remove obsolete MkDocs-only dependencies when safe, and document rollback.

## Surprises & Discoveries

- Observation: Zensical can read `mkdocs.yml` as a transition mechanism, but its own documentation recommends `zensical.toml` for new and migrated projects.
  Evidence: Zensical setup docs state that `mkdocs.yml` is supported for transition, while `zensical.toml` is the recommended project configuration.
- Observation: Zensical supports Python Markdown and Python Markdown Extensions, including snippets and SuperFences, which lowers the risk of preserving the current `--8<--` snippet include and Mermaid diagram setup.
  Evidence: Zensical extension docs list Snippets and SuperFences as supported and show TOML configuration for `pymdownx.superfences` with a Mermaid custom fence.
- Observation: The two current snippet include paths are intentionally different because `README.md` is rooted at the repository root while `docs/index.md` is rooted in the docs source tree.
  Evidence: `README.md` contains `--8<-- "docs/_snippets/intro-quickstart.md"`; `docs/index.md` contains `--8<-- "_snippets/intro-quickstart.md"`.
- Observation: Zensical provides preliminary mkdocstrings support, but not full feature parity.
  Evidence: Zensical mkdocstrings docs say support exists as of 0.0.11 and specifically note preliminary support with missing backlinks.
- Observation: The current docs tree has 52 Markdown files and a duplication hotspot around path-resolution documentation.
  Evidence: `find docs -maxdepth 3 -type f` shows 52 Markdown files, including `docs/path-resolution.md`, `docs/best-practices-path-management.md`, `docs/configuration-path-examples.md`, `docs/migration-path-resolution.md`, `docs/path-resolution-examples.md`, `docs/guides/path-resolution.md`, and `docs/examples/path-resolution-examples.md`.
- Observation: Documentation CI currently validates MkDocs, not Zensical, and docs-only changes do not trigger that workflow.
  Evidence: `.github/workflows/tests.yml` installs `mkdocs mkdocs-material mkdocstrings[python]` and runs `mkdocs build --clean --strict` in the `documentation-build` job, while the workflow `paths-ignore` excludes `**.md` and `docs/**` for push and pull requests.

## Decision Log

- Decision: Implement a full Zensical migration rather than only a content refresh or a Zensical-ready compatibility pass.
  Rationale: The user explicitly selected “Full Zensical migration plus content refresh” during the brainstorm.
  Date/Author: 2026-04-29 / planning agent
- Decision: Use `zensical.toml` as the target canonical configuration instead of relying permanently on Zensical's ability to read `mkdocs.yml`.
  Rationale: Zensical supports `mkdocs.yml` for transition, but the requested end state is a Zensical framework migration and Zensical recommends TOML as the native configuration.
  Date/Author: 2026-04-29 / planning agent
- Decision: Keep the current snippet-based README/docs content policy unless the first Zensical build proves it cannot be preserved.
  Rationale: `docs/_snippets/intro-quickstart.md` is a useful deep boundary that prevents content drift between `README.md` and `docs/index.md`, and Zensical documents support for Python Markdown snippets.
  Date/Author: 2026-04-29 / planning agent
- Decision: Treat MkDocs removal as a final migration step, not a first step.
  Rationale: A temporary parallel build gives a safe comparison point. The end state can still remove obsolete MkDocs dependencies after Zensical renders the site and API docs acceptably.
  Date/Author: 2026-04-29 / planning agent

## Outcomes & Retrospective

No implementation outcomes have been recorded yet. When the first Zensical build succeeds, record the build command and any content changes required to make it work. At the end of the migration, compare the final site against the current MkDocs navigation and list which legacy pages were consolidated, redirected, or intentionally retained.

## Context and Orientation

Duckalog is a Python package and CLI for building DuckDB catalogs from declarative YAML or JSON configuration files. The library code lives under `src/duckalog/`, tests live under `tests/`, and user documentation lives under `docs/`. The current documentation site is configured by `mkdocs.yml` at the repository root and built in GitHub Actions by the `documentation-build` job in `.github/workflows/tests.yml`.

Zensical is the target static site generator. A static site generator reads Markdown files and a configuration file, then produces plain HTML, CSS, and JavaScript into a directory such as `site/`. Zensical can read `mkdocs.yml` during migration, but the target configuration in this plan is a native `zensical.toml` file.

The current docs already use a learning/task/reference/explanation/examples structure:

    docs/
    ├── _snippets/intro-quickstart.md
    ├── tutorials/
    ├── how-to/
    ├── reference/
    ├── explanation/
    ├── examples/
    ├── dashboard/
    ├── architecture/
    ├── guides/
    ├── path-resolution.md
    ├── best-practices-path-management.md
    ├── configuration-path-examples.md
    ├── migration-path-resolution.md
    ├── path-resolution-examples.md
    ├── migration-refactor-config-architecture.md
    ├── dependency-injection-guide.md
    ├── documentation-duplication-policy.md
    └── SECURITY.md

The `guides/` directory is legacy and overlaps with newer taxonomy pages. Path-resolution content is especially duplicated across top-level pages, guides, examples, and migration pages. The implementer must not delete useful content blindly; consolidate by first making a page inventory, choosing canonical destinations, moving unique details, and replacing obsolete pages with short redirect-style stubs only if Zensical or the hosting environment can preserve URLs safely.

The current MkDocs configuration uses these important capabilities:

- Material navigation features `navigation.tabs` and `navigation.sections`.
- Search plugin.
- `mkdocstrings[python]` for API reference rendering, used by `docs/reference/api.md` through the directive `::: duckalog`.
- Markdown extensions `admonition`, `toc` with permalinks, `pymdownx.highlight`, `pymdownx.superfences` with a Mermaid fence, `pymdownx.inlinehilite`, and `pymdownx.snippets`.
- Shared snippet inclusion syntax, with `README.md` using `--8<-- "docs/_snippets/intro-quickstart.md"` from the repository root and `docs/index.md` using `--8<-- "_snippets/intro-quickstart.md"` from inside `docs/`. The migration must preserve or deliberately replace this per-file include behavior.

The project uses `uv` for Python project operations. Prefer `uv add --dev ...` to change development dependencies and `uv run ...` to execute commands. The current `[dependency-groups].dev` list in `pyproject.toml` includes MkDocs-specific packages: `mkdocs`, `mkdocs-material`, and `mkdocstrings[python]`.

## Plan of Work

The work should proceed in five milestones. The first milestone is an enabler because the content refresh must be validated against the target renderer. The next three milestones are user-visible documentation slices that can be reviewed independently. The final milestone switches the official toolchain and removes obsolete MkDocs assumptions after Zensical has proved it can build the site.

Milestone 1 is the Zensical build foundation. Add Zensical to the development dependencies and create `zensical.toml` at the repository root. Start by translating the current `mkdocs.yml` into native TOML. Set `[project]` keys for `site_name`, `site_description`, `site_url`, `repo_url`, `repo_name`, `docs_dir`, and `site_dir`. Set `[project.theme]` to use the `classic` variant initially if visual parity matters, and include features equivalent to the current site: `navigation.tabs`, `navigation.sections`, `content.action.edit`, and `content.action.view` if repository action buttons are desired. Preserve search either by relying on Zensical's default search support and verifying the generated site contains a search index/UI, or by adding the Zensical search configuration required by the installed version. Use an explicit `project.nav` list that mirrors the current navigation but omits or isolates pages that will be consolidated later. Configure Python Markdown extensions for snippets, SuperFences/Mermaid, highlighting, inline code highlighting, admonitions, and TOC permalinks. Configure `project.plugins.mkdocstrings.handlers.python` with `paths = ["src"]` and options equivalent to the current MkDocs handler: Google docstrings, root heading shown if supported, and source hidden. At the end of this milestone, `uv run zensical build` should create `site/` from the existing docs. If it fails, record the exact failures in this ExecPlan and fix only the minimum compatibility issues needed to get a build.

Milestone 2 is the documentation map and consolidation plan. Create or update a maintainer-facing documentation inventory file, preferably `docs/documentation-map.md`, that lists every current page, its user intent, freshness status, canonical destination, and action: keep, revise, merge, redirect/stub, or remove. Use the map to make the navigation smaller and more intentional in `zensical.toml`. Consolidate path-resolution pages first because they are the clearest duplication hotspot. The canonical structure should keep one conceptual explanation page, one task-focused how-to page, one examples page, and one migration page only if each has distinct user value. Preserve old URLs with short stubs that point to the canonical page when removal would otherwise break existing links. At the end of this milestone, a reader looking for path resolution or legacy guides should have one obvious path through the site and no page should duplicate another without saying why it exists.

Milestone 3 is the core user journey refresh. Update `docs/_snippets/intro-quickstart.md`, `README.md`, `docs/index.md`, `docs/tutorials/index.md`, `docs/tutorials/getting-started.md`, `docs/how-to/index.md`, and the most-used examples under `docs/examples/` so that a new user can install Duckalog, initialize or write a small config, run `duckalog run`, query results, and discover next steps. Keep README focused on quick evaluation and installation, and keep `docs/index.md` focused on learning paths and site navigation. Do not duplicate large examples between README and docs; put shared introductory copy in `docs/_snippets/intro-quickstart.md` and deeper examples in docs pages. At the end of this milestone, a novice should be able to follow one tutorial from zero to a working catalog and then choose a how-to or reference page without encountering stale command names.

Milestone 4 is the reference and advanced docs refresh. Update `docs/reference/cli.md`, `docs/reference/config-schema.md`, `docs/reference/api.md`, `docs/reference/api-patterns.md`, `docs/dashboard/`, `docs/explanation/`, `docs/architecture/`, `docs/SECURITY.md`, `docs/dependency-injection-guide.md`, and migration guides so they match the current code. Use `uv run duckalog --help`, `uv run duckalog run --help`, and any other available command help to validate CLI reference text. Use source files under `src/duckalog/` to validate public Python API names. In particular, `src/duckalog/python_api.py` exposes `connect_to_catalog(config_path, database_path=None, read_only=False, force_rebuild=False)`, not `db_path`, and `src/duckalog/connection.py` exposes a `CatalogConnection` whose public methods are `get_connection()` and `close()` plus context-manager support, not raw `execute()`, `rebuild_catalog()`, `is_ready()`, or `get_metadata()` methods. Confirm that `docs/reference/api.md` renders through Zensical mkdocstrings; if preliminary mkdocstrings support drops an option, document the accepted compromise in `docs/reference/api.md` or `docs/documentation-map.md`. At the end of this milestone, advanced users should be able to look up CLI flags, Python entry points, configuration fields, dashboard behavior, and security guidance without relying on stale README-only reference blocks.

Milestone 5 is official toolchain cutover. Change `.github/workflows/tests.yml` so docs-only pull requests and pushes can actually run documentation validation, either by removing `**.md` and `docs/**` from `paths-ignore` or by adding a dedicated documentation workflow that triggers on documentation paths. Change the `documentation-build` job so it installs Zensical dependencies and runs `uv run zensical build` instead of installing and running MkDocs directly. The Zensical build must be a hard CI gate: do not wrap it in `|| echo`, `continue-on-error`, or any other failure-swallowing pattern. Update `pyproject.toml` and `uv.lock` so `zensical` and the mkdocstrings package required by Zensical are in the dev dependency group. Remove `mkdocs`, `mkdocs-material`, and `mkdocstrings[python]` only after the Zensical build, API reference rendering, snippet expansion, Mermaid rendering, search, and navigation are proven. Update `docs/documentation-duplication-policy.md` so its validation checklist says how to validate README/snippet/docs behavior under Zensical. Keep `mkdocs.yml` for one release as a compatibility artifact only if it is still needed for comparison; otherwise delete it and update any references to it. At the end of this milestone, CI should publish the Zensical-generated `site/` artifact and no maintainer instruction should tell contributors to run `mkdocs build` as the canonical docs check.

Milestones 2, 3, and 4 are related but not all blocking. After Milestone 1, one contributor can refresh tutorials/examples while another audits reference docs, provided they coordinate edits to shared files such as `docs/index.md`, `docs/_snippets/intro-quickstart.md`, `README.md`, `docs/reference/api.md`, and `zensical.toml`. Do not edit `zensical.toml` concurrently from multiple branches because navigation conflicts will be hard to merge. Do not remove MkDocs dependencies concurrently with mkdocstrings or snippet compatibility work; that package boundary belongs to Milestone 5.

## Concrete Steps

Start from the repository root.

1. Confirm the current state and inspect the existing docs build configuration.

    pwd
    git status --short
    uv run python - <<'PY'
    from pathlib import Path
    pages = sorted(Path('docs').rglob('*.md'))
    print(f'{len(pages)} documentation pages')
    for page in pages:
        text = page.read_text(encoding='utf-8', errors='ignore')
        title = next((line for line in text.splitlines() if line.startswith('#')), '(no heading)')
        print(f'{page}: {title}')
    PY

    Expect to see about 52 documentation pages and existing modifications only from intentional work in this branch. If unrelated files are modified, do not overwrite them.

2. Add the Zensical development dependencies.

    uv add --dev zensical mkdocstrings-python

    This should update `pyproject.toml` and `uv.lock`. If `uv add --dev mkdocstrings-python` conflicts with the current `mkdocstrings[python]` dependency, keep both temporarily until Milestone 5 validates Zensical API rendering.

3. Create `zensical.toml` at the repository root. Use this as the initial shape and then adjust based on the installed Zensical version's validation errors.

    [project]
    site_name = "Duckalog"
    site_description = "Build DuckDB catalogs from declarative YAML/JSON configs."
    site_url = "https://legout.github.io/duckalog/"
    repo_url = "https://github.com/legout/duckalog"
    repo_name = "legout/duckalog"
    docs_dir = "docs"
    site_dir = "site"
    edit_uri = "edit/main/docs/"
    nav = [
      { "Home" = "index.md" },
      { "Getting Started" = [
        { "Overview" = "tutorials/index.md" },
        { "Tutorial" = "tutorials/getting-started.md" },
        { "Dashboard Tutorial" = "tutorials/dashboard-basics.md" },
      ] },
      { "How-to Guides" = [
        { "Overview" = "how-to/index.md" },
        { "Environment Management" = "how-to/environment-management.md" },
        { "Debugging Builds" = "how-to/debugging-builds.md" },
        { "Migration" = "how-to/migration.md" },
        { "Performance Tuning" = "how-to/performance-tuning.md" },
        { "Secrets Persistence" = "how-to/secrets-persistence.md" },
      ] },
      { "Reference" = [
        { "Overview" = "reference/index.md" },
        { "Python API" = "reference/api.md" },
        { "API Patterns" = "reference/api-patterns.md" },
        { "CLI Commands" = "reference/cli.md" },
        { "Configuration Schema" = "reference/config-schema.md" },
      ] },
      { "Understanding" = [
        { "Architecture" = "explanation/architecture.md" },
        { "Philosophy" = "explanation/philosophy.md" },
        { "Performance" = "explanation/performance.md" },
        { "Limitations" = "explanation/limitations.md" },
        { "Comparison" = "explanation/comparison.md" },
      ] },
      { "Examples" = [
        { "Overview" = "examples/index.md" },
        { "Simple Parquet" = "examples/simple-parquet.md" },
        { "Multi-Source Analytics" = "examples/multi-source-analytics.md" },
        { "DuckDB Secrets" = "examples/duckdb-secrets.md" },
        { "DuckDB Settings" = "examples/duckdb-settings.md" },
        { "Environment Variables" = "examples/environment-vars.md" },
        { "Local Attachments" = "examples/local-attachments.md" },
        { "Path Resolution Examples" = "examples/path-resolution-examples.md" },
        { "Config Imports" = "examples/config-imports.md" },
      ] },
      { "Security" = "SECURITY.md" },
    ]

    [project.theme]
    variant = "classic"
    features = [
      "navigation.tabs",
      "navigation.sections",
      "navigation.path",
      "navigation.top",
      "content.action.edit",
      "content.action.view",
    ]

    [project.markdown_extensions.admonition]
    [project.markdown_extensions.toc]
    permalink = true
    [project.markdown_extensions.pymdownx.highlight]
    anchor_linenums = true
    line_spans = "__span"
    pygments_lang_class = true
    [project.markdown_extensions.pymdownx.inlinehilite]
    [project.markdown_extensions.pymdownx.snippets]
    [project.markdown_extensions.pymdownx.superfences]
    custom_fences = [
      { name = "mermaid", class = "mermaid", format = "pymdownx.superfences.fence_code_format" },
    ]

    [project.plugins.mkdocstrings.handlers.python]
    paths = ["src"]

    [project.plugins.mkdocstrings.handlers.python.options]
    docstring_style = "google"
    show_root_heading = true
    show_source = false

    If the `format` value for the Mermaid fence must use a Zensical-specific import path, use the path shown by the current Zensical docs or error message and record the change in `Surprises & Discoveries`.

4. Build with Zensical and capture failures.

    uv run zensical build

    Expected successful result: `site/` exists and contains generated HTML including `site/index.html`. If the command fails because a snippet path is wrong, remember that current files use different include paths: `README.md` includes `docs/_snippets/intro-quickstart.md`, while `docs/index.md` includes `_snippets/intro-quickstart.md`. Adjust the site-rendered docs path only after confirming whether Zensical resolves snippet paths from repository root or `docs_dir`; separately decide how the repository README should be rendered for GitHub and PyPI. If mkdocstrings fails, first ensure `mkdocstrings-python` is installed and `paths = ["src"]` is set.

5. Create the documentation map and use it before deleting pages.

    uv run python - <<'PY'
    from pathlib import Path
    out = Path('docs/documentation-map.md')
    rows = []
    for page in sorted(Path('docs').rglob('*.md')):
        if page == out:
            continue
        text = page.read_text(encoding='utf-8', errors='ignore')
        title = next((line.lstrip('# ').strip() for line in text.splitlines() if line.startswith('#')), page.stem)
        rows.append(f'| `{page}` | {title} | TBD | TBD | TBD |')
    out.write_text('# Documentation Map\n\nThis file tracks each documentation page, its user intent, canonical destination, and migration action during the Zensical documentation refresh.\n\n| Page | Current title | User intent | Canonical destination | Action |\n|------|---------------|-------------|-----------------------|--------|\n' + '\n'.join(rows) + '\n', encoding='utf-8')
    PY

    Then manually replace the `TBD` cells with concrete decisions. Do not leave this file as a generated-only artifact; it is a working migration map.

6. Refresh content slices in the order described by the milestones. After each slice, run:

    uv run zensical build
    uv run duckalog --help
    uv run pytest tests/test_docstrings.py

    The pytest command is a targeted sanity check for public documentation/docstring conventions. If this repository's test suite changes, use the closest test that validates docs or public API documentation and record the substitution.

7. Switch CI after local Zensical builds pass.

    In `.github/workflows/tests.yml`, first make docs changes trigger docs validation. The existing workflow ignores `**.md` and `docs/**`, so either remove those ignores from the main workflow or create a separate docs workflow with `paths` that include `docs/**`, `README.md`, `zensical.toml`, `pyproject.toml`, `uv.lock`, and `.github/workflows/**`. Then change the documentation dependency installation and build steps so they use project dependencies and Zensical. The final job should resemble this behavior and must fail if Zensical fails:

        - name: Install documentation dependencies
          run: |
            python -m pip install --upgrade pip
            pip install uv
            uv sync --group dev

        - name: Build documentation
          run: |
            echo "📚 Building documentation with Zensical..."
            uv run zensical build

    Do not keep the old `|| echo` failure-swallowing blocks from the MkDocs job. Keep artifact upload from `site/` unchanged unless Zensical writes to a different `site_dir`.

8. Remove or demote MkDocs only after final validation.

    If Zensical now builds the docs, snippets expand, API docs render, Mermaid diagrams render, and CI uses Zensical, remove `mkdocs`, `mkdocs-material`, and `mkdocstrings[python]` from the dev dependency group unless they remain necessary for another maintainer workflow. If `mkdocs.yml` is no longer used, either delete it or move its relevant history into `docs/documentation-map.md` and `zensical.toml` comments. Run `uv lock` if dependency edits were manual.

## Validation and Acceptance

The implementation is complete only when all of these are true:

- Running `uv run zensical build` from the repository root exits successfully and writes `site/index.html`.
- The generated site includes the docs landing page, tutorials, how-to guides, reference pages, explanations, examples, dashboard docs, architecture notes, and security page in the intended navigation.
- Search is preserved from the current MkDocs site: the generated Zensical site exposes a working search UI or generated search index, and the validation notes say how it was checked.
- `docs/reference/api.md` renders API reference content through Zensical's mkdocstrings integration or documents an explicit, accepted limitation with a fallback page.
- Hand-written API examples in `docs/reference/api.md` use real public names from `src/duckalog/python_api.py` and `src/duckalog/connection.py`, including `database_path` rather than `db_path` and `catalog.get_connection().execute(...)` rather than nonexistent direct `CatalogConnection.execute(...)` calls.
- The shared intro/quickstart content remains single-sourced through `docs/_snippets/intro-quickstart.md` or an equivalent documented Zensical-compatible mechanism. Updating the snippet changes both the docs landing page and the README production path as applicable.
- The README rendering story is explicit: either GitHub/PyPI can render the chosen shared-content mechanism correctly, or the repository has a documented pre-render/update step that expands the snippet before publication.
- The path-resolution duplication hotspot is resolved: one canonical conceptual page, one canonical how-to or guide page if needed, one canonical examples page, and one migration page only if it adds unique migration value.
- `.github/workflows/tests.yml` or a dedicated documentation workflow runs on docs-only changes, no longer uses `mkdocs build` as the canonical documentation validation command, runs a Zensical build as a hard failure gate, and uploads the generated `site/` artifact.
- `docs/documentation-duplication-policy.md` explains the new Zensical validation command and no longer tells contributors to run MkDocs as the primary workflow.
- `pyproject.toml` and `uv.lock` agree on the final documentation dependencies.
- No internal Markdown links are knowingly broken. At minimum, inspect Zensical build warnings. If a link-checker is available, run it and record the command in this plan.

A concise success transcript should look like this, allowing for version-specific wording:

    $ uv run zensical build
    ...
    Site built successfully into site

    $ test -f site/index.html && echo ok
    ok

    $ git grep -n "mkdocs build" -- README.md docs .github pyproject.toml
    # no canonical maintainer instruction remains, except historical notes or deliberate migration comments

## Idempotence and Recovery

All planned edits are file-based and can be repeated safely if the implementer checks `git status --short` before each milestone. If `uv add --dev zensical mkdocstrings-python` partially updates dependencies and the build fails, keep the dependency changes while fixing configuration; do not remove Zensical until the failure is understood.

Keep `mkdocs.yml` during early milestones as a fallback. If Zensical build failures block progress, run the old command `uv run mkdocs build --clean --strict` only to compare behavior, not as the final acceptance command. If a content consolidation removes a page and then breaks links, restore the page from git and replace its body with a short pointer to the canonical destination instead of deleting it immediately.

Do not overwrite unrelated local changes. If another contributor has modified the same docs page, preserve their changes and update this plan's `Progress` section with what remains.

## Artifacts and Notes

Important current files and evidence:

    mkdocs.yml
      Current documentation configuration. It defines site metadata, navigation, Material theme features, search, mkdocstrings, snippets, highlighting, and Mermaid SuperFences.

    pyproject.toml
      Current dev dependencies include mkdocs, mkdocs-material, and mkdocstrings[python]. The migration should add zensical and mkdocstrings-python, then remove obsolete MkDocs packages only after validation.

    .github/workflows/tests.yml
      The documentation-build job currently installs MkDocs packages and runs mkdocs build. This is the CI boundary that proves the migration is official.

    docs/_snippets/intro-quickstart.md
      Canonical source for shared README and docs landing-page intro/quickstart content.

    docs/documentation-duplication-policy.md
      Current maintainer policy for avoiding README/docs drift. It must be updated to reference Zensical validation.

    docs/reference/api.md
      Contains the mkdocstrings directive ::: duckalog and is the primary proof point for Zensical API reference rendering.

    ARCHITECTURE.md
      Updated on 2026-04-29 with current documentation-layer context and docs complexity concerns.

## Interfaces and Dependencies

The main new project interface is `zensical.toml` in the repository root. It must be the canonical documentation site configuration at the end of this work. Its stable responsibilities are site metadata, docs source directory, output directory, navigation, theme features, Markdown extensions, repository links, and mkdocstrings plugin configuration.

The command-line interface for maintainers is:

    uv run zensical build
    uv run zensical serve

`uv run zensical build` is the acceptance command. `uv run zensical serve` is optional for local preview.

Development dependencies must include:

- `zensical`, the static site generator.
- `mkdocstrings-python`, because Zensical's mkdocstrings support requires the Python handler to be installed separately.

Current MkDocs dependencies must be handled deliberately:

- `mkdocs` is the old static site generator.
- `mkdocs-material` is the old theme package.
- `mkdocstrings[python]` is the old MkDocs API-reference dependency. It may remain temporarily during migration but should be removed if `mkdocstrings-python` and Zensical fully cover the final docs workflow.

The documentation content interface is the Markdown tree under `docs/`. Keep relative links pointing to Markdown files, not generated HTML, because Zensical rewrites Markdown links into the correct output URLs.

## Revision Notes

- 2026-04-29: Initial ExecPlan drafted after creating the brainstorm, updating architecture context, reading current docs/tooling files, and checking Zensical documentation for TOML configuration, navigation, Markdown extensions, repository integration, and mkdocstrings support.
- 2026-04-29: Improved after a code-grounded review. Fixed the snippet path description, made docs-only CI triggering and hard build failure explicit, preserved search as an acceptance criterion, strengthened API-example correctness checks against `src/duckalog/python_api.py` and `src/duckalog/connection.py`, and required an explicit README rendering story.
