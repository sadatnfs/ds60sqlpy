# SPDX-License-Identifier: Apache-2.0
"""Explicitly bind Python to a reviewed Spark archive and prepare its Torch launcher."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib
import json
import site
import zipfile
from pathlib import Path


def archive_version(path: Path, member: str) -> str:
    with zipfile.ZipFile(path) as source:
        tree = ast.parse(source.read(member).decode())
    versions = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        if any(isinstance(target, ast.Name) and target.id == "__version__" for target in targets):
            if not isinstance(node.value, ast.Constant) or not isinstance(node.value.value, str):
                raise ValueError("Expected one literal version declaration in the prepared archive")
            versions.append(node.value.value)
    if len(versions) != 1:
        raise ValueError("Expected one literal version declaration in the prepared archive")
    return versions[0]


def spark_archives(home: Path) -> tuple[Path, Path]:
    archive = home / "python/lib/pyspark.zip"
    bridge = home / "python/lib/py4j-0.10.9.9-src.zip"
    if any(not path.is_file() or path.is_symlink() for path in (archive, bridge)):
        raise ValueError("Prepare the Spark 4.0.1 distribution and matching Py4J archive")
    if archive_version(archive, "pyspark/version.py") != "4.0.1":
        raise ValueError("The trusted training-wrapper preparation is specific to Spark 4.0.1")
    if archive_version(bridge, "py4j/version.py") != "0.10.9.9":
        raise ValueError("The Spark 4.0.1 Python archive needs its matching Py4J 0.10.9.9")
    return archive.resolve(), bridge.resolve()


def helper():
    return importlib.import_module("ds60_spark_likelihood.integrations.prepare_spark")


def prepare(home: Path, destination: Path, *, apply: bool) -> dict:
    archive, bridge = spark_archives(home)
    if any("\n" in str(path) or "\r" in str(path) for path in (archive, bridge)):
        raise ValueError("Python path entries must each occupy one literal line")
    expected = str(archive) + "\n" + str(bridge) + "\n"
    path_file = destination / "ds60_spark_likelihood_spark.pth"
    if path_file.is_symlink():
        raise ValueError("Refuse a symlink for the managed Python path file")
    if path_file.exists() and path_file.read_text() != expected:
        raise ValueError("Existing managed Python path file selects a different Spark distribution")
    preparation = helper()
    if apply:
        if not destination.is_dir():
            raise ValueError("The selected interpreter's site-packages directory must exist")
        receipt = preparation.patch_archive(archive)
        path_file.write_text(expected)
    else:
        receipt = preparation.wrapper_status(archive)
        if not path_file.is_file() or path_file.read_text() != expected:
            raise ValueError("Run explicit environment preparation before execution")
    status = preparation.wrapper_status(archive)
    if status["status"] != "prepared":
        raise ValueError("The reviewed Spark launcher is not prepared")
    return {
        "spark": "4.0.1",
        "pyspark_archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "py4j_archive_sha256": hashlib.sha256(bridge.read_bytes()).hexdigest(),
        "python_path_file": path_file.name,
        "wrapper": status,
        "preparation": receipt,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spark-home", type=Path, default=Path("/opt/spark"))
    parser.add_argument("--site-packages", type=Path, default=Path(site.getsitepackages()[0]))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = prepare(args.spark_home, args.site_packages, apply=args.apply)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
