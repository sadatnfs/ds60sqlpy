"""Independent numerical and evidence-contract checks for optional Spark MLE."""

from __future__ import annotations

import math
import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest
from ds60_spark_likelihood import (
    ObjectiveError,
    PartitionSummary,
    combine_summaries,
    finite_vector,
    parameter_digest,
)
from ds60_spark_likelihood.contracts import CompensatedSum
from ds60_spark_likelihood.torch_backend import TorchLoss


def summary(
    partition: int,
    count: int,
    weight: float,
    value: float,
    gradient: tuple[float, ...],
    theta: tuple[float, ...] = (0.0,),
) -> PartitionSummary:
    return PartitionSummary(
        partition, parameter_digest(theta), "bernoulli", count, weight, value, gradient
    )


def test_unequal_weighted_partitions_match_one_global_bernoulli_likelihood() -> None:
    # y=[0,1,1], weights=[1,3,2], theta=0 gives p=0.5. Counts differ from weights.
    records = [summary(0, 1, 1, math.log(2), (0.5,)), summary(1, 2, 5, 5 * math.log(2), (-2.5,))]
    total = combine_summaries(
        records, parameters=(0,), model_id="bernoulli", expected_partitions=2, expected_rows=3
    )
    mean = combine_summaries(
        records,
        parameters=(0,),
        model_id="bernoulli",
        expected_partitions=2,
        expected_rows=3,
        reduction="weighted_mean",
    )
    assert total.value == pytest.approx(6 * math.log(2))
    assert total.gradient == pytest.approx((-2.0,))
    assert mean.value == pytest.approx(math.log(2))
    assert mean.gradient == pytest.approx((-1 / 3,))
    wrong_unweighted_partition_gradient = (0.5 / 1 + -2.5 / 5) / 2
    assert not math.isclose(mean.gradient[0], wrong_unweighted_partition_gradient)
    assert mean.row_count == 3 and mean.weight_sum == 6


def test_penalty_is_added_once_after_global_reduction() -> None:
    records = [summary(0, 1, 1, 2, (3,), (2,)), summary(1, 1, 1, 4, (5,), (2,))]
    result = combine_summaries(
        records,
        parameters=(2,),
        model_id="bernoulli",
        expected_partitions=2,
        expected_rows=2,
        reduction="weighted_mean",
        l2_strength=3,
    )
    assert result.penalty_value == 6  # lambda/2 * theta^2
    assert result.value == 9  # mean data NLL 3, one penalty 6
    assert result.gradient == (10,)  # mean data gradient 4, one penalty gradient 6


def test_empty_partition_is_required_and_does_not_change_sum() -> None:
    records = [summary(0, 1, 1, 2, (1,)), summary(1, 0, 0, 0, (0,))]
    result = combine_summaries(
        reversed(records),
        parameters=(0,),
        model_id="bernoulli",
        expected_partitions=2,
        expected_rows=1,
    )
    assert result.value == 2 and result.gradient == (1,)
    assert result.partition_count == 2


def test_ordered_fsum_retains_small_term_between_large_opposite_summands() -> None:
    records = [summary(i, 1, 1, x, (x,)) for i, x in enumerate((1e16, 1.0, -1e16))]
    result = combine_summaries(
        records, parameters=(0,), model_id="bernoulli", expected_partitions=3, expected_rows=3
    )
    assert result.value == 1 and result.gradient == (1,)
    accumulation = CompensatedSum()
    for value in (1e16, 1.0, -1e16):
        accumulation.add(value)
    assert accumulation.value() == 1


@pytest.mark.parametrize("bad", [True, float("nan"), float("inf"), "2"])
def test_parameter_values_are_not_coerced_or_nonfinite(bad: object) -> None:
    with pytest.raises(ObjectiveError):
        finite_vector([bad])  # type: ignore[list-item]


def test_zero_penalty_does_not_square_irrelevant_large_parameter() -> None:
    theta = (1e200,)
    result = combine_summaries(
        [summary(0, 1, 1, 1, (0,), theta)],
        parameters=theta,
        model_id="bernoulli",
        expected_partitions=1,
        expected_rows=1,
    )
    assert result.value == 1 and result.penalty_value == 0


@pytest.mark.parametrize("fault", ["duplicate", "missing", "rows", "stale", "model", "dimension"])
def test_summary_evidence_cannot_mix_or_drop_work(fault: str) -> None:
    a = summary(0, 1, 1, 2, (1,))
    b = summary(1, 1, 1, 2, (1,))
    records = [a, b]
    if fault == "duplicate":
        records = [a, a]
    if fault == "missing":
        records = [a]
    if fault == "rows":
        records = [replace(a, row_count=2), b]
    if fault == "stale":
        records = [replace(a, parameter_digest=parameter_digest((1,))), b]
    if fault == "model":
        records = [replace(a, model_id="other"), b]
    if fault == "dimension":
        records = [replace(a, gradient=(1, 2)), b]
    with pytest.raises(ObjectiveError):
        combine_summaries(
            records, parameters=(0,), model_id="bernoulli", expected_partitions=2, expected_rows=2
        )


def test_zero_total_weight_cannot_define_fit() -> None:
    with pytest.raises(ObjectiveError, match="positive finite total weight"):
        combine_summaries(
            [summary(0, 3, 0, 0, (0,))],
            parameters=(0,),
            model_id="bernoulli",
            expected_partitions=1,
            expected_rows=3,
        )


@pytest.mark.parametrize("bad", [True, -1, 0, 4097])
def test_invalid_partition_contract_is_rejected(bad: int) -> None:
    with pytest.raises(ObjectiveError):
        combine_summaries(
            [], parameters=(0,), model_id="bernoulli", expected_partitions=bad, expected_rows=1
        )


def test_summary_fails_on_nonzero_empty_or_negative_weights() -> None:
    with pytest.raises(ObjectiveError):
        summary(0, 0, 1, 2, (3,))
    with pytest.raises(ObjectiveError):
        summary(0, 1, -1, 2, (3,))
    with pytest.raises(ObjectiveError):
        summary(0, 1, 0, 2, (0,))


def test_package_import_does_not_require_optional_numerical_backends() -> None:
    code = (
        "import sys; import ds60_spark_likelihood; "
        "assert 'torch' not in sys.modules; assert 'pyspark' not in sys.modules"
    )
    subprocess.run(
        [sys.executable, "-c", code],
        env={
            **os.environ,
            "PYTHONPATH": str(
                Path(__file__).resolve().parents[1] / "packages/spark-likelihood/src"
            ),
        },
        check=True,
        timeout=15,
    )


def test_model_shape_contract_is_explicit_without_importing_torch() -> None:
    with pytest.raises(ObjectiveError):
        TorchLoss("invalid name", 2, 1, lambda a, b, c: a)
    with pytest.raises(ObjectiveError):
        TorchLoss("valid", 0, 1, lambda a, b, c: a)
    assert TorchLoss("featureless", 2, 0, lambda a, b, c: a).feature_count == 0
