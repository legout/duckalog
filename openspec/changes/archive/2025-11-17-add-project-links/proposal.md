# Change: Add Project Links to pyproject.toml

## Why
The Duckalog project's `pyproject.toml` file currently lacks comprehensive project links and metadata, which affects:

- **Package Discoverability**: Users cannot easily find documentation, repository, or changelog from PyPI
- **User Experience**: Missing Homepage, Repository, and Documentation links make the package appear incomplete
- **Professional Presentation**: Comprehensive project links are standard practice for professional Python packages
- **Community Engagement**: No clear path for users to contribute, report issues, or access documentation
- **SEO and Ranking**: Missing metadata affects package discoverability on PyPI and search engines
- **Maintainability**: No centralized location for project URLs and external references

Adding comprehensive project links will enhance the project's professional appearance, improve user experience, and provide clear pathways for documentation, support, and community engagement.

## What Changes
- Add `[project.urls]` section to `pyproject.toml` with comprehensive links
- Include Homepage, Repository, Documentation, Changelog, Issues, and Discussions links
- Add Badge links for PyPI version, Python version, and CI status
- Include optional funding, security policy, and contribution guidelines links
- Ensure all links follow standard conventions and best practices
- Update existing project metadata to include proper descriptions and classifiers

## Impact
- Affected specs: Package metadata and distribution capability (enhancement)
- Affected code: pyproject.toml configuration file only
- Benefits: Improved package professionalism, better user experience, enhanced discoverability
- Breaking changes: None - purely additive metadata improvements
- Risk: Low - changes are purely additive and follow Python packaging standards

```

```

# Change Implementation Tasks: Add Project Links to pyproject.toml

## 1. Project Links Addition
- [ ] 1.1 Add `[project.urls]` section to pyproject.toml
- [ ] 1.2 Add Homepage link pointing to documentation or repository
- [ ] 1.3 Add Repository link pointing to GitHub repository
- [ ] 1.4 Add Documentation link pointing to MkDocs site
- [ ] 1.5 Add Changelog link pointing to CHANGELOG.md or release notes

## 2. Community and Support Links
- [ ] 2.1 Add Issues link pointing to GitHub Issues
- [ ] 2.2 Add Discussions link pointing to GitHub Discussions (if enabled)
- [ ] 2.3 Add Security Policy link pointing to security disclosure process
- [ ] 2.4 Add Contributing Guidelines link
- [ ] 2.5 Add License link pointing to license file

## 3. Development and CI Links
- [ ] 3.1 Add CI/Tests link pointing to GitHub Actions
- [ ] 3.2 Add Coverage link pointing to Codecov or similar service
- [ ] 3.3 Add Quality checks link for code quality dashboards
- [ ] 3.4 Add pre-commit hooks or development tools links
- [ ] 3.5 Add OpenSpec documentation link for technical details

## 4. Badge and Status Links
- [ ] 4.1 Add PyPI version badge link
- [ ] 4.2 Add Python version compatibility badge
- [ ] 4.3 Add CI build status badge link
- [ ] 4.4 Add code coverage badge link
- [ ] 4.5 Add security scanning badge link (if applicable)

## 5. Enhanced Project Metadata
- [ ] 5.1 Review and improve project description for clarity
- [ ] 5.2 Add or improve keywords for better discoverability
- [ ] 5.3 Add or update classifiers for PyPI categorization
- [ ] 5.4 Ensure author information is complete and accurate
- [ ] 5.5 Add maintainer information if different from author

## 6. Documentation Integration
- [ ] 6.1 Verify documentation links work correctly
- [ ] 6.2 Ensure repository structure matches linked paths
- [ ] 6.3 Update README.md badges if needed for consistency
- [ ] 6.4 Create or update CONTRIBUTING.md with guidelines
- [ ] 6.5 Create or update SECURITY.md for security policy

## 7. Testing and Validation
- [ ] 7.1 Validate pyproject.toml syntax after changes
- [ ] 7.2 Test package build with updated metadata
- [ ] 7.3 Verify PyPI renders links correctly (using test PyPI)
- [ ] 7.4 Check badge rendering in README and documentation
- [ ] 7.5 Test documentation site builds and links work

## 8. Quality Assurance
- [ ] 8.1 Review all URLs for accuracy and accessibility
- [ ] 8.2 Ensure all linked resources exist and are accessible
- [ ] 8.3 Verify proper HTTP status codes for all links
- [ ] 8.4 Check for consistency across all project documentation
- [ ] 8.5 Validate that changes follow Python packaging best practices

## 9. Community and Maintenance
- [ ] 9.1 Document link maintenance procedures for future updates
- [ ] 9.2 Add instructions for contributors about updating links
- [ ] 9.3 Create checklist for link validation during releases
- [ ] 9.4 Establish process for broken link detection and fixing
- [ ] 9.5 Plan regular review schedule for link accuracy

## 10. Final Integration
- [ ] 10.1 Perform end-to-end validation of complete workflow
- [ ] 10.2 Test package installation and metadata display
- [ ] 10.3 Verify PyPI package page shows all links correctly
- [ ] 10.4 Update any automated documentation that references the package
- [ ] 10.5 Get stakeholder review for metadata completeness and accuracy

## Implementation Summary

This checklist covers the complete enhancement of pyproject.toml with comprehensive project links and metadata. The changes will:

- Add professional project links following Python packaging standards
- Improve package discoverability and user experience
- Provide clear pathways for documentation, support, and contribution
- Enhance the project's professional appearance on PyPI
- Follow established conventions for Python project metadata

Each task should be completed in order, with validation at each phase to ensure the metadata is accurate and properly formatted.

**Prerequisites:**
- Access to pyproject.toml file
- Repository URLs and documentation sites configured
- Basic understanding of Python packaging standards
- Knowledge of PyPI project page layout

**Expected Timeline:** 
- Phase 1-2 (Basic Links): 30 minutes
- Phase 3-4 (Community & Badges): 30 minutes
- Phase 5-6 (Metadata & Documentation): 45 minutes
- Phase 7-8 (Testing & QA): 30 minutes
- Phase 9-10 (Integration): 15 minutes

**Total Estimated Time:** 2.5 hours for complete implementation and validation

```

```

## ADDED Requirements
### Requirement: Comprehensive Project Links in pyproject.toml
The project SHALL include a `[project.urls]` section in `pyproject.toml` with essential project links.

#### Scenario: Package discoverability
- **WHEN** a user visits the PyPI package page for duckalog
- **THEN** they can easily find links to Homepage, Repository, Documentation, and Changelog

#### Scenario: Documentation access
- **WHEN** a user wants to learn more about duckalog
- **THEN** they can quickly access the documentation through the PyPI links

#### Scenario: Community engagement
- **WHEN** a user wants to report an issue or contribute to the project
- **THEN** they can find links to Issues, Discussions, and Contributing guidelines

### Requirement: Professional Package Presentation
The pyproject.toml SHALL provide complete metadata that presents duckalog as a professional Python package.

#### Scenario: PyPI package page
- **WHEN** users browse the duckalog package on PyPI
- **THEN** they see a complete, professional package page with all relevant links and information

#### Scenario: Package installation context
- **WHEN** users install duckalog using pip
- **THEN** they can access additional project information through the enhanced metadata

### Requirement: Standard Python Packaging Links
The project SHALL follow Python packaging standards for project links and metadata.

#### Scenario: Industry standards compliance
- **WHEN** the package is evaluated against Python packaging best practices
- **THEN** it SHALL include all standard project URLs and metadata fields

#### Scenario: Tool compatibility
- **WHEN** Python packaging tools and indexers process the package
- **THEN** they SHALL correctly interpret and display all project links and metadata

### Requirement: Accessible and Valid Links
All project links SHALL be accessible and point to existing, maintained resources.

#### Scenario: Link validation
- **WHEN** the package metadata is processed or displayed
- **THEN** all links SHALL return appropriate HTTP status codes and point to intended content

#### Scenario: Documentation integration
- **WHEN** users follow documentation links from PyPI
- **THEN** they SHALL reach functional documentation that accurately describes the project

### Requirement: Enhanced Package Information
The package metadata SHALL include comprehensive information for better categorization and discoverability.

#### Scenario: Search optimization
- **WHEN** users search for Python packages with specific characteristics
- **THEN** duckalog SHALL be properly categorized with keywords and classifiers

#### Scenario: Professional presentation
- **WHEN** the package is viewed in package management interfaces
- **THEN** it SHALL present a complete and professional profile with proper descriptions and links

### Requirement: Badge and Status Indicators
The project SHALL include appropriate badges and status indicators for transparency and quality assurance.

#### Scenario: Quality transparency
- **WHEN** users evaluate the package's quality and maintenance status
- **THEN** they can see badges for CI status, coverage, and other quality metrics

#### Scenario: Development activity
- **WHEN** users want to assess the project's development activity
- **THEN** they can see current build status and development metrics through badges

### Requirement: Community and Support Links
The project SHALL provide clear pathways for community engagement and support.

#### Scenario: Getting help
- **WHEN** users need help or want to report problems
- **THEN** they can find links to appropriate support channels and community resources

#### Scenario: Contributing
- **WHEN** users want to contribute to the project
- **THEN** they can find guidelines and appropriate contribution channels

```

```

# Design Document: Project Links Enhancement for pyproject.toml

## Context

Duckalog is a Python library and CLI for building DuckDB catalogs from declarative configuration files. The project currently has:
- Complete source code structure and documentation
- PyPI-ready package configuration in `pyproject.toml`
- GitHub repository with Issues, Discussions, and Actions
- MkDocs-based documentation site
- OpenSpec-driven development process

However, the `pyproject.toml` file lacks comprehensive project links and enhanced metadata, which affects the project's professional presentation and user experience on PyPI.

**Stakeholders:**
- Users who discover the package on PyPI
- Contributors who want to engage with the project
- Maintainers who want professional package presentation
- Community members who need support or want to report issues

## Goals / Non-Goals

### Goals
- Enhance pyproject.toml with comprehensive project links
- Improve package professionalism and user experience
- Provide clear pathways for documentation, support, and contribution
- Follow Python packaging best practices and standards
- Increase package discoverability and search ranking
- Support community engagement and contribution

### Non-Goals
- Modify existing package functionality or API
- Change the project's development workflow or architecture
- Add new features or capabilities beyond metadata
- Modify source code or test implementation
- Create new documentation beyond link updates

## Decisions

### Decision: Add comprehensive `[project.urls]` section
**What:** Include all standard project URLs in the `[project.urls]` section of `pyproject.toml`.

**Why:**
- PyPI automatically displays these links on the package page
- Follows Python Packaging User Guide recommendations
- Provides consistent user experience across Python ecosystem
- Improves package discoverability and professional appearance
- Supports community engagement and contribution

**Alternatives considered:**
- Only add basic links (Homepage, Repository) → Misses opportunities for community engagement
- Add links only to README.md → Less prominent and not standard practice
- External metadata files → Not integrated with package distribution

### Decision: Include both GitHub and documentation links
**What:** Add links to both GitHub repository and MkDocs documentation site.

**Why:**
- GitHub repository for source code, issues, and contribution
- Documentation site for user guides and API reference
- Provides multiple access points for different user needs
- Supports both technical and non-technical users
- Follows established Python project patterns

**Alternatives considered:**
- GitHub wiki only → Less comprehensive than dedicated documentation site
- Documentation as GitHub pages → Good but dedicated site provides better user experience
- Single umbrella link → Less specific and harder to navigate

### Decision: Include badge links and status indicators
**What:** Add links to CI/CD, coverage, and quality metrics through both pyproject.toml and README badges.

**Why:**
- Transparency about project quality and maintenance
- Build confidence in package reliability
- Industry standard for professional Python packages
- Helps users make informed decisions about package adoption
- Encourages continuous improvement and maintenance

**Alternatives considered:**
- No badges → Missed opportunity for quality transparency
- Too many badges → Information overload and maintenance burden
- Manual badge updates → Error-prone and not scalable

## Risks / Trade-offs

### Risk: Broken or outdated links
**Risk:** Project links may become invalid over time as resources move or are discontinued.
**Mitigation:**
- Regular link validation in CI/CD pipeline
- Documentation of link maintenance procedures
- Automated checking during release process
- Community reporting for broken links

### Risk: Inconsistent information across platforms
**Risk:** Information may become inconsistent between PyPI, GitHub, and documentation.
**Mitigation:**
- Single source of truth for project metadata
- Automated synchronization where possible
- Regular review and update procedures
- Clear ownership and responsibility for updates

### Risk: Over-maintenance burden
**Risk:** Frequent updates may create maintenance overhead.
**Mitigation:**
- Focus on essential links and metadata
- Automated validation where possible
- Clear prioritization of link importance
- Community contribution for updates

## Migration Plan

### Phase 1: Basic Project Links
1. Add `[project.urls]` section to `pyproject.toml`
2. Include Homepage, Repository, Documentation, and Changelog links
3. Validate syntax and package build
4. Test with test PyPI for verification

### Phase 2: Community and Support Links
1. Add Issues, Discussions, and Security Policy links
2. Create or update contributing guidelines if needed
3. Ensure GitHub repository has appropriate setup
4. Test link accessibility and correctness

### Phase 3: Enhanced Metadata
1. Review and improve project description and keywords
2. Update classifiers for better categorization
3. Add author and maintainer information
4. Validate enhanced metadata displays correctly

### Phase 4: Badge and Status Integration
1. Add appropriate badges to README.md
2. Ensure badge links point to correct services
3. Test badge rendering and accessibility
4. Validate CI/CD integration for badge updates

### Rollback Plan
- Links can be easily removed from `pyproject.toml`
- Previous package versions remain available
- README badges can be reverted to previous state
- No breaking changes to package functionality

## Open Questions

### Q1: Should we include funding/donation links?
**Consideration:** Some projects include donation links to support development.

**Current approach:** Focus on essential project links first, consider funding links in future based on project needs and community feedback.

### Q2: How to handle multiple documentation versions?
**Consideration:** Documentation sites may have multiple versions (latest, v1.0, etc.).

**Current approach:** Link to main documentation site with version selection handled by the documentation system.

### Q3: Should we link to external services beyond GitHub?
**Consideration:** Some projects link to external services like Discord, Stack Overflow, etc.

**Current approach:** Start with essential project links, consider additional community links based on community needs and engagement patterns.

### Q4: How to handle project name changes or reorganizations?
**Consideration:** Projects may rename or reorganize over time.

**Current approach:** Use stable GitHub repository URL as primary reference point, with redirects for renamed projects.

### Q5: Should we include API reference links?
**Consideration:** Some projects link to API documentation directly.

**Current approach:** Link to main documentation site which includes API reference, rather than direct API links for simplicity.

## Success Metrics

- 100% of essential project links working and accessible
- PyPI package page shows complete and professional metadata
- Package discovered through improved search ranking and keywords
- Reduced support burden due to clear documentation links
- Improved contribution rates due to clear contribution guidelines

## Next Steps

1. **Review:** Stakeholder review of proposed link structure
2. **Implementation:** Add links to pyproject.toml following the plan
3. **Testing:** Validate with test PyPI and documentation site
4. **Integration:** Update badges and cross-references
5. **Documentation:** Update any project documentation about metadata

## Security and Privacy Considerations

- Ensure all links use HTTPS where available
- Validate that external services respect privacy
- Avoid linking to services that require authentication
- Ensure GitHub security features are properly linked
- Consider privacy implications of external service links

This design provides a comprehensive approach to enhancing the Duckalog project's metadata and links while maintaining focus on user experience and community engagement.
