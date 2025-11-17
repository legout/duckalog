#!/usr/bin/env python3
"""Utility for extracting version information for GitHub workflows."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Tuple

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def run_git_command(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def parse_semver(value: str) -> Tuple[int, int, int] | None:
    if not SEMVER_RE.match(value):
        return None
    parts = value.split(".")
    try:
        return tuple(int(part) for part in parts)  # type: ignore[return-value]
    except ValueError:
        return None


def compare_versions(
    current: Tuple[int, int, int] | None, latest: Tuple[int, int, int] | None
) -> int:
    if current is None or latest is None:
        return 0
    if current > latest:
        return 1
    if current < latest:
        return -1
    return 0


def load_version(pyproject_path: Path) -> str:
    data = pyproject_path.read_bytes()
    try:
        import tomllib  # type: ignore[attr-defined]
    except ImportError:
        import tomli as tomllib  # type: ignore[no-redef]
    project = tomllib.loads(data.decode("utf-8"))
    return project["project"]["version"]


def detect_version_info(pyproject_path: Path) -> Dict[str, str]:
    current_version = load_version(pyproject_path)
    latest_tag = run_git_command(
        "describe", "--tags", "--abbrev=0", "--match", "v[0-9]*"
    )
    latest_version = latest_tag.lstrip("v") if latest_tag else "0.0.0"
    current_tuple = parse_semver(current_version)
    latest_tuple = parse_semver(latest_version)
    comparison = compare_versions(current_tuple, latest_tuple)

    tag_name = f"v{current_version}"
    tag_exists = bool(run_git_command("rev-parse", "--verify", f"refs/tags/{tag_name}"))

    info = {
        "current_version": current_version,
        "latest_version": latest_version,
        "latest_tag": latest_tag,
        "version_changed": str(current_version != latest_version).lower(),
        "valid_semver": str(current_tuple is not None).lower(),
        "should_tag": str(comparison == 1).lower(),
        "tag_name": tag_name,
        "tag_exists": str(tag_exists).lower(),
    }
    return info


def write_outputs(info: Dict[str, str], output_path: Path | None) -> None:
    if output_path is None:
        return
    with output_path.open("a", encoding="utf-8") as handle:
        for key, value in info.items():
            handle.write(f"{key}={value}\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract version info for GitHub Actions workflows."
    )
    parser.add_argument(
        "--pyproject",
        type=Path,
        default=Path("pyproject.toml"),
        help="Path to the pyproject.toml file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(os.environ.get("GITHUB_OUTPUT", ""))
        if os.environ.get("GITHUB_OUTPUT")
        else None,
        help="Optional path to a GitHub Actions output file.",
    )
    args = parser.parse_args()

    info = detect_version_info(args.pyproject)
    print(json.dumps(info, indent=2))
    write_outputs(info, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
