"""Opt-in native acceptance; the default host skip is not a runtime pass."""

import os

import pytest

if os.environ.get("DS60_SPARK_LIKELIHOOD_NATIVE") != "1":
    pytest.skip("Prepared native Spark/Torch environment required", allow_module_level=True)


def test_installed_native_dataframe_ml():
    from ds60_spark_likelihood.validation_dataframe_ml import main

    assert main()["passed"] is True
