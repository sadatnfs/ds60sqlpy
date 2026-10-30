"""Compile the original probe offline with the already installed Spark toolchain."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = Path(__file__).with_name("Probe.scala")
    home = Path(os.environ.get("SPARK_HOME", "/opt/spark"))
    jars = sorted((home / "jars").glob("*.jar"))
    if not (home / "jars/spark-sql_2.13-4.0.1.jar").is_file():
        raise SystemExit(
            "Prepare Spark 4.0.1 with Scala 2.13 first; compilation never downloads jars"
        )
    if args.output.exists():
        raise SystemExit("Choose a fresh probe output path")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="integration-compile-") as temporary:
        subprocess.run(
            [
                "java",
                "-Xmx512m",
                "-cp",
                os.pathsep.join(map(str, jars)),
                "scala.tools.nsc.Main",
                "-usejavacp",
                "-release",
                "17",
                "-d",
                temporary,
                str(source),
            ],
            check=True,
            timeout=180,
        )
        subprocess.run(
            ["jar", "cf", str(args.output), "-C", temporary, "."], check=True, timeout=30
        )

    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    args.output.with_suffix(".json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "scope": "compilation only",
                "source_sha256": digest(source),
                "compiler_jars": {p.name: digest(p) for p in jars},
                "jar_sha256": digest(args.output),
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
