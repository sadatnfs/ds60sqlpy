"""Lightweight model identity and declared prediction contracts."""

import pytest
from ds60_spark_likelihood import (
    ObjectiveError,
    PredictionTarget,
    RegisteredModel,
    describe_model,
    resolve_model,
)
from ds60_spark_likelihood.models import normal_mean
from ds60_spark_likelihood.registered_models import normal_prediction


def test_descriptors_distinguish_row_group_and_prediction_targets():
    normal = describe_model("normal_mean")
    group = describe_model("gaussian_random_intercept")
    assert normal["factorization"] == "independent_rows" and normal["feature_count"] == 0
    assert group["factorization"] == "complete_groups" and group["max_unit_rows"] == 256
    assert group["default_prediction"] == "new_group_mean"
    assert group["parameter_names"] == ["beta", "log_sigma", "log_tau"]
    assert normal["fingerprint"] != group["fingerprint"]


def test_configuration_and_shapes_are_in_identity():
    a = resolve_model("linear_gaussian", {"feature_count": 2})
    b = resolve_model("linear_gaussian", {"feature_count": 3})
    assert a.parameter_names == ("beta_0", "beta_1", "log_sigma")
    assert a.fingerprint != b.fingerprint
    config = a.configuration
    config["feature_count"] = 99
    assert a.configuration == {"feature_count": 2}
    with pytest.raises(ObjectiveError):
        resolve_model("normal_mean", {"arbitrary_code": "execute()"})
    with pytest.raises(ObjectiveError):
        resolve_model("unknown")


def test_invalid_metadata_and_undeclared_defaults_are_rejected():
    with pytest.raises(ObjectiveError):
        RegisteredModel(normal_mean(), "ab", ())
    with pytest.raises(ObjectiveError):
        RegisteredModel(normal_mean(), ("mu", "mu"), ())
    with pytest.raises(ObjectiveError):
        RegisteredModel(normal_mean(), ("mu", "log_sigma"), (), default_prediction="invented")
    with pytest.raises(ObjectiveError):
        RegisteredModel(normal_mean(), ("mu", "log_sigma"), (), requires_order=True)
    with pytest.raises(ObjectiveError):
        PredictionTarget("unsafe target", normal_prediction)


def test_raw_model_can_remain_nonpredictive():
    model = RegisteredModel(normal_mean(), ("mu", "log_sigma"), ())
    assert model.descriptor()["prediction_targets"] == []
    assert model.default_prediction is None


def test_original_custom_factory_is_explicit_and_configuration_bound():
    from ds60_spark_likelihood import register_model_factory
    from ds60_spark_likelihood.example_models import quadratic_model

    register_model_factory("quadratic_mean", quadratic_model, replace_existing=True)
    first = resolve_model("quadratic_mean", {"sigma": 0.5})
    second = resolve_model("quadratic_mean", {"sigma": 2.0})
    assert first.parameter_names == ("intercept", "curvature")
    assert first.fingerprint != second.fingerprint
    for value in (0, -1, True):
        with pytest.raises(ObjectiveError):
            resolve_model("quadratic_mean", {"sigma": value})


def test_non_gaussian_unit_model_uses_normal_custom_registration():
    from ds60_spark_likelihood import register_model_factory
    from ds60_spark_likelihood.example_gamma_poisson import gamma_poisson_model

    register_model_factory("gamma_poisson_shared_rate", gamma_poisson_model, replace_existing=True)
    model = resolve_model("gamma_poisson_shared_rate")
    assert model.factorization == "complete_groups"
    assert model.parameter_names == ("log_alpha", "log_beta")
    assert model.feature_names == ("exposure",)
    assert model.default_prediction == "new_group_expected_count"
    assert model.requires_order is False
    with pytest.raises(ObjectiveError):
        resolve_model("gamma_poisson_shared_rate", {"scale_instead_of_rate": 2})


IDENTITY_SCALE = 1.0


def identity_fixture(theta, features, targets, scale=1.0, *, offset=0.0):
    return scale * IDENTITY_SCALE * (targets - theta[0]).square() + offset


IDENTITY_LAMBDA = lambda theta, features, targets: targets - theta[0]  # noqa: E731 - regression


def test_named_identity_binds_defaults_keyword_defaults_and_constants(monkeypatch):
    import sys

    from ds60_spark_likelihood.registry import _callable_identity

    first = _callable_identity(identity_fixture)
    monkeypatch.setattr(identity_fixture, "__defaults__", (2.0,))
    second = _callable_identity(identity_fixture)
    assert first != second
    monkeypatch.setattr(identity_fixture, "__kwdefaults__", {"offset": 3.0})
    third = _callable_identity(identity_fixture)
    assert third != second
    monkeypatch.setattr(sys.modules[__name__], "IDENTITY_SCALE", 4.0)
    assert _callable_identity(identity_fixture) != third


def test_ambiguous_and_detached_registered_functions_are_refused(monkeypatch):
    import sys

    from ds60_spark_likelihood.registry import _callable_identity

    with pytest.raises(ObjectiveError, match="importable"):
        _callable_identity(IDENTITY_LAMBDA)
    detached = identity_fixture
    monkeypatch.setattr(sys.modules[__name__], "identity_fixture", lambda: None)
    with pytest.raises(ObjectiveError, match="named module symbol"):
        _callable_identity(detached)


def test_non_json_callable_defaults_are_refused(monkeypatch):
    from ds60_spark_likelihood.registry import _callable_identity

    monkeypatch.setattr(identity_fixture, "__defaults__", (object(),))
    with pytest.raises(ObjectiveError, match="JSON"):
        _callable_identity(identity_fixture)


def alternate_identity_fixture(theta, features, targets, scale=1.0, *, offset=0.0):
    return scale * IDENTITY_SCALE * (targets - theta[0] - 2).square() + offset


def test_live_code_mutation_changes_identity_but_relocation_does_not(monkeypatch):
    from ds60_spark_likelihood.registry import _callable_identity

    first = _callable_identity(identity_fixture)
    relocated = identity_fixture.__code__.replace(
        co_filename="/another/deployment/model.py", co_firstlineno=888
    )
    monkeypatch.setattr(identity_fixture, "__code__", relocated)
    assert _callable_identity(identity_fixture) == first
    monkeypatch.setattr(identity_fixture, "__code__", alternate_identity_fixture.__code__)
    assert _callable_identity(identity_fixture) != first
