"""Fixed installed-wheel and real executor import checks for the owned workshop."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import shutil
import sys
from pathlib import Path
from zipfile import ZipFile


def installed_identity():
    import ds60_spark_likelihood as package

    distribution = importlib.metadata.distribution("ds60-spark-likelihood")
    root = Path(package.__file__).resolve().parent
    if (
        "site-packages" not in root.parts
        or root != distribution.locate_file("ds60_spark_likelihood").resolve()
    ):
        raise RuntimeError("Package import is masked by a source checkout")
    if list(package.__path__) != [str(root)] or distribution.read_text("WHEEL") is None:
        raise RuntimeError("Package must be one ordinary installed wheel")
    direct = distribution.read_text("direct_url.json")
    if direct and json.loads(direct).get("dir_info", {}).get("editable"):
        raise RuntimeError("Editable installation cannot qualify an installed wheel")
    if shutil.which("R") or shutil.which("Rscript"):
        raise RuntimeError("Primary package qualification requires an R-free environment")
    if any(name == "ds60sqlpy" or name.startswith("ds60sqlpy.") for name in sys.modules):
        raise RuntimeError("Standalone check imported classroom code")
    files = {
        "ds60_spark_likelihood/" + path.relative_to(root).as_posix(): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for path in sorted(root.rglob("*.py"))
    }
    return {
        "distribution": distribution.metadata["Name"],
        "version": distribution.version,
        "package_path": str(root),
        "installed_source": files,
        "classroom_imported": False,
        "r_dependency_required": False,
    }


def wheel_identity():
    identity = installed_identity()
    source = Path("/opt/ds60-package-source/src")
    declared = {
        path.relative_to(source).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((source / "ds60_spark_likelihood").rglob("*.py"))
    }
    wheels = list(Path("/opt/ds60-wheels").glob("ds60_spark_likelihood-*.whl"))
    if len(wheels) != 1:
        raise RuntimeError("One retained standalone wheel is required")
    with ZipFile(wheels[0]) as archive:
        names = archive.namelist()
        if len(set(names)) != len(names):
            raise RuntimeError("Duplicate wheel members")
        packaged = {
            name: hashlib.sha256(archive.read(name)).hexdigest()
            for name in names
            if name.startswith("ds60_spark_likelihood/") and name.endswith(".py")
        }
        metadata = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metadata) != 1 or any(name.startswith("ds60sqlpy/") for name in names):
            raise RuntimeError("Unexpected classroom or metadata content in standalone wheel")
        text = archive.read(metadata[0]).decode()
        if any(
            line.startswith("Requires-Dist:")
            and any(word in line.lower() for word in ("rpy2", "ds60sqlpy"))
            for line in text.splitlines()
        ):
            raise RuntimeError("Unexpected R/classroom distribution dependency")
    if not declared or identity["installed_source"] != declared or packaged != declared:
        raise RuntimeError("Wheel, installed package and declared source bytes differ")
    return {
        **identity,
        "isolated_python": bool(sys.flags.isolated),
        "wheel_name": wheels[0].name,
        "wheel_sha256": hashlib.sha256(wheels[0].read_bytes()).hexdigest(),
        "wheel_source": packaged,
        "declared_source": declared,
    }


def executor_identity(index, rows):
    count = sum(1 for _ in rows)
    identity = installed_identity()
    yield {"partition": index, "fixture_rows": count, **identity}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=("identity", "workers", "numerical", "spark", "ml"))
    case = parser.parse_args().case
    if case == "identity":
        print(json.dumps(wheel_identity(), sort_keys=True))
    elif case == "workers":
        from pyspark.sql import SparkSession

        spark = (
            SparkSession.builder.master("local[2]")
            .appName("installed-package-executors")
            .config("spark.ui.enabled", "false")
            .config("spark.driver.host", "127.0.0.1")
            .config("spark.driver.bindAddress", "127.0.0.1")
            .getOrCreate()
        )
        spark.sparkContext.setLogLevel("ERROR")
        try:
            records = (
                spark.sparkContext.parallelize([0, 1], 2)
                .mapPartitionsWithIndex(executor_identity)
                .collect()
            )
            assert sorted(row["partition"] for row in records) == [0, 1]
            assert all(row["fixture_rows"] == 1 for row in records)
            print(
                json.dumps(
                    {
                        "kind": "package-executor-isolation",
                        "passed": True,
                        "spark": spark.version,
                        "records": records,
                    },
                    sort_keys=True,
                )
            )
        finally:
            spark.stop()
    else:
        from ds60_spark_likelihood.validation import main as validate

        validate([case])


if __name__ == "__main__":
    main()
