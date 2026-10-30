#!/usr/bin/env python3
"""Compile only JVM test classes against an already prepared production JAR, offline."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--production-jar", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--spark-home", type=Path, default=Path("/opt/spark"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    source = sorted((root / "src/test/scala").rglob("*.scala"))
    production = args.production_jar.absolute()
    output = args.output.absolute()
    if not production.is_file() or production.is_symlink() or output.exists():
        raise SystemExit("Use a prepared ordinary production JAR and a fresh checks JAR path")
    jars = sorted((args.spark_home.absolute() / "jars").glob("*.jar"))
    if not any(path.name == "spark-sql_2.13-4.0.1.jar" for path in jars):
        raise SystemExit("Prepare exact Spark4.0.1/Scala2.13 jars first")
    before = {str(path.relative_to(root)): digest(path) for path in source}
    production_hash = digest(production)
    tool_hash = digest(Path(__file__))
    compiler = {path.name: digest(path) for path in jars}
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="tmbad-check-classes-") as temporary:
        subprocess.run(
            [
                "java",
                "-Xmx768m",
                "-cp",
                os.pathsep.join(map(str, [*jars, production])),
                "scala.tools.nsc.Main",
                "-usejavacp",
                "-release",
                "17",
                "-d",
                temporary,
                *map(str, source),
            ],
            check=True,
            timeout=180,
        )
        subprocess.run(["jar", "cf", str(output), "-C", temporary, "."], check=True, timeout=30)
    if before != {str(path.relative_to(root)): digest(path) for path in source}:
        raise RuntimeError("Test source changed during compilation")
    if digest(production) != production_hash or digest(Path(__file__)) != tool_hash:
        raise RuntimeError("Prepared production JAR or build helper changed")
    if compiler != {path.name: digest(path) for path in jars}:
        raise RuntimeError("Prepared compiler classpath changed")
    receipt = {
        "kind": "spark-tmbad-jvm-tests-compilation",
        "compiled": True,
        "executed": False,
        "production_jar_sha256": production_hash,
        "checks_jar_sha256": digest(output),
        "test_source_sha256": before,
        "build_script_sha256": tool_hash,
        "compiler_jars": compiler,
        "scope": "tests only; no duplicated production classes",
    }
    output.with_suffix(output.suffix + ".json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({key: value for key, value in receipt.items() if key != "compiler_jars"}))


if __name__ == "__main__":
    main()
