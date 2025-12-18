"""Benchmark suite for Duckalog configuration loading."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from .config.api import load_config
from .config.resolution.imports import RequestContext, request_cache_scope
from .performance import BenchmarkResult, PerformanceTracker


class BenchmarkSuite:
    """Realistic performance benchmarks for configuration loading."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("benchmarks/results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.tracker = PerformanceTracker()

    def run_benchmark(
        self, name: str, config_path: Path, iterations: int = 5, **load_kwargs
    ) -> BenchmarkResult:
        """Run a benchmark for a specific configuration."""
        print(f"Running benchmark: {name} ({iterations} iterations)...")

        total_time = 0.0
        all_summaries = []

        for i in range(iterations):
            ctx = RequestContext()
            start = time.perf_counter()
            load_config(config_path, context=ctx, **load_kwargs)
            duration = time.perf_counter() - start
            total_time += duration
            all_summaries.append(ctx.metrics.get_summary())

        # Aggregate metrics
        avg_metrics = self._aggregate_summaries(all_summaries)

        result = BenchmarkResult(
            name=name,
            iterations=iterations,
            total_time=total_time,
            metrics_summary=avg_metrics,
        )

        self.tracker.add_result(result)
        self._save_result(result)
        return result

    def _aggregate_summaries(self, summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate multiple metrics summaries into one average summary."""
        if not summaries:
            return {}

        aggregated = {}
        # Get all operation names
        op_names = set()
        for s in summaries:
            op_names.update(s.keys())

        for name in op_names:
            counts = [s[name]["count"] for s in summaries if name in s]
            durations = [s[name]["total_duration"] for s in summaries if name in s]

            if not counts:
                continue

            aggregated[name] = {
                "count": sum(counts) / len(summaries),
                "total_duration": sum(durations) / len(summaries),
                "avg": sum(durations) / sum(counts) if sum(counts) > 0 else 0,
            }

        return aggregated

    def _save_result(self, result: BenchmarkResult):
        """Save benchmark result to disk."""
        data = {
            "name": result.name,
            "timestamp": time.time(),
            "iterations": result.iterations,
            "total_time": result.total_time,
            "avg_time": result.avg_time,
            "metrics": result.metrics_summary,
        }

        file_path = self.output_dir / f"{result.name}_{int(time.time())}.json"
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    def create_complex_config(
        self, base_dir: Path, depth: int = 3, width: int = 5
    ) -> Path:
        """Create a complex configuration tree for benchmarking."""
        base_dir.mkdir(parents=True, exist_ok=True)

        def create_level(current_depth: int, prefix: str) -> List[str]:
            if current_depth == 0:
                # Leaf nodes
                leaf_path = base_dir / f"{prefix}.yaml"
                leaf_config = {
                    "version": 1,
                    "duckdb": {"database": ":memory:"},
                    "views": [{"name": f"view_{prefix}", "sql": "SELECT 1"}],
                }
                leaf_path.write_text(yaml.dump(leaf_config))
                return [str(leaf_path.name)]

            # Intermediate nodes
            imports = []
            for i in range(width):
                child_imports = create_level(current_depth - 1, f"{prefix}_{i}")
                imports.extend(child_imports)

            node_path = base_dir / f"{prefix}.yaml"
            node_config = {
                "version": 1,
                "duckdb": {"database": ":memory:"},
                "imports": imports,
                "views": [{"name": f"view_{prefix}", "sql": "SELECT 1"}],
            }
            node_path.write_text(yaml.dump(node_config))
            return [str(node_path.name)]

        root_paths = create_level(depth, "root")
        return base_dir / root_paths[0]

    def create_large_sql_config(self, base_dir: Path, count: int = 100) -> Path:
        """Create a configuration with many SQL files."""
        base_dir.mkdir(parents=True, exist_ok=True)
        sql_dir = base_dir / "sql"
        sql_dir.mkdir(exist_ok=True)

        views = []
        for i in range(count):
            sql_file = sql_dir / f"query_{i}.sql"
            sql_file.write_text(f"SELECT {i} as val")
            views.append({"name": f"view_{i}", "sql": f"file:sql/query_{i}.sql"})

        config_path = base_dir / "sql_config.yaml"
        config = {
            "version": 1,
            "duckdb": {"database": ":memory:"},
            "views": views,
        }
        config_path.write_text(yaml.dump(config))
        return config_path


def run_standard_benchmarks(output_dir: Optional[Path] = None):
    """Run a standard set of benchmarks."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        suite = BenchmarkSuite(output_dir)

        # 1. Baseline (Simple)
        simple_path = tmp_path / "simple.yaml"
        simple_path.write_text(
            yaml.dump(
                {
                    "version": 1,
                    "duckdb": {"database": ":memory:"},
                    "views": [{"name": "v", "sql": "SELECT 1"}],
                }
            )
        )
        suite.run_benchmark("Baseline (Simple)", simple_path)

        # 2. Complex imports (Deep & Wide)
        complex_dir = tmp_path / "complex"
        complex_path = suite.create_complex_config(complex_dir, depth=2, width=10)
        suite.run_benchmark("Complex Imports (100+ files)", complex_path)

        # 3. Large SQL set
        sql_dir = tmp_path / "sql_bench"
        sql_path = suite.create_large_sql_config(sql_dir, count=200)
        suite.run_benchmark("Large SQL Set (200 files)", sql_path)

        # 4. Deep inheritance
        deep_dir = tmp_path / "deep"
        deep_path = suite.create_complex_config(deep_dir, depth=5, width=2)
        suite.run_benchmark("Deep Inheritance (5 levels)", deep_path)


if __name__ == "__main__":
    run_standard_benchmarks()
