# Datastar Bundle Information

This directory contains the vendored Datastar JavaScript bundle for offline use.

## Version Information

- **Datastar Version**: v1.0.0-RC.6
- **Source**: https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.0-RC.6/bundles/datastar.js
- **Download Date**: 2025-11-21
- **File**: datastar.js (29,360 bytes)

## Purpose

This bundled asset is served locally by the Duckalog UI to ensure:
- Offline operation without external CDN dependencies
- Predictable, versioned asset loading
- Supply chain security by pinning to a specific version

## Updating

To update the Datastar bundle:

1. Check the latest available version at https://github.com/starfederation/datastar/releases
2. Download the new bundle:
   ```bash
   curl -L "https://cdn.jsdelivr.net/gh/starfederation/datastar@v{VERSION}/bundles/datastar.js" -o src/duckalog/static/datastar.js
   ```
3. Update the version information in this file
4. Test that the UI still functions correctly
5. Update any relevant documentation

## Integration

The bundle is automatically served via Starlette static routing at `/static/datastar.js` and referenced in the dashboard HTML templates.