# Change: Bundle Datastar assets locally

## Why
The dashboard loads Datastar from a remote RC CDN, creating supply-chain and offline availability risks for a UI intended to run locally. We should pin and bundle the Datastar asset to serve it from the UI itself.

## What Changes
- Pin the Datastar bundle version and serve it locally from the UI package instead of a remote CDN
- Provide an offline-safe asset path for the dashboard
- Add tests/docs to ensure the dashboard renders when offline

## Impact
- Affected specs: web-ui
- Affected code: dashboard HTML generation, static asset serving pipeline/package data
- User-facing behavior: same UI, but assets load locally and predictably
