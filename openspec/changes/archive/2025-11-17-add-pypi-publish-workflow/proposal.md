# Change: Add PyPI Publish GitHub Workflow

## Why
The Duckalog project currently lacks automated packaging and publishing capabilities to PyPI. This means:

- Manual publishing process is error-prone and time-consuming
- No automated release pipeline based on Git tags or version changes
- Risk of inconsistent versioning between code and package metadata
- Limited discoverability for users who want to install via pip
- No automated testing of the packaging process before release

A PyPI publish workflow will enable automated, reproducible releases that trigger on version tags, ensuring consistent and reliable package distribution to the Python community.

## What Changes
- Add `.github/workflows/publish.yml` for automated PyPI publishing
- Configure workflow to trigger on version tags (v*.*.*)
- Include proper Python version matrix testing (3.9, 3.10, 3.11, 3.12)
- Add build and test steps before publishing
- Configure PyPI credentials via GitHub Secrets
- Include package validation and integrity checks
- Add workflow_dispatch capability for manual releases
- Implement proper error handling and rollback mechanisms

## Impact
- Affected specs: Package distribution capability (new)
- Affected code: GitHub workflows directory, CI/CD pipeline
- Benefits: Automated releases, consistent versioning, improved user experience
- Breaking changes: None - adds new capability without affecting existing functionality

```

```
# Change Implementation Tasks: Add PyPI Publish Workflow

## 1. Workflow File Creation
- [ ] 1.1 Create `.github/workflows/publish.yml` with basic structure
- [ ] 1.2 Configure GitHub Actions triggers for version tags (v*.*.*)
- [ ] 1.3 Set up Python version matrix for testing (3.9-3.12)
- [ ] 1.4 Add checkout and setup-python actions
- [ ] 1.5 Configure pip/uv package manager usage

## 2. Build and Test Pipeline
- [ ] 2.1 Add project dependency installation steps
- [ ] 2.2 Include source distribution (sdist) build process
- [ ] 2.3 Add wheel build for universal package
- [ ] 2.4 Include basic smoke tests for the built package
- [ ] 2.5 Add package validation checks (twine check)

## 3. PyPI Publishing Configuration
- [ ] 3.1 Configure PyPI publishing action with proper credentials
- [ ] 3.2 Set up GitHub Secrets documentation (PYPI_API_TOKEN)
- [ ] 3.3 Add conditional publishing (only on tagged releases)
- [ ] 3.4 Include test PyPI publishing option for pre-releases
- [ ] 3.5 Add proper environment isolation and cleanup

## 4. Security and Quality Checks
- [ ] 4.1 Add package signature verification (if applicable)
- [ ] 4.2 Include vulnerability scanning of dependencies
- [ ] 4.3 Add license compliance checks
- [ ] 4.4 Configure safe credential handling (secrets management)
- [ ] 4.5 Add workflow permissions and security hardening

## 5. Manual Release Capability
- [ ] 5.1 Add workflow_dispatch for manual trigger
- [ ] 5.2 Create manual release parameters (version, channel)
- [ ] 5.3 Add confirmation prompts for production releases
- [ ] 5.4 Include rollback capabilities for failed releases
- [ ] 5.5 Add release notes generation integration

## 6. Documentation and Setup
- [ ] 6.1 Update README.md with installation instructions
- [ ] 6.2 Add PyPI badge/status to repository
- [ ] 6.3 Create release process documentation
- [ ] 6.4 Update project documentation with publishing information
- [ ] 6.5 Add troubleshooting guide for common release issues

## 7. Testing and Validation
- [ ] 7.1 Test workflow with a dry-run or test PyPI
- [ ] 7.2 Validate package installation from test PyPI
- [ ] 7.3 Verify version tagging and triggering works correctly
- [ ] 7.4 Test manual dispatch functionality
- [ ] 7.5 Validate error handling and failure scenarios

## 8. Integration with Existing CI
- [ ] 8.1 Review existing GitHub Actions and workflows
- [ ] 8.2 Ensure no conflicts with current CI/CD setup
- [ ] 8.3 Add workflow dependencies and prerequisites
- [ ] 8.4 Configure proper job dependencies and parallelism
- [ ] 8.5 Update any existing release documentation

## 9. Monitoring and Alerts
- [ ] 9.1 Add workflow status notifications (optional)
- [ ] 9.2 Configure failure alerts for publish pipeline
- [ ] 9.3 Add success notifications with release details
- [ ] 9.4 Include metrics collection for release frequency
- [ ] 9.5 Set up monitoring for PyPI package health

## 10. Final Integration and Validation
- [ ] 10.1 Perform end-to-end test of complete workflow
- [ ] 10.2 Validate GitHub Secrets configuration
- [ ] 10.3 Test with actual version tag creation
- [ ] 10.4 Verify PyPI package availability post-release
- [ ] 10.5 Get stakeholder review and approval

```

```
## ADDED Requirements
### Requirement: Automated PyPI Publishing Workflow
The project SHALL provide a GitHub Actions workflow that automatically publishes the package to PyPI when version tags are created.

#### Scenario: Automatic release on version tag
- **WHEN** a developer creates a version tag (e.g., v1.0.0) and pushes it to the main branch
- **THEN** the GitHub Actions workflow triggers, builds the package, runs tests, and publishes to PyPI

#### Scenario: Manual release capability
- **WHEN** a developer needs to trigger a release manually without creating a tag
- **THEN** they can use the workflow_dispatch feature to initiate publishing with specified parameters

#### Scenario: Package validation before publish
- **WHEN** the workflow runs the build process
- **THEN** it SHALL validate the package using twine check and run basic smoke tests before attempting to publish

### Requirement: Multi-Python Version Support
The publishing workflow SHALL test and build the package across multiple Python versions to ensure compatibility.

#### Scenario: Cross-version compatibility testing
- **WHEN** the workflow executes on Python versions 3.9, 3.10, 3.11, and 3.12
- **THEN** it SHALL successfully build and test the package on all specified versions

#### Scenario: Version matrix reporting
- **WHEN** the workflow runs across the Python version matrix
- **THEN** it SHALL provide clear status indicators for each Python version tested

### Requirement: Secure Credential Management
The PyPI publishing workflow SHALL use secure methods for handling PyPI credentials and API tokens.

#### Scenario: GitHub Secrets usage
- **WHEN** the workflow needs to authenticate with PyPI
- **THEN** it SHALL use GitHub Secrets (specifically PYPI_API_TOKEN) and never expose credentials in logs or error messages

#### Scenario: Secure token handling
- **WHEN** the workflow accesses PyPI credentials
- **THEN** it SHALL use the official PyPI publishing action which securely handles API tokens without logging sensitive information

### Requirement: Release Validation and Error Handling
The publishing workflow SHALL include proper validation and error handling to prevent failed releases.

#### Scenario: Package validation failure
- **WHEN** the package fails validation checks (twine check, tests, etc.)
- **THEN** the workflow SHALL stop the publishing process and provide clear error messages

#### Scenario: Network or API failures
- **WHEN** PyPI API calls fail due to network issues or API problems
- **THEN** the workflow SHALL retry appropriate operations and provide meaningful error messages for manual intervention

### Requirement: Package Build and Distribution
The workflow SHALL build both source distribution (sdist) and wheel distributions for optimal package compatibility.

#### Scenario: Universal wheel building
- **WHEN** the workflow builds the package
- **THEN** it SHALL create both sdist and wheel formats to support different installation methods

#### Scenario: Package integrity verification
- **WHEN** the package is built successfully
- **THEN** the workflow SHALL verify package integrity using twine check before attempting to publish

### Requirement: Release Documentation Integration
The publishing workflow SHALL integrate with existing project documentation and release processes.

#### Scenario: Documentation updates
- **WHEN** a new version is published
- **THEN** the workflow SHALL trigger any necessary documentation updates (if configured) and provide release information

#### Scenario: Installation instructions
- **WHEN** users want to install the package
- **THEN** the README and documentation SHALL include clear pip install instructions using the published PyPI package name

```

```
# Design Document: PyPI Publishing Workflow for Duckalog

## Context

Duckalog is a Python library and CLI for building DuckDB catalogs from declarative configuration files. The project currently has:
- Complete source code structure in `src/duckalog/`
- Proper `pyproject.toml` configuration with setuptools build system
- Version `0.1.0` defined in project metadata
- CLI entry point configured as `duckalog`
- GitHub repository with existing CI/CD structure

However, the project lacks automated packaging and distribution to PyPI, which limits discoverability and creates manual overhead for releases. Users currently need to install from source or GitHub releases rather than using standard `pip install duckalog`.

**Stakeholders:**
- Core developers who need to release new versions
- Users who want to install via pip
- DevOps team managing release processes
- Package maintainers ensuring security and quality

## Goals / Non-Goals

### Goals
- Automate the complete PyPI publishing process
- Ensure consistent and reproducible releases
- Maintain security best practices for credential handling
- Support both automatic and manual release triggers
- Validate package integrity before publishing
- Provide clear installation instructions for users

### Non-Goals
- Modify existing code architecture or functionality
- Create additional package formats beyond standard PyPI standards
- Implement complex release branching strategies
- Add付费 distribution channels
- Modify the core DuckDB integration or functionality

## Decisions

### Decision: Use GitHub Actions for PyPI publishing
**What:** Create `.github/workflows/publish.yml` using GitHub's official PyPI publishing action.

**Why:**
- Native integration with GitHub repository
- Secure credential management through GitHub Secrets
- Built-in triggers for version tags and manual dispatch
- Free for public repositories
- Comprehensive ecosystem and community support
- Built-in error handling and retry mechanisms

**Alternatives considered:**
- Travis CI or CircleCI → Additional configuration complexity
- Dedicated publishing tools → More moving parts to maintain
- Manual publishing → Error-prone and time-consuming
- GitHub Releases only → Limits discoverability for pip users

### Decision: Trigger on version tags with manual override
**What:** Configure workflow to trigger on `v*.*.*` tags with additional `workflow_dispatch` for manual control.

**Why:**
- Conventional version tagging follows semantic versioning best practices
- Manual override provides flexibility for hotfixes or special releases
- GitHub Actions `workflow_dispatch` enables controlled manual releases
- Reduces risk of accidental releases while maintaining automation

**Alternatives considered:**
- Trigger on all pushes → Too broad, risks unwanted releases
- Manual only → Loses automation benefits
- Release branch triggers → Additional complexity without clear benefit

### Decision: Multi-Python version testing matrix
**What:** Test building and publishing across Python 3.9, 3.10, 3.11, and 3.12.

**Why:**
- Ensures compatibility across supported Python versions
- Follows Python community standards for compatibility testing
- Catches version-specific issues before publication
- Provides confidence to users on different Python versions

**Alternatives considered:**
- Single Python version testing → May miss compatibility issues
- Extensive version matrix → Unnecessary complexity and resource usage

### Decision: Use PyPI Trusted Publishers (recommended approach)
**What:** Configure PyPI trusted publishing to use GitHub Actions OIDC for authentication.

**Why:**
- Most secure approach - no long-lived API tokens needed
- Automatic token rotation and management
- Reduced security risk from credential exposure
- Industry best practice for modern CI/CD

**Alternatives considered:**
- API tokens in GitHub Secrets → Requires manual token rotation
- Username/password authentication → Deprecated and insecure

## Risks / Trade-offs

### Risk: Accidental releases from tag confusion
**Risk:** Developers might accidentally create version tags that trigger unwanted releases.
**Mitigation:**
- Clear documentation on version tagging conventions
- Use `workflow_dispatch` for testing releases to test PyPI
- Implement pre-release testing workflows
- Require PR reviews for version bumps

### Risk: PyPI API rate limiting or downtime
**Risk:** External dependency on PyPI availability could cause release failures.
**Mitigation:**
- Implement retry logic with exponential backoff
- Clear error messages for manual intervention
- Consider test PyPI workflow for validation

### Risk: Package validation failures
**Risk:** Built packages might fail validation checks or have compatibility issues.
**Mitigation:**
- Comprehensive testing before publish
- Use `twine check` for package validation
- Smoke test installation from built packages
- Rollback capabilities for failed releases

### Risk: Security vulnerabilities in dependencies
**Risk:** Published packages might include vulnerable dependencies.
**Mitigation:**
- Include dependency scanning in workflow
- Regular security updates in development process
- Use dependabot or similar tools for automated updates

## Migration Plan

### Phase 1: Basic Workflow Setup
1. Create `.github/workflows/publish.yml` with basic structure
2. Configure Python version matrix (3.9-3.12)
3. Add build and test steps
4. Configure PyPI trusted publishing or API token authentication

### Phase 2: Security and Validation
1. Implement package validation using `twine check`
2. Add dependency scanning and security checks
3. Configure GitHub Secrets for PyPI authentication
4. Test workflow with dry-run to test PyPI

### Phase 3: Manual Release Capability
1. Add `workflow_dispatch` for manual releases
2. Create confirmation prompts for production releases
3. Implement rollback mechanisms
4. Add release notes integration (if desired)

### Phase 4: Documentation and Integration
1. Update README.md with pip installation instructions
2. Add PyPI badge to repository
3. Create release process documentation
4. Update project documentation with publishing information

### Rollback Plan
- Workflow can be disabled by removing or renaming the workflow file
- GitHub Secrets can be revoked to prevent unauthorized publishing
- Previous package versions remain available on PyPI
- Source distribution remains available through GitHub releases

## Open Questions

### Q1: Should we use test PyPI for testing releases?
**Consideration:** Using test PyPI for validation prevents polluting production PyPI with test packages.

**Current approach:** Include test PyPI publishing as optional step for validation, with manual approval for production.

### Q2: How to handle pre-release versions (alpha, beta, rc)?
**Consideration:** Different pre-release conventions might need different handling.

**Current approach:** Focus on production releases initially, consider pre-release handling in future iteration based on project needs.

### Q3: Should we integrate with existing CI workflows?
**Consideration:** Current project might have existing testing workflows that could be extended.

**Current approach:** Keep publishing workflow separate initially to maintain clarity and avoid complex dependencies.

### Q4: How to handle version consistency between code and pyproject.toml?
**Consideration:** Version mismatches could cause publishing failures.

**Current approach:** Use version from `pyproject.toml` as single source of truth, with validation checks.

### Q5: Should we automatically create GitHub Releases alongside PyPI publishing?
**Consideration:** Coordinated releases could improve user experience.

**Current approach:** Start with PyPI publishing only, evaluate GitHub Release integration based on user feedback.

## Success Metrics

- Zero manual publishing steps required for production releases
- 100% successful package builds across supported Python versions
- Clear installation instructions lead to successful pip installations
- Release process completes within 10 minutes from tag creation
- Zero security incidents related to credential handling

## Next Steps

1. **Setup:** Configure PyPI trusted publishing or create API token
2. **Implementation:** Create workflow file following design specifications
3. **Testing:** Validate workflow with test PyPI and mock scenarios
4. **Documentation:** Update README and project documentation
5. **Validation:** Test complete end-to-end release process

## Security Considerations

### Credential Management
- Use PyPI trusted publishers (OIDC) when possible
- If using API tokens, store in GitHub Secrets only
- Never log or expose credentials in workflow logs
- Rotate tokens regularly

### Access Control
- Limit workflow permissions to minimum required
- Use `permissions` configuration to restrict access
- Require approvals for production releases (if desired)

### Package Integrity
- Validate packages before publishing
- Use checksums for package verification
- Include basic security scanning of dependencies

This design provides a robust, secure, and maintainable approach to automated PyPI publishing for the Duckalog project.