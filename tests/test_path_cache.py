import pytest
from pathlib import Path
from duckalog import load_config
from duckalog.config.security.path import (
    resolve_relative_path,
    validate_path_security,
    path_resolution_context,
    get_current_path_cache,
)


def test_path_resolution_cache():
    config_dir = Path.cwd()
    test_path = "test.sql"

    with path_resolution_context() as cache:
        # First resolution - should be a miss
        res1 = resolve_relative_path(test_path, config_dir)
        initial_misses = cache.misses
        initial_hits = cache.hits

        # Second resolution of same path - should be a hit
        res2 = resolve_relative_path(test_path, config_dir)

        assert res1 == res2
        assert cache.hits == initial_hits + 1
        assert cache.misses == initial_misses

        # Validate security - should use cached results
        validate_path_security(test_path, config_dir)
        assert cache.hits > initial_hits + 1


def test_cache_cleared_after_context():
    with path_resolution_context() as cache:
        assert get_current_path_cache() is cache

    assert get_current_path_cache() is None


def test_nested_cache_context_reuses_cache():
    with path_resolution_context() as outer_cache:
        resolve_relative_path("outer.sql", Path.cwd())
        outer_hits = outer_cache.hits

        with path_resolution_context() as inner_cache:
            assert (
                inner_cache is outer_cache
            )  # Should reuse because it's already active
            resolve_relative_path("inner.sql", Path.cwd())
            assert inner_cache.hits > outer_hits

        # Back in outer context
        assert get_current_path_cache() is outer_cache


def test_load_config_uses_path_cache(tmp_path):
    # Create a config with multiple relative paths to same/different files
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    data_dir = config_dir / "data"
    data_dir.mkdir()
    (data_dir / "test1.parquet").touch()

    config_path = config_dir / "catalog.yaml"
    config_path.write_text(f"""
version: 1
duckdb:
  database: ":memory:"
views:
  - name: v1
    source: parquet
    uri: data/test1.parquet
  - name: v2
    source: parquet
    uri: data/test1.parquet
  - name: v3
    source: parquet
    uri: data/test1.parquet
""")

    with path_resolution_context() as cache:
        load_config(str(config_path))
        # There should be several hits because of 3 views having same URI
        # and each URI being resolved + validated.
        assert cache.hits > 0
        assert cache.misses > 0
