#!/usr/bin/env python3
"""
Automated DuckDB performance tuner.

Analyzes system resources and query patterns to recommend optimal
DuckDB configuration settings.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import argparse


class SystemProfiler:
    """Profile system resources and capabilities."""

    def __init__(self):
        self.system_info = {}

    def profile(self):
        """Profile the current system."""
        print("🔍 Profiling system resources...")

        # CPU Information
        self._profile_cpu()

        # Memory Information
        self._profile_memory()

        # Storage Information
        self._profile_storage()

        # DuckDB Version
        self._profile_duckdb()

        return self.system_info

    def _profile_cpu(self):
        """Profile CPU information."""
        try:
            import psutil
            cpu_count = psutil.cpu_count(logical=False)  # Physical cores
            cpu_count_logical = psutil.cpu_count(logical=True)  # Logical cores

            self.system_info.update({
                "cpu_physical_cores": cpu_count,
                "cpu_logical_cores": cpu_count_logical,
                "cpu_threads_per_core": cpu_count_logical // cpu_count if cpu_count > 0 else 1
            })

            print(f"  CPU: {cpu_count} physical cores, {cpu_count_logical} logical cores")

        except ImportError:
            # Fallback to basic CPU detection
            try:
                result = subprocess.run(['nproc'], capture_output=True, text=True)
                cpu_count = int(result.stdout.strip())
                self.system_info.update({
                    "cpu_physical_cores": cpu_count,
                    "cpu_logical_cores": cpu_count,
                    "cpu_threads_per_core": 1
                })
                print(f"  CPU: {cpu_count} cores (basic detection)")
            except:
                self.system_info.update({
                    "cpu_physical_cores": 4,  # Conservative default
                    "cpu_logical_cores": 4,
                    "cpu_threads_per_core": 1
                })
                print("  CPU: Using default values (4 cores)")

    def _profile_memory(self):
        """Profile memory information."""
        try:
            import psutil
            memory = psutil.virtual_memory()

            total_gb = memory.total / (1024**3)
            available_gb = memory.available / (1024**3)

            self.system_info.update({
                "memory_total_gb": total_gb,
                "memory_available_gb": available_gb,
                "memory_usage_percent": memory.percent
            })

            print(f"  Memory: {total_gb:.1f} GB total, {available_gb:.1f} GB available ({memory.percent:.1f}% used)")

        except ImportError:
            # Fallback
            self.system_info.update({
                "memory_total_gb": 8.0,  # Conservative default
                "memory_available_gb": 4.0,
                "memory_usage_percent": 50.0
            })
            print("  Memory: Using default values (8 GB total)")

    def _profile_storage(self):
        """Profile storage information."""
        try:
            import psutil
            disk = psutil.disk_usage('/')

            total_gb = disk.total / (1024**3)
            free_gb = disk.free / (1024**3)

            self.system_info.update({
                "storage_total_gb": total_gb,
                "storage_free_gb": free_gb
            })

            print(f"  Storage: {total_gb:.1f} GB total, {free_gb:.1f} GB free")

        except ImportError:
            # Fallback
            self.system_info.update({
                "storage_total_gb": 100.0,
                "storage_free_gb": 50.0
            })
            print("  Storage: Using default values (100 GB total)")

    def _profile_duckdb(self):
        """Profile DuckDB version and capabilities."""
        try:
            import duckdb
            version = duckdb.__version__

            self.system_info.update({
                "duckdb_version": version
            })

            print(f"  DuckDB: version {version}")

        except ImportError:
            self.system_info.update({
                "duckdb_version": "unknown"
            })
            print("  DuckDB: Could not determine version")


class PerformanceTuner:
    """Generate optimized DuckDB configurations based on system profiling."""

    def __init__(self, system_info):
        self.system_info = system_info

    def recommend_configuration(self, workload_type="general"):
        """Recommend optimal DuckDB configuration."""
        print(f"\n🎯 Generating configuration for {workload_type} workload...")

        config = {
            "version": 1,
            "duckdb": {
                "database": "optimized_catalog.duckdb",
                "install_extensions": ["httpfs", "parquet", "json"],
                "pragmas": []
            }
        }

        # Determine configuration based on workload type
        if workload_type == "general":
            config = self._configure_general(config)
        elif workload_type == "analytics":
            config = self._configure_analytics(config)
        elif workload_type == "concurrent":
            config = self._configure_concurrent(config)
        elif workload_type == "memory_constrained":
            config = self._configure_memory_constrained(config)

        return config

    def _configure_general(self, config):
        """Configure for general-purpose workloads."""
        cpu_cores = self.system_info.get("cpu_logical_cores", 4)
        memory_gb = self.system_info.get("memory_total_gb", 8)

        # Memory allocation (40% of available RAM)
        memory_limit_gb = max(1, int(memory_gb * 0.4))
        config["duckdb"]["pragmas"].extend([
            f"SET memory_limit='{memory_limit_gb}GB'",
            f"SET threads={cpu_cores}",
            "SET enable_optimizer=true",
            "SET enable_optimizer_caching=true",
            "SET force_parallelism=true",
            "SET enable_progress_bar=true"
        ])

        # Add memory mapping for systems with sufficient RAM
        if memory_gb >= 8:
            config["duckdb"]["pragmas"].append("SET enable_memory_map=true")

        return config

    def _configure_analytics(self, config):
        """Configure for analytical workloads."""
        cpu_cores = self.system_info.get("cpu_logical_cores", 4)
        memory_gb = self.system_info.get("memory_total_gb", 8)

        # Aggressive memory allocation (60% of available RAM)
        memory_limit_gb = max(2, int(memory_gb * 0.6))
        config["duckdb"]["pragmas"].extend([
            f"SET memory_limit='{memory_limit_gb}GB'",
            f"SET threads={max(8, cpu_cores)}",  # At least 8 threads for analytics
            "SET enable_memory_map=true",
            "SET enable_optimizer=true",
            "SET enable_optimizer_caching=true",
            "SET force_parallelism=true",
            "SET enable_profiling=true",
            "SET enable_join_order=true",
            "SET enable_propagate_null_elimination=true",
            "SET enable_distinct_projection_optimization=true"
        ])

        # Add FTS extension for text analytics
        config["duckdb"]["install_extensions"].append("fts")

        return config

    def _configure_concurrent(self, config):
        """Configure for high-concurrency workloads."""
        cpu_cores = self.system_info.get("cpu_logical_cores", 4)
        memory_gb = self.system_info.get("memory_total_gb", 8)

        # Conservative memory allocation to handle multiple connections
        memory_limit_gb = max(1, int(memory_gb * 0.3))
        config["duckdb"]["pragmas"].extend([
            f"SET memory_limit='{memory_limit_gb}GB'",
            f"SET threads={min(cpu_cores, 12)}",  # Cap at 12 threads for concurrency
            "SET enable_optimizer=true",
            "SET enable_optimizer_caching=true",
            "SET force_parallelism=false",  # Let DuckDB decide for concurrent workloads
            "SET enable_object_cache=true",
            "SET wal_autocheckpoint=250000",
            "SET checkpoint_threshold='500MB'"
        ])

        return config

    def _configure_memory_constrained(self, config):
        """Configure for memory-constrained environments."""
        memory_gb = self.system_info.get("memory_total_gb", 8)

        # Very conservative memory allocation (20% of available RAM)
        memory_limit_gb = max(0.5, int(memory_gb * 0.2))
        config["duckdb"]["pragmas"].extend([
            f"SET memory_limit='{memory_limit_gb}GB'",
            "SET threads=2",  # Limited threads to reduce memory pressure
            "SET enable_optimizer=true",
            "SET enable_optimizer_caching=false",  # Disable caching to save memory
            "SET force_parallelism=false",
            "SET enable_progress_bar=true",
            "SET checkpoint_threshold='100MB'",
            "SET enable_profiling=false"  # Disable profiling to save resources
        ])

        # Minimal extensions to reduce memory usage
        config["duckdb"]["install_extensions"] = ["parquet"]

        return config

    def generate_recommendations(self):
        """Generate performance recommendations based on system profile."""
        recommendations = []

        memory_gb = self.system_info.get("memory_total_gb", 8)
        cpu_cores = self.system_info.get("cpu_logical_cores", 4)

        # Memory recommendations
        if memory_gb < 4:
            recommendations.append({
                "category": "Memory",
                "priority": "High",
                "message": "Low memory detected. Consider using memory_constrained configuration or upgrading RAM."
            })
        elif memory_gb >= 16:
            recommendations.append({
                "category": "Memory",
                "priority": "Info",
                "message": "High memory available. Consider analytics configuration for best performance."
            })

        # CPU recommendations
        if cpu_cores < 4:
            recommendations.append({
                "category": "CPU",
                "priority": "Medium",
                "message": "Limited CPU cores. Performance will benefit from more cores for parallel queries."
            })

        # General recommendations
        recommendations.extend([
            {
                "category": "Storage",
                "priority": "Info",
                "message": "Use fast SSD storage for temporary files and databases."
            },
            {
                "category": "Configuration",
                "priority": "Info",
                "message": "Test different configurations with your actual workload for optimal results."
            }
        ])

        return recommendations


def save_configuration(config, filename, output_dir="generated_configs"):
    """Save configuration to a YAML file."""
    import yaml

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    filepath = output_path / filename

    with open(filepath, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)

    print(f"💾 Configuration saved to: {filepath}")
    return filepath


def main():
    """Main performance tuner function."""
    parser = argparse.ArgumentParser(description="DuckDB Performance Tuner")
    parser.add_argument(
        "--workload",
        choices=["general", "analytics", "concurrent", "memory_constrained"],
        default="general",
        help="Type of workload to optimize for"
    )
    parser.add_argument(
        "--output",
        default="generated_configs",
        help="Output directory for generated configurations"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save the generated configuration to a file"
    )
    parser.add_argument(
        "--profile-only",
        action="store_true",
        help="Only profile the system, don't generate configurations"
    )

    args = parser.parse_args()

    print("🚀 DuckDB Performance Tuner")
    print("=" * 50)

    # Profile system
    profiler = SystemProfiler()
    system_info = profiler.profile()

    if args.profile_only:
        print("\n📊 System Profile:")
        print(json.dumps(system_info, indent=2))
        return

    # Generate configuration
    tuner = PerformanceTuner(system_info)
    config = tuner.recommend_configuration(args.workload)

    # Print recommendations
    recommendations = tuner.generate_recommendations()
    if recommendations:
        print("\n💡 Performance Recommendations:")
        for rec in recommendations:
            priority_icon = {"High": "🔴", "Medium": "🟡", "Info": "🔵"}.get(rec["priority"], "⚪")
            print(f"  {priority_icon} {rec['category']}: {rec['message']}")

    # Display generated configuration
    print(f"\n📋 Generated Configuration ({args.workload} workload):")
    print("-" * 30)

    import yaml
    print(yaml.dump(config, default_flow_style=False, indent=2))

    # Save configuration if requested
    if args.save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tuned_{args.workload}_{timestamp}.yaml"
        save_configuration(config, filename, args.output)

        # Also save system profile for reference
        profile_filename = f"system_profile_{timestamp}.json"
        profile_path = Path(args.output) / profile_filename
        with open(profile_path, 'w') as f:
            json.dump(system_info, f, indent=2)
        print(f"💾 System profile saved to: {profile_path}")

    print("\n🎯 Next steps:")
    print("1. Save the configuration: python performance-tuner.py --save --workload analytics")
    print("2. Generate test data: python generate-datasets.py --size medium")
    print("3. Run benchmarks: python benchmark.py --config generated_configs/tuned_analytics.yaml")


if __name__ == "__main__":
    main()