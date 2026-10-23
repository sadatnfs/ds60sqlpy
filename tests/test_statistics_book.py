"""The source outline is a complete, executable tutorial-book contract."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import runpy
import socket
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "courses" / "statistics-ml"
MANIFEST = json.loads((BOOK / "manifest.json").read_text(encoding="utf-8"))
COVERAGE = json.loads((BOOK / "coverage.json").read_text(encoding="utf-8"))
CHAPTERS = MANIFEST["chapters"]


def test_source_provenance_and_every_method_has_one_stable_mapping():
    source = (ROOT / MANIFEST["source"]["path"]).read_bytes()
    digest = hashlib.sha256(source).hexdigest()
    assert digest == MANIFEST["source"]["sha256"] == COVERAGE["source_sha256"]
    sections = re.findall(r"## (\d+)\. (.*?)\n(.*?)(?=\n## |\Z)", source.decode(), re.S)
    expected = []
    for section, title, body in sections:
        labels = re.findall(r"^- \*\*(.*?):\*\*", body, re.M)
        expected.extend((f"stat-{int(section):02d}-{index:02d}", label) for index, label in enumerate(labels, 1))
    actual = [(topic["id"], topic["label"]) for topic in COVERAGE["topics"]]
    assert actual == expected
    assert len(sections) == len(CHAPTERS) == 40
    assert len(actual) == len(set(topic_id for topic_id, _ in actual)) == 1005
    assert MANIFEST["mode"] == "tutorial"


@pytest.mark.parametrize("chapter", CHAPTERS, ids=lambda item: item["id"])
def test_chapter_has_substantive_method_bodies_and_complete_worked_code(chapter):
    path = ROOT / chapter["chapter_path"]
    assert path.is_relative_to(BOOK)
    text = path.read_text(encoding="utf-8")
    assert "\u2014" not in text
    found = re.findall(r"^### (stat-\d{2}-\d{2})$", text, re.M)
    assert found == chapter["topic_ids"]
    assert "## Data science interview discussions" in text
    assert text.count("**Interview:") >= 2
    assert not re.search(r"^#{1,4} (?:Exercises|Problem sets|Exam)\b", text, re.M | re.I)
    for topic in (t for t in COVERAGE["topics"] if t["chapter_id"] == chapter["id"]):
        anchor = topic["anchor"]
        body = text.split(f"### {anchor}\n", 1)[1]
        body = re.split(r"\n(?:### stat-|## )", body, maxsplit=1)[0]
        assert f"**{topic['label']}**" in body
        explanation = body.replace(f"**{topic['label']}**", "").strip()
        assert len(explanation.split()) >= 20, topic["id"]
    for relative in chapter["example_paths"]:
        program = (ROOT / relative).read_text(encoding="utf-8")
        assert program.rstrip() in text
        tree = ast.parse(program)
        assert sum(isinstance(node, ast.Assert) for node in ast.walk(tree)) >= 2
        assert any(isinstance(node, ast.If) and "__name__" in ast.unparse(node.test) for node in tree.body)
        imports = {node.names[0].name.split(".")[0] if isinstance(node, ast.Import) else (node.module or "").split(".")[0] for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))}
        assert imports <= sys.stdlib_module_names | {"numpy", "pandas", "scipy", "sklearn", "statsmodels"}
        assert not imports & {"socket", "urllib", "http", "ftplib", "requests"}
        assert "\u2014" not in program


@pytest.mark.parametrize("chapter", CHAPTERS, ids=lambda item: item["id"])
def test_worked_examples_execute_offline_and_check_their_numerical_claims(chapter, monkeypatch, capsys):
    def no_network(*args, **kwargs):
        raise AssertionError("A statistics book demonstration attempted network access")

    monkeypatch.setattr(socket.socket, "connect", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)
    monkeypatch.setenv("LOKY_MAX_CPU_COUNT", "2")
    for relative in chapter["example_paths"]:
        runpy.run_path(str(ROOT / relative), run_name="__main__")
    assert capsys.readouterr().out.strip()


def test_relative_book_links_resolve_inside_repository():
    missing = []
    for path in [BOOK / "README.md", *(ROOT / c["chapter_path"] for c in CHAPTERS)]:
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if target.startswith(("http:", "https:", "#")):
                continue
            target_path = target.split("#", 1)[0]
            resolved = (path.parent / target_path).resolve()
            if not resolved.is_relative_to(ROOT) or not resolved.exists():
                missing.append((str(path.relative_to(ROOT)), target))
    assert not missing
