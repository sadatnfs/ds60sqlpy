"""Read exact shipped project bytes and installed runtime identities inside a sealed image."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


def main() -> None:
    request: dict[str, Any] = json.load(sys.stdin)
    if set(request) != {"sources", "runtime"} or not isinstance(request["sources"], dict):
        raise ValueError("Fixed scientific image probe request required")
    if not 1 <= len(request["sources"]) <= 1000:
        raise ValueError("Bounded nonempty source selection required")
    sources = {}
    for relative, installed in request["sources"].items():
        path = Path(installed)
        if (
            not isinstance(relative, str)
            or not path.is_absolute()
            or not path.is_relative_to("/opt")
            or ".." in path.parts
            or path.is_symlink()
            or not path.is_file()
            or path.stat().st_size > 8 * 1024 * 1024
        ):
            raise ValueError("Invalid sealed scientific source path")
        sources[relative] = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    aliases = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64"}
    runtime = {
        "system": platform.system(),
        "architecture": aliases.get(platform.machine()),
        "python": platform.python_version(),
    }
    wanted = request["runtime"]
    if not isinstance(wanted, list) or not set(wanted) <= {
        "spark",
        "torch",
        "lightning",
        "scipy",
        "ds60-spark-likelihood",
        "java_major",
        "R",
        "TMB",
        "Matrix",
    }:
        raise ValueError("Unknown runtime probe")
    for package in ("torch", "lightning", "scipy", "ds60-spark-likelihood"):
        if package in wanted:
            runtime[package] = importlib.metadata.version(package)
    if "spark" in wanted:
        jars = list(Path("/opt/spark/jars").glob("spark-core_2.13-*.jar"))
        if len(jars) != 1:
            raise ValueError("Ambiguous Spark runtime jars")
        runtime["spark"] = jars[0].name.removeprefix("spark-core_2.13-").removesuffix(".jar")
    if "java_major" in wanted:
        process = subprocess.run(
            ["java", "-version"], capture_output=True, text=True, check=True, timeout=20
        )
        match = re.search(r'version "([0-9]+)', process.stderr + process.stdout)
        if match is None:
            raise ValueError("Cannot identify installed Java")
        runtime["java_major"] = match[1]
    if set(wanted) & {"R", "TMB", "Matrix"}:
        code = (
            "cat(jsonlite::toJSON(list(R=as.character(getRversion()),"
            'TMB=as.character(packageVersion("TMB")),'
            'Matrix=as.character(packageVersion("Matrix"))),auto_unbox=TRUE))'
        )
        output = subprocess.run(
            ["Rscript", "--vanilla", "-e", code],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        runtime.update(json.loads(output.stdout))
        compiler = subprocess.run(
            ["R", "CMD", "config", "CXX"], capture_output=True, text=True, check=True, timeout=15
        )
        runtime["r_cxx"] = compiler.stdout.strip()[:256]
    print(json.dumps({"sources": sources, "runtime": runtime}, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
