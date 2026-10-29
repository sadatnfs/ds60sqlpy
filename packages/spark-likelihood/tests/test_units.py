"""Complete-unit validation and independent group semantics."""

import pytest
from ds60_spark_likelihood import CompleteUnit, ObjectiveError, resolve_model
from ds60_spark_likelihood.torch_backend import evaluate_partition
from ds60_spark_likelihood.unit_backend import summarize_units, unit_digest, validate_unit


def test_unit_weight_and_order_are_bound_without_conflating_rows():
    a = CompleteUnit("group-a", [(1.0,), (2.0,)], 2)
    b = CompleteUnit("group-a", [(2.0,), (1.0,)], 2)
    c = CompleteUnit("group-a", [(1.0,), (2.0,)], 1)
    assert len({unit_digest(a), unit_digest(b), unit_digest(c)}) == 3
    model = resolve_model("gaussian_random_intercept").loss
    result = summarize_units(0, [a, CompleteUnit("group-b", [(3.0,)], 0.5)], model)
    assert result[1:3] == (2, 3)
    assert a.weight == 2 and a.rows == ((1.0,), (2.0,))


def test_joint_units_cannot_be_row_batched_or_have_per_row_weights():
    model = resolve_model("gaussian_random_intercept", {"max_unit_rows": 2}).loss
    with pytest.raises(ObjectiveError, match="row-batched"):
        validate_unit(CompleteUnit("a", [(1.0,), (2.0,), (3.0,)]), model)
    with pytest.raises(ObjectiveError, match="no row weight"):
        validate_unit(CompleteUnit("a", [(1.0, 1.0)]), model)
    with pytest.raises(ObjectiveError, match="row evaluation"):
        evaluate_partition(0, [(1.0, 1.0)], [0.0, 0.0, 0.0], model)


@pytest.mark.parametrize(
    "rows,weight", [([], 1), ([(True,)], 1), ([(1.0,)], -1), ([(2**53 + 1,)], 1)]
)
def test_invalid_complete_units_fail_before_torch(rows, weight):
    with pytest.raises(ObjectiveError):
        CompleteUnit("a", rows, weight)
