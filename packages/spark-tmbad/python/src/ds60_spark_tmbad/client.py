"""Thin Py4J frontend. All DataFrame execution stays in the JVM and native worker."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ._json import ContractError, dumps, loads
from .runtime import PreparedRuntime
from .spec import ModelSpec


def _session(frame: Any) -> Any:
    if getattr(frame, "isStreaming", False):
        raise ContractError("Spark/TMBad requires a finite batch DataFrame")
    if not hasattr(frame, "_jdf") or not hasattr(frame, "sparkSession"):
        raise ContractError(
            "Expected a classic PySpark DataFrame with a JVM handle; Spark Connect is unsupported"
        )
    session = frame.sparkSession
    if getattr(session, "_jvm", None) is None:
        raise ContractError("The DataFrame has no active classic Spark JVM gateway")
    return session


def _same_session(frame: Any, session: Any) -> None:
    candidate = _session(frame)
    if candidate.sparkContext is not session.sparkContext:
        raise ContractError("All input DataFrames must belong to the same Spark context")


def _bridge(session: Any) -> Any:
    if getattr(session, "_jvm", None) is None:
        raise ContractError("An active classic SparkSession is required")
    jvm = session._jvm
    name = "io.ds60.spark.tmbad.PythonBridge"
    try:
        loader = jvm.java.lang.Thread.currentThread().getContextClassLoader()
        jvm.java.lang.Class.forName(name, True, loader)
    except Exception as exc:
        raise RuntimeError(
            "The prepared Spark/TMBad JVM adapter is unavailable. Start Spark with "
            "the matching JAR in --jars or spark.jars before creating the session."
        ) from exc
    return jvm.io.ds60.spark.tmbad.PythonBridge


def _wrap(jdf: Any, session: Any) -> Any:
    # PySpark is optional until a JVM result needs wrapping. This imports no
    # numerical backend and introduces no Python function into an executor plan.
    from pyspark.sql import DataFrame

    return DataFrame(jdf, session)


def _options(value: Mapping[str, Any] | None) -> str:
    raw = dumps({} if value is None else value)
    parsed = loads(raw)
    if "allow_unconverged" in parsed and type(parsed["allow_unconverged"]) is not bool:
        raise ContractError("allow_unconverged must be an explicit boolean")
    return raw


class SparkTMBad:
    """Select an explicit native runtime and delegate operations to its JVM adapter."""

    def __init__(self, runtime: PreparedRuntime) -> None:
        if not isinstance(runtime, PreparedRuntime):
            raise ContractError("runtime must be a PreparedRuntime")
        self.runtime = runtime

    def describe(self, spark: Any, model_id: str) -> dict[str, Any]:
        """Return bound descriptor metadata, without executing a native Spark task."""
        expected = self.runtime.descriptor(model_id)
        response = loads(_bridge(spark).describe(self.runtime.to_json(), model_id))
        if response.get("artifact_identity") != self.runtime.identity(model_id):
            raise ContractError("JVM descriptor artifact identity does not match this runtime")
        if response.get("model") != expected:
            raise ContractError("JVM descriptor does not match the selected prepared model")
        return response["model"]

    def probe(self, spark: Any, model_id: str) -> dict[str, Any]:
        """Run the adapter's explicit bounded executor/native handshake."""
        self.runtime.descriptor(model_id)
        bridge = _bridge(spark)
        if not hasattr(spark, "_jsparkSession"):
            raise ContractError("The native probe requires a classic SparkSession")
        return loads(bridge.probe(spark._jsparkSession, self.runtime.to_json(), model_id))

    def fit_shared(
        self,
        frame: Any,
        spec: ModelSpec | Mapping[str, Any],
        *,
        options: Mapping[str, Any] | None = None,
    ) -> FittedModel:
        """Fit one parameter vector using all independent units in a DataFrame."""
        spec = self._spec(spec)
        session = _session(frame)
        result = _bridge(session).fitShared(
            frame._jdf, spec.to_json(), self.runtime.to_json(), _options(options)
        )
        return FittedModel(self.runtime, loads(result))

    def fit_groups(
        self,
        frame: Any,
        spec: ModelSpec | Mapping[str, Any],
        *,
        options: Mapping[str, Any] | None = None,
    ) -> GroupedModels:
        """Return a lazy model DataFrame; materialize it before repeated expensive actions."""
        spec = self._spec(spec)
        if not spec.to_dict()["group_columns"]:
            raise ContractError("fit_groups requires explicit group_columns")
        session = _session(frame)
        result = _bridge(session).fitGroups(
            frame._jdf, spec.to_json(), self.runtime.to_json(), _options(options)
        )
        return GroupedModels(self.runtime, _wrap(result, session))

    def from_group_models(self, models: Any) -> GroupedModels:
        """Wrap persisted grouped model rows; JVM validation occurs on execution."""
        _session(models)
        return GroupedModels(self.runtime, models)

    def _spec(self, spec: ModelSpec | Mapping[str, Any]) -> ModelSpec:
        result = spec if isinstance(spec, ModelSpec) else ModelSpec.from_dict(spec)
        result.validate_descriptor(self.runtime.descriptor(result.model_id))
        return result


class FittedModel:
    """A source-bound shared model, represented by data-only JSON."""

    def __init__(self, runtime: PreparedRuntime, model: Mapping[str, Any]) -> None:
        # Validation and persistence are implemented by the shared model contract.
        from .persistence import validate_model

        self.runtime = runtime
        self._json = dumps(validate_model(model, runtime))

    @property
    def model(self) -> dict[str, Any]:
        return loads(self._json)

    def to_json(self) -> str:
        return self._json

    @classmethod
    def from_json(cls, raw: str | bytes, *, runtime: PreparedRuntime) -> FittedModel:
        """Load the common Scala/Python JSON representation against a prepared runtime."""
        return cls(runtime, loads(raw))

    def save(self, path: Any, *, overwrite: bool = False) -> None:
        """Save JSON locally. Existing files are preserved unless explicitly replaced."""
        from .persistence import save_model

        save_model(path, self._json, overwrite=overwrite)

    @classmethod
    def load(cls, path: Any, *, runtime: PreparedRuntime) -> FittedModel:
        """Load only JSON against an explicitly supplied compatible runtime."""
        from ._json import read

        return cls(runtime, read(path))

    def predict(
        self,
        frame: Any,
        *,
        history: Any | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> Any:
        """Evaluate a declared prediction target, optionally conditioned on history."""
        options_json = self._prediction_options(options)
        session = _session(frame)
        bridge = _bridge(session)
        if history is None:
            result = bridge.predict(frame._jdf, self._json, self.runtime.to_json(), options_json)
        else:
            _same_session(history, session)
            result = bridge.predictConditional(
                history._jdf, frame._jdf, self._json, self.runtime.to_json(), options_json
            )
        return _wrap(result, session)

    def forecast(
        self,
        history: Any,
        future: Any,
        *,
        options: Mapping[str, Any] | None = None,
    ) -> Any:
        """Evaluate a declared forecast using separate history and future DataFrames."""
        options_json = self._prediction_options(options)
        session = _session(future)
        _same_session(history, session)
        result = _bridge(session).forecast(
            history._jdf, future._jdf, self._json, self.runtime.to_json(), options_json
        )
        return _wrap(result, session)

    def _prediction_options(self, options: Mapping[str, Any] | None) -> str:
        raw = _options(options)
        if not self.model["fit"]["converged"] and not loads(raw).get("allow_unconverged", False):
            raise ContractError(
                "Prediction requires a converged fit. allow_unconverged=true is an explicit "
                "diagnostic-only override; it does not validate failed estimation."
            )
        return raw


class GroupedModels:
    """Independent model rows kept in a Spark DataFrame, without driver collection."""

    def __init__(self, runtime: PreparedRuntime, models: Any) -> None:
        _session(models)
        self.runtime = runtime
        self.models = models

    def predict(
        self,
        frame: Any,
        *,
        history: Any | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> Any:
        session = _session(frame)
        _same_session(self.models, session)
        bridge = _bridge(session)
        if history is None:
            result = bridge.predictGroups(
                frame._jdf, self.models._jdf, self.runtime.to_json(), _options(options)
            )
        else:
            _same_session(history, session)
            result = bridge.predictConditionalGroups(
                history._jdf,
                frame._jdf,
                self.models._jdf,
                self.runtime.to_json(),
                _options(options),
            )
        return _wrap(result, session)

    def forecast(
        self,
        history: Any,
        future: Any,
        *,
        options: Mapping[str, Any] | None = None,
    ) -> Any:
        session = _session(future)
        _same_session(history, session)
        _same_session(self.models, session)
        result = _bridge(session).forecastGroups(
            history._jdf, future._jdf, self.models._jdf, self.runtime.to_json(), _options(options)
        )
        return _wrap(result, session)
