"""Explicit prepared-artifact selection, with no runtime downloads or compilation."""

from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ._json import ContractError, copy_object, dumps, loads, read
from .spec import column_list

_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def _sha(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise ContractError(f"{field} must be a lowercase SHA-256 digest")
    return value


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{field} must be an object")
    return value


def _fields(
    value: dict[str, Any], required: set[str], field: str, optional: set[str] | None = None
) -> None:
    if required - value.keys() or set(value) - required - (optional or set()):
        raise ContractError(f"{field} fields differ from the supported contract")


def _integer(value: Any, minimum: int, maximum: int, field: str) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ContractError(f"{field} must be an integer in {minimum}..{maximum}")
    return value


def _text(value: Any, maximum: int, field: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= maximum:
        raise ContractError(f"{field} must be a nonempty bounded string")
    return value


def _names(value: Any, maximum: int, field: str, *, nonempty: bool = False) -> list[str]:
    names = column_list(value, field)
    if len(names) > maximum or (nonempty and not names) or any(len(name) > 256 for name in names):
        raise ContractError(f"{field} exceeds its name/count bounds")
    return names


def _file_entry(value: Any, field: str) -> dict[str, Any]:
    entry = _object(value, field)
    path = entry.get("path")
    if not isinstance(path, str) or not 1 <= len(path) <= 4096 or not Path(path).is_absolute():
        raise ContractError(f"{field}.path must be an absolute prepared file path")
    if "\x00" in path:
        raise ContractError(f"{field}.path contains a null character")
    _sha(entry.get("sha256"), f"{field}.sha256")
    return entry


def _verify_file(entry: Mapping[str, Any], field: str) -> None:
    path = Path(entry["path"])
    if not path.is_file():
        raise ContractError(f"Prepared {field} file does not exist: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != entry["sha256"]:
        raise ContractError(f"Prepared {field} SHA-256 does not match its manifest")


def validate_manifest(value: Mapping[str, Any]) -> dict[str, Any]:
    manifest = copy_object(value)
    required = {
        "schema_version",
        "kind",
        "package_version",
        "protocol",
        "build_id",
        "platform",
        "binary",
        "engine",
        "models",
    }
    if required - manifest.keys() or set(manifest) - required - {"jvm", "provenance"}:
        raise ContractError("Artifact manifest fields do not match protocol 1")
    if type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        raise ContractError("Unsupported artifact schema_version")
    if manifest.get("kind") != "spark-tmbad-artifact":
        raise ContractError("Expected a spark-tmbad-artifact manifest")
    if manifest.get("package_version") not in {"0.1.0", "0.2.0"}:
        raise ContractError("This frontend supports package_version 0.1.0 or 0.2.0")
    if type(manifest.get("protocol")) is not int or manifest["protocol"] != 1:
        raise ContractError("This frontend requires native protocol 1")
    _sha(manifest.get("build_id"), "build_id")
    platform = _object(manifest.get("platform"), "platform")
    _fields(platform, {"os", "arch"}, "platform")
    if platform.get("os") != "linux" or platform.get("arch") not in ("arm64", "amd64"):
        raise ContractError("The prepared native platform must be linux arm64 or amd64")
    binary = _file_entry(manifest.get("binary"), "binary")
    _fields(binary, {"path", "sha256"}, "binary")
    engine = _object(manifest.get("engine"), "engine")
    _fields(engine, {"name", "version", "source_sha256"}, "engine")
    if engine.get("name") != "TMBad" or engine.get("version") != "1.9.25":
        raise ContractError("The prepared engine must be TMBad 1.9.25")
    _sha(engine.get("source_sha256"), "engine.source_sha256")
    models = manifest.get("models")
    if not isinstance(models, list) or not 1 <= len(models) <= 128:
        raise ContractError("Artifact models must be a nonempty descriptor list")
    model_ids: set[str] = set()
    for model in models:
        descriptor = _object(model, "model descriptor")
        model_id = descriptor.get("id")
        if not isinstance(model_id, str) or not model_id:
            raise ContractError("Every model descriptor requires id")
        if model_id in model_ids:
            raise ContractError(f"Duplicate prepared model_id: {model_id}")
        model_ids.add(model_id)
        _sha(descriptor.get("digest"), f"{model_id}.digest")
        _validate_descriptor(descriptor)
    if "jvm" in manifest:
        jvm = _file_entry(manifest["jvm"], "jvm")
        _fields(jvm, {"path", "sha256", "spark_version", "scala_binary_version", "java_min"}, "jvm")
        if jvm.get("spark_version") != "4.0.1" or jvm.get("scala_binary_version") != "2.13":
            raise ContractError("The prepared JVM adapter requires Spark 4.0.1 / Scala 2.13")
        if type(jvm.get("java_min")) is not int or jvm["java_min"] != 17:
            raise ContractError("The JVM adapter must declare java_min of 17")
    return manifest


def _validate_descriptor(descriptor: Mapping[str, Any]) -> None:
    _fields(
        dict(descriptor),
        {
            "id",
            "version",
            "digest",
            "fit_kind",
            "fit_fields",
            "parameter_names",
            "parameter_bounds",
            "marginalization",
            "random_dimension",
            "ordered",
            "max_unit_rows",
            "derivative_orders",
            "predict",
            "forecast",
        },
        "model descriptor",
    )
    if re.fullmatch(r"[a-z][a-z0-9_]{0,63}", _text(descriptor["id"], 64, "model id")) is None:
        raise ContractError("Invalid prepared model identifier")
    if descriptor.get("fit_kind") not in ("rows", "unit"):
        raise ContractError("Prepared model fit_kind must be rows or unit")
    _text(descriptor["version"], 32, "model version")
    _names(descriptor["fit_fields"], 256, "fit_fields", nonempty=True)
    names = _names(descriptor["parameter_names"], 64, "parameter_names", nonempty=True)
    if descriptor["marginalization"] not in ("none", "exact", "laplace"):
        raise ContractError("Unknown prepared marginalization")
    _integer(descriptor["random_dimension"], 0, 8, "random_dimension")
    _integer(descriptor["max_unit_rows"], 1, 256, "max_unit_rows")
    orders = descriptor["derivative_orders"]
    if (
        not isinstance(orders, list)
        or not 1 <= len(orders) <= 2
        or any(type(order) is not int or order not in (1, 2) for order in orders)
        or 1 not in orders
        or len(set(orders)) != len(orders)
    ):
        raise ContractError("Prepared model must declare unique supported derivative orders")
    for order in orders:
        _integer(order, 1, 2, "derivative order")
    if type(descriptor.get("ordered")) is not bool:
        raise ContractError("Prepared model ordered flag must be boolean")
    bounds = descriptor.get("parameter_bounds")
    if not isinstance(bounds, list) or len(bounds) != len(names):
        raise ContractError("Prepared model requires one bound pair per parameter")
    for pair in bounds:
        if not isinstance(pair, list) or len(pair) != 2:
            raise ContractError("Prepared parameter bounds must be pairs")
        for value in pair:
            if value is not None and (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise ContractError("Prepared parameter bounds must be finite numbers or null")
        if all(value is not None for value in pair) and pair[0] > pair[1]:
            raise ContractError("Prepared parameter lower bound exceeds upper bound")
    for operation in ("predict", "forecast"):
        targets = _object(descriptor.get(operation), operation)
        if len(targets) > 64:
            raise ContractError("Too many prepared prediction targets")
        for name, target in targets.items():
            if re.fullmatch(r"[a-z][a-z0-9_]{0,63}", name) is None:
                raise ContractError("Invalid prepared target identifier")
            target = _object(target, f"{operation}.{name}")
            _fields(
                target,
                {"fields", "columns", "needs_history", "conditioning", "uncertainty"},
                "target",
            )
            _names(target.get("fields"), 256, f"{operation}.{name}.fields")
            _names(target.get("columns"), 256, f"{operation}.{name}.columns", nonempty=True)
            if type(target.get("needs_history")) is not bool:
                raise ContractError(f"{operation}.{name}.needs_history must be boolean")
            for field in ("conditioning", "uncertainty"):
                _text(target.get(field), 4096, f"{operation}.{name}.{field}")


class PreparedRuntime:
    """Immutable selection of an explicitly prepared native artifact.

    Constructing this object validates metadata only. ``from_manifest`` verifies
    local file hashes by default. Neither route starts a process, downloads a
    file, adds a JAR to Spark, nor compiles a model.
    """

    def __init__(self, manifest: Mapping[str, Any]) -> None:
        self._json = dumps(validate_manifest(manifest))

    @classmethod
    def from_manifest(cls, path: str | Path, *, verify_files: bool = True) -> PreparedRuntime:
        runtime = cls(read(path))
        if verify_files:
            runtime.verify_files()
        return runtime

    @property
    def manifest(self) -> dict[str, Any]:
        return loads(self._json)

    @property
    def model_ids(self) -> tuple[str, ...]:
        return tuple(model["id"] for model in self.manifest["models"])

    def descriptor(self, model_id: str) -> dict[str, Any]:
        for descriptor in self.manifest["models"]:
            if descriptor["id"] == model_id:
                return descriptor
        raise ContractError(f"Model is absent from the prepared artifact: {model_id}")

    def verify_files(self) -> None:
        """Hash the local binary and optional JAR without loading either file."""
        manifest = self.manifest
        _verify_file(manifest["binary"], "binary")
        if "jvm" in manifest:
            _verify_file(manifest["jvm"], "jvm")

    def identity(self, model_id: str) -> dict[str, Any]:
        """Return content identity; prepared absolute paths may be relocated."""
        manifest = self.manifest
        self.descriptor(model_id)
        return {
            "build_id": manifest["build_id"],
            "binary_sha256": manifest["binary"]["sha256"],
            "platform": manifest["platform"],
            "engine": manifest["engine"],
            "jvm_sha256": manifest.get("jvm", {}).get("sha256"),
        }

    def to_json(self) -> str:
        return self._json

    def __repr__(self) -> str:
        manifest = self.manifest
        return f"PreparedRuntime(build_id={manifest['build_id']!r}, models={self.model_ids!r})"
