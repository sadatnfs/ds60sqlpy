"""Additive global objectives and independent unit fits using prepared TMB models.

An RDD item is {"unit_id": str, "data": declared numeric vectors}. Each item is
one complete independent unit or independent-row batch. This is a bounded
teaching adapter, not a scheduler for arbitrary coupled latent models.
"""

from __future__ import annotations

import hashlib
import json
import math
from functools import partial

from ds60_spark_likelihood.contracts import (
    PartitionSummary,
    combine_summaries,
    parameter_digest,
)

from .registry import ModelContractError, load_registry, payload_for
from .runtime import PROJECT_ROOT, evaluate_prepared, fit_prepared, verify_prepared

MAX_UNITS_PER_PARTITION = 256
MAX_PARTITIONS = 64


def _units(iterator, *, root, model_id):
    specification = load_registry(root)["models"][model_id]
    names = specification["fixed_parameters"]
    for index, unit in enumerate(iterator):
        if index >= MAX_UNITS_PER_PARTITION:
            raise ModelContractError("Partition exceeds bounded independent-unit capacity")
        if (
            not isinstance(unit, dict)
            or set(unit) != {"unit_id", "data"}
            or not isinstance(unit["unit_id"], str)
            or not 1 <= len(unit["unit_id"]) <= 128
        ):
            raise ModelContractError("Each unit needs a bounded string unit_id and declared data")
        payload = payload_for(root, model_id, unit["data"], [0.0] * len(names))
        yield {
            "unit_id": unit["unit_id"],
            "data": {field: payload["data"][field] for field in specification["data"]},
        }


class _UnitLedger:
    """Bounded identities/counts only; never retain observation arrays."""

    def __init__(self, index, response):
        self.index, self.response = index, response
        self.ids, self.seen, self.digest, self.rows = [], set(), 0, 0

    def add(self, unit):
        if unit["unit_id"] in self.seen:
            raise ModelContractError("Duplicate independent-unit ID")
        self.seen.add(unit["unit_id"])
        self.ids.append(unit["unit_id"])
        encoded = json.dumps(unit, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        self.digest = (self.digest + int(hashlib.sha256(encoded).hexdigest(), 16)) % (1 << 256)
        self.rows += len(unit["data"][self.response])

    def result(self):
        return {
            "partition_id": self.index,
            "unit_ids": self.ids,
            "digest": f"{self.digest:064x}",
            "rows": self.rows,
        }


def _inspect(index, iterator, *, root, model_id):
    ledger = _UnitLedger(index, load_registry(root)["models"][model_id]["response"])
    for unit in _units(iterator, root=root, model_id=model_id):
        ledger.add(unit)
    yield ledger.result()


def _evaluate(index, iterator, *, root, build_dir, model_id, theta):
    ledger = _UnitLedger(index, load_registry(root)["models"][model_id]["response"])
    values = []
    for unit in _units(iterator, root=root, model_id=model_id):
        ledger.add(unit)
        values.append(
            evaluate_prepared(model_id, unit["data"], theta, root=root, build_dir=build_dir)
        )
    metadata = ledger.result()
    source_ids = {r["artifact_source_sha256"] for r in values}
    library_ids = {r["artifact_library_sha256"] for r in values}
    identities = {
        json.dumps({"registry": r["artifact_registry_sha256"], "abi": r["abi"]}, sort_keys=True)
        for r in values
    }
    if len(source_ids) > 1 or len(library_ids) > 1 or len(identities) > 1:
        raise ModelContractError("A partition mixed prepared model artifacts")
    summary = PartitionSummary(
        index,
        parameter_digest(theta),
        "prepared-tmb-" + model_id,
        metadata["rows"],
        float(metadata["rows"]),
        math.fsum(r["value"] for r in values),
        tuple(math.fsum(r["gradient"][j] for r in values) for j in range(len(theta))),
    )
    yield {
        "metadata": metadata,
        "summary": summary,
        "sources": sorted(source_ids),
        "libraries": sorted(library_ids),
        "identities": sorted(identities),
    }


def _fit_units(index, iterator, *, root, build_dir, model_id, initial):
    ledger = _UnitLedger(index, load_registry(root)["models"][model_id]["response"])
    fits = []
    for unit in _units(iterator, root=root, model_id=model_id):
        ledger.add(unit)
        fits.append(
            {
                "unit_id": unit["unit_id"],
                "fit": fit_prepared(
                    model_id, unit["data"], initial, root=root, build_dir=build_dir
                ),
            }
        )
    yield {"metadata": ledger.result(), "fits": fits}


class SparkTMBObjective:
    """Materialize a bounded unit ledger, then evaluate one shared parameter vector.

    Callers should persist a deterministic RDD. The ledger binds every subsequent
    evaluation to complete unit IDs and numeric data. It cannot infer whether a
    scientist has mislabeled two correlated units as independent.
    """

    def __init__(self, rdd, model_id, *, root=None, build_dir="/opt/spark-tmb-models"):
        self.root = str(PROJECT_ROOT if root is None else root)
        registry = load_registry(self.root)
        if model_id not in registry["models"]:
            raise ModelContractError("Unknown prepared model")
        self.rdd, self.model_id, self.build_dir = rdd, model_id, str(build_dir)
        receipt = verify_prepared(self.root, self.build_dir, model_id)
        self.expected_artifact = receipt["models"][model_id]
        self.expected_identity = json.dumps(
            {"registry": receipt["registry_sha256"], "abi": receipt["abi"]}, sort_keys=True
        )
        self.partitions = rdd.getNumPartitions()
        if not 1 <= self.partitions <= MAX_PARTITIONS:
            raise ModelContractError("Teaching adapter permits 1..64 partitions")
        self.ledger = rdd.mapPartitionsWithIndex(
            partial(_inspect, root=self.root, model_id=model_id)
        ).collect()
        ids = [key for row in self.ledger for key in row["unit_ids"]]
        if not ids or len(ids) != len(set(ids)):
            raise ModelContractError("Global independent-unit IDs must be present and unique")
        self.rows = sum(row["rows"] for row in self.ledger)
        self._by_partition = {row["partition_id"]: row for row in self.ledger}

    def evaluate(self, theta):
        parameters = tuple(theta)
        records = self.rdd.mapPartitionsWithIndex(
            partial(
                _evaluate,
                root=self.root,
                build_dir=self.build_dir,
                model_id=self.model_id,
                theta=parameters,
            )
        ).collect()
        for result in records:
            meta = result["metadata"]
            if meta != self._by_partition.get(meta["partition_id"]):
                raise ModelContractError(
                    "Independent units or numeric data changed after materialization"
                )
        sources = {x for row in records for x in row["sources"]}
        libraries = {x for row in records for x in row["libraries"]}
        identities = {x for row in records for x in row["identities"]}
        if (
            sources != {self.expected_artifact["source_sha256"]}
            or libraries != {self.expected_artifact["library_sha256"]}
            or identities != {self.expected_identity}
        ):
            raise ModelContractError("Global result mixed prepared artifacts")
        return combine_summaries(
            [row["summary"] for row in records],
            parameters=parameters,
            model_id="prepared-tmb-" + self.model_id,
            expected_partitions=self.partitions,
            expected_rows=self.rows,
            reduction="sum",
        )

    def fit_independent_units(self, initial):
        """Return one detached local estimate per independent unit, never their average."""
        results = self.rdd.mapPartitionsWithIndex(
            partial(
                _fit_units,
                root=self.root,
                build_dir=self.build_dir,
                model_id=self.model_id,
                initial=tuple(initial),
            )
        ).collect()
        for result in results:
            meta = result["metadata"]
            if meta != self._by_partition.get(meta["partition_id"]):
                raise ModelContractError("Independent fit data changed after materialization")
        results = [fit for record in results for fit in record["fits"]]
        if any(
            row["fit"]["artifact_source_sha256"] != self.expected_artifact["source_sha256"]
            or row["fit"]["artifact_library_sha256"] != self.expected_artifact["library_sha256"]
            or json.dumps(
                {"registry": row["fit"]["artifact_registry_sha256"], "abi": row["fit"]["abi"]},
                sort_keys=True,
            )
            != self.expected_identity
            for row in results
        ):
            raise ModelContractError("Independent fits differ from the driver's prepared artifact")
        expected = {key for row in self.ledger for key in row["unit_ids"]}
        actual = [row["unit_id"] for row in results]
        if len(set(actual)) != len(actual) or set(actual) != expected:
            raise ModelContractError("Independent fit membership changed")
        return results
