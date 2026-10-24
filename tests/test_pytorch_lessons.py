"""Complete PyTorch route contracts and opt-in prepared-CPU numerical evidence."""

from __future__ import annotations

import ast
import hashlib
import importlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "courses/deep-learning-pytorch"
ENTRIES = json.loads((BASE / "lessons.json").read_text())["lessons"]
PLAN = {row["id"]: row for row in json.loads((BASE / "track.json").read_text())["lessons"]}


def reference(lesson_id: str) -> ModuleType:
    path = BASE / "solutions" / f"{lesson_id}_solution.py"
    spec = importlib.util.spec_from_file_location(lesson_id.replace("-", "_"), path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_complete_route_has36_real_bundles_and_exact_tensorflow_pairs() -> None:
    assert len(ENTRIES) == len(PLAN) == 36
    assert {entry["id"] for entry in ENTRIES} == {f"torch-{i:03d}" for i in range(1, 37)}
    for entry in ENTRIES:
        lesson = PLAN[entry["id"]]
        paired = f"tf-{int(entry['id'][-3:]):03d}"
        assert lesson["paired_lesson_id"] == paired
        assert entry["runtime_profile"] == lesson["runtime"]
        assert entry["runtime_profile"] == (
            "reading" if entry["id"] == "torch-001" else "llm-torch-cpu"
        )
        for relative in [entry["source_path"], entry["guide_path"], *entry["solution_paths"]]:
            path = ROOT / relative
            assert path.is_file() and path.resolve().is_relative_to(BASE)
            text = path.read_text()
            assert "\u2014" not in text and "\u200b" not in text
            if path.suffix == ".py":
                ast.parse(text, filename=relative)
        guide = (ROOT / entry["guide_path"]).read_text()
        assert f"../../deep-learning-tensorflow/guides/{paired}.md" in guide
        assert (ROOT / "courses/deep-learning-tensorflow/guides" / f"{paired}.md").is_file()
        assert all(f"### Example {label}:" in guide for label in "ABC")
        assert "## Interview reasoning with worked answers" in guide
        assert len(re.findall(r"^\s*[1-6]\. \*\*", guide, re.MULTILINE)) == 6
        assert guide.count("**Expected:**") >= 9
        assert entry["guide_path"] in guide and entry["source_path"] in guide
        for prerequisite in lesson["prerequisites"]:
            assert f"`{prerequisite}`" in guide


def test_shared_teaching_depth_and_practice_contracts() -> None:
    from ds60sqlpy.catalog import Catalog, Lesson
    from scripts.audit_lesson_depth import audit
    from scripts.audit_practice import count_practice

    lessons = []
    for entry in ENTRIES:
        spec = PLAN[entry["id"]]
        lessons.append(
            Lesson(
                id=entry["id"],
                track="deep-learning-pytorch",
                day=int(entry["id"][-3:]),
                title=spec["title"],
                level=spec["level"],
                phase="PyTorch foundations and model evidence",
                estimated_minutes=spec["minutes"],
                prerequisites=tuple(spec["prerequisites"]),
                lesson_path=entry["source_path"],
                guide_path=entry["guide_path"],
                solution_paths=tuple(entry["solution_paths"]),
                dependency_group="core",
                network="offline",
                runner="none" if entry["language"] == "markdown" else "python",
            )
        )
        for relative in [entry["source_path"], entry["guide_path"], *entry["solution_paths"]]:
            assert count_practice(ROOT / relative, solution="/solutions/" in relative) >= 6
    catalog = Catalog(
        ROOT,
        lessons,
        tracks={
            "deep-learning-pytorch": {
                "title": "Deep learning with PyTorch",
                "plan": "courses/deep-learning-pytorch/README.md",
            }
        },
    )
    failures = [(row.lesson_id, row.issues) for row in audit(catalog) if not row.passes]
    assert not failures


@pytest.mark.skipif(
    os.environ.get("DS60_TEST_TORCH") != "1",
    reason="Requires the separately prepared PyTorch2.9 CPU runtime",
)
@pytest.mark.parametrize(
    "lesson_id", [entry["id"] for entry in ENTRIES if entry["language"] == "python"]
)
def test_every_pytorch_reference_executes_six_real_checks(lesson_id: str) -> None:
    assert reference(lesson_id).verify() == {"checks": 6, "status": "passed"}


@pytest.mark.parametrize("lesson_id", ["torch-028", "torch-032", "torch-036"])
def test_fresh_process_sources_compile_and_report_child_failures(lesson_id: str) -> None:
    path = BASE / "solutions" / f"{lesson_id}_solution.py"
    source = path.read_text()
    tree = ast.parse(source)
    programs = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id in {"child", "program"}
                for target in node.targets
            )
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "dedent"
        ):
            literal = ast.literal_eval(node.value.args[0])
            assert isinstance(literal, str)
            program = textwrap.dedent(literal)
            compile(program, f"{lesson_id}-child", "exec")
            programs.append(program)
    assert len(programs) == 1
    assert "result.stderr" in source and "timeout=60" in source and "weights_only=True" in source
    assert "TemporaryDirectory" in source and "temporary.cleanup()" in source


def test_default_sources_have_no_model_data_or_package_downloads() -> None:
    forbidden = ("requests", "urllib", "huggingface_hub", "torchvision", "transformers")
    for entry in ENTRIES:
        if entry["language"] != "python":
            continue
        source = (ROOT / entry["solution_paths"][0]).read_text()
        tree = ast.parse(source)
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        assert not imported.intersection(forbidden)
        assert (
            "pip install" not in source
            and "torch.hub.load" not in source
            and "download=True" not in source
        )
    loader = (BASE / "solutions/torch-015_solution.py").read_text()
    assert "num_workers=0" in loader


@pytest.mark.skipif(
    os.environ.get("DS60_TEST_TORCH") != "1", reason="Requires prepared PyTorch CPU runtime"
)
def test_attention_rejects_mask_errors_and_preserves_nonuniform_prefixes() -> None:
    torch = importlib.import_module("torch")

    module = reference("torch-022")
    q = torch.tensor([[1.0, 2.0], [0.0, 1.0], [2.0, -1.0]], dtype=torch.float64)
    k = torch.tensor([[2.0, 0.0], [1.0, 1.0], [-1.0, 2.0]], dtype=torch.float64)
    v = torch.tensor([[1.0, 3.0], [2.0, 4.0], [5.0, 7.0]], dtype=torch.float64)
    allowed = torch.ones((3, 3), dtype=torch.bool).tril()
    full = module.attention(q, k, v, allowed)
    torch.testing.assert_close(
        module.attention(q[:2], k[:2], v[:2], allowed[:2, :2]), full[:2], atol=1e-12, rtol=0
    )
    with pytest.raises(TypeError):
        module.attention(q, k, v, allowed.long())
    broken = allowed.clone()
    broken[0] = False
    with pytest.raises(ValueError):
        module.attention(q, k, v, broken)


@pytest.mark.skipif(
    os.environ.get("DS60_TEST_TORCH") != "1", reason="Requires prepared PyTorch CPU runtime"
)
def test_gradcheck_detects_a_wrong_custom_backward_rule() -> None:
    torch = importlib.import_module("torch")

    module = reference("torch-026")

    def wrong_cube(value: Any) -> Any:
        # Preserve the cube forward value but deliberately differentiate a square.
        wrong_path = value**2
        return value.detach() ** 3 + wrong_path - wrong_path.detach()

    values = torch.tensor([0.2, -0.7], dtype=torch.float64, requires_grad=True)
    assert torch.autograd.gradcheck(module.Cube.apply, (values,))
    assert not torch.autograd.gradcheck(wrong_cube, (values,), raise_exception=False)


@pytest.mark.skipif(
    os.environ.get("DS60_TEST_TORCH") != "1", reason="Requires prepared PyTorch CPU runtime"
)
def test_inference_contract_rejects_silent_coercion_and_preserves_ownership() -> None:
    torch = importlib.import_module("torch")

    module = reference("torch-033")
    values = torch.tensor([[2.0, 1.0], [4.0, 3.0]], dtype=torch.float32)
    before = values.clone()
    output = module.predict(values)
    assert output.tolist() == [3.0, 5.0]
    output[0] = 999
    assert torch.equal(values, before)
    with pytest.raises(TypeError):
        module.predict(values.double())
    with pytest.raises(ValueError):
        module.predict(torch.empty((0, 2)))
    with pytest.raises(ValueError):
        module.predict(torch.tensor([[float("inf"), 1.0]]))


def test_depth_reviews_cover_the_route_with_topic_specific_reasoning() -> None:
    matrix = json.loads((BASE / "authoring/review_matrix.json").read_text())["chapters"]
    assert [row["id"] for row in matrix] == [entry["id"] for entry in ENTRIES]
    diagnoses = []
    for row in matrix:
        assert row["status"] == "reviewed_and_deepened", row["id"]
        assert len(row["findings"]) >= 2
        assert row["paired_guide_reviewed"] == PLAN[row["id"]]["paired_lesson_id"]
        guide = (BASE / "guides" / f"{row['id']}.md").read_text()
        decisions = guide.split("## Design decisions and when to use this method\n", 1)[1]
        decisions = decisions.split("\n## ", 1)[0].strip()
        assert decisions and "##" not in decisions
        diagnosis = guide.split("## Common pitfalls and diagnosis\n", 1)[1]
        diagnosis = diagnosis.split("\n## ", 1)[0].strip()
        assert diagnosis and "locate the first intermediate value that violates" not in diagnosis
        diagnoses.append(diagnosis)
    assert len(set(diagnoses)) == len(ENTRIES)


@pytest.mark.parametrize(
    "windows_text_defaults", [False, True], ids=["native-text", "windows-text"]
)
def test_portable_authoring_recreates_all_published_artifacts(
    tmp_path: Path, windows_text_defaults: bool
) -> None:
    destination = tmp_path / "courses/deep-learning-pytorch"
    for directory in ["guides", "lessons", "solutions", "authoring"]:
        (destination / directory).mkdir(parents=True)
    for filename in ["track.json", "lessons.json", "authoring/review_runtime_evidence.json"]:
        shutil.copyfile(BASE / filename, destination / filename)
    # Reproduce the published authoring pipeline, including reviewed prose/math
    # normalization, in the isolated root rather than copying published output.
    (tmp_path / "scripts").mkdir()
    (tmp_path / "curriculum").mkdir()
    for filename in ("normalize_lesson_prose.py", "normalize_math_prose.py"):
        shutil.copyfile(ROOT / "scripts" / filename, tmp_path / "scripts" / filename)
    for filename in ("prose-repairs.json", "math-prose.json"):
        shutil.copyfile(ROOT / "curriculum" / filename, tmp_path / "curriculum" / filename)
    program = "\n".join(
        [
            "import sys",
            "from pathlib import Path",
            "if sys.argv[3] == 'windows':",
            "    import io",
            "    io.text_encoding = lambda encoding, stacklevel=2: "
            "'cp1252' if encoding in (None, 'locale') else encoding",
            "    original_open = Path.open",
            "    def windows_open(path, mode='r', buffering=-1, "
            "encoding=None, errors=None, newline=None):",
            "        if 'b' not in mode and any(flag in mode for flag in 'wax+') "
            "and newline is None:",
            "            newline = '\\r\\n'",
            "        return original_open(path, mode, buffering, encoding, errors, newline)",
            "    Path.open = windows_open",
            "sys.path.insert(0, sys.argv[1])",
            "import render",
            "import specs",
            "from depth_reviews import apply_reviews, write_review_matrix",
            "render.ROOT = Path(sys.argv[2])",
            "apply_reviews(render.SPECS)",
            "render.write_all()",
            "write_review_matrix(render.ROOT)",
        ]
    )
    completed = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            program,
            str(BASE / "authoring"),
            str(tmp_path),
            "windows" if windows_text_defaults else "native",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    normalized = subprocess.run(
        [sys.executable, "-B", str(tmp_path / "scripts/normalize_lesson_prose.py"), "--write"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert normalized.returncode == 0, normalized.stderr
    files = ["track.json", "lessons.json", "authoring/review_matrix.json"]
    for entry in ENTRIES:
        files.extend(
            str(Path(relative).relative_to("courses/deep-learning-pytorch"))
            for relative in [entry["guide_path"], entry["source_path"], *entry["solution_paths"]]
        )
    mismatches = [
        name for name in files if (destination / name).read_bytes() != (BASE / name).read_bytes()
    ]
    assert mismatches == []


def test_worked_sequences_compile_and_share_the_reference_setup() -> None:
    for entry in ENTRIES:
        if entry["language"] != "python":
            continue
        guide = (ROOT / entry["guide_path"]).read_text()
        assert "Run the three worked blocks in order in one scratch file" in guide
        section = guide.split("## Worked example / walkthrough\n", 1)[1]
        section = section.split("## Prediction before your attempt", 1)[0]
        blocks = re.findall(r"```python\n(.*?)\n```", section, re.DOTALL)
        assert len(blocks) == 3, entry["id"]
        tree = ast.parse("\n\n".join(blocks))
        reference_tree = ast.parse((ROOT / entry["solution_paths"][0]).read_text())
        verify = next(
            node
            for node in reference_tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "verify"
        )
        setup = reference_tree.body[1 : reference_tree.body.index(verify)]
        assert isinstance(reference_tree.body[0], ast.Expr)
        assert isinstance(reference_tree.body[0].value, ast.Constant)
        # The sequential worked program consists of the identical setup and the
        # reference's first three exercises. Comments and whitespace are irrelevant.
        prefix = [*setup, *verify.body[: len(tree.body) - len(setup)]]
        assert [ast.dump(node) for node in tree.body] == [ast.dump(node) for node in prefix], entry[
            "id"
        ]


def test_review_runtime_evidence_matches_current_references_and_worked_programs() -> None:
    evidence = json.loads((BASE / "authoring/review_runtime_evidence.json").read_text())["records"]
    references = [record for record in evidence if record["kind"] == "reference"]
    worked = [record for record in evidence if record["kind"] == "worked_sequence"]
    assert {record["lesson_id"] for record in references} == {
        "torch-005",
        "torch-012",
        "torch-014",
        "torch-015",
        "torch-016",
        "torch-030",
    }
    assert {record["lesson_id"] for record in worked} == {
        "torch-005",
        "torch-012",
        "torch-015",
        "torch-016",
    }
    from scripts.normalize_math_prose import protected_code

    presentation = json.loads((ROOT / "curriculum/presentation-parity.json").read_text())
    bindings = {row["path"]: row for row in presentation["records"]}
    for record in evidence:
        assert record["status"] == "succeeded" and record["runtime_profile"] == "llm-torch-cpu"
        assert record["image_id"].startswith("sha256:")
        if record["kind"] == "reference":
            source = (ROOT / record["source_path"]).read_bytes()
        else:
            guide = (ROOT / record["guide_path"]).read_bytes()
            guide_digest = hashlib.sha256(guide).hexdigest()
            if record["guide_path"] in bindings:
                # The runtime receipt keeps the historical guide hash. A
                # separate typography binding proves current prose/code parity.
                binding = bindings[record["guide_path"]]
                assert binding["historical_sha256"] == record["guide_sha256"]
                assert guide_digest == binding["presentation_sha256"]
                assert [
                    hashlib.sha256(block.encode()).hexdigest()
                    for block in protected_code(guide.decode())
                ] == binding["code_block_sha256"]
            else:
                assert guide_digest == record["guide_sha256"]
            section = guide.decode().split("## Worked example / walkthrough\n", 1)[1]
            section = section.split("## Prediction before your attempt", 1)[0]
            blocks = re.findall(r"```python\n(.*?)\n```", section, re.DOTALL)
            assert len(blocks) == 3
            source = ("\n\n".join(blocks) + "\n").encode()
        assert hashlib.sha256(source).hexdigest() == record["source_sha256"]
