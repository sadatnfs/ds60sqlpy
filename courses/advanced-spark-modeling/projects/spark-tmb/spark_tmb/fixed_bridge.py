"""Bounded detached Spark-to-R/TMB evaluation; no embedded R in Spark closures."""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

from ds60_spark_likelihood.contracts import (
    ObjectiveError,
    PartitionSummary,
    combine_summaries,
    finite_number,
    finite_vector,
    parameter_digest,
)

from spark_tmb import evaluate_prepared
from spark_tmb.registry import ModelContractError, payload_for

MAX_ROWS = 4096
MAX_BYTES = 1_000_000
MAX_GROUPS = 256
MODELS = {
    "normal_mean": ("mu", "log_sigma"),
    "random_intercept": ("beta", "log_sigma", "log_tau"),
}


@dataclass(frozen=True)
class PreparedTMB:
    project_root: str = str(Path(__file__).resolve().parents[1])
    build_dir: str = "/opt/spark-tmb-models"
    timeout_seconds: int = 45

    def __post_init__(self):
        if type(self.timeout_seconds) is not int or not 1 <= self.timeout_seconds <= 120:
            raise ObjectiveError("R evaluation timeout must be within 1..120 seconds")


DEFAULT_PREPARED = PreparedTMB()


def bounded_rows(records):
    result, seen = [], set()
    for row in records:
        if len(result) >= MAX_ROWS:
            raise ObjectiveError(
                "Partition exceeds bounded row capacity; repartition complete units"
            )
        if not isinstance(row, dict) or set(row) != {"row_id", "group_id", "y"}:
            raise ObjectiveError("Each row needs exactly row_id, group_id and y")
        for key in ("row_id", "group_id"):
            if not isinstance(row[key], str) or not 1 <= len(row[key]) <= 128:
                raise ObjectiveError("IDs must be nonempty strings of at most 128 characters")
        if row["row_id"] in seen:
            raise ObjectiveError("Duplicate row identity inside one partition")
        seen.add(row["row_id"])
        result.append(
            {
                "row_id": row["row_id"],
                "group_id": row["group_id"],
                "y": finite_number(row["y"], "response"),
            }
        )
    return result


def membership_digest(records):
    """Order-independent multiset checksum, not a security or uniqueness proof."""
    total = 0
    for row in records:
        payload = json.dumps(row, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        total = (total + int(hashlib.sha256(payload).hexdigest(), 16)) % (1 << 256)
    return f"{total:064x}"


def request_for(model, records, parameters):
    if model not in MODELS:
        raise ObjectiveError("Only fixed normal_mean and random_intercept models are allowed")
    rows = bounded_rows(records)
    theta = finite_vector(parameters)
    if len(theta) != len(MODELS[model]):
        raise ObjectiveError("Fixed parameter dimension does not match model")
    if len(rows) < 2:
        raise ObjectiveError("This prepared TMB protocol needs at least two observations per call")
    data = {"y": [row["y"] for row in rows]}
    starts = dict(zip(MODELS[model], theta, strict=True))
    random = None
    if model == "random_intercept":
        groups = sorted({row["group_id"] for row in rows})
        if len(groups) > MAX_GROUPS:
            raise ObjectiveError("Too many complete groups in one bounded partition")
        ids = {key: index for index, key in enumerate(groups)}
        data["group"] = [ids[row["group_id"]] for row in rows]
        starts["u"] = [0.0] * len(groups)
        random = "u"
    return {
        "schema_version": 1,
        "model": model,
        "data": data,
        "parameters": starts,
        "theta": list(theta),
        "random": random,
    }


def evaluate_r(request, prepared=DEFAULT_PREPARED):
    """Adapt fixed workshop requests to the one source-bound prepared runtime."""
    if (
        not isinstance(request, dict)
        or type(request.get("schema_version")) is not int
        or request["schema_version"] != 1
        or request.get("model") not in MODELS
    ):
        raise ObjectiveError("Unsupported fixed workshop request")
    try:
        canonical = payload_for(
            prepared.project_root, request["model"], request["data"], request["theta"]
        )
        expected = {
            "schema_version": 1,
            "model": request["model"],
            "data": canonical["data"],
            "parameters": canonical["parameters"],
            "theta": canonical["theta"],
            "random": canonical["random"],
        }
        if request != expected:
            raise ObjectiveError("Workshop request differs from the prepared model contract")
        result = evaluate_prepared(
            request["model"],
            request["data"],
            request["theta"],
            root=prepared.project_root,
            build_dir=prepared.build_dir,
            timeout=prepared.timeout_seconds,
        )
    except ModelContractError as exc:
        raise ObjectiveError(str(exc)) from exc
    provenance = {
        **result["abi"],
        "source_sha256": result["artifact_source_sha256"],
        "library_sha256": result["artifact_library_sha256"],
        "registry_sha256": result["artifact_registry_sha256"],
    }
    return result["value"], tuple(result["gradient"]), provenance


def partition_result(index, records, model, parameters, prepared=DEFAULT_PREPARED):
    rows = bounded_rows(records)
    theta = finite_vector(parameters)
    if model not in MODELS or len(theta) != len(MODELS[model]):
        raise ObjectiveError("Unknown model or incorrect parameter dimension")
    value, gradient, provenance = 0.0, (0.0,) * len(theta), None
    if rows:
        value, gradient, provenance = evaluate_r(request_for(model, rows, theta), prepared)
    summary = PartitionSummary(
        index, parameter_digest(theta), "tmb-" + model, len(rows), float(len(rows)), value, gradient
    )
    return {
        "summary": asdict(summary),
        "membership_digest": membership_digest(rows),
        "groups": sorted({row["group_id"] for row in rows}),
        "provenance": provenance,
    }


def combine_results(results, *, parameters, model, expected_rows, expected_partitions):
    records = list(results)
    if len(records) != expected_partitions:
        raise ObjectiveError("Missing or repeated partition result")
    expected = bounded_rows(expected_rows)
    observed = sum(int(row["membership_digest"], 16) for row in records) % (1 << 256)
    if f"{observed:064x}" != membership_digest(expected):
        raise ObjectiveError("Input row membership/content changed during evaluation")
    if model == "random_intercept":
        owners = {}
        for result in records:
            for group in result["groups"]:
                if group in owners:
                    raise ObjectiveError("A dependent group was split across partitions")
                owners[group] = result["summary"]["partition_id"]
    identities = {
        json.dumps(row["provenance"], sort_keys=True)
        for row in records
        if row["summary"]["row_count"]
    }
    if len(identities) != 1:
        raise ObjectiveError("Mixed or missing compiled-model runtime identities")
    return combine_summaries(
        [PartitionSummary(**row["summary"]) for row in records],
        parameters=parameters,
        model_id="tmb-" + model,
        expected_partitions=expected_partitions,
        expected_rows=len(expected),
        reduction="sum",
    )


def normal_oracle(records, parameters):
    mu, log_sigma = finite_vector(parameters)
    variance = math.exp(2 * log_sigma)
    residuals = [row["y"] - mu for row in records]
    n = len(residuals)
    rss = math.fsum(r * r for r in residuals)
    value = n * (log_sigma + 0.5 * math.log(2 * math.pi)) + rss / (2 * variance)
    return value, (-math.fsum(residuals) / variance, n - rss / variance)


def laplace_oracle(records, parameters):
    """Exact rank-one Gaussian integral, independent of TMB or matrix libraries."""
    beta, log_sigma, log_tau = finite_vector(parameters)
    sigma2, tau2 = math.exp(2 * log_sigma), math.exp(2 * log_tau)
    groups = defaultdict(list)
    for row in records:
        groups[row["group_id"]].append(row["y"] - beta)
    value, gradient = 0.0, [0.0, 0.0, 0.0]
    for residual in groups.values():
        n, total = len(residual), math.fsum(residual)
        denominator = sigma2 + n * tau2
        inv_r = [r / sigma2 - tau2 * total / (sigma2 * denominator) for r in residual]
        quadratic = math.fsum(r * z for r, z in zip(residual, inv_r, strict=True))
        logdet = (n - 1) * math.log(sigma2) + math.log(denominator)
        value += 0.5 * (n * math.log(2 * math.pi) + logdet + quadratic)
        gradient[0] -= total / denominator
        gradient[1] += sigma2 * (
            (n - 1) / sigma2 + 1 / denominator - math.fsum(z * z for z in inv_r)
        )
        gradient[2] += tau2 * (n / denominator - (total / denominator) ** 2)
    return value, tuple(gradient)
