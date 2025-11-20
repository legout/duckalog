# Change: Rescope local UI security and API surface

## Why
The existing `secure-and-simplify-ui` proposal overreaches for a localhost-only UI: it removes the ad-hoc query endpoint, mandates heavy service-layer splits, and makes authentication mandatory even for single-user setups. We need a narrower, pragmatic scope that keeps local convenience while adding the necessary hardening already covered by other changes.

## What Changes
- Keep `/api/query` but enforce read-only, single-statement execution (pairs with `harden-ui-readonly-config`)
- Make admin token authentication optional (opt-in) and applied only to mutating endpoints when enabled
- Allow exports from either view names or read-only queries (not view-only), with read-only enforcement
- Preserve a lightweight architecture (no mandatory service-layer split), focusing on DRY helpers instead
- Align CORS defaults with localhost posture and retain the existing endpoint set

## Impact
- Affected specs: web-ui
- Interacts with: `harden-ui-readonly-config` (read-only enforcement), `bundle-datastar-assets` (asset source), `fix-export-formats` (export fidelity)
- Replaces over-strict parts of `secure-and-simplify-ui` without duplicating the export/query/CORS hardening already scoped in other changes
