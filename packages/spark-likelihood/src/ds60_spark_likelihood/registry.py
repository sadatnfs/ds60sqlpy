"""Explicit trusted model factories and JSON-only source/config identities."""

from __future__ import annotations

import functools
import hashlib
import inspect
import json
import re
import sys
import types
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, cast

from ._version import __version__
from .contracts import MODEL_ID, ObjectiveError
from .torch_backend import TorchLoss
from .unit_backend import TorchUnitLoss

NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,63}\Z")
MAX_CONFIGURATION_BYTES = 16_384


def configuration_json(configuration: Mapping[str, Any] | None) -> str:
    def validate(value: Any, depth: int = 0) -> None:
        if depth > 8:
            raise ObjectiveError("model configuration nesting exceeds the bounded contract")
        if isinstance(value, dict):
            if len(value) > 256 or not all(isinstance(key, str) for key in value):
                raise ObjectiveError("model configuration needs bounded string-key mappings")
            for item in value.values():
                validate(item, depth + 1)
        elif isinstance(value, (list, tuple)):
            if len(value) > 256:
                raise ObjectiveError("model configuration arrays are too large")
            for item in value:
                validate(item, depth + 1)
        elif value is not None and not isinstance(value, (str, bool, int, float)):
            raise ObjectiveError("model configuration must be JSON data, not executable objects")

    if configuration is None:
        configuration = {}
    if not isinstance(configuration, Mapping):
        raise ObjectiveError("model configuration must be a mapping")
    value = dict(configuration)
    validate(value)
    try:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ObjectiveError("model configuration must contain finite JSON values") from exc
    if len(encoded.encode("utf-8")) > MAX_CONFIGURATION_BYTES:
        raise ObjectiveError("model configuration exceeds 16 KiB")
    return encoded


def _code_identity(code: types.CodeType) -> dict[str, Any]:
    """Bind live executable structure while permitting source-path relocation."""
    budget = [4096]

    def encode(value: Any, depth: int = 0) -> Any:
        budget[0] -= 1
        if budget[0] < 0 or depth > 16:
            raise ObjectiveError("model code structure exceeds its identity bound")
        if isinstance(value, types.CodeType):
            return {
                "bytecode": value.co_code.hex(),
                "exception_table": getattr(value, "co_exceptiontable", b"").hex(),
                "constants": [encode(item, depth + 1) for item in value.co_consts],
                "names": value.co_names,
                "variables": value.co_varnames,
                "free_variables": value.co_freevars,
                "cell_variables": value.co_cellvars,
                "arguments": [
                    value.co_argcount,
                    value.co_posonlyargcount,
                    value.co_kwonlyargcount,
                    value.co_nlocals,
                ],
                "flags": value.co_flags,
                "stack_size": value.co_stacksize,
            }
        if value is Ellipsis:
            return ["ellipsis"]
        if isinstance(value, bytes):
            return ["bytes", value.hex()]
        if isinstance(value, tuple):
            return ["tuple", [encode(item, depth + 1) for item in value]]
        if isinstance(value, frozenset):
            items = [encode(item, depth + 1) for item in value]
            return ["frozenset", sorted(items, key=lambda item: json.dumps(item, sort_keys=True))]
        if isinstance(value, complex):
            return ["complex", value.real, value.imag]
        if value is None or isinstance(value, (str, bool, int, float)):
            return [type(value).__name__, value]
        raise ObjectiveError("model code contains an unsupported constant type")

    try:
        payload = json.dumps(encode(code), sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (ValueError, TypeError, OverflowError) as error:
        raise ObjectiveError("model code constants need a bounded finite representation") from error
    if len(payload.encode()) > 262_144:
        raise ObjectiveError("model code identity exceeds 256 KiB")
    return {
        "python_minor": list(sys.version_info[:2]),
        "sha256": hashlib.sha256(payload.encode()).hexdigest(),
    }


def _callable_identity(function: Any) -> dict[str, Any]:
    if isinstance(function, functools.partial):
        return {
            "function": _callable_identity(function.func),
            "partial": json.loads(
                configuration_json({"args": function.args, "keywords": function.keywords or {}})
            ),
        }
    if (
        not inspect.isfunction(function)
        or function.__module__ == "__main__"
        or "<" in function.__qualname__
        or function.__closure__ is not None
    ):
        raise ObjectiveError(
            "registered models need functions in an importable module; "
            "use raw TorchLoss for ephemeral callables"
        )
    module = inspect.getmodule(function)
    if module is None:
        raise ObjectiveError("model function module cannot be identified")
    resolved: Any = module
    for part in function.__qualname__.split("."):
        resolved = getattr(resolved, part, None)
    if resolved is not function:
        raise ObjectiveError("model function must resolve to its declared named module symbol")
    state: dict[str, Any] = {
        "defaults": function.__defaults__,
        "keyword_defaults": function.__kwdefaults__,
        "referenced_constants": {},
    }
    for name in function.__code__.co_names:
        if name not in function.__globals__:
            continue
        value = function.__globals__[name]
        if value is None or isinstance(value, (str, bool, int, float, list, tuple, dict)):
            state["referenced_constants"][name] = value
        elif not (
            inspect.ismodule(value)
            or inspect.isfunction(value)
            or inspect.isclass(value)
            or inspect.isbuiltin(value)
        ):
            raise ObjectiveError("model function has unsupported hidden global state: " + name)
    bound_state = json.loads(configuration_json(state))
    filename = getattr(module, "__file__", None)
    source = None
    if filename and Path(filename).is_file():
        source = Path(filename).read_bytes()
    else:
        loader = getattr(module, "__loader__", None)
        if loader is not None and hasattr(loader, "get_source"):
            text = loader.get_source(module.__name__)
            if text is not None:
                source = text.encode("utf-8")
    if source is None:
        raise ObjectiveError("model source is unavailable; prepare an importable source module")
    return {
        "module": function.__module__,
        "name": function.__qualname__,
        "bound_state": bound_state,
        "live_code": _code_identity(function.__code__),
        "module_source_sha256": hashlib.sha256(source).hexdigest(),
    }


@dataclass(frozen=True)
class PredictionTarget:
    name: str
    function: Callable[[Any, Any], Any]

    def __post_init__(self) -> None:
        if (
            not isinstance(self.name, str)
            or not NAME.fullmatch(self.name)
            or not callable(self.function)
        ):
            raise ObjectiveError("prediction targets need a stable name and label-free callable")


@dataclass(frozen=True)
class RegisteredModel:
    loss: TorchLoss | TorchUnitLoss
    parameter_names: tuple[str, ...]
    feature_names: tuple[str, ...]
    version: str = "1"
    prediction_targets: tuple[PredictionTarget, ...] = ()
    default_prediction: str | None = None
    requires_order: bool = False
    configuration_json: str = "{}"
    factory_identity_json: str = "null"

    def __post_init__(self) -> None:
        if not isinstance(self.loss, (TorchLoss, TorchUnitLoss)):
            raise ObjectiveError("registered model needs a row or complete-unit Torch loss")
        for values, count in (
            (self.parameter_names, self.loss.parameter_count),
            (self.feature_names, self.loss.feature_count),
        ):
            if (
                isinstance(values, (str, bytes))
                or not isinstance(values, (list, tuple))
                or len(values) != count
                or not all(isinstance(name, str) and NAME.fullmatch(name) for name in values)
                or len(set(values)) != len(values)
            ):
                raise ObjectiveError("canonical parameter/feature names must match the model shape")
        if not isinstance(self.version, str) or not 1 <= len(self.version) <= 64:
            raise ObjectiveError("declare a bounded model version")
        if not isinstance(self.prediction_targets, (list, tuple)) or not all(
            isinstance(target, PredictionTarget) for target in self.prediction_targets
        ):
            raise ObjectiveError(
                "prediction_targets must contain explicit PredictionTarget objects"
            )
        names = [target.name for target in self.prediction_targets]
        if len(set(names)) != len(names) or len(names) > 16:
            raise ObjectiveError("prediction target names must be unique and bounded")
        if self.default_prediction is not None and self.default_prediction not in names:
            raise ObjectiveError("default prediction must name an explicitly registered target")
        if type(self.requires_order) is not bool or (
            self.requires_order and isinstance(self.loss, TorchLoss)
        ):
            raise ObjectiveError("ordering is an explicit complete-unit model contract")
        try:
            normalized_configuration = configuration_json(json.loads(self.configuration_json))
            json.loads(self.factory_identity_json)
        except (ValueError, TypeError) as exc:
            raise ObjectiveError(
                "model identity must use valid bounded JSON configuration"
            ) from exc
        object.__setattr__(self, "configuration_json", normalized_configuration)
        object.__setattr__(self, "parameter_names", tuple(self.parameter_names))
        object.__setattr__(self, "feature_names", tuple(self.feature_names))
        object.__setattr__(self, "prediction_targets", tuple(self.prediction_targets))

    @property
    def model_id(self) -> str:
        return self.loss.model_id

    @property
    def parameter_count(self) -> int:
        return self.loss.parameter_count

    @property
    def feature_count(self) -> int:
        return self.loss.feature_count

    @property
    def factorization(self) -> str:
        return "complete_groups" if isinstance(self.loss, TorchUnitLoss) else "independent_rows"

    @property
    def configuration(self) -> dict[str, Any]:
        return cast(dict[str, Any], json.loads(self.configuration_json))

    @property
    def fingerprint(self) -> str:
        return cast(str, self.descriptor()["fingerprint"])

    def descriptor(self) -> dict[str, Any]:
        loss_function = (
            self.loss.per_unit
            if isinstance(self.loss, TorchUnitLoss)
            else self.loss.per_observation
        )
        result = {
            "schema_version": 1,
            "package_version": __version__,
            "model_id": self.model_id,
            "model_version": self.version,
            "backend": "torch-cpu-float64",
            "factorization": self.factorization,
            "parameter_names": list(self.parameter_names),
            "feature_names": list(self.feature_names),
            "parameter_count": self.parameter_count,
            "feature_count": self.feature_count,
            "requires_order": self.requires_order,
            "max_unit_rows": self.loss.max_unit_rows
            if isinstance(self.loss, TorchUnitLoss)
            else None,
            "configuration": self.configuration,
            "prediction_targets": [target.name for target in self.prediction_targets],
            "default_prediction": self.default_prediction,
            "sources": {
                "factory": json.loads(self.factory_identity_json),
                "loss": _callable_identity(loss_function),
                "prediction": {
                    target.name: _callable_identity(target.function)
                    for target in self.prediction_targets
                },
            },
        }
        encoded = json.dumps(
            result, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
        return {**result, "fingerprint": hashlib.sha256(encoded).hexdigest()}


_FACTORIES: dict[str, Callable[[dict[str, Any]], RegisteredModel]] = {}


def register_model_factory(
    model_id: str,
    factory: Callable[[dict[str, Any]], RegisteredModel],
    *,
    replace_existing: bool = False,
) -> None:
    """Register trusted application code explicitly, never code named by an artifact."""
    if not isinstance(model_id, str) or not MODEL_ID.fullmatch(model_id) or not callable(factory):
        raise ObjectiveError("model registration needs a stable ID and callable factory")
    if type(replace_existing) is not bool:
        raise ObjectiveError("replace_existing must be boolean")
    if model_id in _FACTORIES and not replace_existing:
        raise ObjectiveError("model ID is already registered")
    _callable_identity(factory)
    _FACTORIES[model_id] = factory


def resolve_model(model_id: str, configuration: Mapping[str, Any] | None = None) -> RegisteredModel:
    if not isinstance(model_id, str) or model_id not in _FACTORIES:
        raise ObjectiveError("unknown model ID; register its trusted source before loading")
    encoded = configuration_json(configuration)
    factory = _FACTORIES[model_id]
    model = factory(json.loads(encoded))
    if not isinstance(model, RegisteredModel) or model.model_id != model_id:
        raise ObjectiveError("factory returned a different or invalid model contract")
    return replace(
        model,
        configuration_json=encoded,
        factory_identity_json=json.dumps(_callable_identity(factory), sort_keys=True),
    )


def describe_model(
    model_or_id: RegisteredModel | str, configuration: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    model = (
        model_or_id
        if isinstance(model_or_id, RegisteredModel)
        else resolve_model(model_or_id, configuration)
    )
    if isinstance(model_or_id, RegisteredModel) and configuration is not None:
        raise ObjectiveError("an already resolved model owns its configuration")
    return model.descriptor()


def _configuration(config: Mapping[str, Any], allowed: Sequence[str]) -> None:
    if set(config) - set(allowed):
        raise ObjectiveError("unsupported model configuration fields")


def _names(count: int) -> tuple[str, ...]:
    return tuple(f"x{i}" for i in range(count))


def _normal(config: dict[str, Any]) -> RegisteredModel:
    from .models import normal_mean
    from .registered_models import normal_prediction

    _configuration(config, ())
    return RegisteredModel(
        normal_mean(),
        ("mu", "log_sigma"),
        (),
        prediction_targets=(PredictionTarget("conditional_mean", normal_prediction),),
        default_prediction="conditional_mean",
    )


def _logistic(config: dict[str, Any]) -> RegisteredModel:
    from .models import logistic
    from .registered_models import logistic_prediction

    _configuration(config, ("feature_count",))
    count = config.get("feature_count", 1)
    loss = logistic(count)
    return RegisteredModel(
        loss,
        tuple(f"beta_{i}" for i in range(count)),
        _names(count),
        prediction_targets=(PredictionTarget("success_probability", logistic_prediction),),
        default_prediction="success_probability",
    )


def _linear(config: dict[str, Any]) -> RegisteredModel:
    from .registered_models import linear_gaussian, linear_prediction

    _configuration(config, ("feature_count",))
    count = config.get("feature_count", 1)
    loss = linear_gaussian(count)
    return RegisteredModel(
        loss,
        tuple(f"beta_{i}" for i in range(count)) + ("log_sigma",),
        _names(count),
        prediction_targets=(PredictionTarget("conditional_mean", linear_prediction),),
        default_prediction="conditional_mean",
    )


def _nonlinear(config: dict[str, Any]) -> RegisteredModel:
    from .models import nonlinear_gaussian
    from .registered_models import nonlinear_prediction

    _configuration(config, ())
    return RegisteredModel(
        nonlinear_gaussian(),
        ("amplitude", "log_rate", "offset", "log_sigma"),
        ("time",),
        prediction_targets=(PredictionTarget("conditional_mean", nonlinear_prediction),),
        default_prediction="conditional_mean",
    )


def _poisson(config: dict[str, Any]) -> RegisteredModel:
    from .models import poisson_exposure
    from .registered_models import poisson_prediction

    _configuration(config, ("design_columns",))
    count = config.get("design_columns", 1)
    loss = poisson_exposure(count)
    return RegisteredModel(
        loss,
        tuple(f"beta_{i}" for i in range(count)),
        _names(count) + ("exposure",),
        prediction_targets=(PredictionTarget("expected_count", poisson_prediction),),
        default_prediction="expected_count",
    )


def _group(config: dict[str, Any]) -> RegisteredModel:
    from .registered_models import gaussian_random_intercept, normal_prediction

    _configuration(config, ("max_unit_rows",))
    loss = gaussian_random_intercept(config.get("max_unit_rows", 256))
    return RegisteredModel(
        loss,
        ("beta", "log_sigma", "log_tau"),
        (),
        prediction_targets=(PredictionTarget("new_group_mean", normal_prediction),),
        default_prediction="new_group_mean",
    )


for _identifier, _factory in {
    "normal_mean": _normal,
    "logistic": _logistic,
    "linear_gaussian": _linear,
    "nonlinear_gaussian": _nonlinear,
    "poisson_exposure": _poisson,
    "gaussian_random_intercept": _group,
}.items():
    register_model_factory(_identifier, _factory)
