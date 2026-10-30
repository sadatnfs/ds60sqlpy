"""Declared parameters for truthful simulation, sensitivity and posterior-draw prediction."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ._json import ContractError, copy_object, dumps, loads, read
from ._targets import parameters as _parameters
from .runtime import PreparedRuntime, _fields, _integer, _names, _object, _sha, _text

FIELDS = {
    "schema_version",
    "kind",
    "package_version",
    "model_id",
    "model_digest",
    "artifact_identity",
    "parameter_names",
    "parameters",
    "parameter_set_id",
    "purpose",
    "layout",
    "provenance",
}


def validate_layout(value: Any, descriptor: Mapping[str, Any]) -> dict[str, Any]:
    layout = _object(value, "parameter-set layout")
    _fields(layout, {"id_columns", "group_columns", "order_columns"}, "parameter-set layout")
    for name in ("id_columns", "group_columns", "order_columns"):
        _names(layout[name], 64, name, nonempty=name == "id_columns")
    if descriptor["fit_kind"] == "unit" and not layout["group_columns"]:
        raise ContractError("Complete-unit parameter sets require explicit group_columns")
    if descriptor["ordered"] and not layout["order_columns"]:
        raise ContractError("Ordered parameter sets require explicit order_columns")
    return layout


def validate_provenance(value: Any, purpose: str) -> dict[str, Any]:
    provenance = _object(value, "parameter provenance")
    if purpose == "simulation_truth":
        _fields(
            provenance,
            {"kind", "generator_source_sha256", "seed"},
            "simulation provenance",
            {"fixture_sha256"},
        )
        _sha(provenance["generator_source_sha256"], "generator source digest")
        _integer(provenance["seed"], 0, 2**53 - 1, "simulation seed")
        if "fixture_sha256" in provenance:
            _sha(provenance["fixture_sha256"], "fixture digest")
    elif purpose == "posterior_draw":
        _fields(
            provenance,
            {"kind", "posterior_target_sha256", "sampler_receipt_sha256", "chain_id", "draw_index"},
            "posterior-draw provenance",
        )
        _sha(provenance["posterior_target_sha256"], "posterior target digest")
        _sha(provenance["sampler_receipt_sha256"], "sampler receipt digest")
        _text(provenance["chain_id"], 128, "chain ID")
        _integer(provenance["draw_index"], 0, 2**53 - 1, "draw index")
    elif purpose == "sensitivity":
        _fields(provenance, {"kind", "reference_sha256"}, "sensitivity provenance")
        _sha(provenance["reference_sha256"], "sensitivity reference digest")
    else:
        raise ContractError("Unknown declared-parameter purpose")
    if provenance["kind"] != purpose:
        raise ContractError("Parameter purpose and provenance kind must agree")
    return provenance


def validate_parameter_set(value: Mapping[str, Any], runtime: PreparedRuntime) -> dict[str, Any]:
    if not isinstance(runtime, PreparedRuntime):
        raise ContractError("Declared parameters require an explicit PreparedRuntime")
    obj = copy_object(value)
    _fields(obj, FIELDS, "parameter set")
    _integer(obj["schema_version"], 1, 1, "parameter-set schema")
    if (
        obj["kind"] != "spark-tmbad-parameter-set"
        or obj["package_version"] != runtime.manifest["package_version"]
    ):
        raise ContractError("Parameter-set kind/version differs from the selected runtime")
    descriptor = runtime.descriptor(obj["model_id"])
    if obj["model_digest"] != descriptor["digest"] or obj["artifact_identity"] != runtime.identity(
        obj["model_id"]
    ):
        raise ContractError("Parameter-set source/artifact identity differs")
    if obj["parameter_names"] != descriptor["parameter_names"]:
        raise ContractError("Parameter-set order differs from the prepared model")
    if not isinstance(obj["parameters"], list):
        raise ContractError("Saved parameter-set coordinates must be a JSON array")
    _parameters(obj["parameters"], descriptor)
    _text(obj["parameter_set_id"], 128, "parameter-set ID")
    validate_layout(obj["layout"], descriptor)
    _text(obj["purpose"], 32, "parameter purpose")
    validate_provenance(obj["provenance"], obj["purpose"])
    return obj


class PreparedParameters:
    """One source-bound parameter vector, without fitted-model or convergence claims.

    Provenance is structurally validated. A posterior_draw label does not certify
    that a sampler ran, converged or produced scientifically calibrated samples.
    """

    def __init__(self, runtime: PreparedRuntime, document: Mapping[str, Any]) -> None:
        self.runtime = runtime
        self._json = dumps(validate_parameter_set(document, runtime))

    @classmethod
    def from_parameters(
        cls,
        runtime: PreparedRuntime,
        model_id: str,
        parameters: Any,
        *,
        purpose: str,
        parameter_set_id: str,
        layout: Mapping[str, Any],
        provenance: Mapping[str, Any],
    ) -> PreparedParameters:
        if not isinstance(runtime, PreparedRuntime):
            raise ContractError("Declared parameters require an explicit PreparedRuntime")
        descriptor = runtime.descriptor(model_id)
        if not isinstance(layout, Mapping) or not isinstance(provenance, Mapping):
            raise ContractError("Layout and provenance must be JSON mappings")
        document = {
            "schema_version": 1,
            "kind": "spark-tmbad-parameter-set",
            "package_version": runtime.manifest["package_version"],
            "model_id": model_id,
            "model_digest": descriptor["digest"],
            "artifact_identity": runtime.identity(model_id),
            "parameter_names": descriptor["parameter_names"],
            "parameters": _parameters(parameters, descriptor),
            "parameter_set_id": parameter_set_id,
            "purpose": purpose,
            "layout": dict(layout),
            "provenance": dict(provenance),
        }
        return cls(runtime, document)

    @property
    def document(self) -> dict[str, Any]:
        return loads(self._json)

    def to_json(self) -> str:
        return self._json

    @classmethod
    def from_json(cls, raw: str | bytes, *, runtime: PreparedRuntime) -> PreparedParameters:
        return cls(runtime, loads(raw))

    @classmethod
    def load(cls, path: Any, *, runtime: PreparedRuntime) -> PreparedParameters:
        return cls(runtime, read(path))

    def save(self, path: Any, *, overwrite: bool = False) -> None:
        from .persistence import save_model

        save_model(path, self._json, overwrite=overwrite)

    def _options(self, options: Mapping[str, Any] | None) -> str:
        from .client import _options

        raw = _options(options)
        if "allow_unconverged" in loads(raw):
            raise ContractError("allow_unconverged is not a declared-parameter option")
        return raw

    def predict(
        self, frame: Any, *, history: Any | None = None, options: Mapping[str, Any] | None = None
    ) -> Any:
        from .client import _bridge, _same_session, _session, _wrap

        raw = self._options(options)
        session = _session(frame)
        method = "predictAtParameters" if history is None else "predictConditionalAtParameters"
        bridge = _bridge(session, required_method=method)
        if history is None:
            result = bridge.predictAtParameters(frame._jdf, self._json, self.runtime.to_json(), raw)
        else:
            _same_session(history, session)
            result = bridge.predictConditionalAtParameters(
                history._jdf, frame._jdf, self._json, self.runtime.to_json(), raw
            )
        return _wrap(result, session)

    def forecast(
        self, history: Any, future: Any, *, options: Mapping[str, Any] | None = None
    ) -> Any:
        from .client import _bridge, _same_session, _session, _wrap

        raw = self._options(options)
        session = _session(future)
        _same_session(history, session)
        result = _bridge(session, required_method="forecastAtParameters").forecastAtParameters(
            history._jdf, future._jdf, self._json, self.runtime.to_json(), raw
        )
        return _wrap(result, session)
