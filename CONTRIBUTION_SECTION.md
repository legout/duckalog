---

## Contributing

We welcome contributions to duckalog! This section provides guidelines and instructions for contributing to the project.

### Development Setup

**Requirements:** Python 3.9 or newer

#### Using uv (recommended for development)

```bash
# Clone the repository
git clone https://github.com/legout/duckalog.git
cd duckalog

# Install in development mode
uv pip install -e .
```

#### Using pip

```bash
# Clone the repository
git clone https://github.com/legout/duckalog.git
cd duckalog

# Install in development mode
pip install -e .
```

#### Install development dependencies

```bash
# Using uv
uv pip install -e ".[dev]"

# Using pip
pip install -e ".[dev]"
```

### Coding Standards

We follow the conventions documented in [`openspec/project.md`](openspec/project.md):

- **Python Style**: Follow PEP 8 with type hints on public functions and classes
- **Module Structure**: Prefer small, focused modules over large monoliths
- **Configuration**: Use Pydantic models as the single source of truth for config schemas
- **Architecture**: Separate concerns between config, SQL generation, and engine layers
- **Naming**: Use descriptive, domain-aligned names (e.g., `AttachmentConfig`, `ViewConfig`)
- **Testing**: Keep core logic pure and testable; isolate I/O operations

### Testing

We use pytest for testing. The test suite includes both unit and integration tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=duckalog

# Run specific test file
pytest tests/test_config.py
```

**Testing Strategy:**
- **Unit tests**: Config parsing, validation, and SQL generation
- **Integration tests**: End-to-end catalog building with temporary DuckDB files
- **Deterministic tests**: Avoid network dependencies unless explicitly required
- **Test-driven development**: Add tests for new behaviors before implementation

### Change Proposal Process

For significant changes, we use OpenSpec to manage proposals and specifications:

1. **Create a change proposal**: Use the OpenSpec CLI to create a new change
   ```bash
   openspec new "your-change-description"
   ```

2. **Define requirements**: Write specs with clear requirements and scenarios in `changes/<id>/specs/`

3. **Plan implementation**: Break down the work into tasks in `changes/<id>/tasks.md`

4. **Validate your proposal**: Ensure it meets project standards
   ```bash
   openspec validate <change-id> --strict
   ```

5. **Implement and test**: Work through the tasks sequentially

See [`openspec/project.md`](openspec/project.md) for detailed project conventions and the OpenSpec workflow.

### Pull Request Guidelines

When submitting pull requests:

1. **Branch naming**: Use small, focused branches with the OpenSpec change-id (e.g., `add-s3-parquet-support`)

2. **Commit messages**: 
   - Keep spec changes (`openspec/`, `docs/`) and implementation changes (`src/`, `tests/`) clear
   - Reference relevant OpenSpec change IDs in PR titles or first commit messages

3. **PR description**: Include a clear description of the change and link to relevant OpenSpec proposals

4. **Testing**: Ensure all tests pass and add new tests for new functionality

5. **Review process**: Be responsive to review feedback and address all comments

We prefer incremental, reviewable PRs over large multi-feature changes.

### Getting Help

- **Project Documentation**: See [`docs/PRD_Spec.md`](docs/PRD_Spec.md) for the full product and technical specification
- **Project Conventions**: Refer to [`openspec/project.md`](openspec/project.md) for detailed development guidelines
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/legout/duckalog/issues)
- **Discussions**: Join project discussions on [GitHub Discussions](https://github.com/legout/duckalog/discussions)

Thank you for contributing to duckalog! 🚀