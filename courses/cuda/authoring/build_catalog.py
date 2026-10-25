#!/usr/bin/env python3
"""Assemble the CUDA subject from reviewed author-owned teaching fragments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def artifacts() -> dict[Path, str]:
    lessons, admissions = [], []
    for name in ("cpp_manifest.json", "python_manifest.json", "spark_manifest.json"):
        fragment = json.loads((HERE / name).read_text(encoding="utf-8"))
        lessons.extend(fragment["track_lessons"])
        admissions.extend(fragment["admissions"])
    optional = json.loads((HERE / "cpp_optional_gpu_variants.json").read_text(encoding="utf-8"))
    for row in admissions:
        if row["id"] in optional:
            row.setdefault("variants", []).append(optional[row["id"]])
        for record in [row, *row.get("variants", [])]:
            paths = [record["source_path"], *record["solution_paths"]]
            if "guide_path" in record:
                paths.append(record["guide_path"])
            for name in paths:
                path = Path(name)
                if path.is_absolute() or ".." in path.parts or not name.startswith("courses/cuda/"):
                    raise ValueError(f"Invalid CUDA content path: {name}")
                if not (ROOT / path).is_file():
                    raise ValueError(f"Missing authored CUDA artifact: {name}")
    expected = {f"cuda-{number:03d}" for number in range(1, 129)}
    if len(lessons) != 128 or {row["id"] for row in lessons} != expected:
        raise ValueError("The authored CUDA plan must contain exactly cuda-001 through cuda-128.")
    if len(admissions) != 128 or {row["id"] for row in admissions} != expected:
        raise ValueError("Every planned CUDA lesson needs its authored admission.")
    plan = {
        "schema_version": 1,
        "id": "cuda",
        "title": "GPU computing: CUDA, Python, machine learning and Spark",
        "summary": (
            "Learn GPU architecture, CUDA C++, Python arrays, PyTorch, TensorFlow and GPU Spark. "
            "Reading and bounded CPU models work without NVIDIA hardware. Optional CUDA "
            "variants require separately prepared NVIDIA workers and real device readiness."
        ),
        "lessons": sorted(lessons, key=lambda row: row["id"]),
    }
    manifest = {
        "schema_version": 1,
        "track_id": "cuda",
        "lessons": sorted(admissions, key=lambda row: row["id"]),
    }
    return {
        ROOT / "courses/cuda/track.json": json.dumps(plan, indent=2, ensure_ascii=False) + "\n",
        ROOT / "courses/cuda/lessons.json": json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed = []
    for path, content in artifacts().items():
        if not path.exists() or json.loads(path.read_text(encoding="utf-8")) != json.loads(content):
            changed.append(path.relative_to(ROOT).as_posix())
            if not args.check:
                path.write_text(content, encoding="utf-8", newline="\n")
    if args.check and changed:
        print("Regenerate CUDA catalog: " + ", ".join(changed))
        return 1
    print("CUDA catalog: 128 authored canonical lessons, with separately identified variants.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
