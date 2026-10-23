#!/usr/bin/env python3
"""Package the complete Windows Docker starter without Git or Python prerequisites."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_app import stage_course  # noqa: E402

README = """DS60 Learning Lab: Docker classroom starter

1. Right-click the ZIP and choose Extract All. Open the extracted DS60LearningLab folder.
2. Start an installed Docker-compatible Linux-container engine. Windows uses WSL 2.
3. Double-click START_DOCKER_CLASSROOM.cmd. Keep its window open for build logs.
4. The thin launcher builds locally and opens the classroom after readiness succeeds.

Docker and Compose are the classroom prerequisites. No host Python, PostgreSQL,
PowerShell tutorial or Git installation is needed for the ordinary module route.
The first build needs internet. No image is pushed to a registry.

The default button prepares Python/NumPy and the original Python/SQL course.
Read docs/docker-classroom.md to add TensorFlow, C++ and Scala/Spark with Docker
commands, save/backup local volumes and resume. Kubernetes has separate explicit
owned-cluster preparation; it is not silently provisioned by the classroom.

Progress stays in a local Docker learning volume; PostgreSQL has another volume.
Stop/start and container replacement retain both. Do not delete your volumes.
The older host .learning workflow remains an optional separate storage route.

If an engine is not installed yet, read docs/docker-beginners.md. The older
START_DOCKER_LAB.cmd first-run setup wizard remains an optional Windows helper.
The complete course, Dockerfiles and build sources are included.
"""


def build_archive(output: Path, *, source_root: Path = ROOT) -> int:
    """Build a clean portable source archive; never copy learner-local state."""
    required = (
        "START_DOCKER_LAB.cmd",
        "scripts/start_docker_windows.ps1",
        "scripts/docker_lab.ps1",
        "Dockerfile",
        "compose.yaml",
        "curriculum/catalog.json",
    )
    for name in required:
        if not (source_root / name).is_file() or (source_root / name).is_symlink():
            raise FileNotFoundError(f"Starter asset missing: {name}")
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ds60-windows-starter-") as temporary:
        payload = Path(temporary) / "DS60LearningLab"
        stage_course(payload, source_root=source_root)
        (payload / "START-WINDOWS.txt").write_text(README, encoding="utf-8", newline="\r\n")
        paths = sorted(path for path in payload.rglob("*") if path.is_file())
        with ZipFile(output, "w", ZIP_DEFLATED, compresslevel=6) as archive:
            for path in paths:
                archive.write(path, path.relative_to(payload.parent))
        with ZipFile(output) as archive:
            bad = archive.testzip()
            if bad:
                raise ValueError(f"Archive integrity check failed: {bad}")
        return len(paths)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "dist/DS60LearningLab-0.3.0-Windows-Starter.zip"
    )
    args = parser.parse_args(argv)
    for checker in ("build_course_guide.py", "build_lesson_readers.py"):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / checker), "--check"], cwd=ROOT, check=False
        )
        if result.returncode:
            print("Run make generate before packaging the starter.", file=sys.stderr)
            return result.returncode
    try:
        count = build_archive(args.output)
    except (OSError, ValueError) as exc:
        print(f"Could not build Windows starter: {exc}", file=sys.stderr)
        return 2
    print(f"Built {args.output.resolve()} with {count} files. No learner state included.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
