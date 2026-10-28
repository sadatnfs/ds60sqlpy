"""Independent shape and forecast-origin checks for optional legacy references."""

from __future__ import annotations

import ast
import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import nbformat
import pytest

from scripts.audit_practice import count_practice

ROOT = Path(__file__).resolve().parents[1]
SOLUTION_ROOT = ROOT / "python/ds-60day/solutions"
read_notebook: Callable[..., nbformat.NotebookNode] = nbformat.read


def reference_paths(day: int) -> tuple[Path, Path]:
    markdown = next(SOLUTION_ROOT.glob(f"day{day}_*/day{day}_solutions.md"))
    return markdown, markdown.with_suffix(".ipynb")


def reference_code(day: int) -> list[str]:
    markdown, _ = reference_paths(day)
    return re.findall(r"```python\n(.*?)```", markdown.read_text(), re.DOTALL)


def functions_only(day: int, cell: int) -> dict[str, Any]:
    namespace: dict[str, Any] = {
        "np": pytest.importorskip("numpy"),
        "pd": pytest.importorskip("pandas"),
        "FEATURES": ["lag1", "lag7", "roll7"],
    }
    tree = ast.parse(reference_code(day)[cell])
    definitions = ast.Module(
        body=[node for node in tree.body if isinstance(node, ast.FunctionDef)],
        type_ignores=[],
    )
    exec(compile(definitions, f"day{day}-functions", "exec"), namespace)
    return namespace


@pytest.mark.parametrize("day", [43, 47, 50])
def test_solution_notebooks_match_their_durable_markdown(day: int) -> None:
    markdown, path = reference_paths(day)
    notebook = read_notebook(path, as_version=4)
    nbformat.validate(notebook)
    notebook_code = [cell.source for cell in notebook.cells if cell.cell_type == "code"]
    markdown_code = reference_code(day)
    assert len(notebook_code) == len(markdown_code)
    for executable, source in zip(notebook_code, markdown_code, strict=True):
        assert ast.dump(ast.parse(executable)) == ast.dump(ast.parse(source))
    assert "\u2014" not in markdown.read_text()
    for cell in notebook.cells:
        if cell.cell_type == "code":
            assert cell.execution_count is None and cell.outputs == []
    baseline = json.loads((ROOT / "curriculum/practice_baseline.json").read_text())
    target = baseline["lessons"][f"python-{day}"]["target"]
    assert count_practice(markdown, solution=True) >= target
    assert count_practice(path, solution=True) >= target


def test_shap_class_selection_preserves_samples_under_both_supported_representations() -> None:
    namespace = functions_only(43, 1)
    np = namespace["np"]
    select = namespace["select_class_shap"]
    negative = np.arange(15).reshape(5, 3)
    positive = negative + 100
    legacy = [negative, positive]
    modern = np.stack(legacy, axis=-1)
    np.testing.assert_array_equal(select(legacy, (5, 3)), positive)
    np.testing.assert_array_equal(select(modern, (5, 3)), positive)
    np.testing.assert_array_equal(select(modern, (5, 3), 0), negative)


@pytest.mark.parametrize("case", ["single_array", "wrong_axes", "wrong_class_count", "nonfinite"])
def test_shap_unrecognized_output_cannot_be_reported_as_a_skipped_dependency(case: str) -> None:
    namespace = functions_only(43, 1)
    np = namespace["np"]
    values: Any = np.zeros((5, 3, 2))
    if case == "single_array":
        values = values[:, :, 1]
    elif case == "wrong_axes":
        values = values.transpose(2, 0, 1)
    elif case == "wrong_class_count":
        values = [np.zeros((5, 3))]
    else:
        values[0, 0, 1] = np.nan
    with pytest.raises(ValueError):
        namespace["select_class_shap"](values, (5, 3))
    tree = ast.parse(reference_code(43)[1])
    handlers = [node for node in ast.walk(tree) if isinstance(node, ast.ExceptHandler)]
    assert len(handlers) == 1
    assert isinstance(handlers[0].type, ast.Name)
    assert handlers[0].type.id == "ModuleNotFoundError"


def test_amp_reference_defaults_to_cpu_and_uses_current_explicit_device_api() -> None:
    code = "\n".join(reference_code(47))
    tree = ast.parse(code)
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    device = [node for node in calls if ast.unparse(node.func) == "torch.device"]
    assert len(device) == 1 and ast.literal_eval(device[0].args[0]) == "cpu"
    scaler = [node for node in calls if ast.unparse(node.func) == "torch.amp.GradScaler"]
    autocast = [node for node in calls if ast.unparse(node.func) == "torch.amp.autocast"]
    assert len(scaler) == len(autocast) == 1
    assert ast.literal_eval(scaler[0].args[0]) == "cuda"
    assert {keyword.arg for keyword in autocast[0].keywords} == {"device_type", "enabled"}
    assert "torch.cuda.amp." not in code
    assert "torch.cuda.is_available" not in code


def test_fourteen_day_baseline_repeats_observed_week_without_new_actuals() -> None:
    namespace = functions_only(50, 1)
    pd = namespace["pd"]
    history = pd.Series([2, 3, 5, 7, 11, 13, 17], index=pd.date_range("2020-01-01", periods=7))
    targets = pd.date_range("2020-01-08", periods=14)
    result = namespace["seasonal_naive_forecast"](history, targets)
    assert result.tolist() == [2, 3, 5, 7, 11, 13, 17] * 2
    assert result.index.equals(targets)


def test_recursive_forecast_uses_its_own_predictions_in_later_lags() -> None:
    namespace = functions_only(50, 2)
    pd = namespace["pd"]
    history = pd.Series(range(1, 8), index=pd.date_range("2020-01-01", periods=7))
    targets = pd.date_range("2020-01-08", periods=14)
    rows = []

    class LagSevenModel:
        def predict(self, features: Any) -> list[float]:
            rows.append(features.iloc[0].to_dict())
            return [float(features.iloc[0]["lag7"])]

    forecast = namespace["recursive_forecast"](LagSevenModel(), history, targets)
    assert forecast.tolist() == list(range(1, 8)) * 2
    assert rows[0] == {"lag1": 7, "lag7": 1, "roll7": 4}
    assert rows[1] == {"lag1": 1, "lag7": 2, "roll7": 4}
    assert rows[7] == rows[0]


def test_final_holdout_mutation_cannot_change_selection_or_fixed_origin_predictions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    np = pytest.importorskip("numpy")
    pd = pytest.importorskip("pandas")
    pytest.importorskip("sklearn")
    pytest.importorskip("matplotlib")
    monkeypatch.setenv("MPLBACKEND", "Agg")
    import matplotlib.pyplot as plt

    monkeypatch.setattr(plt, "show", lambda: plt.close("all"))
    code = reference_code(50)

    def run(holdout_shift: int) -> dict[str, Any]:
        namespace: dict[str, Any] = {"__name__": "__reference_test__"}
        exec(compile(code[0], "day50-setup", "exec"), namespace)
        if holdout_shift:
            namespace["df"].iloc[-14:, 0] += holdout_shift
            namespace["test"] = namespace["df"]["y"].iloc[-14:].copy()
        for index, source in enumerate(code[1:], start=1):
            exec(compile(source, f"day50-cell{index}", "exec"), namespace)
        return namespace

    original = run(0)
    changed = run(1000)
    pd.testing.assert_frame_equal(original["cv"], changed["cv"])
    assert original["selected_name"] == changed["selected_name"]
    np.testing.assert_array_equal(original["fc"], changed["fc"])
    np.testing.assert_array_equal(original["baseline_fc"], changed["baseline_fc"])
    assert original["base_mape"] != changed["base_mape"]
    assert len(original["cv"]["origin"].unique()) == 4
    assert original["cv"]["origin"].max() < original["test"].index.min()
    assert original["fc"].index.equals(original["test"].index)
