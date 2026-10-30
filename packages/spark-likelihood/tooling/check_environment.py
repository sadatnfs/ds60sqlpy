# SPDX-License-Identifier: Apache-2.0
"""Check an explicitly prepared image without installing packages or starting Spark."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
import os
import platform
import re
import site
import subprocess
import sys
from pathlib import Path

from locks import check_versions, selected_lock
from prepare_environment import prepare

PACKAGE = Path(__file__).resolve().parents[1]


def check() -> dict:
    architecture = {"aarch64": "arm64", "x86_64": "amd64"}.get(platform.machine())
    if platform.system() != "Linux" or architecture is None or sys.version_info[:2] != (3, 12):
        raise ValueError("This prepared image targets native Linux ARM64/AMD64 with Python 3.12")
    versions = check_versions(selected_lock("cpu", architecture))
    versions.update(check_versions(selected_lock("scientific", architecture)))
    spark_home = Path(os.environ.get("SPARK_HOME", "/opt/spark"))
    spark = prepare(spark_home, Path(site.getsitepackages()[0]), apply=False)
    for name in ("torch", "numpy", "scipy", "pandas", "pyarrow", "lightning", "pyspark", "py4j"):
        importlib.import_module(name)
    pyspark = sys.modules["pyspark"]
    if pyspark.__version__ != "4.0.1" or not str(pyspark.__file__).startswith(
        str(spark_home / "python/lib/pyspark.zip") + "/"
    ):
        raise ValueError(
            "Python imported another PySpark installation instead of the prepared archive"
        )
    package = importlib.import_module("ds60_spark_likelihood")
    installed = Path(package.__file__).resolve().parent
    if installed.is_relative_to(PACKAGE):
        raise ValueError(
            "Package import resolved through the source project instead of the installed wheel"
        )
    expected = {
        str(path.relative_to(PACKAGE / "src/ds60_spark_likelihood")): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for path in (PACKAGE / "src/ds60_spark_likelihood").rglob("*.py")
    }
    observed = {
        str(path.relative_to(installed)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in installed.rglob("*.py")
    }
    if not expected or expected != observed:
        raise ValueError("Installed wheel Python source differs from the copied project")
    if "ds60sqlpy" in sys.modules or importlib.util.find_spec("ds60sqlpy") is not None:
        raise ValueError("The image exposes an unintended classroom Python import dependency")
    result = subprocess.run(
        ["java", "-version"], check=True, capture_output=True, text=True, timeout=20
    )
    java = result.stdout + result.stderr
    match = re.search(r'version "(\d+)', java)
    if match is None or int(match[1]) not in {17, 21}:
        raise ValueError("Spark preparation needs a supported Java 17 or 21 runtime")
    return {
        "kind": "prepared-image-import-and-source-check",
        "architecture": architecture,
        "python": platform.python_version(),
        "java": java.strip(),
        "versions": versions,
        "spark": spark,
        "installed_package_sources": observed,
        "classroom_imported": False,
        "spark_application_executed": False,
        "distributed_training_executed": False,
        "passed": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    text = json.dumps(check(), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
