"""Regression checks for optional legacy lesson execution boundaries."""

from __future__ import annotations

import ast
import re
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import nbformat
import pytest

from scripts.audit_practice import count_practice, practice_targets

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "python/ds-60day"
DAYS = (27, 39, 43, 46, 47, 48, 49, 50, 52, 53, 56)
read_notebook: Callable[..., nbformat.NotebookNode] = nbformat.read


def learner(day: int) -> Path:
    return next((BASE / "notebooks").glob(f"day{day:02d}_*.ipynb"))


def source(day: int, index: int) -> str:
    return str(read_notebook(learner(day), as_version=4).cells[index].source)


def flag_enabled(code: str, name: str) -> ast.Module:
    tree = ast.parse(code)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            node.value = ast.Constant(True)
    return ast.fix_missing_locations(tree)


@pytest.mark.parametrize("day", DAYS)
def test_optional_guides_describe_actual_core_and_prepared_route(day: int) -> None:
    guide = next((BASE / "companion-guides").glob(f"day{day:02d}_*.md"))
    text = guide.read_text()
    assert "default Core does not include" in text
    assert "Prepared browser alternative" in text
    assert "host notebook environment and a Docker app image are separate" in text
    for link in re.findall(r"\]\((\.\./\.\./\.\./courses/[^)]+)\)", text):
        assert (guide.parent / link).resolve().is_file()
    for path in (learner(day), guide):
        assert count_practice(path) >= practice_targets()[f"python-{day:02d}"]["target"]
    nbformat.validate(read_notebook(learner(day), as_version=4))


def test_external_geodata_is_not_fetched_by_default() -> None:
    # No geodatasets import or gpd object is needed in the disabled branch.
    exec(compile(source(27, 8), "geodata-default", "exec"), {})


def test_cached_sentiment_is_not_loaded_by_default() -> None:
    exec(compile(source(49, 1), "sentiment-default", "exec"), {})


def test_sentiment_enabled_without_assets_fails_before_loading(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    called: list[str] = []
    transformer = ModuleType("transformers")
    loader = SimpleNamespace(from_pretrained=lambda *args, **kwargs: called.append("load"))
    transformer.AutoTokenizer = loader  # type: ignore[attr-defined]
    transformer.AutoModelForSequenceClassification = loader  # type: ignore[attr-defined]
    transformer.pipeline = lambda *args, **kwargs: called.append("pipeline")  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "transformers", transformer)
    with pytest.raises(FileNotFoundError, match="Prepare the model snapshot"):
        exec(
            compile(
                flag_enabled(source(49, 1), "RUN_CACHED_SENTIMENT"), "sentiment-enabled", "exec"
            ),
            {},
        )
    assert called == []


def test_all_transformer_loaders_are_local_only() -> None:
    ref = next((BASE / "solutions").glob("day49_*/day49_solutions.ipynb"))
    codes = [source(49, 1)] + [
        str(c.source) for c in read_notebook(ref, as_version=4).cells if c.cell_type == "code"
    ]
    count = 0
    for code in codes:
        for node in ast.walk(ast.parse(code)):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "from_pretrained"
            ):
                kwargs = {keyword.arg: keyword.value for keyword in node.keywords}
                local_only = kwargs.get("local_files_only")
                assert isinstance(local_only, ast.Constant)
                assert local_only.value is True
                assert isinstance(node.args[0], ast.Name), (
                    "Use the prepared local directory, not an implicit Hub identifier"
                )
                count += 1
    assert count >= 5


def test_day47_preprocessor_never_fits_held_out_rows() -> None:
    calls: list[tuple[str, object]] = []

    class Array:
        def astype(self, dtype: object) -> Array:
            return self

    train, test = Array(), Array()

    class Scaler:
        def fit_transform(self, rows: object) -> object:
            calls.append(("fit", rows))
            return rows

        def transform(self, rows: object) -> object:
            calls.append(("transform", rows))
            return rows

    tree = ast.parse(source(47, 1))
    prefix: list[ast.stmt] = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(node, ast.Assign) and any(
            isinstance(n, ast.Attribute) and n.attr == "from_numpy" for n in ast.walk(node)
        ):
            break
        prefix.append(node)
    namespace = {
        "make_classification": lambda **kwargs: ("raw features", "labels"),
        "train_test_split": lambda *args, **kwargs: (train, test, "train labels", "test labels"),
        "StandardScaler": Scaler,
        "np": SimpleNamespace(float32="float32"),
        "torch": SimpleNamespace(
            manual_seed=lambda seed: None, set_num_threads=lambda threads: None
        ),
    }
    exec(
        compile(ast.Module(body=prefix, type_ignores=[]), "preprocessing-prefix", "exec"), namespace
    )
    assert calls == [("fit", train), ("transform", test)]


def test_mlflow_setup_overrides_ambient_store_before_any_lookup(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    events: list[tuple[str, object]] = []

    def create_experiment(name: str, **kwargs: object) -> str:
        events.append(("create", kwargs))
        return "7"

    fake = SimpleNamespace(
        active_run=lambda: None,
        set_tracking_uri=lambda uri: events.append(("tracking", uri)),
        set_registry_uri=lambda uri: events.append(("registry", uri)),
        get_experiment_by_name=lambda name: events.append(("lookup", name)),
        create_experiment=create_experiment,
        set_experiment=lambda **kwargs: events.append(("select", kwargs)),
    )
    code = source(53, 1)
    setup = code[code.index("from pathlib import Path") : code.index("with mlflow.start_run(")]
    exec(compile(setup, "local-mlflow-setup", "exec"), {"mlflow": fake})
    assert [name for name, _ in events] == ["tracking", "registry", "lookup", "create", "select"]
    assert events[0][1] == "sqlite:///" + str(tmp_path / "artifacts/day53/tracking.sqlite")
    assert events[3][1] == {"artifact_location": (tmp_path / "artifacts/day53/runs").as_uri()}


def test_mlflow_refuses_reused_experiment_with_foreign_artifact_store(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    fake = SimpleNamespace(
        active_run=lambda: None,
        set_tracking_uri=lambda uri: None,
        set_registry_uri=lambda uri: None,
        get_experiment_by_name=lambda name: SimpleNamespace(
            artifact_location="https://example.invalid/foreign"
        ),
    )
    code = source(53, 1)
    setup = code[code.index("from pathlib import Path") : code.index("with mlflow.start_run(")]
    with pytest.raises(RuntimeError, match="different artifact location"):
        exec(compile(setup, "local-mlflow-setup", "exec"), {"mlflow": fake})


@pytest.mark.parametrize(
    "api",
    [
        None,
        "https://remote.invalid/api",
        "http://user:password@localhost:4200/api",  # secret-scan: allow-fixture
    ],
)
def test_prefect_opt_in_refuses_unowned_or_remote_api(
    monkeypatch: pytest.MonkeyPatch, api: str | None
) -> None:
    prefect = ModuleType("prefect")
    prefect.task = lambda function: function  # type: ignore[attr-defined]
    prefect.flow = lambda function: function  # type: ignore[attr-defined]
    settings = ModuleType("prefect.settings")
    settings.PREFECT_API_URL = SimpleNamespace(value=lambda: api)  # type: ignore[attr-defined]
    teaching = ModuleType("ds60sqlpy.teaching_data")
    teaching.load_teaching_frame = lambda name: pytest.fail("Flow data should not be loaded")  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "prefect", prefect)
    monkeypatch.setitem(sys.modules, "prefect.settings", settings)
    monkeypatch.setitem(sys.modules, "ds60sqlpy.teaching_data", teaching)
    with pytest.raises(RuntimeError, match="loopback Prefect API"):
        exec(
            compile(
                flag_enabled(source(56, 1), "RUN_LOCAL_PREFECT_FLOW"), "prefect-opt-in", "exec"
            ),
            {},
        )


def test_amp_extension_reports_missing_modern_api_without_running() -> None:
    reference = next((BASE / "solutions").glob("day47_*/day47_solutions.ipynb"))
    codes = [
        str(cell.source)
        for cell in read_notebook(reference, as_version=4).cells
        if cell.cell_type == "code"
    ]
    amp = next(code for code in codes if "torch.amp.GradScaler" in code)
    exec(compile(amp, "old-torch-amp-boundary", "exec"), {"torch": SimpleNamespace()})


def test_shap_learner_and_reference_share_the_tested_shape_guard() -> None:
    reference = next((BASE / "solutions").glob("day43_*/day43_solutions.ipynb"))
    codes = [
        str(cell.source)
        for cell in read_notebook(reference, as_version=4).cells
        if cell.cell_type == "code"
    ]
    functions = []
    for code in [source(43, 1), next(code for code in codes if "def select_class_shap" in code)]:
        functions.append(
            next(
                node
                for node in ast.parse(code).body
                if isinstance(node, ast.FunctionDef) and node.name == "select_class_shap"
            )
        )
    assert ast.dump(functions[0]) == ast.dump(functions[1])


def test_prefect_deployment_extension_checks_api_before_serving(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = ModuleType("prefect.settings")
    settings.PREFECT_API_URL = SimpleNamespace(value=lambda: "https://remote.invalid/api")  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "prefect.settings", settings)
    reference = next((BASE / "solutions").glob("day56_*/day56_solutions.ipynb"))
    code = next(
        str(cell.source)
        for cell in read_notebook(reference, as_version=4).cells
        if cell.cell_type == "code" and "def serve_daily" in cell.source
    )
    namespace: dict[str, Any] = {
        "etl_flow": SimpleNamespace(
            serve=lambda **kwargs: pytest.fail("Remote deployment must not be created")
        )
    }
    exec(compile(code, "local-deployment-boundary", "exec"), namespace)
    with pytest.raises(RuntimeError, match="loopback Prefect API"):
        namespace["serve_daily"]()
