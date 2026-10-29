#!/usr/bin/env python3
"""Compile the original Scala adapter with prepared Spark jars, then execute it offline."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile-only", action="store_true")
    args = parser.parse_args()
    home = Path(os.environ.get("SPARK_HOME", "/opt/spark"))
    if not (home / "jars/spark-sql_2.13-4.0.1.jar").is_file():
        raise SystemExit("Prepare the exact Spark 4.0.1 / Scala 2.13 environment first")
    version = subprocess.run(
        ["java", "-version"], capture_output=True, text=True, check=True, timeout=15
    )
    if not re.search(r'version "21[.\"]', version.stderr + version.stdout):
        raise SystemExit("This Scala/TMB project requires the prepared JDK 21")
    root = Path(__file__).resolve().parent
    sources = sorted((root / "src/main/scala").rglob("*.scala"))
    if len(sources) != 2:
        raise SystemExit("Expected the complete two-file Scala adapter and example")
    project = root.parent
    boundary_paths = [
        project / "registry.json",
        project / "R/evaluate_registered.R",
        *(
            project / "spark_tmb" / name
            for name in ("__init__.py", "cli.py", "registry.py", "runtime.py", "processes.py")
        ),
        *sorted((project / "models").glob("*.cpp")),
    ]
    boundary_hashes = {
        str(path.relative_to(project)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in boundary_paths
    }
    owned_paths = [*sources, root / "run.py"]
    owned_hashes = {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in owned_paths
    }
    jars = os.pathsep.join(str(path) for path in sorted((home / "jars").glob("*.jar")))
    with tempfile.TemporaryDirectory(prefix="ds60-scala-tmb-build-") as directory:
        work = Path(directory)
        classes = work / "classes"
        classes.mkdir()
        subprocess.run(
            [
                "java",
                "-Xmx768m",
                "-cp",
                jars,
                "scala.tools.nsc.Main",
                "-usejavacp",
                "-d",
                str(classes),
                *map(str, sources),
            ],
            check=True,
            timeout=120,
        )
        jar = work / "scala-tmb.jar"
        subprocess.run(["jar", "cf", str(jar), "-C", str(classes), "."], check=True, timeout=30)
        if not args.compile_only:
            subprocess.run(
                [
                    str(home / "bin/spark-submit"),
                    "--master",
                    "local[2]",
                    "--driver-memory",
                    "512m",
                    "--class",
                    "ds60.spark.tmb.Example",
                    str(jar),
                ],
                check=True,
                timeout=600,
            )
        if any(
            hashlib.sha256(path.read_bytes()).hexdigest()
            != owned_hashes[str(path.relative_to(root))]
            for path in owned_paths
        ):
            raise RuntimeError("Scala source changed during qualification")
        if any(
            hashlib.sha256(path.read_bytes()).hexdigest()
            != boundary_hashes[str(path.relative_to(project))]
            for path in boundary_paths
        ):
            raise RuntimeError("Prepared-model boundary source changed during qualification")
        spec = importlib.util.find_spec("spark_tmb.cli")
        cli = None if spec is None or spec.origin is None else Path(spec.origin)
        print(
            json.dumps(
                {
                    "kind": "scala-tmb-compilation-and-execution",
                    "compiled": True,
                    "owned_source_sha256": owned_hashes,
                    "boundary_source_sha256": boundary_hashes,
                    "executed": not args.compile_only,
                    "scope": "native single-host CPU; no remote cluster or performance claim",
                    "sources": {
                        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in sources
                    },
                    "cli_sha256": None
                    if cli is None
                    else hashlib.sha256(cli.read_bytes()).hexdigest(),
                },
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
