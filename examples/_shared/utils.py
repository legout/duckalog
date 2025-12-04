"""Shared utilities for duckalog examples."""

import subprocess
import sys

import duckdb


def check_duckalog_installed() -> bool:
    """Check if duckalog is installed and available."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "duckalog", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False


def verify_duckdb(db_path: str) -> bool:
    """Open DuckDB connection and verify it works.

    Args:
        db_path: Path to DuckDB database file

    Returns:
        True if connection successful, False otherwise
    """
    try:
        conn = duckdb.connect(db_path)
        result = conn.execute("SELECT 1").fetchone()
        conn.close()
        return result is not None
    except Exception:
        return False


def run_sample_query(db_path: str, query: str) -> bool:
    """Execute a sample query and return results.

    Args:
        db_path: Path to DuckDB database file
        query: SQL query to execute

    Returns:
        True if query successful, False otherwise
    """
    try:
        conn = duckdb.connect(db_path)
        result = conn.execute(query).fetchall()
        conn.close()
        print(f"Query successful! Returned {len(result)} rows")
        return True
    except Exception as e:
        print(f"Query failed: {e}")
        return False


def check_prerequisites() -> None:
    """Check if prerequisites for examples are met."""
    print("Checking prerequisites...")

    # Check duckalog
    if check_duckalog_installed():
        print("✓ duckalog is installed")
    else:
        print("✗ duckalog is NOT installed")
        print("  Install with: pip install duckalog")
        sys.exit(1)

    # Check Python version
    if sys.version_info >= (3, 12):
        print(
            f"✓ Python {sys.version_info.major}.{sys.version_info.minor} is installed"
        )
    else:
        print(
            f"✗ Python 3.12+ required, found {sys.version_info.major}.{sys.version_info.minor}"
        )
        sys.exit(1)


def print_separator() -> None:
    """Print a separator line."""
    print("\n" + "=" * 60 + "\n")
