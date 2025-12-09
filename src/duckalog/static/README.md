# Static Assets Directory

This directory contains static assets for the Duckalog dashboard.

## Current Status: CDN Delivery (Temporary)

**IMPORTANT**: The dashboard currently loads UI assets (Tailwind CSS, Basecoat CSS, and Datastar JS) from CDNs as a temporary measure to expedite shipping. This is an interim solution.

## Datastar JavaScript Bundle

- **Datastar Version**: v1.0.0-RC.6
- **Source**: https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.0-RC.6/bundles/datastar.js
- **Original Download Date**: 2025-11-21
- **File**: datastar.js (29,360 bytes) - No longer actively used

## Purpose (Original)

This directory was originally intended to contain vendored assets for offline use:
- Offline operation without external CDN dependencies
- Predictable, versioned asset loading
- Supply chain security by pinning to a specific version

## Temporary CDN Approach

As of the current implementation:
- Tailwind CSS is loaded from `https://cdn.tailwindcss.com`
- Basecoat CSS is loaded from `https://cdn.jsdelivr.net/npm/basecoat-css@latest/dist/basecoat.cdn.min.css`
- Datastar JS is loaded from `https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.0-RC.6/bundles/datastar.js`

## Offline Limitations

The dashboard currently **does not support offline mode** due to CDN dependencies. This is an accepted limitation during the interim period.

## Future Bundling Plan

All assets will eventually be bundled locally for offline support as originally specified. This CDN approach is temporary and will be replaced with proper offline asset bundling in a future release.

## Updating (When Bundling is Implemented)

To update the Datastar bundle when offline bundling is restored:

1. Check the latest available version at https://github.com/starfederation/datastar/releases
2. Download the new bundle:
   ```bash
   curl -L "https://cdn.jsdelivr.net/gh/starfederation/datastar@v{VERSION}/bundles/datastar.js" -o src/duckalog/static/datastar.js
   ```
3. Update the version information in this file
4. Test that the UI still functions correctly
5. Update any relevant documentation

## Integration (When Bundling is Restored)

The bundle will be automatically served via Starlette static routing at `/static/datastar.js` and referenced in the dashboard HTML templates.