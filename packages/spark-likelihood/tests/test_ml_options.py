"""ML option precision checks when the optional PySpark dependency is prepared."""

import pytest

pytest.importorskip("pyspark")
from ds60_spark_likelihood.ml import SparkLikelihoodEstimator  # noqa: E402


@pytest.mark.parametrize("option", ["tol", "l2Strength"])
@pytest.mark.parametrize("bad", [2**53 + 1, True, float("inf"), float("nan"), "1"])
def test_ml_options_reject_precision_loss_and_nonfinite_coercions(option, bad):
    with pytest.raises((TypeError, ValueError)):
        SparkLikelihoodEstimator(**{option: bad})


def test_ml_options_keep_exact_large_integer_and_explicit_float():
    estimator = SparkLikelihoodEstimator(tol=2**54, l2Strength=1.5)
    assert estimator.getOrDefault("tol") == float(2**54)
    assert estimator.getOrDefault("l2Strength") == 1.5
