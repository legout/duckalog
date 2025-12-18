import os
import pytest
import yaml
import tempfile
from pathlib import Path
from typing import Generator

from duckalog.config.api import load_config
from duckalog.config.resolution.imports import request_cache_scope, RequestContext
from duckalog.config.models import Config


@pytest.fixture
def large_config_tree(tmp_path: Path) -> Path:
    """Creates a large configuration tree with many imports.

    Structure:
    root.yaml
      - imports: mid_0.yaml ... mid_9.yaml
    mid_i.yaml
      - imports: leaf_i0.yaml ... leaf_i9.yaml
    """
    base_dir = tmp_path / "large_config"
    base_dir.mkdir()

    # Create 100 leaf configs
    for i in range(100):
        leaf_path = base_dir / f"leaf_{i}.yaml"
        leaf_config = {
            "version": 1,
            "duckdb": {"database": ":memory:"},
            "views": [{"name": f"view_leaf_{i}", "sql": f"SELECT {i} as val"}],
        }
        leaf_path.write_text(yaml.dump(leaf_config))

    # Create 10 middle configs that import 10 leaves each (No overlap)
    for i in range(10):
        mid_path = base_dir / f"mid_{i}.yaml"
        start_idx = i * 10
        end_idx = start_idx + 10
        imports = [f"leaf_{j}.yaml" for j in range(start_idx, end_idx)]
        mid_config = {
            "version": 1,
            "duckdb": {"database": ":memory:"},
            "imports": imports,
            "views": [{"name": f"view_mid_{i}", "sql": f"SELECT {i} * 100 as val"}],
        }
        mid_path.write_text(yaml.dump(mid_config))

    # Create root config that imports all mid configs
    root_path = base_dir / "root.yaml"
    root_config = {
        "version": 1,
        "duckdb": {"database": ":memory:"},
        "imports": [f"mid_{i}.yaml" for i in range(10)],
        "views": [{"name": "root_view", "sql": "SELECT 'root' as val"}],
    }
    root_path.write_text(yaml.dump(root_config))

    return root_path


@pytest.mark.benchmark(group="config_loading")
def test_load_config_no_cache_reuse(benchmark, large_config_tree):
    """Benchmark loading a config where cache is fresh for each call."""

    def load():
        # Every call to load_config creates its own request_cache_scope
        return load_config(large_config_tree)

    config = benchmark(load)
    assert len(config.views) > 100


@pytest.mark.benchmark(group="config_loading")
def test_load_config_with_cache_reuse(benchmark, large_config_tree):
    """Benchmark loading a config where the same RequestContext is reused."""
    ctx = RequestContext()

    def load_cached():
        # We manually use the same context to simulate cross-request caching
        from duckalog.config.resolution.imports import _load_config_with_imports

        return _load_config_with_imports(
            file_path=str(large_config_tree),
            import_context=ctx.import_context,
            env_cache=ctx.env_cache,
        )

    # Warm up the cache
    load_cached()

    config = benchmark(load_cached)
    assert len(config.views) > 100


@pytest.mark.benchmark(group="env_processing")
def test_env_interpolation_performance(benchmark):
    """Benchmark environment variable interpolation."""
    from duckalog.config.resolution.env import _interpolate_env

    large_dict = {f"key_{i}": f"value_${{VAR_{i % 10}}}_suffix" for i in range(1000)}

    # Set some env vars
    for i in range(10):
        os.environ[f"VAR_{i}"] = f"val_{i}"

    benchmark(_interpolate_env, large_dict)


@pytest.mark.benchmark(group="sql_loading")
def test_sql_file_loading_performance(benchmark, tmp_path):
    """Benchmark loading many SQL files."""
    from duckalog.config.loading.sql import load_sql_files_from_config
    from duckalog.config.models import Config, ViewConfig, DuckDBConfig

    sql_dir = tmp_path / "sql"
    sql_dir.mkdir()

    views = []
    for i in range(100):
        sql_file = sql_dir / f"query_{i}.sql"
        sql_file.write_text(f"SELECT {i} FROM table_{i}")
        views.append(ViewConfig(name=f"view_{i}", sql=f"file:{sql_file}"))

    config = Config(version=1, duckdb=DuckDBConfig(), views=views)

    benchmark(load_sql_files_from_config, config, tmp_path / "dummy.yaml")


@pytest.mark.limit_memory("100MB")
def test_memory_usage_large_config(large_config_tree):
    """Test memory usage for loading a large config."""
    for _ in range(5):  # Repeated loading to check for leaks
        load_config(large_config_tree)


def test_cache_hit_ratios(large_config_tree):
    """Measure cache hit/miss ratios manually."""
    with request_cache_scope() as ctx:
        from duckalog.config.resolution.imports import _load_config_with_imports

        _load_config_with_imports(
            file_path=str(large_config_tree),
            import_context=ctx.import_context,
            env_cache=ctx.env_cache,
        )

        # Check cache size
        # Total distinct files: root.yaml, 10x mid_i.yaml, 100x leaf_i.yaml = 111 files
        # For local files, resolved_path and normalized_path are the same.
        assert len(ctx.import_context.config_cache) >= 111
