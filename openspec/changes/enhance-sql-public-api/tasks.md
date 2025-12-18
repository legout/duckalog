## 1. Analyze Current API Structure
- [ ] 1.1 Review existing `__all__` exports in `src/duckalog/__init__.py`
- [ ] 1.2 Identify commonly requested but missing SQL exports
- [ ] 1.3 Map user import patterns from examples and tests
- [ ] 1.4 Document current API organization and gaps

## 2. Organize SQL Exports
- [ ] 2.1 Group SQL generation functions (`generate_view_sql`, `generate_all_views_sql`, `generate_secret_sql`)
- [ ] 2.2 Group SQL utilities (`quote_ident`, `quote_literal`, `render_options`)
- [ ] 2.3 Group SQL file loading (`SQLFileLoader`, error classes)
- [ ] 2.4 Organize exports in logical order for better discoverability

## 3. Enhance Public API
- [ ] 3.1 Update `src/duckalog/__init__.py` with enhanced exports
- [ ] 3.2 Add convenience imports for commonly used SQL functionality
- [ ] 3.3 Ensure all existing exports are preserved (backward compatibility)
- [ ] 3.4 Add clear documentation and docstrings for new exports
- [ ] 3.5 Test that all imports work as expected

## 4. Documentation and Examples
- [ ] 4.1 Update README examples to use enhanced API where appropriate
- [ ] 4.2 Fix any broken documentation references
- [ ] 4.3 Ensure examples demonstrate the improved API structure
- [ ] 4.4 Update API documentation to reflect new organization

## 5. Validation and Testing
- [ ] 5.1 Test that all new exports work correctly
- [ ] 5.2 Verify backward compatibility for existing imports
- [ ] 5.3 Run import analysis to confirm improved API surface
- [ ] 5.4 Validate that documentation builds correctly with enhanced API
- [ ] 5.5 Test user workflows to ensure improved discoverability