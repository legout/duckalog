# Flatten Documentation Navigation

## Why

The current MkDocs documentation uses a nested navigation structure where major sections like "User Guide", "Examples", and "API Reference" appear as dropdown menus in the top navigation bar. This creates several usability challenges:

1. **Deeper Navigation Levels**: Users must navigate through multiple menu layers to reach content
2. **Hidden Content**: Important sections are buried in dropdown menus, reducing discoverability
3. **Navigation Overhead**: Each additional click adds friction to the user experience
4. **Content Visibility**: Primary documentation sections are not immediately visible in the top navigation

By flattening the navigation structure and making each major section a standalone page in the top bar, users can:
- Access all major documentation sections directly from the top navigation
- Move more efficiently between different parts of the documentation
- Have better overview and discoverability of available content
- Experience faster navigation with reduced clicks

## What Changes

- Create dedicated index pages for major navigation sections (User Guide, Examples, API Reference)
- Restructure `mkdocs.yml` navigation from nested to flat format
- Move individual documentation pages into their respective section index pages
- Ensure all existing content remains accessible but organized under section index pages
- Maintain Material theme consistency while improving navigation structure
- Preserve all existing content, links, and functionality

## Impact

- **Improved User Experience**: Direct access to major documentation sections from top navigation
- **Better Content Discovery**: All primary sections visible immediately in the navigation bar
- **Reduced Navigation Complexity**: Fewer clicks needed to reach any section
- **Enhanced Information Architecture**: Clearer separation and organization of documentation content
- **Consistent Navigation**: Top navigation bar shows all major sections as equal page entries
- **Maintained Functionality**: All existing features, search, and cross-references preserved

The change improves the overall documentation structure while maintaining all existing functionality and content accessibility.