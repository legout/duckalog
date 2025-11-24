#!/usr/bin/env python3
"""
Configuration validation script for Duckalog CI/CD pipeline.

This script validates Duckalog configurations across different environments,
ensuring consistency and correctness before deployment.

Usage: python validate-configs.py [--environment ENV] [--strict]
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml

    from duckalog import ConfigError, load_config
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install with: pip install duckalog pyyaml")
    sys.exit(1)


class ConfigValidator:
    """Validates Duckalog configurations across environments."""

    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self, environment: str = None, strict: bool = False) -> bool:
        """Validate all configurations."""
        print("🔍 Starting configuration validation...")

        if environment:
            return self._validate_environment(environment, strict)
        else:
            # Validate all environments
            environments = self._get_environments()
            success = True

            for env in environments:
                env_success = self._validate_environment(env, strict)
                success = success and env_success

            if len(environments) > 1:
                self._validate_cross_environment_consistency()

            return success

    def _get_environments(self) -> List[str]:
        """Get list of available environments."""
        if not self.config_dir.exists():
            self.errors.append(f"Configuration directory not found: {self.config_dir}")
            return []

        environments = []
        for config_file in self.config_dir.glob("catalog-*.yaml"):
            env = config_file.stem.replace("catalog-", "")
            environments.append(env)

        return sorted(environments)

    def _validate_environment(self, environment: str, strict: bool = False) -> bool:
        """Validate a specific environment configuration."""
        print(f"\n📋 Validating {environment} environment...")

        config_path = self.config_dir / f"catalog-{environment}.yaml"

        if not config_path.exists():
            self.errors.append(f"Configuration file not found: {config_path}")
            return False

        try:
            # Load and validate configuration
            config = load_config(str(config_path))
            print(f"  ✅ Configuration syntax valid for {environment}")

            # Validate content
            self._validate_config_content(config, environment, strict)

            # Validate data sources
            self._validate_data_sources(config, environment)

            # Validate semantic models if present
            if hasattr(config, "semantic_models") and config.semantic_models:
                self._validate_semantic_models(config, environment)

            return len(self.errors) == 0

        except ConfigError as e:
            self.errors.append(
                f"Configuration validation failed for {environment}: {e}"
            )
            return False
        except Exception as e:
            self.errors.append(f"Unexpected error validating {environment}: {e}")
            return False

    def _validate_config_content(self, config: Any, environment: str, strict: bool):
        """Validate configuration content."""
        # Check required sections
        if not hasattr(config, "duckdb") or not config.duckdb:
            self.errors.append(f"Missing duckdb configuration in {environment}")

        if not hasattr(config, "views") or not config.views:
            self.warnings.append(f"No views defined in {environment}")

        if strict and len(config.views) == 0:
            self.errors.append(f"Strict mode: No views defined in {environment}")

        # Validate views
        for i, view in enumerate(config.views):
            if not hasattr(view, "name") or not view.name:
                self.errors.append(f"View {i} missing name in {environment}")

            if not hasattr(view, "sql") and not hasattr(view, "source"):
                self.errors.append(
                    f"View {view.name} missing sql or source in {environment}"
                )

            # Check for SQL injection patterns in strict mode
            if strict and hasattr(view, "sql") and view.sql:
                dangerous_patterns = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]
                sql_upper = view.sql.upper()
                for pattern in dangerous_patterns:
                    if pattern in sql_upper:
                        self.errors.append(
                            f"View {view.name} contains dangerous SQL pattern: {pattern}"
                        )

        print(f"  ✅ Content validation completed for {environment}")

    def _validate_data_sources(self, config: Any, environment: str):
        """Validate data source configurations."""
        print(f"  🔍 Checking data sources for {environment}...")

        missing_files = []
        for view in config.views:
            if hasattr(view, "source") and view.source in ["parquet", "csv", "json"]:
                if hasattr(view, "uri") and view.uri:
                    # Check if data file exists (relative to project root)
                    uri_path = Path(view.uri)
                    if not uri_path.exists():
                        missing_files.append(f"{view.name}: {view.uri}")

        if missing_files:
            self.warnings.append(
                f"Data files not found in {environment}: {missing_files}"
            )
        else:
            print(f"  ✅ All data sources accessible for {environment}")

    def _validate_semantic_models(self, config: Any, environment: str):
        """Validate semantic model configurations."""
        print(f"  🔍 Checking semantic models for {environment}...")

        for model in config.semantic_models:
            # Check if base view exists
            base_view_names = {view.name for view in config.views}
            if model.base_view not in base_view_names:
                self.errors.append(
                    f"Semantic model {model.name} references non-existent base view: {model.base_view}"
                )

            # Validate dimensions
            for dimension in model.dimensions:
                if not hasattr(dimension, "name") or not dimension.name:
                    self.errors.append(f"Dimension missing name in model {model.name}")
                if not hasattr(dimension, "expression") or not dimension.expression:
                    self.errors.append(
                        f"Dimension {dimension.name} missing expression in model {model.name}"
                    )

            # Validate measures
            for measure in model.measures:
                if not hasattr(measure, "name") or not measure.name:
                    self.errors.append(f"Measure missing name in model {model.name}")
                if not hasattr(measure, "expression") or not measure.expression:
                    self.errors.append(
                        f"Measure {measure.name} missing expression in model {model.name}"
                    )

        print(f"  ✅ Semantic models validation completed for {environment}")

    def _validate_cross_environment_consistency(self):
        """Validate consistency across environments."""
        print("\n🔍 Checking cross-environment consistency...")

        environments = self._get_environments()
        if len(environments) < 2:
            return

        # Load all configurations
        configs = {}
        for env in environments:
            try:
                config_path = self.config_dir / f"catalog-{env}.yaml"
                configs[env] = load_config(str(config_path))
            except Exception as e:
                self.errors.append(f"Failed to load {env} configuration: {e}")
                return

        # Check view consistency
        base_views = {
            view.name: view
            for view in configs.get("dev", configs[environments[0]]).views
        }

        for env in environments[1:]:
            env_views = {view.name: view for view in configs[env].views}

            # Check for missing views
            missing_views = set(base_views.keys()) - set(env_views.keys())
            if missing_views:
                self.warnings.append(f"Views missing in {env}: {missing_views}")

            # Check for extra views
            extra_views = set(env_views.keys()) - set(base_views.keys())
            if extra_views:
                self.warnings.append(f"Extra views in {env}: {extra_views}")

        print("  ✅ Cross-environment consistency check completed")

    def print_results(self):
        """Print validation results."""
        print("\n" + "=" * 50)
        print("VALIDATION RESULTS")
        print("=" * 50)

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All validations passed!")
        elif not self.errors:
            print(f"\n✅ No errors found ({len(self.warnings)} warnings)")

        print(f"\nSummary: {len(self.errors)} errors, {len(self.warnings)} warnings")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Validate Duckalog configurations")
    parser.add_argument(
        "--environment",
        "-e",
        help="Specific environment to validate (dev, staging, prod)",
    )
    parser.add_argument(
        "--config-dir", "-c", default="configs", help="Configuration directory path"
    )
    parser.add_argument(
        "--strict", "-s", action="store_true", help="Enable strict validation mode"
    )
    parser.add_argument("--output", "-o", help="Output results to JSON file")

    args = parser.parse_args()

    # Create validator and run validation
    validator = ConfigValidator(args.config_dir)
    success = validator.validate_all(args.environment, args.strict)

    # Print results
    validator.print_results()

    # Save results to file if requested
    if args.output:
        results = {
            "success": success,
            "errors": validator.errors,
            "warnings": validator.warnings,
        }
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Results saved to {args.output}")

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
