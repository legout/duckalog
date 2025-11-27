# Duckalog Dashboard (starhtml/starui)

The dashboard is a lightweight, local-only web UI for exploring a Duckalog catalog. It is built entirely in Python using **starhtml** and **starui**—no frontend build tools or external CDNs are required.

## Launch from the CLI

```bash
duckalog ui catalog.yaml --host 127.0.0.1 --port 8787 --row-limit 500
```

- Binds to loopback by default; only expose other hosts if you understand the risk.
- `--row-limit` caps ad-hoc query results (defaults to 500 rows).
- The CLI prints the dashboard URL after startup.
- Install dependencies with `pip install duckalog[ui]` to get `uvicorn`, `starlette`, `starhtml`, and `starui`.

## Launch from Python

```python
from duckalog.dashboard import run_dashboard

run_dashboard("catalog.yaml", host="127.0.0.1", port=8787, row_limit=500)
```

Pass a `Config` object instead of a path if you already loaded one.

## What you can do

- **Home**: See config path, DuckDB database, counts (views/attachments/semantic models), and last build status. Trigger a build.
- **Views**: Browse views with source type and location/attachment info; search by name.
- **View detail**: Inspect the view definition (SQL or source fields) and any semantic-layer dimensions/measures.
- **Query**: Run ad-hoc SQL against the catalog with row-limit enforcement and clear error display.
- **Build**: Kick off a catalog build with the same semantics as `duckalog build`; status is shown on the home page.

## Scope and limitations

- Single-user, local-first; no authentication is provided.
- No external assets or CDNs; everything is served from the duckalog installation.
- Focused on tables and text—charts/advanced visuals are out of scope for this version.
