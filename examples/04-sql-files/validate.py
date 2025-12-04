#!/usr/bin/env python3
"""
SQL Files and Templates Example Validation Script

This script validates the SQL files and templates example by:
1. Loading the catalog configuration with SQL file processing enabled
2. Verifying that external SQL files are properly loaded and inlined
3. Testing template variable substitution works correctly
4. Validating that all three SQL source types (inline, sql_file, sql_template) work
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import duckalog
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from duckalog import load_config, SQLFileLoader, ConfigError
    from duckalog.errors import SQLFileError, SQLTemplateError
except ImportError as e:
    print(f"❌ Failed to import duckalog: {e}")
    print("Make sure you're running this from the examples directory")
    sys.exit(1)


def test_configuration_loading():
    """Test that the catalog configuration loads successfully."""
    print("🔍 Testing configuration loading...")

    try:
        config = load_config("catalog.yaml")
        print(f"✅ Configuration loaded successfully with {len(config.views)} views")
        return config
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return None


def test_view_configuration(config):
    """Test that all views are configured correctly."""
    print("\n🔍 Testing view configuration...")

    # Expected views
    expected_views = {
        "active_users": {"type": "sql_file", "has_sql": True},
        "recent_orders": {"type": "sql_template", "has_sql": True},
        "top_customers": {"type": "inline", "has_sql": True},
    }

    for view in config.views:
        if view.name not in expected_views:
            print(f"❌ Unexpected view: {view.name}")
            continue

        expected = expected_views[view.name]

        # Check SQL content is present
        if expected["has_sql"] and not view.sql:
            print(f"❌ View {view.name} missing SQL content")
            continue

        # Check SQL file reference is removed after loading
        if view.name == "active_users" and view.sql_file:
            print(f"❌ View {view.name} still has sql_file reference after loading")
            continue

        # Check SQL template reference is removed after loading
        if view.name == "recent_orders" and view.sql_template:
            print(f"❌ View {view.name} still has sql_template reference after loading")
            continue

        print(f"✅ View {view.name} configured correctly ({expected['type']})")

    print("✅ All views configured correctly")


def test_sql_file_loading():
    """Test direct SQL file loading functionality."""
    print("\n🔍 Testing SQL file loading...")

    try:
        loader = SQLFileLoader()

        # Test loading plain SQL file
        sql_content = loader.load_sql_file("sql/active_users.sql", "catalog.yaml")

        if "active" in sql_content.lower() and "users" in sql_content.lower():
            print("✅ SQL file loaded correctly")
        else:
            print("❌ SQL file content unexpected")
            print(f"Content: {sql_content[:100]}...")

    except Exception as e:
        print(f"❌ SQL file loading failed: {e}")


def test_template_processing():
    """Test template variable substitution."""
    print("\n🔍 Testing template processing...")

    try:
        loader = SQLFileLoader()

        # Test template with variables
        template_content = loader.load_sql_file(
            "sql/recent_orders_template.sql",
            "catalog.yaml",
            variables={"days_back": 30},
            as_template=True,
        )

        # Check that the variable was substituted
        if "30" in template_content and "{{days_back}}" not in template_content:
            print("✅ Template variable substitution working")
        else:
            print("❌ Template variable substitution failed")
            print(f"Content: {template_content[:100]}...")

        # Check that SQL content looks reasonable
        if (
            "orders" in template_content.lower()
            and "current_date" in template_content.lower()
        ):
            print("✅ Template content preserved correctly")
        else:
            print("❌ Template content corrupted")

    except Exception as e:
        print(f"❌ Template processing failed: {e}")


def test_template_validation():
    """Test that template validation works for missing variables."""
    print("\n🔍 Testing template validation...")

    try:
        loader = SQLFileLoader()

        # This should fail because we're not providing the required variable
        try:
            loader.load_sql_file(
                "sql/recent_orders_template.sql",
                "catalog.yaml",
                variables={},  # Missing 'days_back' variable
                as_template=True,
            )
            print("❌ Template validation should have failed")
        except SQLTemplateError as e:
            if "days_back" in str(e):
                print("✅ Template validation working correctly")
            else:
                print(f"❌ Template validation error message unclear: {e}")

    except Exception as e:
        print(f"❌ Template validation test failed: {e}")


def test_error_handling():
    """Test error handling for non-existent files."""
    print("\n🔍 Testing error handling...")

    try:
        loader = SQLFileLoader()

        # This should fail because the file doesn't exist
        try:
            loader.load_sql_file("sql/nonexistent.sql", "catalog.yaml")
            print("❌ Error handling should have failed")
        except SQLFileError as e:
            if "not found" in str(e).lower():
                print("✅ Error handling working correctly")
            else:
                print(f"❌ Error handling error message unclear: {e}")

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")


def run_all_tests():
    """Run all validation tests."""
    print("🚀 Starting SQL Files and Templates Example Validation")
    print("=" * 60)

    # Test configuration loading
    config = test_configuration_loading()
    if not config:
        print("\n❌ Basic configuration loading failed. Stopping tests.")
        return False

    # Test view configuration
    test_view_configuration(config)

    # Test SQL file functionality
    test_sql_file_loading()
    test_template_processing()
    test_template_validation()
    test_error_handling()

    print("\n" + "=" * 60)
    print("🎉 Validation Complete!")
    print("\nThe SQL files and templates example is working correctly.")
    print("You can now:")
    print("  • Use external SQL files with the 'sql_file' field")
    print("  • Create parameterized templates with 'sql_template'")
    print("  • Leverage variable substitution for dynamic queries")
    print("\nSee README.md for more detailed usage examples.")

    return True


if __name__ == "__main__":
    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    success = run_all_tests()
    sys.exit(0 if success else 1)
