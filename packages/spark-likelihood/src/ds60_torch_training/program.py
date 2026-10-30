# SPDX-License-Identifier: Apache-2.0
"""Named ordinary PyTorch factories with explicit source/config identities.

Describing a program does not import Torch or Spark.
"""

from __future__ import annotations

import functools
import hashlib
import importlib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ds60_spark_likelihood.registry import _callable_identity, configuration_json

from .contracts import (
    TrainingError,
    canonical_json,
    digest,
    exact_keys,
    integer,
    require_sha,
)

KIND = "ds60-torch-training-program"


def _module_source(name: str) -> str:
    if (
        not isinstance(name, str)
        or not name
        or name == "__main__"
        or any(part.startswith("<") for part in name.split("."))
    ):
        raise TrainingError("Program modules must be explicit importable sources")
    module = importlib.import_module(name)
    filename = getattr(module, "__file__", None)
    if filename and Path(filename).is_file():
        with Path(filename).open("rb") as stream:
            raw = stream.read(1024 * 1024 + 1)
    else:
        loader = getattr(module, "__loader__", None)
        text = (
            loader.get_source(name)
            if loader is not None and hasattr(loader, "get_source")
            else None
        )
        if text is None:
            raise TrainingError("Program module has no prepared inspectable source")
        raw = text.encode("utf-8")
    if len(raw) > 1024 * 1024:
        raise TrainingError("Program module source exceeds its bound")
    return hashlib.sha256(raw).hexdigest()


def _named_identity(function):
    try:
        return _callable_identity(function)
    except (TypeError, ValueError) as error:
        raise TrainingError("Training factories need the existing named source contract") from error


def _factory_module(identity):
    return _factory_module(identity["function"]) if "partial" in identity else identity["module"]


def _resolve_factory(identity):
    if "partial" in identity:
        exact_keys(identity, {"function", "partial"}, name="partial factory")
        partial = exact_keys(identity["partial"], {"args", "keywords"}, name="partial arguments")
        value = functools.partial(
            _resolve_factory(identity["function"]),
            *partial["args"],
            **partial["keywords"],
        )
    else:
        exact_keys(
            identity,
            {"module", "name", "bound_state", "live_code", "module_source_sha256"},
            name="factory identity",
        )
        value: Any = importlib.import_module(identity["module"])
        for part in identity["name"].split("."):
            value = getattr(value, part)
    if _named_identity(value) != identity:
        raise TrainingError("Live factory/source identity differs from the submitted program")
    return value


@dataclass(frozen=True)
class TrainingProgram:
    model_factory: Callable
    loss_factory: Callable
    optimizer_factory: Callable
    feature_names: tuple[str, ...]
    configuration: dict | None = None
    precision: str = "float64"
    target_domain: str = "binary"
    code_modules: tuple[str, ...] = ()

    def descriptor(self) -> dict:
        if (
            type(self.feature_names) is not tuple
            or not 1 <= len(self.feature_names) <= 64
            or len(set(self.feature_names)) != len(self.feature_names)
            or any(
                type(name) is not str or not name or len(name.encode("utf-8")) > 256
                for name in self.feature_names
            )
        ):
            raise TrainingError("Program feature_names must be a bounded ordered tuple")
        if self.precision not in {"float32", "float64"} or self.target_domain not in {
            "binary",
            "real",
            "class_index",
        }:
            raise TrainingError("Unsupported CPU precision or target domain")
        identities = {
            name: _named_identity(getattr(self, name))
            for name in ("model_factory", "loss_factory", "optimizer_factory")
        }
        required_modules = {_factory_module(value) for value in identities.values()}
        if type(self.code_modules) is not tuple or len(self.code_modules) > 64:
            raise TrainingError("Program code_modules must be a bounded tuple")
        modules = sorted(required_modules | set(self.code_modules))
        if not all(isinstance(name, str) for name in modules):
            raise TrainingError("Invalid prepared code module")
        import json

        configuration = json.loads(configuration_json(self.configuration))
        source = {name: _module_source(name) for name in modules}
        body = {
            "schema_version": 1,
            "kind": KIND,
            "factories": identities,
            "feature_names": list(self.feature_names),
            "configuration": configuration,
            "precision": self.precision,
            "target_domain": self.target_domain,
            "code_modules": source,
            "code_digest": digest(source),
        }
        canonical_json(body, limit=262144)
        return body | {"program_digest": digest(body)}

    @classmethod
    def from_descriptor(cls, value: dict) -> TrainingProgram:
        exact_keys(
            value,
            {
                "schema_version",
                "kind",
                "factories",
                "feature_names",
                "configuration",
                "precision",
                "target_domain",
                "code_modules",
                "code_digest",
                "program_digest",
            },
            name="training program",
        )
        if (
            type(value["schema_version"]) is not int
            or value["schema_version"] != 1
            or value["kind"] != KIND
        ):
            raise TrainingError("Unsupported training program schema")
        require_sha(value["program_digest"])
        body = {key: item for key, item in value.items() if key != "program_digest"}
        if (
            digest(body) != value["program_digest"]
            or digest(value["code_modules"]) != value["code_digest"]
        ):
            raise TrainingError("Program digest mismatch")
        exact_keys(
            value["factories"],
            {"model_factory", "loss_factory", "optimizer_factory"},
            name="program factories",
        )
        for name, expected in value["code_modules"].items():
            if _module_source(name) != expected:
                raise TrainingError("Prepared program code source changed")
        result = cls(
            **{name: _resolve_factory(identity) for name, identity in value["factories"].items()},
            feature_names=tuple(value["feature_names"]),
            configuration=value["configuration"],
            precision=value["precision"],
            target_domain=value["target_domain"],
            code_modules=tuple(value["code_modules"]),
        )
        if result.descriptor() != value:
            raise TrainingError("Program reconstruction differs from submitted definition")
        return result


def schedule(
    assignment: dict,
    *,
    epochs: int,
    steps_per_epoch: int,
    max_batch_rows: int,
    seed: int,
) -> dict:
    integer(epochs, "epochs", 1, 128)
    integer(steps_per_epoch, "steps_per_epoch", 1, 1024)
    integer(max_batch_rows, "max_batch_rows", 1, 32768)
    integer(seed, "seed", 0, 2**53 - 1)
    ranges = []
    for rank in assignment["ranks"]:
        count = integer(rank["rows"], "rank rows", 1, 32768)
        if (
            count < steps_per_epoch
            or (count + steps_per_epoch - 1) // steps_per_epoch > max_batch_rows
        ):
            raise TrainingError("A common positive, bounded step schedule is impossible")
        ranges.append(
            {
                "rank": rank["rank"],
                "ranges": [
                    [
                        step * count // steps_per_epoch,
                        (step + 1) * count // steps_per_epoch,
                    ]
                    for step in range(steps_per_epoch)
                ],
            }
        )
    body = {
        "kind": "fixed_order_training_schedule_v1",
        "epochs": epochs,
        "steps_per_epoch": steps_per_epoch,
        "max_batch_rows": max_batch_rows,
        "seed": seed,
        "assignment_digest": assignment["assignment_digest"],
        "ranks": ranges,
    }
    return body | {"schedule_digest": digest(body)}


def ledger(rows: list[dict], steps: int) -> dict:
    import math

    ids, data = hashlib.sha256(), hashlib.sha256()
    for row in rows:
        ids.update(canonical_json(row["id"]) + b"\n")
        data.update(canonical_json(row) + b"\n")
    weight = math.fsum(row["weight"] for row in rows)
    if not math.isfinite(weight):
        raise TrainingError("Rank weight mass exceeds finite range")
    return {
        "row_count": len(rows),
        "weight_sum": weight,
        "membership_digest": ids.hexdigest(),
        "data_digest": data.hexdigest(),
        "steps": steps,
    }
