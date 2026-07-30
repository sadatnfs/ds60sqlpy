"""python-ml-01 learner lab: reproducible local model delivery."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping, Sequence

Scalar = str | int | float | bool | None


def canonical_record_hash(records: Sequence[Mapping[str, Scalar]]) -> str:
    """Return an order-independent SHA-256 snapshot identifier.

    TODO: require a unique ``record_id``, sort records by that ID, serialize
    canonical JSON, and hash UTF-8 bytes.
    """

    raise NotImplementedError("complete canonical_record_hash")


def hash_text(text: str) -> str:
    """Worked example: hashes identify bytes, not semantic equivalence."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def schema_compatible(
    expected: Sequence[tuple[str, str]],
    actual: Sequence[tuple[str, str]],
) -> bool:
    """TODO: require exact ordered names and types for this strict model."""

    raise NotImplementedError("complete schema_compatible")


def self_check() -> None:
    left = json.dumps({"x": 1, "y": 2})
    right = json.dumps({"y": 2, "x": 1})
    print("Worked raw hashes differ:", hash_text(left) != hash_text(right))
    checks: tuple[tuple[str, Callable[[], object]], ...] = (
        (
            "canonical data snapshot",
            lambda: canonical_record_hash([{"record_id": "b", "x": 2}, {"record_id": "a", "x": 1}]),
        ),
        (
            "feature compatibility",
            lambda: schema_compatible([("x", "float")], [("x", "float")]),
        ),
    )
    for label, call in checks:
        try:
            print(label, "->", call())
        except NotImplementedError:
            print("TODO:", label)


# === Numbered professional practice ===
#
# Attempt every exercise before opening solutions. Keep evidence in a copy
# under .learning/ or in tests; do not overwrite the reference solution.
# Full acceptance checks and progressive hints:
# companion-guides/py_ml_01_reproducible_delivery.md
#
# Exercise 1 — Complete snapshot hashing
# Prompt: Require a nonempty unique `record_id`, sort by it, serialize with sorted keys,
# reject NaN, and hash UTF-8 bytes. Verify reversed rows retain the hash while one changed
# value does not. Explain what the hash does *not* prove: source ownership, legality,
# labeling quality, representativeness, or absence of leakage.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 2 — Fit and serialize the local model
# Prompt: Fit `y = intercept + coefficient*x` on three deterministic points. Store only
# format identifier, feature name, and numeric parameters in JSON. Do not use pickle:
# loading an untrusted pickle can execute code.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 3 — Version the feature schema
# Prompt: Declare feature name, ordered position, dtype, required status, and schema
# version. Test exact compatibility, reordered input, a renamed feature, and a version
# change. Decide which future changes could be safely additive for a different consumer
# contract.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 4 — Define runtime compatibility
# Prompt: Declare Python 3.11 through below 3.13 and required package major versions.
# Inject the observed versions into the check rather than dumping a machine-specific
# environment. Report every incompatibility, not only the first.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 5 — Build and tamper with a bundle
# Prompt: Write model, schema, and manifest into a temporary directory. Verify all hashes.
# Replace `model.json` with `{}` and confirm loading fails before parsing or prediction.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 6 — Promote with evidence
# Prompt: Register a candidate with: - tests passed, - compatibility passed, - named
# metric and threshold, - metric value, and - 64-character manifest hash. Move it to
# staging and production. Reject a version with missing tests even if its metric is high.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 7 — Rehearse rollback
# Prompt: Promote version 1, then version 2. Record a simulated latency regression and
# roll back to archived version 1. Confirm one production version remains and the event
# trail preserves action, target, and reason.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 8 — Relate the lab to MLflow
# Prompt: Map snapshot, manifest, metrics, and stages to local MLflow concepts from Day
# 53. MLflow can store evidence; it does not define your compatibility or approval policy
# automatically.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 9 — rebuild a bundle deterministically
# Prompt: Build the JSON model bundle twice from canonical records and the same
# configuration. Compare manifest/artifact hashes and diagnose any nondeterministic field
# such as timestamps, path order, or float serialization.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 10 — write a claim-bounded model card
# Prompt: Create a model card from the manifest and evaluation evidence: intended and
# excluded use, population, metric/threshold, slices/support, data provenance,
# limitations, monitoring, owners, and stop conditions.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 11 — design shadow and canary evidence
# Prompt: Specify a no-side-effect shadow comparison followed by a bounded canary. Define
# routing, success/guardrail metrics, sample/time minimums, stop rules, rollback, and how
# delayed labels are handled.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 12 — separate drift from compatibility
# Prompt: Create examples of schema incompatibility, valid schema with shifted
# distribution, and stable inputs with performance degradation. Route each to reject,
# monitor/investigate, or rollback/retrain policy.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 13 — test forward and backward compatibility
# Prompt: Build a matrix of producer/consumer schema and model versions. Test an additive
# optional field, required rename, reordered feature, and changed numeric meaning across
# old/new readers.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 14 — capture dependency and supply-chain evidence
# Prompt: Create a local release manifest containing reviewed lock hash, direct runtime
# requirements, Python range, package major versions, artifact hashes, source
# revision/dirty flag, and a generated component inventory.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 15 — verify artifact trust before parsing
# Prompt: Model a trusted local manifest root and verify every bundle file's relative
# path, size, and SHA-256 before JSON parsing. Reject path traversal, symlink escape,
# extra required files, and pickle.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 16 — rehearse rollback dependency failure
# Prompt: Archive version 1, promote version 2, then discover that version 1's runtime
# dependency is unavailable. Define rollback-target readiness, fallback decision, event
# trail, and prevention.
# Evidence: add a boundary check and explain the failure policy.
#
# === End numbered professional practice ===

if __name__ == "__main__":
    self_check()
