#!/usr/bin/env python3
"""Package the complete Docker classroom source for Linux, macOS and Windows/WSL 2."""

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

from scripts.course_payload import stage_course  # noqa: E402

README = """DS60 Classroom: complete Docker source starter

1. Extract the entire archive and open its DS60LearningLab folder.
2. Install and start a Linux-container Docker engine with Compose 2.28 or newer.
   Windows: use Ubuntu in WSL 2 with your engine's WSL integration enabled.
   macOS and Linux: use a normal terminal with access to the running engine.
3. From that folder run: ./classroom doctor
4. Then run: ./classroom
   If extraction dropped executable permissions, use: bash classroom
   Windows can also use START_DOCKER_CLASSROOM.cmd; macOS can use
   START_DOCKER_CLASSROOM.command after preparing its Docker engine.
5. Follow the build logs. Startup prepares missing images, waits for readiness
   and opens the actual local /classroom address. No image is published.

No host Python, compiler or PostgreSQL installation is required. Git is optional.
The first preparation needs internet and substantial disk space. All sixteen
ordinary workers are selected on a new project. For a smaller start, use
./classroom --starter. Every lesson remains readable; add its runtime later.
Optional NVIDIA GPU and owned Kubernetes runtimes require separate setup.

Use ./classroom stop to pause and ./classroom resume to return without builds
or downloads. Use ./classroom --local-build --rebuild to install changed source.
In remembered Hub mode, --rebuild alone refreshes published images instead.
Reuse the same --project NAME on every command if you chose a custom name.

Source drafts, notes, progress and saved results live in named Docker volumes.
PostgreSQL has its own volume. Stop/start and container replacement preserve them.
The .classroom/<project>/ directory stores launcher preferences, not learner data.
Never delete volumes to repair startup. This source ZIP contains no personal state.

Start with README.md and docs/one-command-classroom.md. docs/README.md maps the
learner, developer and tutoring guides. Backup and transfer instructions are in
docs/docker-classroom.md. The entire source, curriculum and build tools are included.
"""


def build_archive(output: Path, *, source_root: Path = ROOT) -> int:
    """Build a clean portable source archive; never copy learner-local state."""
    required = (
        "classroom",
        "classroom.cmd",
        "scripts/classroom.sh",
        "START_DOCKER_CLASSROOM.cmd",
        "START_DOCKER_CLASSROOM.command",
        "compose.classroom.yaml",
        "compose.classroom.kubernetes.yaml",
        "Dockerfile",
        "compose.yaml",
        "curriculum/catalog.json",
    )
    for name in required:
        if not (source_root / name).is_file() or (source_root / name).is_symlink():
            raise FileNotFoundError(f"Starter asset missing: {name}")
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ds60-docker-starter-") as temporary:
        payload = Path(temporary) / "DS60LearningLab"
        stage_course(payload, source_root=source_root)
        (payload / "START.txt").write_text(README, encoding="utf-8", newline="\r\n")
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
        "--output", type=Path, default=ROOT / "dist/DS60LearningLab-Docker-Starter.zip"
    )
    args = parser.parse_args(argv)
    checks = (
        ("check_public_release.py",),
        ("check_repository_guidance.py",),
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
        print(f"Could not build Docker starter: {exc}", file=sys.stderr)
        return 2
    print(f"Built {args.output.resolve()} with {count} files. No learner state included.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
