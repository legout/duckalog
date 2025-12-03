# Contributing Examples

This guide explains how to create high-quality examples for the Duckalog examples library.

## Example Requirements

### Standard Structure

Every example MUST include:

```
[example-name]/
├── README.md              # Business context and setup
├── catalog.yaml           # Duckalog configuration
├── data/
│   └── generate.py        # Data generation script
└── validate.py            # Validation script
```

### README.md Template

```markdown
# [Example Name]

[Category: Business Intelligence/Data Integration/Production/Advanced]
[Difficulty: Level 1/2/3/4]

## Business Context

[Brief description of the real-world business problem this example solves]

## What You'll Learn

- [Learning objective 1]
- [Learning objective 2]
- [Key Duckalog feature demonstrated]

## Prerequisites

- [Required knowledge/skills]
- [System requirements]
- [External dependencies]

## Setup Instructions

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Results

[Description of what users should see after running the example]

## Learning Path

- **Next examples**: [Related examples to try next]
- **Prerequisites**: [Examples to complete first]
```

### Data Generation Script Standards

- **Deterministic**: Same inputs produce same outputs
- **Parameterized**: Support different data sizes/configurations
- **Documented**: Clear schema and business rules
- **Validated**: Include data quality checks

```python
#!/usr/bin/env python3
"""
Data generation for [example-name].

Usage: python generate.py [--rows 10000] [--output data/]
"""

import argparse
import polars as pl
import random
from datetime import datetime, timedelta

def generate_data(rows: int, output_dir: str):
    """Generate synthetic data for the example."""
    records = [
        {
            "id": i,
            "value": random.random(),
            "created_at": datetime.utcnow(),
        }
        for i in range(rows)
    ]
    df = pl.DataFrame(records)
    pl.Config.set_tbl_rows(5)
    df.write_parquet(f"{output_dir}/data.parquet", compression="zstd")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate example data")
    parser.add_argument("--rows", type=int, default=10000, help="Number of rows to generate")
    parser.add_argument("--output", type=str, default="data/", help="Output directory")
    args = parser.parse_args()

    generate_data(args.rows, args.output)
```

### Validation Script Standards

```python
#!/usr/bin/env python3
"""
Validation script for [example-name].

Ensures the example works correctly and produces expected results.
"""

import sys
from pathlib import Path
from duckalog import load_config

def validate_example():
    """Validate the example functionality."""
    try:
        # Load and validate configuration
        config = load_config("catalog.yaml")
        print("✅ Configuration validation passed")

        # Check expected views exist
        expected_views = ["view1", "view2"]  # Replace with actual views
        # Implementation here

        # Validate data quality
        # Implementation here

        print("✅ All validations passed")
        return True

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    success = validate_example()
    sys.exit(0 if success else 1)
```

## Quality Standards

### Code Quality
- **Python 3.12+** compatibility
- **Type hints** on public functions
- **Error handling** with clear messages
- **No external dependencies** beyond Duckalog and common libraries

### Data Quality
- **Synthetic data** only (no real user/business data)
- **Realistic patterns** that represent actual business scenarios
- **Deterministic generation** for reproducible results
- **Documentation** of schema and business rules

### Documentation Quality
- **Business context** explaining the real-world problem
- **Learning objectives** clearly stated
- **Setup instructions** that work consistently
- **Expected results** users should see

## Submission Process

1. **Create example** following standards above
2. **Test locally** with `python validate.py`
3. **Update examples index** in main README.md
4. **Submit PR** with description of the example
5. **Code review** by maintainers
6. **Merge** and celebrate!

## Review Criteria

Examples are evaluated on:

- ✅ **Business relevance**: Solves real-world problems
- ✅ **Educational value**: Clear learning objectives
- ✅ **Code quality**: Clean, documented, tested
- ✅ **Consistency**: Follows template and standards
- ✅ **Functionality**: Works as documented
- ✅ **Performance**: Reasonable execution time and resources

## Getting Help

- Check existing examples for patterns
- Ask questions in GitHub discussions
- Review the contribution guidelines
- Contact maintainers for clarification
