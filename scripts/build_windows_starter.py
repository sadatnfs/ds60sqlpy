#!/usr/bin/env python3
"""Package the complete Windows Docker starter without Git or Python prerequisites."""

from __future__ import annotations

import argparse
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_app import stage_course  # noqa: E402

README = """DS60 Learning Lab: Docker classroom starter

1. Right-click the ZIP and choose Extract All. Open the extracted DS60LearningLab folder.
2. Start a Docker-compatible Linux-container engine with integration enabled for Ubuntu in WSL 2.
3. Double-click START_DOCKER_CLASSROOM.cmd. Keep its window open for build logs.
4. The shared ./classroom entrypoint builds missing images on first preparation,
   waits for readiness, and opens one classroom for all subjects.
   Later starts reuse local images and resume the same project containers.
5. Choose any learning path and pace. Code, notes and saved runs stay separate
   for each lesson and language. Equations and code highlights render offline.

Docker, Compose and the WSL 2 Ubuntu shell are the Windows launcher prerequisites.
No host Python, PostgreSQL,
PowerShell tutorial or Git installation is needed for the ordinary module route.
The first build needs internet. No image is pushed to a registry.

A new default project prepares all fifteen ordinary language/framework workers.
Use ./classroom --starter in WSL for a smaller Python/SQL start. That selection
is remembered; ./classroom --all selects the full set later. ./classroom resume
never builds or pulls. Use ./classroom --rebuild to install updated source files.
Keep the same custom --project name on later commands if you chose one. Read
docs/one-command-classroom.md for setup, ports, stopping and recovery, and
docs/docker-classroom.md for manual Compose and backups.
Kubernetes has separate explicit
owned-cluster preparation; it is not silently provisioned by the classroom.

Progress stays in a local Docker learning volume; PostgreSQL has another volume.
Stop/start and container replacement retain both. Do not delete your volumes.
The ignored .classroom/<project>/ folder stores launcher preferences, not a
backup of learning work. Interrupted preparation retains completed images.
The older host .learning workflow remains an optional separate storage route.

If an engine is not installed yet, read docs/docker-beginners.md. The older
START_DOCKER_LAB.cmd first-run setup wizard remains an optional Windows helper.
The complete course, Dockerfiles and build sources are included.
"""


def build_archive(output: Path, *, source_root: Path = ROOT) -> int:
    """Build a clean portable source archive; never copy learner-local state."""
    required = (
        "START_DOCKER_LAB.cmd",
        "classroom",
        "classroom.cmd",
        "scripts/classroom.sh",
        "START_DOCKER_CLASSROOM.cmd",
        "START_DOCKER_CLASSROOM.command",
        "compose.classroom.yaml",
        "compose.classroom.kubernetes.yaml",
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
                member = ZipInfo.from_file(path, path.relative_to(payload.parent))
                # The payload is public source. A local owner-only checkout mode
                # must not become an unreadable root-owned file after Docker COPY.
                executable = bool(path.stat().st_mode & 0o111)
                mode = 0o755 if executable else 0o644
                member.create_system = 3
                member.external_attr = (stat.S_IFREG | mode) << 16
                member.compress_type = ZIP_DEFLATED
                with path.open("rb") as source, archive.open(member, "w") as target:
                    shutil.copyfileobj(source, target, length=1024 * 1024)
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
    checks = (
        ("check_public_release.py",),
        ("normalize_lesson_prose.py",),
        ("check_content_rendering.py",),
        ("build_course_guide.py", "--check"),
        ("build_lesson_readers.py", "--check"),
        ("check_published_links.py",),
        ("check_modules.py",),
    )
    for checker, *options in checks:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / checker), *options], cwd=ROOT, check=False
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
