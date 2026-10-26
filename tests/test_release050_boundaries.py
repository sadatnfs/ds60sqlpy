"""Independent release boundary checks, without workers, servers or learner state."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from collections.abc import Iterator
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from ds60sqlpy import reader_tex
from ds60sqlpy.catalog import Catalog
from ds60sqlpy.classroom_runs import ClassroomRunStore
from ds60sqlpy.module_jobs import MAX_RESPONSE
from ds60sqlpy.module_worker import WorkerJob
from ds60sqlpy.modules import ModuleCatalog, ModuleState
from ds60sqlpy.plot_artifacts import read_artifacts, validate_artifacts

ROOT = Path(__file__).resolve().parents[1]


def chart(text_size: int = 0) -> dict[str, Any]:
    return {
        "kind": "plotly",
        "figure": {"data": [{"type": "scatter", "x": [1], "y": [2], "text": ["x" * text_size]}]},
    }


def test_valid_worker_output_and_figures_fit_the_controller_wire_limit() -> None:
    figures = validate_artifacts([chart(170_000), chart(170_000)])
    job = WorkerJob(
        "a" * 32,
        "python-core",
        "print(1)",
        "python",
        15,
        None,
        status="succeeded",
        returncode=0,
        output="\x01" * 128_000,
        artifacts=figures,
    )
    # The worker emits JSON, so a legal control-character transcript expands
    # sixfold on the wire before the valid plot payload is included.
    encoded = json.dumps(job.snapshot(), ensure_ascii=False, allow_nan=False).encode()
    assert len(encoded) <= MAX_RESPONSE


def test_invalid_later_figure_does_not_discard_an_earlier_valid_one(tmp_path: Path) -> None:
    first = chart()
    (tmp_path / "ds60-figures.json").write_text(json.dumps([first, chart(181_000)]))
    artifacts, warning = read_artifacts(tmp_path)
    assert artifacts == validate_artifacts([first])
    assert warning


@pytest.fixture
def tex_assets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    folder = tmp_path / "assets/vendor/textbook"
    folder.mkdir(parents=True)
    monkeypatch.setattr(reader_tex, "files", lambda package: tmp_path)
    reader_tex.compiled_expressions.cache_clear()
    yield folder
    reader_tex.compiled_expressions.cache_clear()


def test_missing_compiled_cache_preserves_safe_native_source(tex_assets: Path) -> None:
    document = reader_tex.render_lesson_math("x+1")
    assert "<math" in document
    assert 'encoding="application/x-tex">x+1</annotation>' in document


@pytest.mark.parametrize("entry_kind", ["injected_html", "missing_html", "wrong_entry_type"])
def test_corrupt_compiled_entry_is_rejected_or_uses_safe_fallback(
    tex_assets: Path, entry_kind: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    entry: dict[str, Any] | bool = {"source": "x+1", "display": False}
    if entry_kind == "injected_html":
        entry = {
            "source": "x+1",
            "display": False,
            "html": '<img src=x onerror="alert(1)">unrelated formula',
        }
    elif entry_kind == "wrong_entry_type":
        entry = True
    payload = {
        "schema_version": 1,
        "compiler": "KaTeX 0.19.1",
        "expressions": {reader_tex.expression_key("x+1", False): entry},
    }
    encoded = json.dumps(payload).encode()
    (tex_assets / "compiled-tex.json").write_bytes(encoded)
    if entry_kind != "injected_html":
        # Exercise structural validation independently from the integrity gate.
        # HTML tampering keeps the real expected digest and must fail that gate.
        monkeypatch.setattr(reader_tex, "TEX_CACHE_SHA256", hashlib.sha256(encoded).hexdigest())
    document = reader_tex.render_lesson_math("x+1")
    assert "<img" not in document and "onerror" not in document
    assert "<math" in document and "x+1" in document


def test_compiler_collection_uses_reader_boundaries_and_restores_the_renderer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec = importlib.util.spec_from_file_location(
        "release050_compile_probe", ROOT / "scripts/compile_lesson_tex.py"
    )
    assert spec is not None and spec.loader is not None
    compiler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(compiler)
    guide = tmp_path / "guide.md"
    guide.write_text(
        "# Fixture\n\nInline \\(x^2\\).\n\n"
        "\\[\ny=x+1\n\\]\n\n"
        "```python\nliteral = r'\\(not compiled\\)'\n```\n\n"
        "Inline code `\\(also not compiled\\)` remains literal.\n"
    )
    monkeypatch.setattr(compiler.Catalog, "load", lambda root: SimpleNamespace())
    monkeypatch.setattr(
        compiler.lesson_reader, "artifact_targets", lambda catalog: {guide: "g.html"}
    )
    monkeypatch.setattr(compiler.lesson_reader, "reference_source_paths", lambda catalog: [])
    original = compiler.lesson_reader.render_math
    result = compiler.collect(tmp_path)
    assert {(row["source"], row["display"]) for row in result} == {
        ("x^2", False),
        ("y=x+1", True),
    }
    assert compiler.lesson_reader.render_math is original

    def fail(*args: object, **kwargs: object) -> None:
        raise ValueError("owned reader failure")

    monkeypatch.setattr(compiler.lesson_reader, "render_artifact", fail)
    with pytest.raises(ValueError, match="owned reader failure"):
        compiler.collect(tmp_path)
    assert compiler.lesson_reader.render_math is original


def test_check_inputs_refuses_stale_cache_without_requiring_node(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    spec = importlib.util.spec_from_file_location(
        "release050_compile_integrity_probe", ROOT / "scripts/compile_lesson_tex.py"
    )
    assert spec is not None and spec.loader is not None
    compiler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(compiler)
    inputs = tmp_path / "curriculum/tex-inputs.json"
    inputs.parent.mkdir()
    inputs.write_text("[]\n")
    output = tmp_path / "src/ds60sqlpy/assets/vendor/textbook/compiled-tex.json"
    output.parent.mkdir(parents=True)
    output.write_text("corrupt cache")
    (output.parent / "fonts.css").write_text("owned matching font fixture\n")
    monkeypatch.setattr(compiler, "ROOT", tmp_path)
    monkeypatch.setattr(compiler, "font_stylesheet", lambda: "owned matching font fixture\n")
    monkeypatch.setattr(compiler, "collect", lambda root: [])
    monkeypatch.setattr("sys.argv", ["compile_lesson_tex.py", "--check-inputs"])

    def no_process(*args: object, **kwargs: object) -> None:
        raise AssertionError("Source/integrity checking must not invoke Node")

    monkeypatch.setattr(compiler.subprocess, "run", no_process)
    assert compiler.main() == 1
    assert "Compiled TeX integrity is stale" in capsys.readouterr().out


def test_dax_draft_restart_and_failed_save_preserve_other_saved_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    catalog = cast(
        ModuleCatalog, SimpleNamespace(root=tmp_path, get=lambda key: SimpleNamespace(id=key))
    )
    directory = tmp_path / "modules"
    state = ModuleState(catalog, directory)
    state.save("torch-001", {"source": "previous saved Python", "review": "reviewed"})
    source = 'EVALUATE ROW("Label", "caf\u00e9")\r\n// source remains exact\r\n'
    state.save("dax-001", {"source": source, "prediction": "A single row"})
    reopened = ModuleState(catalog, directory)
    assert reopened.read("dax-001")["source"] == source
    assert reopened.read("torch-001")["review"] == "reviewed"
    before = state.path.read_bytes()

    def refuse_write(*args: object, **kwargs: object) -> None:
        raise OSError("owned fixture storage failure")

    monkeypatch.setattr("ds60sqlpy.modules.atomic_json_write", refuse_write)
    with pytest.raises(OSError, match="storage failure"):
        reopened.save("dax-001", {"source": "new unsaved draft"})
    assert state.path.read_bytes() == before
    assert reopened.read("dax-001")["source"] == source


def test_old_and_plot_receipts_roundtrip_without_replaying_or_relabelling(tmp_path: Path) -> None:
    catalog = Catalog.load(ROOT)
    store = ClassroomRunStore(catalog, tmp_path / "runs")
    base = {
        "language": "python",
        "returncode": 0,
        "output": "a checked value\n",
        "elapsed_seconds": 0.125,
        "stopped": None,
        "figures": [],
    }
    old = store.record("python-01", "python", "snippet", "old source\n", base)
    new = store.record(
        "python-01", "python", "snippet", "plot source\n", {**base, "artifacts": [chart()]}
    )
    restarted = ClassroomRunStore(catalog, tmp_path / "runs")
    assert restarted.get("python-01", "python", "snippet", old["id"]) == old
    assert restarted.get("python-01", "python", "snippet", new["id"]) == new
    assert "artifacts" not in old["result"]
