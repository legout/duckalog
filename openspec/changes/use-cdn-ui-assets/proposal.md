# Change: Use CDN-hosted UI assets temporarily

## Why
To ship quickly, we will load Tailwind, Basecoat, and Datastar JS from CDNs instead of bundling. This aligns with current implementation and defers bundling work. Datastar-py latest available is 0.7.0.

## What Changes
- Update specs to permit CDN loading for Tailwind, Basecoat, and Datastar JS as an interim measure.
- Document the temporary nature and offline limitations.
- Ensure integrity attributes and fallbacks are considered.

## Impact
- Specs: `dashboard-ui`
- Code: `components/layout.py` references may stay; annotate as interim.
- Docs: note CDN usage and planned bundling.
