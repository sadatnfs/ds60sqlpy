#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Assemble verified native/JVM files into a fresh relocatable installation."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
from pathlib import Path

from build_native import inventory, sha, source_build_id


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--native-build", type=Path, required=True)
    p.add_argument("--sdk", type=Path, required=True)
    p.add_argument("--jar", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--runtime-root", type=Path)
    a = p.parse_args()
    if platform.system() != "Linux" or platform.machine() not in ("aarch64", "x86_64"):
        raise ValueError("Assemble and probe on the native supported Linux platform")
    out = a.output.absolute()
    runtime = a.runtime_root or out
    if not runtime.is_absolute() or out.exists() or out.is_symlink():
        raise ValueError("Use a fresh installation and an absolute runtime path")
    receipt = json.loads((a.native_build / "build.json").read_text())
    if source_build_id(receipt) != receipt["build_id"]:
        raise ValueError("Native retained provenance does not reproduce its build identity")
    if any(
        receipt.get(key) is not True
        for key in (
            "compiled",
            "native_math_checks",
            "native_process_checks",
            "native_protocol_tests",
        )
    ):
        raise ValueError("Native build receipt lacks required preparation checks")
    package = Path(__file__).resolve().parents[1]
    if (
        inventory(package / "native") != receipt["native_source"]
        or inventory(package / "tooling") != receipt["build_scripts"]
        or inventory(a.sdk) != receipt["sdk_files"]
    ):
        raise ValueError("Retained native source, preparation or SDK changed since compilation")
    binary = a.native_build / "tmbad-worker"
    if sha(binary) != receipt["binary_sha256"] or receipt["architecture"] != platform.machine():
        raise ValueError("Native binary identity differs from its build receipt")
    descriptor = json.loads(
        subprocess.run(
            [str(binary.absolute()), "--describe"], check=True, capture_output=True, timeout=30
        ).stdout
    )
    if descriptor["build_id"] != receipt["build_id"]:
        raise ValueError("Native worker identity differs from its build receipt")
    jvm_receipt = json.loads(a.jar.with_suffix(a.jar.suffix + ".json").read_text())
    if (
        sha(a.jar) != jvm_receipt["jar_sha256"]
        or jvm_receipt["spark"] != "4.0.1"
        or jvm_receipt["scala_binary"] != "2.13"
        or jvm_receipt["bytecode_release"] != "17"
    ):
        raise ValueError("JVM artifact differs from its supported build receipt")
    if sha(package / "jvm/build.py") != jvm_receipt.get("build_script_sha256"):
        raise ValueError("JVM build script changed since compilation")
    expected_jvm_sources = jvm_receipt["source_sha256"]
    if type(jvm_receipt.get("include_tests")) is not bool:
        raise ValueError("JVM receipt must declare its complete source-selection mode")
    selected = list((package / "jvm/src/main/scala").rglob("*.scala"))
    if jvm_receipt["include_tests"]:
        selected += list((package / "jvm/src/test/scala").rglob("*.scala"))
    if {p.relative_to(package / "jvm").as_posix() for p in selected} != set(expected_jvm_sources):
        raise ValueError("JVM source set changed since compilation")
    if any(sha(package / "jvm" / path) != digest for path, digest in expected_jvm_sources.items()):
        raise ValueError("JVM source changed since compilation")
    out.mkdir(parents=True)
    shutil.copy2(binary, out / "tmbad-worker")
    (out / "tmbad-worker").chmod(0o555)
    shutil.copy2(a.jar, out / "spark-tmbad.jar")
    (out / "spark-tmbad.jar").chmod(0o444)
    shutil.copytree(a.sdk / "sources", out / "sources")
    shutil.copytree(a.sdk / "notices", out / "notices")
    shutil.copy2(package / "python/LICENSE", out / "notices/ORIGINAL-SOURCE-MIT.txt")
    shutil.copytree(package / "native", out / "sources/package-native")
    shutil.copytree(
        package / "tooling",
        out / "sources/package-tooling",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    (out / "native-build.json").write_text(json.dumps(receipt, indent=2) + "\n")
    (out / "jvm-build.json").write_text(json.dumps(jvm_receipt, indent=2) + "\n")
    manifest = {
        "schema_version": 1,
        "kind": "spark-tmbad-artifact",
        "package_version": "0.1.0",
        "protocol": 1,
        "build_id": descriptor["build_id"],
        "platform": {
            "os": "linux",
            "arch": "arm64" if platform.machine() == "aarch64" else "amd64",
        },
        "binary": {"path": str(runtime / "tmbad-worker"), "sha256": sha(out / "tmbad-worker")},
        "jvm": {
            "path": str(runtime / "spark-tmbad.jar"),
            "sha256": sha(out / "spark-tmbad.jar"),
            "spark_version": "4.0.1",
            "scala_binary_version": "2.13",
            "java_min": 17,
        },
        "engine": descriptor["engine"],
        "models": descriptor["models"],
        "provenance": {
            "native_receipt": "native-build.json",
            "jvm_receipt": "jvm-build.json",
            "retained_dependency_sources": "sources/",
            "retained_notices": "notices/",
            "runtime_qualification": (
                "Compilation and native numerical checks only; "
                "Spark execution requires separate acceptance."
            ),
        },
    }
    (out / "artifact.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"build_id": manifest["build_id"], "artifact": str(out / "artifact.json")}))


if __name__ == "__main__":
    main()
