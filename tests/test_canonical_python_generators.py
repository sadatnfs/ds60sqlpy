"""Owner generation can update displayed code without rewriting frozen artifacts."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "track,lesson,specification",
    [
        ("deep-learning-pytorch", "torch-002", "specs"),
        ("deep-learning-tensorflow", "tf-009", "tf"),
        ("llm-theory", "llm-043", "specs"),
        ("llm-applied", "llm-applied-001", "specs"),
    ],
)
def test_python_markdown_only_generation_preserves_metadata_and_programs(
    tmp_path: Path, track: str, lesson: str, specification: str
) -> None:
    tracks = [track, "llm-theory"] if track == "deep-learning-tensorflow" else [track]
    protected = []
    for name in tracks:
        destination = tmp_path / "courses" / name
        for directory in ("guides", "solutions", "lessons", "authoring"):
            (destination / directory).mkdir(parents=True, exist_ok=True)
        for filename in ("track.json", "lessons.json"):
            source = ROOT / "courses" / name / filename
            if source.is_file():
                path = destination / filename
                shutil.copyfile(source, path)
                protected.append(path)
        plan = tmp_path / "docs/expansion/plans" / (name + ".json")
        source_plan = ROOT / "docs/expansion/plans" / (name + ".json")
        if source_plan.is_file():
            plan.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_plan, plan)
            protected.append(plan)
    for relative in (
        f"lessons/{lesson}.py",
        f"solutions/{lesson}_solution.py",
        "authoring/review_matrix.json",
    ):
        path = tmp_path / "courses" / track / relative
        path.write_text("Frozen artifact sentinel\n")
        protected.append(path)
    hashes = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in protected}
    program = "\n".join(
        [
            "import importlib,json,sys",
            "from pathlib import Path",
            "sys.path.insert(0, sys.argv[1])",
            "import render",
            "render.GUIDES_ONLY = True",
            "importlib.import_module(sys.argv[4])",
            "if sys.argv[5] == 'deep-learning-pytorch':",
            "    from depth_reviews import apply_reviews",
            "    apply_reviews(render.SPECS)",
            "source_root = render.SOURCE_ROOT",
            "render.ROOT = Path(sys.argv[2])",
            "render.write_all(only={sys.argv[3]}, markdown_only=True)",
            "assert 'torch' not in sys.modules and 'tensorflow' not in sys.modules",
            "print(json.dumps({'source_root':str(source_root),'output_root':str(render.ROOT)}))",
        ]
    )
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    environment["PATH"] = (
        str(Path(sys.executable).parent) + os.pathsep + environment.get("PATH", "")
    )
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            program,
            str(ROOT / "courses" / track / "authoring"),
            str(tmp_path),
            lesson,
            specification,
            track,
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=environment,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    observed = json.loads(result.stdout.splitlines()[-1])
    assert observed == {"source_root": str(ROOT), "output_root": str(tmp_path)}
    assert hashes == {
        str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in protected
    }
    generated = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*.md"))
    assert generated == [
        f"courses/{track}/guides/{lesson}.md",
        f"courses/{track}/solutions/{lesson}_solutions.md",
    ]
