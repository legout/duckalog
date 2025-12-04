# Spec: Examples Structure

## Summary
Define the new directory structure and naming conventions for the examples ecosystem.

## ADDED Requirements

### Requirement: Numbered Category System
The examples **SHALL** use a numbered category system for clear learning progression.

#### Scenario: Category Structure
```
examples/
├── 01-getting-started/
├── 02-intermediate/
├── 03-advanced/
├── 04-external-services/
├── 05-use-cases/
└── playground/
```

**Scenario: Sorting**
When users list the examples directory, the categories appear in learning order due to numerical prefixes.

---

### Requirement: Consistent Example Template
Each example **SHALL** follow a consistent directory template.

#### Scenario: Template Structure
Every example directory contains:
- `README.md` - Documentation with what, prerequisites, quick start
- `catalog.yaml` - Duckalog configuration
- `setup.py` - Data generation script
- `data/.gitkeep` - Empty directory for generated files
- Optional `sql/` directory - For external SQL files
- Optional `Makefile` - For docker-based examples

**Scenario: README Content**
README.md must include:
- One-sentence description of what the example demonstrates
- Prerequisites section
- Quick start section with 3-5 commands maximum
- Expected output description
- Key concepts highlighted
- Next steps recommendations

---

### Requirement: Shared Utilities
A shared utilities directory **SHALL** exist for common functionality.

#### Scenario: Shared Directory
```
examples/_shared/
├── data_generators/
│   ├── __init__.py
│   ├── users.py
│   ├── events.py
│   ├── sales.py
│   └── timeseries.py
└── utils.py
```

**Scenario: Data Generators**
All examples use shared data generators from `_shared/data_generators/` instead of creating their own data generation logic.

**Scenario: No Pre-built Data**
Data directories contain only `.gitkeep` files. All data must be generated via `setup.py` scripts.

---

### Requirement: Main README
A main README.md in the examples root **SHALL** provide learning path guidance.

#### Scenario: Learning Path
The README includes:
- Overview of each category
- Prerequisites for all examples
- Quick start guide
- Suggested learning sequence
- Links to each category

---

## MODIFIED Requirements

### Requirement: Git Ignore Patterns
Existing gitignore patterns **SHALL** be extended to exclude generated data.

#### Scenario: Excluded Patterns
The following patterns must be excluded from git:
- `examples/*/data/*.parquet`
- `examples/*/data/*.duckdb`
- `examples/*/data/*.csv`
- `examples/*/data/*.db`

---

## REMOVED Requirements

### Requirement: Old Folder Structure
The old examples folder structure **SHALL** be removed.

#### Scenario: Deleted Directories
The following directories are deleted:
- `semantic_layer_v2/`
- `production-operations/`
- `business-intelligence/`
- `data-integration/`
- `simple_parquet/`

**Scenario: Deleted Files**
The following files are deleted:
- All pre-built `.duckdb` files
- All pre-built `.parquet` files
- All pre-built `.db` files
- `sql-file-references-example.yaml`
- `production-operations/ci-cd-integration/`

---

## Validation

**Check: Directory Structure**
```bash
ls examples/
# Expected: README.md, _shared/, 01-getting-started/, 02-intermediate/, 03-advanced/, 04-external-services/, 05-use-cases/, playground/
```

**Check: Example Template**
```bash
ls examples/01-getting-started/01-parquet-basics/
# Expected: README.md, catalog.yaml, setup.py, data/.gitkeep
```

**Check: Git Ignore**
```bash
git status examples/
# Expected: No untracked data files
```
