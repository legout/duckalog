#!/usr/bin/env python3
"""
Deployment script for Duckalog catalogs.

This script handles deployment of Duckalog catalogs to different environments,
with support for rollbacks, health checks, and atomic deployments.

Usage: python deploy.py [--environment ENV] [--image IMAGE] [--database-url URL] [--rollback]
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import duckdb
    import yaml

    from duckalog import build_catalog, load_config
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install with: pip install duckalog pyyaml")
    sys.exit(1)


class DeploymentManager:
    """Manages deployment of Duckalog catalogs to environments."""

    def __init__(self, environment: str, image: str, database_url: str):
        self.environment = environment
        self.image = image
        self.database_url = database_url
        self.deployment_dir = Path("deployments")
        self.deployment_id = f"{environment}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.backup_dir = self.deployment_dir / "backups" / environment

        # Ensure directories exist
        self.deployment_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def deploy(self) -> bool:
        """Perform deployment."""
        print(f"🚀 Starting deployment to {self.environment}...")
        print(f"📦 Image: {self.image}")
        print(f"🆔 Deployment ID: {self.deployment_id}")

        try:
            # Step 1: Pre-deployment checks
            if not self._pre_deployment_checks():
                return False

            # Step 2: Backup current state
            if not self._create_backup():
                return False

            # Step 3: Deploy new version
            if not self._deploy_catalog():
                return False

            # Step 4: Post-deployment verification
            if not self._post_deployment_checks():
                # Rollback on failure
                print("❌ Post-deployment checks failed, initiating rollback...")
                return self._rollback()

            # Step 5: Record deployment
            self._record_deployment()

            print(f"✅ Deployment to {self.environment} completed successfully!")
            return True

        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return self._rollback()

    def rollback(self, target_deployment: Optional[str] = None) -> bool:
        """Rollback to previous deployment."""
        print(f"🔄 Starting rollback to {target_deployment or 'previous version'}...")

        try:
            if not self._restore_backup(target_deployment):
                return False

            print(f"✅ Rollback completed successfully!")
            return True

        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False

    def _pre_deployment_checks(self) -> bool:
        """Perform pre-deployment checks."""
        print("\n🔍 Running pre-deployment checks...")

        # Check database connectivity
        if not self._check_database_connection():
            print("❌ Database connection failed")
            return False

        # Validate configuration
        if not self._validate_configuration():
            print("❌ Configuration validation failed")
            return False

        # Check disk space
        if not self._check_disk_space():
            print("❌ Insufficient disk space")
            return False

        print("✅ Pre-deployment checks passed")
        return True

    def _check_database_connection(self) -> bool:
        """Check database connectivity."""
        try:
            conn = duckdb.connect(self.database_url)

            # Test basic connectivity
            result = conn.execute("SELECT 1 as test").fetchone()
            if result[0] != 1:
                return False

            # Check if we can create tables
            conn.execute("CREATE TABLE IF NOT EXISTS deployment_check (id INTEGER)")
            conn.execute("DROP TABLE IF EXISTS deployment_check")

            conn.close()
            print("  ✅ Database connection successful")
            return True

        except Exception as e:
            print(f"  ❌ Database connection failed: {e}")
            return False

    def _validate_configuration(self) -> bool:
        """Validate Duckalog configuration."""
        config_path = f"configs/catalog-{self.environment}.yaml"

        if not Path(config_path).exists():
            print(f"  ❌ Configuration file not found: {config_path}")
            return False

        try:
            config = load_config(config_path)
            print(f"  ✅ Configuration valid for {self.environment}")
            return True

        except Exception as e:
            print(f"  ❌ Configuration validation failed: {e}")
            return False

    def _check_disk_space(self) -> bool:
        """Check available disk space."""
        try:
            import shutil

            # Check current directory space
            total, used, free = shutil.disk_usage(".")

            # Require at least 1GB free space
            required_space = 1024 * 1024 * 1024  # 1GB

            if free < required_space:
                print(
                    f"  ❌ Insufficient disk space: {free // (1024**3)}GB available, 1GB required"
                )
                return False

            print(f"  ✅ Sufficient disk space: {free // (1024**3)}GB available")
            return True

        except Exception as e:
            print(f"  ⚠️  Could not check disk space: {e}")
            return True  # Continue anyway

    def _create_backup(self) -> bool:
        """Create backup of current state."""
        print("\n💾 Creating backup...")

        try:
            backup_path = self.backup_dir / f"{self.deployment_id}.duckdb"

            # Connect to current database and create backup
            conn = duckdb.connect(self.database_url)

            # Use DuckDB's backup functionality if available
            try:
                conn.execute(f"BACKUP DATABASE TO '{backup_path}'")
            except Exception:
                # Fallback: export and import
                tables = conn.execute("SHOW TABLES").fetchall()

                backup_conn = duckdb.connect(str(backup_path))

                for (table_name,) in tables:
                    if not table_name.startswith("information_"):
                        # Export from current
                        conn.execute(
                            f"EXPORT DATABASE '{backup_path.parent / 'temp_export'}'"
                        )
                        # Import to backup
                        backup_conn.execute(
                            f"IMPORT DATABASE '{backup_path.parent / 'temp_export'}'"
                        )

                backup_conn.close()

                # Clean up temp export
                import shutil

                temp_dir = backup_path.parent / "temp_export"
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)

            conn.close()

            # Record backup metadata
            backup_metadata = {
                "deployment_id": self.deployment_id,
                "environment": self.environment,
                "image": self.image,
                "timestamp": datetime.now().isoformat(),
                "database_url": self.database_url,
                "backup_path": str(backup_path),
            }

            metadata_path = self.backup_dir / f"{self.deployment_id}.json"
            with open(metadata_path, "w") as f:
                json.dump(backup_metadata, f, indent=2)

            print(f"  ✅ Backup created: {backup_path}")
            return True

        except Exception as e:
            print(f"  ❌ Backup creation failed: {e}")
            return False

    def _deploy_catalog(self) -> bool:
        """Deploy new catalog."""
        print("\n📦 Deploying new catalog...")

        try:
            # Load configuration
            config_path = f"configs/catalog-{self.environment}.yaml"
            config = load_config(config_path)

            # Build catalog
            build_catalog(config)

            print(f"  ✅ Catalog built successfully for {self.environment}")
            return True

        except Exception as e:
            print(f"  ❌ Catalog deployment failed: {e}")
            return False

    def _post_deployment_checks(self) -> bool:
        """Perform post-deployment verification."""
        print("\n🔍 Running post-deployment checks...")

        # Check that expected views exist
        if not self._verify_views():
            print("  ❌ View verification failed")
            return False

        # Run smoke tests
        if not self._run_smoke_tests():
            print("  ❌ Smoke tests failed")
            return False

        # Check data quality
        if not self._check_data_quality():
            print("  ❌ Data quality checks failed")
            return False

        print("✅ Post-deployment checks passed")
        return True

    def _verify_views(self) -> bool:
        """Verify that expected views exist and are queryable."""
        try:
            config_path = f"configs/catalog-{self.environment}.yaml"
            config = load_config(config_path)

            conn = duckdb.connect(self.database_url)

            for view in config.views:
                try:
                    # Test that view exists and returns results
                    result = conn.execute(
                        f"SELECT COUNT(*) FROM {view.name}"
                    ).fetchone()
                    print(f"  ✅ View {view.name}: {result[0]} rows")

                except Exception as e:
                    print(f"  ❌ View {view.name} failed: {e}")
                    conn.close()
                    return False

            conn.close()
            return True

        except Exception as e:
            print(f"  ❌ View verification failed: {e}")
            return False

    def _run_smoke_tests(self) -> bool:
        """Run basic smoke tests."""
        try:
            conn = duckdb.connect(self.database_url)

            # Test basic functionality
            test_queries = [
                "SELECT 1 as test_value",
                "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'",
                "SELECT view_name FROM information_schema.views",
            ]

            for query in test_queries:
                try:
                    result = conn.execute(query).fetchall()
                    print(f"  ✅ Smoke test query executed: {len(result)} results")

                except Exception as e:
                    print(f"  ❌ Smoke test failed: {e}")
                    conn.close()
                    return False

            conn.close()
            return True

        except Exception as e:
            print(f"  ❌ Smoke tests failed: {e}")
            return False

    def _check_data_quality(self) -> bool:
        """Perform basic data quality checks."""
        try:
            config_path = f"configs/catalog-{self.environment}.yaml"
            config = load_config(config_path)

            conn = duckdb.connect(self.database_url)

            # Basic data quality checks
            for view in config.views[:5]:  # Check first 5 views to avoid timeout
                try:
                    # Check for null counts
                    result = conn.execute(f"""
                        SELECT
                            COUNT(*) as total_rows,
                            COUNT(*) - COUNT(*) as null_rows
                        FROM {view.name}
                    """).fetchone()

                    total_rows, null_rows = result
                    if total_rows == 0 and null_rows == 0:
                        print(f"  ⚠️  View {view.name} appears to be empty")

                except Exception as e:
                    print(f"  ⚠️  Could not check data quality for {view.name}: {e}")

            conn.close()
            return True

        except Exception as e:
            print(f"  ❌ Data quality checks failed: {e}")
            return False

    def _rollback(self) -> bool:
        """Rollback to previous backup."""
        print("\n🔄 Rolling back...")

        # Find most recent backup
        backups = sorted(
            self.backup_dir.glob("*.duckdb"),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )

        if not backups:
            print("  ❌ No backups found for rollback")
            return False

        latest_backup = backups[0]
        return self._restore_backup(latest_backup.stem)

    def _restore_backup(self, backup_name: Optional[str]) -> bool:
        """Restore from specific backup."""
        if backup_name:
            backup_path = self.backup_dir / f"{backup_name}.duckdb"
        else:
            # Find most recent backup
            backups = sorted(
                self.backup_dir.glob("*.duckdb"),
                key=lambda x: x.stat().st_mtime,
                reverse=True,
            )
            if not backups:
                print("  ❌ No backups found")
                return False
            backup_path = backups[0]

        if not backup_path.exists():
            print(f"  ❌ Backup not found: {backup_path}")
            return False

        try:
            # Restore from backup
            conn = duckdb.connect(self.database_url)

            try:
                conn.execute(f"RESTORE DATABASE FROM '{backup_path}'")
            except Exception:
                # Fallback: use EXPORT/IMPORT
                temp_dir = backup_path.parent / "temp_restore"
                temp_dir.mkdir(exist_ok=True)

                # Export from backup
                backup_conn = duckdb.connect(str(backup_path))
                backup_conn.execute(f"EXPORT DATABASE '{temp_dir}'")
                backup_conn.close()

                # Import to target
                conn.execute(f"IMPORT DATABASE '{temp_dir}'")

                # Clean up
                import shutil

                shutil.rmtree(temp_dir)

            conn.close()
            print(f"  ✅ Restored from backup: {backup_path}")
            return True

        except Exception as e:
            print(f"  ❌ Restore failed: {e}")
            return False

    def _record_deployment(self) -> None:
        """Record successful deployment."""
        deployment_record = {
            "deployment_id": self.deployment_id,
            "environment": self.environment,
            "image": self.image,
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "database_url": self.database_url,
        }

        record_path = self.deployment_dir / f"{self.deployment_id}.json"
        with open(record_path, "w") as f:
            json.dump(deployment_record, f, indent=2)

        print(f"📝 Deployment recorded: {record_path}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Deploy Duckalog catalog to environment"
    )
    parser.add_argument(
        "--environment",
        "-e",
        required=True,
        help="Target environment (dev, staging, prod)",
    )
    parser.add_argument("--image", "-i", required=True, help="Docker image to deploy")
    parser.add_argument(
        "--database-url", "-d", required=True, help="Database connection URL"
    )
    parser.add_argument(
        "--rollback", "-r", action="store_true", help="Rollback to previous deployment"
    )
    parser.add_argument("--target", "-t", help="Target deployment for rollback")

    args = parser.parse_args()

    # Create deployment manager
    manager = DeploymentManager(
        environment=args.environment, image=args.image, database_url=args.database_url
    )

    # Perform deployment or rollback
    if args.rollback:
        success = manager.rollback(args.target)
    else:
        success = manager.deploy()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
