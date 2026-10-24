"""Authored UTF-8 remains portable even without Python's UTF-8 environment mode."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import IO, Any

import pytest

from scripts import normalize_lesson_prose, normalize_math_prose


@pytest.mark.parametrize("pipeline", ["prose", "math"])
def test_normalizers_preserve_unicode_code_with_legacy_windows_text_defaults(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, pipeline: str
) -> None:
    note = "A “café” mergedword has sqrt(n) units."
    code = 'print("東京 mergedword sqrt(n)")\n'
    fenced = "```python\n" + code + "```\n"
    notebook_code = {
        "cell_type": "code",
        "source": [code],
        "metadata": {"label": "“café”"},
        "execution_count": 1,
        "outputs": [{"output_type": "stream", "name": "stdout", "text": ["東京\n"]}],
    }
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {"label": "東京"},
        "cells": [
            {"cell_type": "markdown", "metadata": {}, "source": [note + "\n"]},
            notebook_code,
        ],
    }
    metadata = {
        "id": "mergedword",
        "summary": note,
        "runtime": "python-core",
        "source_path": "mergedword.py",
    }
    authoring = (
        'add("stable-id", "A “café” mergedword", "Trace mergedword", [], '
        "helper=\"print('東京 mergedword')\")\n"
    )
    documents = {
        "curriculum/prose-repairs.json": json.dumps(
            {"note": "“café”", "repairs": {"mergedword": "merged word"}}, ensure_ascii=False
        ),
        "curriculum/math-prose.json": json.dumps(
            {"note": "“café”", "rules": [{"source": "sqrt(n)", "latex": r"\sqrt{n}"}]},
            ensure_ascii=False,
        ),
        "courses/example/guide.md": note + "\n\n" + fenced,
        "courses/example/track.json": json.dumps(metadata, ensure_ascii=False),
        "courses/example/authoring/plan.py": authoring,
        "python/example.ipynb": json.dumps(notebook, ensure_ascii=False),
    }
    for relative, source in documents.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(source.encode("utf-8"))

    real_open = Path.open

    def legacy_open(
        path: Path,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> IO[Any]:
        if "b" not in mode:
            if encoding in {None, "locale"}:
                encoding = "cp1252"
            if newline is None and any(flag in mode for flag in "wax+"):
                newline = "\r\n"
        return real_open(path, mode, buffering, encoding, errors, newline)

    # This models the actual Windows failure independently of PYTHONUTF8=1.
    # It also models Windows newline translation to protect program bytes.
    # pathlib resolves a missing encoding through io.text_encoding before
    # calling Path.open. Override that resolution too, including under the
    # PYTHONUTF8=1 environment used by CI.
    monkeypatch.setattr(
        "io.text_encoding",
        lambda encoding, stacklevel=2: "cp1252" if encoding in {None, "locale"} else encoding,
    )
    monkeypatch.setattr(Path, "open", legacy_open)
    with pytest.raises(UnicodeDecodeError):
        (tmp_path / "courses/example/guide.md").read_text()

    report = tmp_path / "report.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["normalizer", "--root", str(tmp_path), "--write", "--report", str(report)],
    )
    entrypoint = normalize_lesson_prose.main if pipeline == "prose" else normalize_math_prose.main
    entrypoint()

    guide = (tmp_path / "courses/example/guide.md").read_bytes()
    assert "“café”".encode() in guide and fenced.encode() in guide
    assert b"\r\n" not in guide
    assert rb"\(\sqrt{n}\)" in guide
    expected = "merged word" if pipeline == "prose" else "mergedword"
    assert f"“café” {expected}".encode() in guide
    saved = json.loads((tmp_path / "python/example.ipynb").read_bytes())
    assert saved["cells"][1] == notebook_code
    assert saved["metadata"] == notebook["metadata"]
    assert rb"\(\sqrt{n}\)" in "".join(saved["cells"][0]["source"]).encode()
    saved_metadata = json.loads((tmp_path / "courses/example/track.json").read_bytes())
    assert saved_metadata["id"] == metadata["id"]
    assert saved_metadata["runtime"] == metadata["runtime"]
    assert saved_metadata["source_path"] == metadata["source_path"]
    assert "“café”" in saved_metadata["summary"]
    assert expected in saved_metadata["summary"]
    saved_authoring = (tmp_path / "courses/example/authoring/plan.py").read_bytes()
    assert b"\r\n" not in saved_authoring
    helper_values = [
        ast.literal_eval(keyword.value)
        for call in ast.walk(ast.parse(saved_authoring))
        if isinstance(call, ast.Call)
        for keyword in call.keywords
        if keyword.arg == "helper"
    ]
    assert helper_values == ["print('東京 mergedword')"]
    if pipeline == "prose":
        assert "“café” merged word".encode() in saved_authoring
    else:
        assert saved_authoring == authoring.encode()
    assert json.loads(report.read_bytes())
    assert b"\r\n" not in report.read_bytes()

    # A second dry run is both read-only and idempotent with the same defaults.
    before = {path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}
    monkeypatch.setattr(sys, "argv", ["normalizer", "--root", str(tmp_path)])
    entrypoint()
    assert {path: path.read_bytes() for path in before} == before
