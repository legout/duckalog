import pytest
from duckalog.performance import BenchmarkResult, RegressionDetector


def test_regression_detection():
    baseline = BenchmarkResult(
        name="test",
        iterations=1,
        total_time=1.0,
        metrics_summary={"parsing": {"count": 1, "total_duration": 0.5, "avg": 0.5}},
    )

    # Normal case - no regression
    current_ok = BenchmarkResult(
        name="test",
        iterations=1,
        total_time=1.1,
        metrics_summary={"parsing": {"count": 1, "total_duration": 0.55, "avg": 0.55}},
    )

    detector = RegressionDetector(threshold=0.2)
    assert len(detector.detect(current_ok, baseline)) == 0

    # Regression in overall time
    current_bad_overall = BenchmarkResult(
        name="test",
        iterations=1,
        total_time=1.3,
        metrics_summary={"parsing": {"count": 1, "total_duration": 0.55, "avg": 0.55}},
    )
    regressions = detector.detect(current_bad_overall, baseline)
    assert len(regressions) == 1
    assert regressions[0]["type"] == "overall"

    # Regression in specific metric
    current_bad_metric = BenchmarkResult(
        name="test",
        iterations=1,
        total_time=1.1,
        metrics_summary={"parsing": {"count": 1, "total_duration": 0.8, "avg": 0.8}},
    )
    regressions = detector.detect(current_bad_metric, baseline)
    assert len(regressions) == 1
    assert regressions[0]["type"] == "metric"
    assert regressions[0]["operation"] == "parsing"


if __name__ == "__main__":
    test_regression_detection()
