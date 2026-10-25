#!/usr/bin/env python3
"""Validate portable CUDA curricula without fabricating GPU execution evidence."""

from __future__ import annotations

import argparse
import ast
import concurrent.futures
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def execute(path: Path) -> tuple[str, int, str]:
    result = subprocess.run(
        [sys.executable, str(path)], cwd=ROOT, text=True, capture_output=True, timeout=90
    )
    return str(path.relative_to(ROOT)), result.returncode, (result.stdout + result.stderr)[-6000:]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--framework", choices=["torch", "tensorflow"], action="append", default=[])
    parser.add_argument("--pyspark", action="store_true")
    args = parser.parse_args()
    base = ROOT / "courses/cuda"
    files = [*base.glob("python/**/*.py"), *base.glob("spark/**/*.py")]
    for path in files:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    ordinary = sorted(base.glob("python/references/*_cpu.py")) + sorted(
        base.glob("spark/references/*_cpu.py")
    )
    ordinary += sorted(base.glob("python/lessons/*_cpu.py")) + sorted(
        base.glob("spark/lessons/*_cpu.py")
    )
    assert len(ordinary) == 128
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(execute, ordinary))
    optional = []
    for framework in args.framework:
        optional.extend(sorted(base.glob(f"python/references/*_{framework}-cpu.py")))
    if args.pyspark:
        optional.extend(sorted(base.glob("spark/references/*_pyspark-cpu.py")))
    # Framework processes are sequential to bound memory use and isolate global runtime state.
    results.extend(execute(path) for path in optional)
    failed = [row for row in results if row[1] != 0]
    for name, status, output in failed:
        print(name, status, output)
    fragments = [
        json.loads((base / "authoring" / f"{name}_manifest.json").read_text())
        for name in ["python", "spark"]
    ]
    all_ids = [row["id"] for fragment in fragments for row in fragment["admissions"]]
    assert len(all_ids) == len(set(all_ids)) == 64
    for fragment in fragments:
        assert len(fragment["track_lessons"]) == len(fragment["admissions"])
        for row in fragment["admissions"]:
            for key in ["guide_path", "source_path"]:
                assert (ROOT / row[key]).is_file(), row[key]
            guide = (ROOT / row["guide_path"]).read_text()
            assert "\u2014" not in guide
            assert guide.count("### Exercise ") == 6
            assert "### Worked example 1" in guide and "### Worked example 2" in guide
            assert row["runtime_profile"] == "reading"
    print(
        json.dumps(
            {
                "python_artifacts_parsed": len(files),
                "portable_programs": 128,
                "optional_programs": len(optional),
                "passed": len(results) - len(failed),
                "failed": len(failed),
                "gpu_executed": False,
                "scala_executed": False,
            }
        )
    )
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
