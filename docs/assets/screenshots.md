# Dashboard Screenshots

This section contains screenshots showing the dashboard interface and features.

## Screenshots Overview

### Home Page
**File**: `home-page.png`

**Description**: Dashboard home page showing:
- Configuration path and database location
- Catalog statistics (views, attachments, semantic models)
- Build status and rebuild controls
- Recent activity summary

### Views Listing
**File**: `views-listing.png`

**Description**: Views browsing page showing:
- Search functionality for filtering views
- Table of all catalog views with source information
- Semantic model indicators
- View detail links

### View Detail
**File**: `view-detail.png`

**Description**: Individual view page showing:
- SQL definition or source file details
- Metadata and source information
- Related semantic models
- Query execution button

### Query Interface
**File**: `query-interface.png`

**Description**: Query execution interface showing:
- SQL query editor with syntax highlighting
- Real-time loading indicators
- Results table with export options
- Security enforcement messages

### Query Results Streaming
**File**: `query-streaming.png`

**Description**: Real-time query execution showing:
- Loading indicators during execution
- Progressive result display
- Success/error states
- Export functionality

### Build Status
**File**: `build-status.png`

**Description**: Build interface showing:
- Build trigger button
- Real-time build progress
- Success/error status messages
- Build completion details

### Dark Theme
**File**: `dark-theme.png`

**Description**: Dashboard in dark mode showing:
- Dark color scheme with high contrast
- Theme toggle functionality
- Responsive layout maintenance
- Accessibility features

### Mobile Responsive
**File**: `mobile-responsive.png`

**Description**: Mobile view showing:
- Responsive layout adaptation
- Touch-friendly navigation
- Optimized form layouts
- Mobile query interface

## Generating Screenshots

To update screenshots for documentation:

### Automated Screenshot Generation

```bash
# Install screenshot dependencies
pip install playwright

# Generate screenshots
python scripts/generate_screenshots.py

# Screenshots will be saved to:
# docs/assets/images/dashboard/
```

### Manual Screenshot Guidelines

**Requirements:**
- Browser: Chrome, Firefox, Safari, or Edge (latest version)
- Resolution: 1920x1080 (desktop), 375x812 (mobile)
- Format: PNG with lossless compression
- File naming: kebab-case with descriptive names

**Screenshot Process:**
1. Start dashboard: `duckalog ui catalog.yaml`
2. Navigate to feature to document
3. Set up appropriate data/state
4. Capture clean screenshot (no browser chrome)
5. Optimize file size (under 500KB)
6. Add to docs/assets/images/

### Image Optimization

```bash
# Optimize PNG screenshots
optipng -o7 docs/assets/images/dashboard/*.png

# Compress large screenshots
pngquant --quality=85 docs/assets/images/dashboard/*.png

# WebP conversion for web use
cwebp -q 85 input.png -o output.webp
```

## Screenshot Checklist

### Before Capturing

- [ ] Clean browser cache and cookies
- [ ] Disable browser extensions
- [ ] Set consistent zoom level (100%)
- [ ] Choose appropriate test data
- [ ] Verify feature is working correctly

### Composition Guidelines

- [ ] Center important elements
- [ ] Include relevant UI context
- [ ] Avoid window chrome (unless showing browser features)
- [ ] Maintain consistent aspect ratios
- [ ] Ensure text is readable

### Technical Requirements

- [ ] Resolution: 1920x1080 (desktop)
- [ ] Format: PNG (lossless)
- [ ] File size: < 500KB
- [ ] Color profile: sRGB
- [ ] No compression artifacts

### File Organization

```
docs/assets/images/dashboard/
├── home-page.png
├── views-listing.png
├── view-detail.png
├── query-interface.png
├── query-streaming.png
├── build-status.png
├── dark-theme.png
├── mobile-responsive.png
├── semantic-layer.png
└── export-dialog.png
```

## Including Screenshots in Documentation

### Markdown Usage

```markdown
<!-- Standard screenshot -->
![Dashboard Home Page](../assets/images/dashboard/home-page.png)

<!-- With caption and alt text -->
![Query Interface with Results](../assets/images/dashboard/query-interface.png)
*The query interface showing real-time result streaming and export options.*

<!-- Responsive images -->
<picture>
  <source srcset="../assets/images/dashboard/mobile-responsive.webp" type="image/webp">
  <source srcset="../assets/images/dashboard/mobile-responsive.png" type="image/png">
  <img src="../assets/images/dashboard/mobile-responsive.png" alt="Mobile dashboard view">
</picture>
```

### Figure Captions

Use descriptive figure captions:

```markdown
<figure>
  <img src="../assets/images/dashboard/query-streaming.png" alt="Real-time query execution">
  <figcaption>Real-time query execution showing progressive result loading and live status updates.</figcaption>
</figure>
```

## Updating Screenshots

### When to Update

- New features added
- UI redesigns
- Bug fixes affecting appearance
- Documentation updates
- Accessibility improvements

### Version Control

- Commit screenshots with feature changes
- Use descriptive commit messages
- Track screenshot history
- Maintain backup versions

### Quality Assurance

- Review screenshots for clarity
- Test documentation links
- Verify alt text accuracy
- Check file sizes
- Validate responsive behavior

## Accessibility Considerations

### Alt Text Guidelines

Provide descriptive alt text for all screenshots:

```markdown
<!-- Poor alt text -->
![Home page](home-page.png)

<!-- Good alt text -->
![Dashboard home page showing catalog statistics, build status, and navigation menu](home-page.png)
```

### Color and Contrast

- Ensure sufficient contrast
- Test with color blind simulators
- Verify readability in different themes
- Include dark/light mode examples

This screenshot documentation helps users understand the dashboard interface and features through visual examples.