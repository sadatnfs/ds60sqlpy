"""Explicit build-time compiler for trusted registry templates, never a runtime API."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from spark_tmb.registry import load_registry, sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build_dir", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    registry = load_registry(root)
    build = args.build_dir.resolve()
    build.mkdir(parents=True, exist_ok=True)
    receipt = build / "receipt.json"
    receipt.unlink(missing_ok=True)
    subprocess.run(
        ["Rscript", "--vanilla", str(root / "R/compile_registered.R"), str(root), str(build)],
        check=True,
        timeout=900,
        env={**os.environ, "MAKEFLAGS": "-j1", "OMP_NUM_THREADS": "1"},
    )
    records = {}
    for name, spec in registry["models"].items():
        library = build / (name + ".so")
        if not library.is_file():
            raise RuntimeError("Native Linux compiled artifact is missing")
        records[name] = {
            "source_sha256": sha256(root / spec["source"]),
            "library_sha256": sha256(library),
            "library": library.name,
        }
    receipt.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "registry_sha256": sha256(root / "registry.json"),
                "abi": json.loads((build / "abi.json").read_text()),
                "models": records,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
