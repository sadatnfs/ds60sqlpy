#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile a source-bound native worker with a prepared, verified SDK."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from prepare import DEPENDENCIES, prepare

FLAGS = ["-std=c++17", "-O1", "-g0", "-DNDEBUG"]


BUILD_FIELDS = {
    "schema_version",
    "package_version",
    "native_source",
    "build_scripts",
    "sdk_files",
    "compiler",
    "flags",
    "link_flags",
    "openssl_version",
    "architecture",
}
DERIVED_FIELDS = {
    "build_id",
    "binary_sha256",
    "compiled",
    "native_math_checks",
    "native_process_checks",
    "native_protocol_tests",
    "spark_execution",
}


def source_build_id(receipt: dict) -> str:
    if not receipt.keys() >= BUILD_FIELDS or set(receipt) - BUILD_FIELDS - DERIVED_FIELDS:
        raise ValueError("Native build receipt fields differ from the preparation contract")
    source = {key: receipt[key] for key in BUILD_FIELDS}
    return hashlib.sha256(
        json.dumps(source, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inventory(root: Path) -> dict[str, str]:
    paths = sorted(
        p for p in root.rglob("*") if "__pycache__" not in p.parts and p.suffix != ".pyc"
    )
    if any(p.is_symlink() for p in paths):
        raise ValueError("Native source/SDK trees cannot contain symlinks")
    return {p.relative_to(root).as_posix(): sha(p) for p in paths if p.is_file()}


def output(command: list[str]) -> str:
    result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
    return result.stdout.strip()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sdk", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--compiler", default="g++-12")
    a = p.parse_args()
    if platform.system() != "Linux" or platform.machine() not in ("aarch64", "x86_64"):
        raise ValueError("Build natively on supported Linux ARM64 or AMD64")
    sdk = a.sdk.resolve(strict=True)
    root = Path(__file__).resolve().parents[1]
    native = root / "native"
    dest = a.output.absolute()
    if dest.exists() or dest.is_symlink():
        raise ValueError("Use a fresh build output directory")
    compiler = shutil.which(a.compiler)
    if not compiler:
        raise ValueError("Install the explicitly prepared C++ compiler")
    prepared = json.loads((sdk / "sdk.json").read_text())
    if prepared["dependencies"] != {k: v[0] for k, v in DEPENDENCIES.items()}:
        raise ValueError("SDK dependency identity changed")
    sdk_files = inventory(sdk)
    expected = {**prepared["files"], "sdk.json": sha(sdk / "sdk.json")}
    if sdk_files != expected:
        raise ValueError("SDK files changed since preparation")
    for name, (digest, _) in DEPENDENCIES.items():
        if sha(sdk / "sources" / name) != digest:
            raise ValueError("Source archive does not match pinned dependency")
    # Reconstruct from pinned archives, so editing both headers and sdk.json cannot
    # silently claim to be the original dependency implementation.
    with tempfile.TemporaryDirectory(prefix="spark-tmbad-sdk-check-") as temporary:
        clean = Path(temporary) / "sdk"
        prepare(clean, sdk / "sources", False)
        if inventory(clean) != sdk_files:
            raise ValueError("SDK content differs from the pinned source reconstruction")
    source = inventory(native)
    provenance = {
        "schema_version": 1,
        "package_version": "0.1.0",
        "native_source": source,
        "build_scripts": inventory(root / "tooling"),
        "sdk_files": sdk_files,
        "compiler": {
            "sha256": sha(Path(compiler).resolve()),
            "version": output([compiler, "--version"]),
            "target": output([compiler, "-dumpmachine"]),
        },
        "flags": FLAGS,
        "link_flags": ["-ldl", "-lcrypto"],
        "openssl_version": output(["openssl", "version"]),
        "architecture": platform.machine(),
    }
    build_id = source_build_id(provenance)
    dest.mkdir(parents=True)
    include = [
        "-I" + str(d) for d in (native / "include", sdk / "include", sdk / "eigen", sdk / "json")
    ]
    common = [compiler, *FLAGS, f'-DDS60_NATIVE_BUILD_ID="{build_id}"', *include]
    # Empty toolchain-injection variables; use only reviewed flags and prepared include paths.
    env = {
        k: v
        for k, v in os.environ.items()
        if k
        not in (
            "CPATH",
            "CPLUS_INCLUDE_PATH",
            "C_INCLUDE_PATH",
            "LIBRARY_PATH",
            "LD_PRELOAD",
            "LD_LIBRARY_PATH",
        )
    }
    with (dest / "compile.log").open("w") as log:
        commands = [
            [*common, "-c", str(native / "src/ad_runtime.cpp"), "-o", str(dest / "ad_runtime.o")],
            [
                *common,
                str(native / "src/worker.cpp"),
                str(dest / "ad_runtime.o"),
                "-ldl",
                "-lcrypto",
                "-o",
                str(dest / "tmbad-worker"),
            ],
            [
                *common,
                str(native / "tests/math_checks.cpp"),
                str(dest / "ad_runtime.o"),
                "-ldl",
                "-lcrypto",
                "-o",
                str(dest / "math-checks"),
            ],
        ]
        commands.append(
            [*common, str(native / "tests/sandbox_checks.cpp"), "-o", str(dest / "sandbox-checks")]
        )
        for command in commands:
            subprocess.run(
                command, check=True, stdout=log, stderr=subprocess.STDOUT, env=env, timeout=600
            )
    if inventory(native) != source or inventory(sdk) != sdk_files:
        raise ValueError("Source or SDK changed during compilation; discard this candidate")
    (dest / "tmbad-worker").chmod(0o555)
    math = subprocess.run(
        [str(dest / "math-checks")],
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )
    (dest / "math-checks.log").write_text(math.stdout + math.stderr)
    guards = subprocess.run(
        [str(dest / "sandbox-checks")],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )
    (dest / "sandbox-checks.log").write_text(guards.stdout + guards.stderr)
    protocol = subprocess.run(
        [sys.executable, str(native / "tests/test_worker_protocol.py")],
        check=True,
        capture_output=True,
        text=True,
        timeout=180,
        env={**env, "DS60_NATIVE_BINARY": str(dest / "tmbad-worker")},
    )
    (dest / "protocol-checks.log").write_text(protocol.stdout + protocol.stderr)
    described = subprocess.run(
        [str(dest / "tmbad-worker"), "--describe"],
        check=True,
        capture_output=True,
        timeout=30,
        env=env,
    )
    if len(described.stdout) > 4 * 1024 * 1024:
        raise ValueError("Worker description exceeds bound")
    metadata = json.loads(described.stdout)
    if metadata["build_id"] != build_id or metadata["protocol"] != 1:
        raise ValueError("Compiled worker has unexpected identity")
    (dest / "describe.json").write_text(json.dumps(metadata, indent=2) + "\n")
    libraries = output(["ldd", str(dest / "tmbad-worker")])
    if "libR.so" in libraries or "libpython" in libraries or "not found" in libraries:
        raise ValueError("Native worker has an unsupported or missing runtime dependency")
    (dest / "runtime-libraries.txt").write_text(libraries + "\n")
    provenance.update(
        build_id=build_id,
        binary_sha256=sha(dest / "tmbad-worker"),
        compiled=True,
        native_math_checks=True,
        native_process_checks=True,
        native_protocol_tests=True,
        spark_execution=False,
    )
    (dest / "build.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(
        json.dumps(
            {
                "build_id": build_id,
                "binary_sha256": provenance["binary_sha256"],
                "compiled": True,
                "native_math_checks": True,
                "spark_execution": False,
            }
        )
    )


if __name__ == "__main__":
    main()
