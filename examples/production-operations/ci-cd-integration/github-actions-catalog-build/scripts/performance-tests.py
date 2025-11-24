#!/usr/bin/env python3
"""
Performance regression testing script for Duckalog catalogs.

This script runs performance tests on Duckalog catalogs and compares results
against baselines to detect performance regressions.

Usage: python performance-tests.py [--baseline HASH] [--current HASH] [--output-dir DIR]
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import duckdb
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns

    from duckalog import build_catalog, load_config
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install with: pip install duckalog pandas matplotlib seaborn")
    sys.exit(1)


class PerformanceTestSuite:
    """Performance testing suite for Duckalog catalogs."""

    def __init__(self, config_path: str, output_dir: str = "reports"):
        self.config_path = config_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Load configuration
        self.config = load_config(config_path)

        # Connect to database
        self.conn = duckdb.connect(self.config.duckdb.database)

        # Performance thresholds (in seconds)
        self.thresholds = {
            "view_creation": 5.0,
            "simple_query": 1.0,
            "complex_query": 10.0,
            "large_dataset_query": 30.0,
        }

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all performance tests."""
        print("🚀 Running performance test suite...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "config": str(self.config_path),
            "tests": {},
        }

        # Test view creation performance
        results["tests"]["view_creation"] = self._test_view_creation()

        # Test query performance
        results["tests"]["simple_queries"] = self._test_simple_queries()
        results["tests"]["complex_queries"] = self._test_complex_queries()
        results["tests"]["large_dataset_queries"] = self._test_large_dataset_queries()

        # Test catalog build performance
        results["tests"]["catalog_build"] = self._test_catalog_build()

        # Test memory usage
        results["tests"]["memory_usage"] = self._test_memory_usage()

        # Generate summary
        results["summary"] = self._generate_summary(results["tests"])

        return results

    def _test_view_creation(self) -> Dict[str, Any]:
        """Test view creation performance."""
        print("\n📊 Testing view creation performance...")

        results = {"total_views": len(self.config.views), "view_times": {}}

        total_time = 0

        for view in self.config.views:
            start_time = time.time()

            try:
                # Test view creation by selecting from it
                result = self.conn.execute(
                    f"SELECT COUNT(*) FROM {view.name}"
                ).fetchone()
                creation_time = time.time() - start_time

                results["view_times"][view.name] = {
                    "time_seconds": creation_time,
                    "row_count": result[0] if result else 0,
                }

                total_time += creation_time
                print(f"  ✅ {view.name}: {creation_time:.3f}s ({result[0]} rows)")

            except Exception as e:
                results["view_times"][view.name] = {
                    "error": str(e),
                    "time_seconds": None,
                }
                print(f"  ❌ {view.name}: {e}")

        results["total_time_seconds"] = total_time
        results["average_time_per_view"] = total_time / len(self.config.views)
        results["within_threshold"] = total_time <= self.thresholds[
            "view_creation"
        ] * len(self.config.views)

        print(f"  📈 Total view creation time: {total_time:.3f}s")
        print(f"  📈 Average per view: {results['average_time_per_view']:.3f}s")

        return results

    def _test_simple_queries(self) -> Dict[str, Any]:
        """Test simple query performance."""
        print("\n🔍 Testing simple query performance...")

        # Simple queries that should run quickly
        test_queries = [
            {
                "name": "count_all_views",
                "query": "SELECT COUNT(*) FROM information_schema.views",
            },
            {
                "name": "list_tables",
                "query": "SELECT table_name FROM information_schema.tables LIMIT 10",
            },
            {
                "name": "database_size",
                "query": "SELECT pg_size_pretty(pg_database_size(current_database()))",
            },
        ]

        results = {"queries": {}, "total_time": 0, "within_threshold": True}

        for query_test in test_queries:
            try:
                start_time = time.time()
                result = self.conn.execute(query_test["query"]).fetchall()
                query_time = time.time() - start_time

                results["queries"][query_test["name"]] = {
                    "query": query_test["query"],
                    "time_seconds": query_time,
                    "result_count": len(result),
                }

                results["total_time"] += query_time

                if query_time > self.thresholds["simple_query"]:
                    results["within_threshold"] = False

                print(f"  ✅ {query_test['name']}: {query_time:.3f}s")

            except Exception as e:
                results["queries"][query_test["name"]] = {
                    "query": query_test["query"],
                    "error": str(e),
                    "time_seconds": None,
                }
                print(f"  ❌ {query_test['name']}: {e}")

        print(f"  📈 Total simple query time: {results['total_time']:.3f}s")

        return results

    def _test_complex_queries(self) -> Dict[str, Any]:
        """Test complex query performance."""
        print("\n🧮 Testing complex query performance...")

        results = {"queries": {}, "total_time": 0, "within_threshold": True}

        # Test complex queries on available views
        if self.config.views:
            # Test aggregation queries
            view_name = self.config.views[0].name

            complex_queries = [
                {
                    "name": "group_by_aggregation",
                    "query": f"""
                        SELECT
                            COUNT(*) as total_count,
                            AVG(CAST(id AS INTEGER)) as avg_id,
                            COUNT(DISTINCT id) as unique_ids
                        FROM {view_name}
                        WHERE id IS NOT NULL
                    """,
                },
                {
                    "name": "window_function",
                    "query": f"""
                        SELECT
                            id,
                            ROW_NUMBER() OVER (ORDER BY id) as row_num,
                            LAG(id, 1) OVER (ORDER BY id) as prev_id
                        FROM {view_name}
                        WHERE id IS NOT NULL
                        LIMIT 100
                    """,
                },
            ]

            for query_test in complex_queries:
                try:
                    start_time = time.time()
                    result = self.conn.execute(query_test["query"]).fetchall()
                    query_time = time.time() - start_time

                    results["queries"][query_test["name"]] = {
                        "query": query_test["query"],
                        "time_seconds": query_time,
                        "result_count": len(result),
                    }

                    results["total_time"] += query_time

                    if query_time > self.thresholds["complex_query"]:
                        results["within_threshold"] = False

                    print(f"  ✅ {query_test['name']}: {query_time:.3f}s")

                except Exception as e:
                    # Some queries might fail due to schema differences
                    results["queries"][query_test["name"]] = {
                        "query": query_test["query"],
                        "error": str(e),
                        "time_seconds": None,
                    }
                    print(f"  ⚠️  {query_test['name']}: {e}")

        print(f"  📈 Total complex query time: {results['total_time']:.3f}s")

        return results

    def _test_large_dataset_queries(self) -> Dict[str, Any]:
        """Test performance on large datasets."""
        print("\n📊 Testing large dataset query performance...")

        results = {"queries": {}, "total_time": 0, "within_threshold": True}

        # Find the largest view
        largest_view = None
        max_rows = 0

        for view in self.config.views:
            try:
                result = self.conn.execute(
                    f"SELECT COUNT(*) FROM {view.name}"
                ).fetchone()
                row_count = result[0] if result else 0

                if row_count > max_rows:
                    max_rows = row_count
                    largest_view = view.name

            except Exception:
                continue

        if largest_view:
            large_queries = [
                {
                    "name": "full_scan",
                    "query": f"SELECT * FROM {largest_view} LIMIT 10000",
                },
                {
                    "name": "aggregation_on_large",
                    "query": f"""
                        SELECT
                            COUNT(*) as total_rows,
                            COUNT(DISTINCT id) as unique_ids
                        FROM {largest_view}
                    """,
                },
            ]

            for query_test in large_queries:
                try:
                    start_time = time.time()
                    result = self.conn.execute(query_test["query"]).fetchall()
                    query_time = time.time() - start_time

                    results["queries"][query_test["name"]] = {
                        "query": query_test["query"],
                        "time_seconds": query_time,
                        "result_count": len(result),
                        "estimated_dataset_size": max_rows,
                    }

                    results["total_time"] += query_time

                    if query_time > self.thresholds["large_dataset_query"]:
                        results["within_threshold"] = False

                    print(
                        f"  ✅ {query_test['name']}: {query_time:.3f}s (dataset: {max_rows} rows)"
                    )

                except Exception as e:
                    results["queries"][query_test["name"]] = {
                        "query": query_test["query"],
                        "error": str(e),
                        "time_seconds": None,
                    }
                    print(f"  ❌ {query_test['name']}: {e}")
        else:
            print("  ⚠️  No suitable large dataset found for testing")

        print(f"  📈 Total large dataset query time: {results['total_time']:.3f}s")

        return results

    def _test_catalog_build(self) -> Dict[str, Any]:
        """Test catalog build performance."""
        print("\n🏗️ Testing catalog build performance...")

        try:
            start_time = time.time()

            # Rebuild the catalog
            build_catalog(self.config)

            build_time = time.time() - start_time

            results = {
                "build_time_seconds": build_time,
                "view_count": len(self.config.views),
                "within_threshold": build_time
                <= self.thresholds["view_creation"] * len(self.config.views),
                "views_per_second": len(self.config.views) / build_time
                if build_time > 0
                else 0,
            }

            print(
                f"  ✅ Catalog build: {build_time:.3f}s ({results['views_per_second']:.1f} views/sec)"
            )

            return results

        except Exception as e:
            print(f"  ❌ Catalog build failed: {e}")
            return {
                "error": str(e),
                "build_time_seconds": None,
                "within_threshold": False,
            }

    def _test_memory_usage(self) -> Dict[str, Any]:
        """Test memory usage during operations."""
        print("\n💾 Testing memory usage...")

        try:
            import psutil

            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Perform memory-intensive operations
            large_view = None
            for view in self.config.views:
                try:
                    result = self.conn.execute(
                        f"SELECT COUNT(*) FROM {view.name}"
                    ).fetchone()
                    if result and result[0] > 1000:  # Find a reasonably sized view
                        large_view = view.name
                        break
                except Exception:
                    continue

            if large_view:
                # Run memory-intensive query
                self.conn.execute(f"SELECT * FROM {large_view} ORDER BY id").fetchall()

                # Check peak memory usage
                peak_memory = process.memory_info().rss / 1024 / 1024  # MB

                results = {
                    "initial_memory_mb": initial_memory,
                    "peak_memory_mb": peak_memory,
                    "memory_increase_mb": peak_memory - initial_memory,
                    "test_view": large_view,
                }

                print(
                    f"  📊 Memory usage: {initial_memory:.1f}MB → {peak_memory:.1f}MB (+{results['memory_increase_mb']:.1f}MB)"
                )

                return results
            else:
                print("  ⚠️  No suitable view found for memory testing")
                return {"error": "No suitable view found"}

        except ImportError:
            print("  ⚠️  psutil not available, skipping memory tests")
            return {"error": "psutil not available"}
        except Exception as e:
            print(f"  ❌ Memory test failed: {e}")
            return {"error": str(e)}

    def _generate_summary(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance summary."""
        summary = {"overall_status": "PASS", "issues": [], "recommendations": []}

        # Check each test category
        for test_name, test_result in test_results.items():
            if isinstance(test_result, dict) and "within_threshold" in test_result:
                if not test_result["within_threshold"]:
                    summary["overall_status"] = "FAIL"
                    summary["issues"].append(
                        f"{test_name} exceeded performance thresholds"
                    )

        # Add recommendations based on results
        if "view_creation" in test_results:
            avg_time = test_results["view_creation"].get("average_time_per_view", 0)
            if avg_time > 1.0:
                summary["recommendations"].append(
                    "Consider optimizing complex views or adding indexes"
                )

        if (
            "memory_usage" in test_results
            and "memory_increase_mb" in test_results["memory_usage"]
        ):
            memory_increase = test_results["memory_usage"]["memory_increase_mb"]
            if memory_increase > 500:  # 500MB increase
                summary["recommendations"].append(
                    "High memory usage detected, consider query optimization"
                )

        return summary

    def compare_with_baseline(
        self, current_results: Dict[str, Any], baseline_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare current results with baseline."""
        print("\n📊 Comparing with baseline...")

        comparison = {
            "timestamp": datetime.now().isoformat(),
            "baseline_timestamp": baseline_results.get("timestamp"),
            "comparisons": {},
            "regressions": [],
            "improvements": [],
        }

        # Compare test results
        for test_name in current_results["tests"]:
            if test_name in baseline_results["tests"]:
                current_test = current_results["tests"][test_name]
                baseline_test = baseline_results["tests"][test_name]

                comparison_result = self._compare_test_results(
                    test_name, current_test, baseline_test
                )
                comparison["comparisons"][test_name] = comparison_result

                # Track regressions and improvements
                if comparison_result.get("regression"):
                    comparison["regressions"].append(
                        f"{test_name}: {comparison_result['description']}"
                    )

                if comparison_result.get("improvement"):
                    comparison["improvements"].append(
                        f"{test_name}: {comparison_result['description']}"
                    )

        # Overall status
        comparison["overall_regression"] = len(comparison["regressions"]) > 0

        print(f"  📈 Regressions detected: {len(comparison['regressions'])}")
        print(f"  📉 Improvements detected: {len(comparison['improvements'])}")

        return comparison

    def _compare_test_results(
        self, test_name: str, current: Dict[str, Any], baseline: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare individual test results."""
        comparison = {
            "test_name": test_name,
            "regression": False,
            "improvement": False,
            "description": "",
        }

        # Handle different test types
        if test_name == "view_creation":
            current_time = current.get("total_time_seconds", 0)
            baseline_time = baseline.get("total_time_seconds", 0)

            if baseline_time > 0:
                change_percent = ((current_time - baseline_time) / baseline_time) * 100
                comparison["change_percent"] = change_percent

                if change_percent > 20:  # 20% slower
                    comparison["regression"] = True
                    comparison["description"] = f"{change_percent:.1f}% slower"
                elif change_percent < -10:  # 10% faster
                    comparison["improvement"] = True
                    comparison["description"] = f"{abs(change_percent):.1f}% faster"
                else:
                    comparison["description"] = (
                        f"No significant change ({change_percent:.1f}%)"
                    )

        elif test_name == "simple_queries" or test_name == "complex_queries":
            current_time = current.get("total_time", 0)
            baseline_time = baseline.get("total_time", 0)

            if baseline_time > 0:
                change_percent = ((current_time - baseline_time) / baseline_time) * 100
                comparison["change_percent"] = change_percent

                if change_percent > 15:
                    comparison["regression"] = True
                    comparison["description"] = f"{change_percent:.1f}% slower"
                elif change_percent < -10:
                    comparison["improvement"] = True
                    comparison["description"] = f"{abs(change_percent):.1f}% faster"
                else:
                    comparison["description"] = (
                        f"No significant change ({change_percent:.1f}%)"
                    )

        elif test_name == "catalog_build":
            current_time = current.get("build_time_seconds", 0)
            baseline_time = baseline.get("build_time_seconds", 0)

            if baseline_time > 0:
                change_percent = ((current_time - baseline_time) / baseline_time) * 100
                comparison["change_percent"] = change_percent

                if change_percent > 25:
                    comparison["regression"] = True
                    comparison["description"] = f"{change_percent:.1f}% slower"
                elif change_percent < -15:
                    comparison["improvement"] = True
                    comparison["description"] = f"{abs(change_percent):.1f}% faster"
                else:
                    comparison["description"] = (
                        f"No significant change ({change_percent:.1f}%)"
                    )

        return comparison

    def generate_report(
        self, results: Dict[str, Any], comparison: Dict[str, Any] = None
    ) -> str:
        """Generate HTML performance report."""
        report_path = (
            self.output_dir
            / f"performance-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
        )

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Duckalog Performance Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f8ff; padding: 20px; border-radius: 5px; }}
                .summary {{ background-color: #e8f5e8; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .regression {{ background-color: #ffe8e8; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .improvement {{ background-color: #e8ffe8; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .test-section {{ margin: 30px 0; }}
                .test-result {{ background-color: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .pass {{ color: green; font-weight: bold; }}
                .fail {{ color: red; font-weight: bold; }}
                .warning {{ color: orange; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 Duckalog Performance Report</h1>
                <p><strong>Generated:</strong> {results["timestamp"]}</p>
                <p><strong>Configuration:</strong> {results["config"]}</p>
            </div>

            <div class="summary">
                <h2>📊 Summary</h2>
                <p><strong>Overall Status:</strong> <span class="{results["summary"]["overall_status"].lower()}">{results["summary"]["overall_status"]}</span></p>
        """

        if comparison:
            status_class = "fail" if comparison["overall_regression"] else "pass"
            status_text = (
                "REGRESSION DETECTED"
                if comparison["overall_regression"]
                else "NO REGRESSIONS"
            )
            html_content += f"""
                <p><strong>Regression Analysis:</strong> <span class="{status_class}">{status_text}</span></p>
                <p><strong>Regressions:</strong> {len(comparison["regressions"])}</p>
                <p><strong>Improvements:</strong> {len(comparison["improvements"])}</p>
            """

        html_content += """
            </div>
        """

        # Add regression details
        if comparison and comparison["regressions"]:
            html_content += f"""
            <div class="regression">
                <h2>⚠️ Performance Regressions</h2>
                <ul>
                    {"".join(f"<li>{regression}</li>" for regression in comparison["regressions"])}
                </ul>
            </div>
            """

        # Add improvement details
        if comparison and comparison["improvements"]:
            html_content += f"""
            <div class="improvement">
                <h2>✅ Performance Improvements</h2>
                <ul>
                    {"".join(f"<li>{improvement}</li>" for improvement in comparison["improvements"])}
                </ul>
            </div>
            """

        # Add detailed test results
        html_content += "<div class='test-section'>"
        for test_name, test_result in results["tests"].items():
            html_content += f"<h3>🔍 {test_name.replace('_', ' ').title()}</h3>"

            if isinstance(test_result, dict) and "within_threshold" in test_result:
                status_class = "pass" if test_result["within_threshold"] else "fail"
                status_text = "PASS" if test_result["within_threshold"] else "FAIL"

                html_content += f"""
                <div class="test-result">
                    <p><strong>Status:</strong> <span class="{status_class}">{status_text}</span></p>
                """

                if "total_time_seconds" in test_result:
                    html_content += f"<p><strong>Total Time:</strong> {test_result['total_time_seconds']:.3f}s</p>"

                if "average_time_per_view" in test_result:
                    html_content += f"<p><strong>Average per View:</strong> {test_result['average_time_per_view']:.3f}s</p>"

                html_content += "</div>"

        html_content += """
            </div>
        </body>
        </html>
        """

        with open(report_path, "w") as f:
            f.write(html_content)

        print(f"\n📄 Performance report generated: {report_path}")
        return str(report_path)

    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, "conn"):
            self.conn.close()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Run performance regression tests for Duckalog catalogs"
    )
    parser.add_argument(
        "--config", "-c", required=True, help="Path to Duckalog configuration file"
    )
    parser.add_argument("--baseline", "-b", help="Path to baseline performance results")
    parser.add_argument(
        "--output-dir", "-o", default="reports", help="Output directory for reports"
    )
    parser.add_argument(
        "--save-results", help="Path to save current results for future comparison"
    )

    args = parser.parse_args()

    # Create test suite
    test_suite = PerformanceTestSuite(args.config, args.output_dir)

    try:
        # Run performance tests
        results = test_suite.run_all_tests()

        # Load baseline if provided
        comparison = None
        if args.baseline and Path(args.baseline).exists():
            with open(args.baseline, "r") as f:
                baseline_results = json.load(f)
            comparison = test_suite.compare_with_baseline(results, baseline_results)

        # Generate report
        report_path = test_suite.generate_report(results, comparison)

        # Save results if requested
        if args.save_results:
            with open(args.save_results, "w") as f:
                json.dump(results, f, indent=2)
            print(f"📄 Results saved to {args.save_results}")

        # Print summary
        print(f"\n{'=' * 50}")
        print("PERFORMANCE TEST SUMMARY")
        print(f"{'=' * 50}")
        print(f"Overall Status: {results['summary']['overall_status']}")

        if comparison:
            regression_status = (
                "REGRESSIONS DETECTED"
                if comparison["overall_regression"]
                else "NO REGRESSIONS"
            )
            print(f"Regression Analysis: {regression_status}")

        if results["summary"]["issues"]:
            print("\n⚠️ Issues:")
            for issue in results["summary"]["issues"]:
                print(f"  • {issue}")

        if results["summary"]["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in results["summary"]["recommendations"]:
                print(f"  • {rec}")

        # Exit with appropriate code
        exit_code = 0
        if results["summary"]["overall_status"] == "FAIL":
            exit_code = 1
        if comparison and comparison["overall_regression"]:
            exit_code = 1

        sys.exit(exit_code)

    finally:
        test_suite.cleanup()


if __name__ == "__main__":
    main()
