import pytest
import yaml
from pathlib import Path
from duckalog.config.api import load_config
from duckalog.config.resolution.imports import request_cache_scope


def test_performance_metrics_collection(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        yaml.dump(
            {
                "version": 1,
                "duckdb": {"database": ":memory:"},
                "views": [{"name": "test_view", "sql": "SELECT 1"}],
            }
        )
    )

    with request_cache_scope() as ctx:
        load_config(config_path, context=ctx)
        summary = ctx.metrics.get_summary()

        assert "file_io" in summary
        assert "parsing" in summary
        assert "validation" in summary
        assert summary["validation"]["count"] == 1
