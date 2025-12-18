#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from duckalog.benchmarks import BenchmarkSuite, run_standard_benchmarks
from duckalog.performance import PerformanceTracker, PerformanceReporter


def main():
    print("Duckalog Performance Benchmark Runner")
    print("=====================================")

    output_dir = Path("benchmarks/results")
    run_standard_benchmarks(output_dir)

    tracker = PerformanceTracker()
    results = tracker.get_history()

    if not results:
        print("No results collected.")
        return

    print("\nBenchmark Results Summary:")
    print("--------------------------")
    for result in results:
        print(PerformanceReporter.generate_text_report(result))
        print("-" * 40)

    markdown_report = PerformanceReporter.generate_markdown_report(results)
    with open("benchmarks/REPORT.md", "w") as f:
        f.write(markdown_report)

    print(f"\nMarkdown report saved to benchmarks/REPORT.md")


if __name__ == "__main__":
    main()
