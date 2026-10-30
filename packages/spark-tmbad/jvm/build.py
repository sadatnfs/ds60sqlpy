#!/usr/bin/env python3
"""Compile only with the explicitly prepared Spark 4.0.1 Scala 2.13 jar toolchain."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

LICENSE_TEXT = """MIT License

Copyright (c) 2026 DS60 contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

This MIT license applies to the original Spark/TMBad Python frontend, JVM
adapter, and native wrapper/model source written by DS60 contributors. It does
not replace the licenses of upstream dependency code. TMBad retains TMB's GPL-2
terms; Eigen and code distributed with RcppEigen retain their respective
upstream terms and notices; nlohmann/json retains its own MIT license and
copyright notice. Preserve the corresponding dependency sources and notices
with the prepared installation. The compiled native worker and its dependency
combination are not relicensed as MIT by this original-source notice.

The Python wheel contains only the frontend. Installing it does not install
or relicense TMBad, Spark, Eigen, nlohmann/json, or their dependencies.
"""

NOTICE_TEXT = """This JAR contains original DS60 Scala/JVM adapter and example bytecode.
The original source is licensed under MIT; see META-INF/LICENSE.

Spark and Scala are provided by the prepared runtime, not bundled in this JAR.
They retain their respective upstream license terms and notices.

The native TMBad worker is prepared and distributed separately. TMBad retains
TMB GPL-2 terms. Eigen/RcppEigen and nlohmann/json retain their respective
upstream terms and notices. Preserve their corresponding sources and notices
in the prepared installation. This JAR's original-source notice does not
relicense the compiled native worker or its dependency combination as MIT.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spark-home", type=Path, default=Path(os.environ.get("SPARK_HOME", "/opt/spark"))
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--include-tests", action="store_true")
    args = parser.parse_args()
    home = args.spark_home.absolute()
    jars = sorted((home / "jars").glob("*.jar"))
    if not (home / "jars/spark-sql_2.13-4.0.1.jar").is_file():
        raise SystemExit("Prepare exact Spark4.0.1/Scala2.13 jars before compiling")
    version = subprocess.run(
        ["java", "-version"], capture_output=True, text=True, check=True, timeout=15
    )
    match = re.search(r'version "(17|21)(?:[.\"])', version.stderr + version.stdout)
    if match is None:
        raise SystemExit("Use a prepared compatible JDK17 or JDK21")
    root = Path(__file__).resolve().parent
    sources = sorted((root / "src/main/scala").rglob("*.scala"))
    if args.include_tests:
        sources += sorted((root / "src/test/scala").rglob("*.scala"))
    if not sources:
        raise SystemExit("No JVM source files found")
    output = args.output.absolute()
    if output.exists() or output.is_symlink():
        raise SystemExit("Choose a fresh output JAR path")
    output.parent.mkdir(parents=True, exist_ok=True)

    def file_digest(path: Path) -> str:
        with path.open("rb") as stream:
            return hashlib.file_digest(stream, "sha256").hexdigest()

    before = {str(path.relative_to(root)): file_digest(path) for path in sources}
    build_hash = file_digest(root / "build.py")
    compiler_jars = {path.name: file_digest(path) for path in jars}
    with tempfile.TemporaryDirectory(prefix="ds60-spark-tmbad-jvm-") as temporary:
        classes = Path(temporary) / "classes"
        classes.mkdir()
        subprocess.run(
            [
                "java",
                "-Xmx768m",
                "-cp",
                os.pathsep.join(map(str, jars)),
                "scala.tools.nsc.Main",
                "-usejavacp",
                "-release",
                "17",
                "-d",
                str(classes),
                *map(str, sources),
            ],
            check=True,
            timeout=180,
        )
        metadata = classes / "META-INF"
        metadata.mkdir()
        (metadata / "LICENSE").write_text(LICENSE_TEXT, encoding="utf-8")
        (metadata / "NOTICE").write_text(NOTICE_TEXT, encoding="utf-8")
        subprocess.run(["jar", "cf", str(output), "-C", str(classes), "."], check=True, timeout=30)
    after = {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sources
    }
    if before != after or file_digest(root / "build.py") != build_hash:
        raise RuntimeError("Source/build script changed during compilation")
    if compiler_jars != {path.name: file_digest(path) for path in jars}:
        raise RuntimeError("Prepared compiler classpath changed during compilation")
    receipt = {
        "kind": "spark-tmbad-jvm-compilation",
        "compiled": True,
        "executed": False,
        "spark": "4.0.1",
        "scala_binary": "2.13",
        "java_major": match.group(1),
        "bytecode_release": "17",
        "source_sha256": before,
        "include_tests": args.include_tests,
        "build_script_sha256": build_hash,
        "compiler_jars": compiler_jars,
        "java_runtime": (version.stderr + version.stdout).strip(),
        "jar_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "metadata_sha256": {
            "META-INF/LICENSE": hashlib.sha256(LICENSE_TEXT.encode("utf-8")).hexdigest(),
            "META-INF/NOTICE": hashlib.sha256(NOTICE_TEXT.encode("utf-8")).hexdigest(),
        },
        "scope": "compilation only, no worker or Spark execution claim",
    }
    output.with_suffix(output.suffix + ".json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
