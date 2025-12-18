"""Performance monitoring and benchmarking system for Duckalog."""

from __future__ import annotations

import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class OperationMetric:
    """Metric for a single operation."""

    name: str
    duration: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class PerformanceMetrics:
    """Collection of performance metrics for a configuration load operation."""

    def __init__(self):
        self.metrics: List[OperationMetric] = []
        self._start_times: Dict[str, float] = {}

    def start_timer(self, name: str) -> None:
        """Start a timer for an operation."""
        self._start_times[name] = time.perf_counter()

    def stop_timer(self, name: str, **metadata) -> float:
        """Stop a timer and record the metric."""
        if name not in self._start_times:
            return 0.0

        duration = time.perf_counter() - self._start_times.pop(name)
        self.metrics.append(
            OperationMetric(name=name, duration=duration, metadata=metadata)
        )
        return duration

    @contextmanager
    def timer(self, name: str, **metadata):
        """Context manager for timing an operation."""
        start = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start
            self.metrics.append(
                OperationMetric(name=name, duration=duration, metadata=metadata)
            )

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        summary = defaultdict(
            lambda: {"count": 0, "total_duration": 0.0, "min": float("inf"), "max": 0.0}
        )

        for metric in self.metrics:
            s = summary[metric.name]
            s["count"] += 1
            s["total_duration"] += metric.duration
            s["min"] = min(s["min"], metric.duration)
            s["max"] = max(s["max"], metric.duration)

        for name, s in summary.items():
            s["avg"] = s["total_duration"] / s["count"]
            if s["min"] == float("inf"):
                s["min"] = 0.0

        return dict(summary)

    def clear(self):
        """Clear all metrics."""
        self.metrics.clear()
        self._start_times.clear()


@dataclass
class BenchmarkResult:
    """Result of a benchmark run."""

    name: str
    iterations: int
    total_time: float
    metrics_summary: Dict[str, Any]
    avg_time: float = 0.0

    def __post_init__(self):
        if self.iterations > 0:
            self.avg_time = self.total_time / self.iterations


class PerformanceTracker:
    """Global tracker for performance metrics (optional singleton)."""

    _instance: Optional[PerformanceTracker] = None
    history: List[BenchmarkResult] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PerformanceTracker, cls).__new__(cls)
            cls._instance.history = []
        return cls._instance

    def add_result(self, result: BenchmarkResult):
        self.history.append(result)

    def get_history(self) -> List[BenchmarkResult]:
        return self.history


class RegressionDetector:
    """Detects performance regressions compared to historical data."""

    def __init__(self, threshold: float = 0.2):
        self.threshold = threshold  # 20% degradation is a regression

    def detect(
        self, current: BenchmarkResult, baseline: BenchmarkResult
    ) -> List[Dict[str, Any]]:
        """Compare current result with baseline and return regressions."""
        regressions = []

        # Overall time comparison
        if current.avg_time > baseline.avg_time * (1 + self.threshold):
            regressions.append(
                {
                    "type": "overall",
                    "name": current.name,
                    "current": current.avg_time,
                    "baseline": baseline.avg_time,
                    "degradation": (current.avg_time / baseline.avg_time) - 1,
                }
            )

        # Per-metric comparison
        for op_name, current_stats in current.metrics_summary.items():
            if op_name in baseline.metrics_summary:
                baseline_stats = baseline.metrics_summary[op_name]
                curr_total = current_stats["total_duration"]
                base_total = baseline_stats["total_duration"]

                if curr_total > base_total * (1 + self.threshold):
                    regressions.append(
                        {
                            "type": "metric",
                            "operation": op_name,
                            "current": curr_total,
                            "baseline": base_total,
                            "degradation": (curr_total / base_total) - 1,
                        }
                    )

        return regressions


class PerformanceReporter:
    """Generates reports from performance metrics."""

    @staticmethod
    def generate_text_report(result: BenchmarkResult) -> str:
        """Generate a text report for a benchmark result."""
        lines = [
            f"Benchmark: {result.name}",
            f"Iterations: {result.iterations}",
            f"Total Time: {result.total_time:.4f}s",
            f"Average Time: {result.avg_time:.4f}s",
            "",
            "Detailed Breakdown:",
            f"{'Operation':<25} | {'Avg Time':<10} | {'Total Time':<10} | {'Count':<6}",
            "-" * 60,
        ]

        # Sort metrics by total duration
        sorted_metrics = sorted(
            result.metrics_summary.items(),
            key=lambda x: x[1]["total_duration"],
            reverse=True,
        )

        for name, stats in sorted_metrics:
            lines.append(
                f"{name:<25} | {stats['avg']:<10.4f} | {stats['total_duration']:<10.4f} | {int(stats['count']):<6}"
            )

        return "\n".join(lines)

    @staticmethod
    def generate_markdown_report(results: List[BenchmarkResult]) -> str:
        """Generate a markdown report for multiple benchmark results."""
        lines = ["# Performance Benchmark Report", ""]

        for result in results:
            lines.extend(
                [
                    f"## {result.name}",
                    "",
                    f"- **Average Time**: {result.avg_time:.4f}s",
                    f"- **Iterations**: {result.iterations}",
                    "",
                    "| Operation | Avg Duration | Total Duration | Count |",
                    "| :--- | :--- | :--- | :--- |",
                ]
            )

            # Sort metrics by total duration
            sorted_metrics = sorted(
                result.metrics_summary.items(),
                key=lambda x: x[1]["total_duration"],
                reverse=True,
            )

            for name, stats in sorted_metrics:
                lines.append(
                    f"| {name} | {stats['avg']:.4f}s | {stats['total_duration']:.4f}s | {int(stats['count'])} |"
                )
            lines.append("")

        return "\n".join(lines)
