"""CUDA chapter guides share one study guide instead of repeating operating boilerplate."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDY_GUIDE = ROOT / "courses/cuda/STUDY-GUIDE.md"
LINK = re.compile(r"\]\(([^)#]*STUDY-GUIDE\.md)(?:#([^)]*))?\)")


def _anchor(heading: str) -> str:
    return re.sub(r"[^a-z0-9 -]", "", heading.lower()).replace(" ", "-")


def test_every_cuda_guide_links_the_shared_study_guide_with_valid_anchors() -> None:
    anchors = {
        _anchor(line[3:].strip())
        for line in STUDY_GUIDE.read_text(encoding="utf-8").splitlines()
        if line.startswith("## ")
    }
    rows = json.loads((ROOT / "courses/cuda/lessons.json").read_text(encoding="utf-8"))["lessons"]
    assert len(rows) == 128
    for row in rows:
        guide = ROOT / row["guide_path"]
        links = LINK.findall(guide.read_text(encoding="utf-8"))
        assert any((guide.parent / target).resolve() == STUDY_GUIDE for target, _ in links), guide
        for _, anchor in links:
            assert not anchor or anchor in anchors, f"{guide}: #{anchor}"
