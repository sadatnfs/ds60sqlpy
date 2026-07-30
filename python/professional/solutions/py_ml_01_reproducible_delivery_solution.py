"""Reference implementation for python-ml-01.

Artifacts are canonical JSON plus SHA-256 manifests. No pickle, hosted registry,
network account, or machine-specific environment capture is required.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from statistics import mean
from typing import Literal, TypeAlias

Scalar: TypeAlias = str | int | float | bool | None
Record: TypeAlias = Mapping[str, Scalar]
Stage = Literal["candidate", "staging", "production", "archived"]


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    dtype: Literal["float"]
    required: bool = True


@dataclass(frozen=True)
class FeatureSchema:
    version: int
    features: tuple[FeatureSpec, ...]


@dataclass(frozen=True)
class LinearModel:
    feature_name: str
    coefficient: float
    intercept: float

    def predict(self, features: Mapping[str, float]) -> float:
        try:
            value = features[self.feature_name]
        except KeyError as exc:
            raise ValueError(f"missing feature: {self.feature_name}") from exc
        return self.intercept + self.coefficient * value


@dataclass(frozen=True)
class RuntimeRequirement:
    python_min: tuple[int, int]
    python_max_exclusive: tuple[int, int]
    packages: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Manifest:
    artifact_sha256: str
    schema_sha256: str
    data_snapshot_sha256: str
    runtime: RuntimeRequirement


@dataclass(frozen=True)
class CompatibilityReport:
    compatible: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class PromotionEvidence:
    tests_passed: bool
    compatibility_passed: bool
    metric_name: str
    metric_value: float
    minimum_metric: float
    manifest_sha256: str

    @property
    def approved(self) -> bool:
        return (
            self.tests_passed
            and self.compatibility_passed
            and self.metric_value >= self.minimum_metric
            and len(self.manifest_sha256) == 64
        )


@dataclass(frozen=True)
class RegistryEntry:
    version: str
    stage: Stage
    evidence: PromotionEvidence


@dataclass(frozen=True)
class RegistryEvent:
    action: Literal["registered", "promoted", "rollback"]
    version: str
    reason: str


class LocalRegistry:
    def __init__(self) -> None:
        self._entries: dict[str, RegistryEntry] = {}
        self._events: list[RegistryEvent] = []

    @property
    def entries(self) -> tuple[RegistryEntry, ...]:
        return tuple(self._entries[key] for key in sorted(self._entries))

    @property
    def events(self) -> tuple[RegistryEvent, ...]:
        return tuple(self._events)

    def register(self, version: str, evidence: PromotionEvidence) -> None:
        if not version or version in self._entries:
            raise ValueError("version must be new and non-empty")
        self._entries[version] = RegistryEntry(version, "candidate", evidence)
        self._events.append(RegistryEvent("registered", version, "candidate created"))

    def stage(self, version: str) -> None:
        entry = self._entry(version)
        if entry.stage != "candidate":
            raise ValueError("only a candidate can enter staging")
        if not entry.evidence.approved:
            raise ValueError("promotion evidence is incomplete")
        self._entries[version] = replace(entry, stage="staging")

    def promote(self, version: str, *, reason: str) -> None:
        entry = self._entry(version)
        if entry.stage != "staging" or not entry.evidence.approved:
            raise ValueError("only an approved staging version can reach production")
        if not reason.strip():
            raise ValueError("promotion reason is required")
        for key, current in tuple(self._entries.items()):
            if current.stage == "production":
                self._entries[key] = replace(current, stage="archived")
        self._entries[version] = replace(entry, stage="production")
        self._events.append(RegistryEvent("promoted", version, reason))

    def rollback(self, version: str, *, reason: str) -> None:
        target = self._entry(version)
        if target.stage != "archived":
            raise ValueError("rollback target must be a previously archived version")
        if not reason.strip():
            raise ValueError("rollback reason is required")
        for key, current in tuple(self._entries.items()):
            if current.stage == "production":
                self._entries[key] = replace(current, stage="archived")
        self._entries[version] = replace(target, stage="production")
        self._events.append(RegistryEvent("rollback", version, reason))

    def production(self) -> RegistryEntry | None:
        return next(
            (entry for entry in self._entries.values() if entry.stage == "production"),
            None,
        )

    def _entry(self, version: str) -> RegistryEntry:
        try:
            return self._entries[version]
        except KeyError as exc:
            raise ValueError(f"unknown version: {version}") from exc


def canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_record_hash(records: Sequence[Record]) -> str:
    seen: set[str] = set()
    normalized: list[dict[str, Scalar]] = []
    for record in records:
        record_id = record.get("record_id")
        if not isinstance(record_id, str) or not record_id:
            raise ValueError("every record needs a non-empty string record_id")
        if record_id in seen:
            raise ValueError(f"duplicate record_id: {record_id}")
        seen.add(record_id)
        normalized.append(dict(record))
    normalized.sort(key=lambda record: str(record["record_id"]))
    return sha256_text(canonical_json(normalized))


def fit_linear_model(
    rows: Sequence[tuple[float, float]],
    *,
    feature_name: str = "x",
) -> LinearModel:
    if len(rows) < 2:
        raise ValueError("training needs at least two rows")
    x_values = [row[0] for row in rows]
    y_values = [row[1] for row in rows]
    x_mean = mean(x_values)
    y_mean = mean(y_values)
    denominator = sum((value - x_mean) ** 2 for value in x_values)
    if denominator == 0:
        raise ValueError("feature must vary")
    coefficient = (
        sum((x_value - x_mean) * (y_value - y_mean) for x_value, y_value in rows) / denominator
    )
    intercept = y_mean - coefficient * x_mean
    return LinearModel(feature_name, coefficient, intercept)


def schema_payload(schema: FeatureSchema) -> dict[str, object]:
    return {
        "version": schema.version,
        "features": [
            {
                "name": feature.name,
                "dtype": feature.dtype,
                "required": feature.required,
            }
            for feature in schema.features
        ],
    }


def model_payload(model: LinearModel) -> dict[str, object]:
    return {
        "format": "ds60-linear-json-v1",
        "feature_name": model.feature_name,
        "coefficient": model.coefficient,
        "intercept": model.intercept,
    }


def manifest_payload(manifest: Manifest) -> dict[str, object]:
    return {
        "artifact_sha256": manifest.artifact_sha256,
        "schema_sha256": manifest.schema_sha256,
        "data_snapshot_sha256": manifest.data_snapshot_sha256,
        "runtime": {
            "python_min": list(manifest.runtime.python_min),
            "python_max_exclusive": list(manifest.runtime.python_max_exclusive),
            "packages": [list(item) for item in manifest.runtime.packages],
        },
    }


def write_bundle(
    directory: Path,
    *,
    model: LinearModel,
    schema: FeatureSchema,
    data_snapshot_sha256: str,
    runtime: RuntimeRequirement,
) -> Manifest:
    directory.mkdir(parents=True, exist_ok=False)
    artifact_text = canonical_json(model_payload(model))
    schema_text = canonical_json(schema_payload(schema))
    artifact_hash = sha256_text(artifact_text)
    schema_hash = sha256_text(schema_text)
    manifest = Manifest(artifact_hash, schema_hash, data_snapshot_sha256, runtime)
    (directory / "model.json").write_text(artifact_text, encoding="utf-8")
    (directory / "schema.json").write_text(schema_text, encoding="utf-8")
    (directory / "manifest.json").write_text(
        canonical_json(manifest_payload(manifest)),
        encoding="utf-8",
    )
    return manifest


def verify_bundle(directory: Path, expected: Manifest) -> None:
    artifact_text = (directory / "model.json").read_text(encoding="utf-8")
    schema_text = (directory / "schema.json").read_text(encoding="utf-8")
    manifest_text = (directory / "manifest.json").read_text(encoding="utf-8")
    if sha256_text(artifact_text) != expected.artifact_sha256:
        raise ValueError("model artifact hash mismatch")
    if sha256_text(schema_text) != expected.schema_sha256:
        raise ValueError("feature schema hash mismatch")
    if manifest_text != canonical_json(manifest_payload(expected)):
        raise ValueError("manifest content mismatch")


def compatibility_report(
    *,
    expected_schema: FeatureSchema,
    actual_schema: FeatureSchema,
    runtime: RuntimeRequirement,
    python_version: tuple[int, int],
    package_versions: Mapping[str, str],
) -> CompatibilityReport:
    reasons: list[str] = []
    if expected_schema != actual_schema:
        reasons.append("feature schema differs")
    if not runtime.python_min <= python_version < runtime.python_max_exclusive:
        reasons.append(f"Python {python_version} is outside the declared range")
    for package, required_major in runtime.packages:
        actual = package_versions.get(package)
        if actual is None:
            reasons.append(f"missing package {package}")
        elif actual.split(".", 1)[0] != required_major:
            reasons.append(f"{package} major {actual.split('.', 1)[0]} != {required_major}")
    return CompatibilityReport(not reasons, tuple(reasons))


def main() -> int:
    rows = [(0.0, 1.0), (1.0, 3.0), (2.0, 5.0)]
    records: list[Record] = [
        {"record_id": "r1", "x": 0.0, "y": 1.0},
        {"record_id": "r2", "x": 1.0, "y": 3.0},
        {"record_id": "r3", "x": 2.0, "y": 5.0},
    ]
    model = fit_linear_model(rows)
    schema = FeatureSchema(1, (FeatureSpec("x", "float"),))
    runtime = RuntimeRequirement((3, 11), (3, 13), (("ds60-runtime", "1"),))
    with tempfile.TemporaryDirectory(prefix="ds60-model-bundle-") as directory:
        bundle = Path(directory) / "bundle"
        manifest = write_bundle(
            bundle,
            model=model,
            schema=schema,
            data_snapshot_sha256=canonical_record_hash(records),
            runtime=runtime,
        )
        verify_bundle(bundle, manifest)
        report = compatibility_report(
            expected_schema=schema,
            actual_schema=schema,
            runtime=runtime,
            python_version=sys.version_info[:2],
            package_versions={"ds60-runtime": "1.0"},
        )
        print("prediction:", model.predict({"x": 3.0}))
        print("manifest:", sha256_text(canonical_json(manifest_payload(manifest))))
        print("compatible:", report.compatible)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
