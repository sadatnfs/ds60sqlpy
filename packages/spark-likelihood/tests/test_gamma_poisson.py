"""Native regression for cancellation that otherwise reports false stationarity."""

import pytest
from ds60_spark_likelihood import CompleteUnit, ObjectiveError
from ds60_spark_likelihood.unit_backend import evaluate_units
from ds60_spark_likelihood.validation_gamma_poisson import poisson_limit_checks, resolved


def test_large_shape_zero_and_nonzero_count_poisson_limits():
    pytest.importorskip("torch")
    assert poisson_limit_checks() < 1e-9


def test_reference_precision_and_recurrence_boundaries_fail_closed():
    pytest.importorskip("torch")
    model = resolved()
    with pytest.raises(ObjectiveError, match="total group count"):
        evaluate_units(0, [CompleteUnit("too-many", [(1.0, 10001.0)])], (0.0, 0.0), model.loss)
    with pytest.raises(ObjectiveError, match="log parameters"):
        evaluate_units(0, [CompleteUnit("extreme", [(1.0, 0.0)])], (301.0, 0.0), model.loss)
