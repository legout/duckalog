#!/usr/bin/env python3
"""
Validation script for Duckalog CI/CD example.

This script validates the complete CI/CD example setup, including
configurations, data generation, and basic functionality tests.

Usage: python validate.py [--environment ENV] [--verbose]
"""

import argparse
import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List

try:
    import duckdb
    import pandas as pd

    from duckalog import build_catalog, load_config
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install with: pip install duckalog pandas")
    sys.exit(1)


class CIExampleValidator:
    """Validates the CI/CD integration example."""

    def __init__(self, example_dir: str = "."):
        self.example_dir = Path(example_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.success_count = 0
        self.total_tests = 0

    def validate_all(self, environment: str = "dev", verbose: bool = False) -> bool:
        """Run all validation tests."""
        print("🔍 Starting CI/CD example validation...")
        print(f"📁 Example directory: {self.example_dir.absolute()}")
        print(f"🌍 Environment: {environment}")

        # Run validation tests
        tests = [
            ("Directory Structure", self._validate_directory_structure),
            ("Configuration Files", self._validate_configurations),
            ("Data Generation", self._validate_data_generation),
            ("Docker Configuration", self._validate_docker_setup),
            ("GitHub Actions Workflows", self._validate_github_actions),
            ("Scripts", self._validate_scripts),
            ("Catalog Building", self._validate_catalog_building),
            ("Data Quality", self._validate_data_quality),
        ]

        for test_name, test_func in tests:
            self.total_tests += 1
            if verbose:
                print(f"\n🧪 Running test: {test_name}")

            try:
                if test_func(environment):
                    self.success_count += 1
                    print(f"  ✅ {test_name} - PASSED")
                else:
                    print(f"  ❌ {test_name} - FAILED")
            except Exception as e:
                print(f"  ❌ {test_name} - ERROR: {e}")
                if verbose:
                    traceback.print_exc()

        return self._print_results()

    def _validate_directory_structure(self, environment: str) -> bool:
        """Validate required directory structure."""
        required_dirs = ["configs", "data", "scripts", "docker", ".github/workflows"]

        missing_dirs = []
        for dir_path in required_dirs:
            full_path = self.example_dir / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)

        if missing_dirs:
            self.errors.append(f"Missing directories: {missing_dirs}")
            return False

        return True

    def _validate_configurations(self, environment: str) -> bool:
        """Validate configuration files."""
        config_file = self.example_dir / "configs" / f"catalog-{environment}.yaml"

        if not config_file.exists():
            self.errors.append(f"Configuration file not found: {config_file}")
            return False

        try:
            config = load_config(str(config_file))

            # Basic validation
            if not hasattr(config, "duckdb") or not config.duckdb:
                self.errors.append("Missing duckdb configuration")
                return False

            if not hasattr(config, "views") or not config.views:
                self.warnings.append("No views defined in configuration")

            print(
                f"    📋 Configuration loaded successfully ({len(config.views)} views)"
            )
            return True

        except Exception as e:
            self.errors.append(f"Configuration validation failed: {e}")
            return False

    def _validate_data_generation(self, environment: str) -> bool:
        """Validate data generation setup."""
        data_dir = self.example_dir / "data" / environment
        generate_script = self.example_dir / "data" / "generate.py"

        if not generate_script.exists():
            self.errors.append("Data generation script not found")
            return False

        # Check if data exists or can be generated
        users_file = data_dir / "users.parquet"
        events_file = data_dir / "events.parquet"

        if not (users_file.exists() and events_file.exists()):
            self.warnings.append("Data files not found. Run: python data/generate.py")
            return True  # Not an error, just needs to be run

        # Validate data files
        try:
            users_df = pd.read_parquet(users_file)
            events_df = pd.read_parquet(events_file)

            if len(users_df) == 0:
                self.errors.append("Users data file is empty")
                return False

            if len(events_df) == 0:
                self.errors.append("Events data file is empty")
                return False

            print(
                f"    📊 Data files valid ({len(users_df)} users, {len(events_df)} events)"
            )
            return True

        except Exception as e:
            self.errors.append(f"Data file validation failed: {e}")
            return False

    def _validate_docker_setup(self, environment: str) -> bool:
        """Validate Docker configuration."""
        dockerfile = self.example_dir / "docker" / "Dockerfile"

        if not dockerfile.exists():
            self.errors.append("Dockerfile not found")
            return False

        # Basic Dockerfile validation
        try:
            with open(dockerfile, "r") as f:
                content = f.read()

            required_directives = ["FROM", "WORKDIR", "COPY"]
            for directive in required_directives:
                if directive not in content:
                    self.errors.append(f"Dockerfile missing {directive}")
                    return False

            print(f"    🐳 Dockerfile appears valid")
            return True

        except Exception as e:
            self.errors.append(f"Dockerfile validation failed: {e}")
            return False

    def _validate_github_actions(self, environment: str) -> bool:
        """Validate GitHub Actions workflows."""
        workflows_dir = self.example_dir / ".github" / "workflows"

        if not workflows_dir.exists():
            self.errors.append("GitHub workflows directory not found")
            return False

        # Check for required workflows
        required_workflows = ["build-catalog.yml"]
        missing_workflows = []

        for workflow in required_workflows:
            workflow_path = workflows_dir / workflow
            if not workflow_path.exists():
                missing_workflows.append(workflow)

        if missing_workflows:
            self.errors.append(f"Missing GitHub workflows: {missing_workflows}")
            return False

        # Validate workflow structure
        build_workflow = workflows_dir / "build-catalog.yml"
        try:
            with open(build_workflow, "r") as f:
                content = f.read()

            required_keys = ["on:", "jobs:"]
            for key in required_keys:
                if key not in content:
                    self.errors.append(f"Build workflow missing {key}")
                    return False

            print(f"    🔄 GitHub workflows appear valid")
            return True

        except Exception as e:
            self.errors.append(f"GitHub workflows validation failed: {e}")
            return False

    def _validate_scripts(self, environment: str) -> bool:
        """Validate deployment and validation scripts."""
        scripts_dir = self.example_dir / "scripts"
        required_scripts = ["validate-configs.py", "deploy.py"]

        missing_scripts = []
        for script in required_scripts:
            script_path = scripts_dir / script
            if not script_path.exists():
                missing_scripts.append(script)

        if missing_scripts:
            self.errors.append(f"Missing scripts: {missing_scripts}")
            return False

        # Test script syntax
        for script in required_scripts:
            script_path = scripts_dir / script
            try:
                with open(script_path, "r") as f:
                    content = f.read()

                # Basic Python syntax check
                compile(content, str(script_path), "exec")

            except SyntaxError as e:
                self.errors.append(f"Syntax error in {script}: {e}")
                return False
            except Exception as e:
                self.warnings.append(f"Could not validate {script}: {e}")

        print(f"    📜 Scripts appear valid")
        return True

    def _validate_catalog_building(self, environment: str) -> bool:
        """Validate catalog building process."""
        config_file = self.example_dir / "configs" / f"catalog-{environment}.yaml"

        if not config_file.exists():
            self.warnings.append("Cannot test catalog building without config file")
            return True

        try:
            # Load configuration
            config = load_config(str(config_file))

            # Test building catalog in memory
            db_file = self.example_dir / "data" / f"test_{environment}.duckdb"

            try:
                # Build catalog
                build_catalog(config)
                print(f"    🔨 Catalog building successful")
                return True

            except Exception as e:
                self.errors.append(f"Catalog building failed: {e}")
                return False

        except Exception as e:
            self.errors.append(f"Catalog building test failed: {e}")
            return False

    def _validate_data_quality(self, environment: str) -> bool:
        """Validate data quality checks."""
        data_dir = self.example_dir / "data" / environment
        users_file = data_dir / "users.parquet"
        events_file = data_dir / "events.parquet"

        if not (users_file.exists() and events_file.exists()):
            self.warnings.append("Cannot test data quality without data files")
            return True

        try:
            # Load data
            users_df = pd.read_parquet(users_file)
            events_df = pd.read_parquet(events_file)

            issues = []

            # Check users data
            if users_df["user_id"].duplicated().any():
                issues.append("Duplicate user IDs found")

            if users_df["email"].isnull().any():
                issues.append("Null email addresses found")

            # Check events data
            if events_df["event_id"].duplicated().any():
                issues.append("Duplicate event IDs found")

            if events_df["event_timestamp"].isnull().any():
                issues.append("Null event timestamps found")

            # Check referential integrity
            event_users = set(events_df["user_id"].unique())
            user_ids = set(users_df["user_id"].unique())
            orphaned_events = event_users - user_ids

            if orphaned_events:
                issues.append(
                    f"Events for unknown users: {len(orphaned_events)} events"
                )

            if issues:
                self.warnings.extend(issues)
                print(f"    ⚠️  Data quality issues found: {len(issues)}")
            else:
                print(f"    ✅ Data quality checks passed")

            return True

        except Exception as e:
            self.errors.append(f"Data quality validation failed: {e}")
            return False

    def _print_results(self) -> bool:
        """Print validation results."""
        print("\n" + "=" * 60)
        print("CI/CD EXAMPLE VALIDATION RESULTS")
        print("=" * 60)

        success_rate = (
            (self.success_count / self.total_tests) * 100 if self.total_tests > 0 else 0
        )

        print(
            f"\n📊 Test Results: {self.success_count}/{self.total_tests} passed ({success_rate:.1f}%)"
        )

        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")

        if self.errors:
            print(f"\n🔧 To fix issues:")
            print(f"  1. Run: python data/generate.py")
            print(f"  2. Check configuration files")
            print(f"  3. Verify all required files exist")
            return False
        elif self.warnings:
            print(f"\n✅ Validation passed with warnings")
            return True
        else:
            print(f"\n🎉 All validations passed!")
            return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Validate Duckalog CI/CD example")
    parser.add_argument(
        "--environment",
        "-e",
        default="dev",
        help="Environment to validate (dev, staging, prod)",
    )
    parser.add_argument(
        "--example-dir", "-d", default=".", help="Path to CI/CD example directory"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Create validator and run validation
    validator = CIExampleValidator(args.example_dir)
    success = validator.validate_all(args.environment, args.verbose)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
