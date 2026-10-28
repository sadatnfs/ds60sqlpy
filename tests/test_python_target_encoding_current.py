"""Independent leakage and categorical-dtype proofs for Day 51 target encoding."""

from __future__ import annotations

import ast
import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import nbformat
import numpy as np
import pandas as pd  # type: ignore[import-untyped]
import pytest
from sklearn.model_selection import StratifiedKFold  # type: ignore[import-untyped]

from scripts.audit_practice import count_practice
from scripts.build_solution_notebooks import build_notebook

ROOT = Path(__file__).resolve().parents[1]
BASE = Path("python/ds-60day")
LEARNER = BASE / "notebooks/day51_advanced_feature_engineering_target_encoding.ipynb"
GUIDE = BASE / "companion-guides/day51_advanced_feature_engineering_target_encoding.md"
SOLUTION = BASE / "solutions/day51_advanced_feature_engineering_target_encoding/day51_solutions.md"
REFERENCE = SOLUTION.with_suffix(".ipynb")
read_notebook: Callable[..., nbformat.NotebookNode] = nbformat.read


def functions(relative: Path) -> dict[str, Any]:
    notebook = read_notebook(ROOT / relative, as_version=4)
    source = next(
        cell.source
        for cell in notebook.cells
        if cell.cell_type == "code" and "def kfold_target_encode(" in cell.source
    )
    tree = ast.parse(source)
    definitions = ast.Module(
        body=[node for node in tree.body if isinstance(node, ast.FunctionDef)],
        type_ignores=[],
    )
    namespace: dict[str, Any] = {"np": np, "pd": pd, "StratifiedKFold": StratifiedKFold}
    exec(compile(definitions, str(relative), "exec"), namespace)
    return namespace


@pytest.fixture(params=[LEARNER, REFERENCE], ids=["learner", "reference"])
def encoder(request: pytest.FixtureRequest) -> dict[str, Any]:
    return functions(request.param)


def test_unique_categorical_rows_use_training_fold_prior_in_source_order(
    encoder: dict[str, Any],
) -> None:
    index = pd.Index([91, 5, 73, 2, 44, 19, 88, 7, 63], name="source_row")
    levels = [f"row-{position}" for position in range(9)]
    cat = pd.Series(
        pd.Categorical(levels, categories=[*levels, "unused"]), index=index, name="category"
    )
    target = pd.Series([1, 0, 1, 0, 1, 0, 1, 0, 1], index=index, name="target")
    before_cat, before_target = cat.copy(deep=True), target.copy(deep=True)
    expected: list[float | None] = [None] * len(cat)
    fold_priors = []
    for fit, validation in StratifiedKFold(3, shuffle=True, random_state=42).split(cat, target):
        # Independent oracle: every category is absent from the fit partition.
        prior = sum(int(target.iloc[position]) for position in fit) / len(fit)
        fold_priors.append(prior)
        fit_categories = {cat.iloc[position] for position in fit}
        for position in validation:
            assert cat.iloc[position] not in fit_categories
            expected[position] = prior
    assert set(fold_priors) == {1 / 2, 2 / 3}
    assert all(prior != 5 / 9 for prior in fold_priors)
    actual = encoder["kfold_target_encode"](cat, target, n_splits=3, smoothing=7)
    pd.testing.assert_series_equal(actual, pd.Series(expected, index=index, dtype=float))
    assert pd.api.types.is_float_dtype(actual.dtype)
    assert np.isfinite(actual.to_numpy()).all()
    pd.testing.assert_series_equal(cat, before_cat)
    pd.testing.assert_series_equal(target, before_target)


def test_full_training_smoothing_handles_known_unused_unseen_and_missing(
    encoder: dict[str, Any],
) -> None:
    index = pd.Index([80, 11, 29, 3], name="source_row")
    cat = pd.Series(
        pd.Categorical(["a", "a", "a", "b"], categories=["a", "b", "unused"]), index=index
    )
    target = pd.Series([1, 1, 0, 1], index=index)
    mapping, prior = encoder["fit_target_map"](cat, target, smoothing=3)
    assert prior == 3 / 4
    assert mapping.index.tolist() == ["a", "b"]
    assert mapping.loc["a"] == pytest.approx((2 + 3 * (3 / 4)) / 6)
    assert mapping.loc["b"] == pytest.approx((1 + 3 * (3 / 4)) / 4)
    new = pd.Series(
        pd.Categorical(["b", "a", "unused", "unseen", None]),
        index=pd.Index([101, 17, 32, 4, 8], name="inference_row"),
    )
    before = new.copy(deep=True)
    actual = encoder["transform_target_encode"](new, mapping, prior)
    expected = pd.Series([13 / 16, 17 / 24, 3 / 4, 3 / 4, 3 / 4], index=new.index)
    pd.testing.assert_series_equal(actual, expected)
    assert np.isfinite(actual.to_numpy()).all()
    pd.testing.assert_series_equal(new, before)
    # Even a fully known one-to-one categorical mapping must convert before fillna.
    known = pd.Series(pd.Categorical(["a", "b"]))
    known_result = encoder["transform_target_encode"](known, mapping, prior)
    np.testing.assert_allclose(known_result, [17 / 24, 13 / 16])


def test_all_missing_training_categories_have_finite_fold_fallbacks(
    encoder: dict[str, Any],
) -> None:
    cat = pd.Series(pd.Categorical([None] * 9, categories=["unused"]))
    target = pd.Series([1, 0, 1, 0, 1, 0, 1, 0, 1])
    mapping, prior = encoder["fit_target_map"](cat, target)
    assert mapping.empty and prior == 5 / 9
    result = encoder["kfold_target_encode"](cat, target, n_splits=3)
    assert set(result) == {1 / 2, 2 / 3}
    assert np.isfinite(result.to_numpy()).all()


@pytest.mark.parametrize("function", ["fit_target_map", "kfold_target_encode"])
def test_misaligned_target_indexes_are_rejected(encoder: dict[str, Any], function: str) -> None:
    cat = pd.Series(["a", "b", "c"], index=[8, 3, 1])
    target = pd.Series([0, 1, 0], index=[3, 8, 1])
    with pytest.raises(ValueError, match="indexes must match"):
        encoder[function](cat, target)


@pytest.mark.parametrize("bad_target", [[], [0, np.nan], [1, np.inf], [0, -np.inf]])
@pytest.mark.parametrize("function", ["fit_target_map", "kfold_target_encode"])
def test_nonfinite_or_empty_targets_are_rejected(
    encoder: dict[str, Any], function: str, bad_target: list[float]
) -> None:
    target = pd.Series(bad_target, dtype=float)
    cat = pd.Series(["a"] * len(target), dtype=object)
    with pytest.raises(ValueError, match="nonempty and finite"):
        encoder[function](cat, target)


@pytest.mark.parametrize("smoothing", [-1, np.nan, np.inf])
def test_invalid_smoothing_is_rejected(encoder: dict[str, Any], smoothing: float) -> None:
    with pytest.raises(ValueError, match="finite and nonnegative"):
        encoder["fit_target_map"](pd.Series(["a", "a"]), pd.Series([0, 1]), smoothing)


def test_nonfinite_encoded_values_are_rejected(encoder: dict[str, Any]) -> None:
    with pytest.raises(ValueError, match="must be finite"):
        encoder["transform_target_encode"](pd.Series(["a"]), pd.Series({"a": np.inf}), 0.5)


def test_reference_generation_practice_and_clean_notebook_contracts() -> None:
    generated = build_notebook(ROOT / SOLUTION, ROOT)
    actual = read_notebook(ROOT / REFERENCE, as_version=4)
    assert actual.metadata == generated.metadata
    assert len(actual.cells) == len(generated.cells)
    for cell, expected in zip(actual.cells, generated.cells, strict=True):
        assert cell.id == expected.id and cell.cell_type == expected.cell_type
        assert cell.source.rstrip() == expected.source.rstrip()
    baseline = json.loads((ROOT / "curriculum/practice_baseline.json").read_text())
    assert baseline["lessons"]["python-51"]["target"] == 6
    for relative in [LEARNER, GUIDE, SOLUTION, REFERENCE]:
        path = ROOT / relative
        assert count_practice(path, solution=relative in [SOLUTION, REFERENCE]) >= 6
        assert "\u2014" not in path.read_text()
        if path.suffix == ".ipynb":
            notebook = read_notebook(path, as_version=4)
            nbformat.validate(notebook)
            assert len({cell.id for cell in notebook.cells}) == len(notebook.cells)
            assert notebook.metadata.kernelspec.name == "ds60sqlpy"
            for cell in notebook.cells:
                if cell.cell_type == "code":
                    assert cell.execution_count is None and cell.outputs == []
    for relative in [GUIDE, SOLUTION]:
        text = (ROOT / relative).read_text()
        assert "outer training partition" in text
        assert "inner CV loop" in text
        assert "not a drop-in scikit-learn transformer" in text.replace("\n", " ")


def test_heldout_examples_fit_smoothed_maps_using_training_labels_only() -> None:
    learner = read_notebook(ROOT / LEARNER, as_version=4)
    inference = next(
        cell.source
        for cell in learner.cells
        if cell.cell_type == "code" and "Xte_te = Xte.copy()" in cell.source
    )
    tree = ast.parse(inference)
    fit_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "fit_target_map"
    ]
    assert len(fit_calls) == 1
    assert ast.unparse(fit_calls[0].args[1]) == "ytr"
    assert any(
        keyword.arg == "smoothing"
        and isinstance(keyword.value, ast.Constant)
        and keyword.value.value == 10
        for keyword in fit_calls[0].keywords
    )
    reference_code = re.findall(r"```python\n(.*?)```", (ROOT / SOLUTION).read_text(), re.DOTALL)
    reference_tree = ast.parse("\n".join(reference_code))
    reference_fit = next(
        node
        for node in reference_tree.body
        if isinstance(node, ast.Assign)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Name)
        and node.value.func.id == "fit_target_map"
    )
    assert isinstance(reference_fit.value, ast.Call)
    assert ast.unparse(reference_fit.value.args[1]) == "train_df['y']"
