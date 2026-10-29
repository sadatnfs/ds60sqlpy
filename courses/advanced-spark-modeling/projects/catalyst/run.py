#!/usr/bin/env python3
"""Compile and execute inside a separately prepared Spark 4.0.1 Linux environment."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path


def main():
    home = Path(os.environ.get("SPARK_HOME", "/opt/spark"))
    jars = sorted((home / "jars").glob("*.jar"))
    if not list((home / "jars").glob("spark-sql_2.13-4.0.1.jar")):
        raise SystemExit("Prepare Spark 4.0.1, Scala 2.13 and JDK 17 before this project")
    root = Path(__file__).resolve().parent
    sources = sorted((root / "src/main/scala").rglob("*.scala"))
    with tempfile.TemporaryDirectory(prefix="ds60-catalyst-") as work:
        classes = Path(work) / "classes"
        classes.mkdir()
        subprocess.run(
            [
                "java",
                "-Xmx768m",
                "-cp",
                os.pathsep.join(map(str, jars)),
                "scala.tools.nsc.Main",
                "-usejavacp",
                "-d",
                str(classes),
                *map(str, sources),
            ],
            check=True,
        )
        archive = Path(work) / "teaching.jar"
        subprocess.run(["jar", "cf", str(archive), "-C", str(classes), "."], check=True)
        subprocess.run(
            [
                str(home / "bin/spark-submit"),
                "--master",
                "local[2]",
                "--driver-memory",
                "512m",
                "--class",
                "ds60.spark.Probe",
                str(archive),
            ],
            check=True,
        )
        print(
            json.dumps(
                {
                    "scope": "single-host CPU Spark/Catalyst compilation and execution",
                    "spark": "4.0.1",
                    "sources": {
                        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in sources
                    },
                }
            )
        )


if __name__ == "__main__":
    main()
