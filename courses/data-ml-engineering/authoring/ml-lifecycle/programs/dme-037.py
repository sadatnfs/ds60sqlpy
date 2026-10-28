"""Bind real training to ordered data, configuration and numerical evidence."""

import hashlib
import importlib.metadata
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier

from ds60sqlpy.plot_artifacts import publish_report, publish_table


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def dataset():
    rng = np.random.default_rng(2037)
    x = rng.normal(size=(160, 2))
    y = (x[:, 0] - 0.6 * x[:, 1] + rng.normal(scale=0.8, size=len(x)) > 0).astype(int)
    return [
        {"id": i, "features": row.tolist(), "label": int(label)}
        for i, (row, label) in enumerate(zip(x, y, strict=True))
    ]


def environment_identity():
    return {
        "python": ".".join(map(str, sys.version_info[:3])),
        "packages": {name: importlib.metadata.version(name) for name in ("numpy", "scikit-learn")},
    }


def accept_evidence(accepted, identity, probabilities):
    candidate = digest(probabilities)
    if identity in accepted and accepted[identity] != candidate:
        raise ValueError("Different output already exists for this recipe identity")
    accepted[identity] = candidate


def train(rows, seed=37):
    if not rows or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Training rows require unique stable identities")
    configuration = {"n_estimators": 32, "max_depth": 4, "random_state": seed, "n_jobs": 1}
    ordered_sha = digest(rows)
    relation_sha = digest(sorted(rows, key=lambda row: row["id"]))
    identity = {
        "algorithm": "sklearn.ensemble.RandomForestClassifier",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "ordered_data_sha256": ordered_sha,
        "configuration": configuration,
        "environment": environment_identity(),
        "feature_names": ["signal", "load"],
        "feature_units": ["dimensionless", "dimensionless"],
    }
    model = RandomForestClassifier(**configuration)
    model.fit(np.array([row["features"] for row in rows]), np.array([row["label"] for row in rows]))
    probe = np.array([[-1.0, 0.0], [0.0, 0.0], [1.0, 0.0], [1.0, 2.0]])
    probabilities = model.predict_proba(probe)[:, 1].tolist()
    return {
        "recipe_sha256": digest(identity),
        "identity": identity,
        "unordered_relation_sha256": relation_sha,
        "probe_probabilities": probabilities,
        "numerical_tolerance": {"relative": 0.0, "absolute": 1e-12},
    }


def example_one():
    rows = dataset()
    first, repeated = train(rows), train(rows)
    assert first["recipe_sha256"] == repeated["recipe_sha256"]
    delta = float(
        np.max(np.abs(np.array(first["probe_probabilities"]) - repeated["probe_probabilities"]))
    )
    assert np.allclose(
        first["probe_probabilities"], repeated["probe_probabilities"], rtol=0, atol=1e-12
    )
    return {
        "first": first,
        "repeat_max_absolute_error": delta,
        "same_process_and_prepared_environment": True,
        "cross_platform_bitwise_claim": False,
    }


def example_two():
    rows = dataset()
    original, changed_seed, reordered = (
        train(rows),
        train(rows, seed=38),
        train(list(reversed(rows))),
    )
    assert len({r["recipe_sha256"] for r in (original, changed_seed, reordered)}) == 3
    assert original["unordered_relation_sha256"] == reordered["unordered_relation_sha256"]
    assert (
        original["identity"]["ordered_data_sha256"] != reordered["identity"]["ordered_data_sha256"]
    )
    accepted = {}
    accept_evidence(accepted, original["recipe_sha256"], original["probe_probabilities"])
    original_evidence = accepted.copy()
    conflicting_output = [0.0] * len(original["probe_probabilities"])
    conflict_rejected = False
    try:
        accept_evidence(accepted, original["recipe_sha256"], conflicting_output)
    except ValueError:
        conflict_rejected = True
    assert conflict_rejected and accepted == original_evidence
    return {
        "original_id": original["recipe_sha256"],
        "changed_seed_id": changed_seed["recipe_sha256"],
        "reordered_input_id": reordered["recipe_sha256"],
        "same_relation_different_computation_order": True,
        "changed_seed_probabilities": changed_seed["probe_probabilities"],
        "reordered_probabilities": reordered["probe_probabilities"],
        "conflicting_evidence_rejected": conflict_rejected,
    }


def main():
    first, second = example_one(), example_two()
    probabilities = first["first"]["probe_probabilities"]
    publish_table(
        [
            "probe",
            "original probability",
            "changed-seed probability",
            "reordered-input probability",
        ],
        [
            [index, original, changed, reordered]
            for index, (original, changed, reordered) in enumerate(
                zip(
                    probabilities,
                    second["changed_seed_probabilities"],
                    second["reordered_probabilities"],
                    strict=True,
                ),
                start=1,
            )
        ],
        description="Actual forest predictions: repeated, changed seed and reordered input",
    )
    publish_report(
        {"case_one": first, "case_two": second},
        description="Input and environment identities with local numerical tolerances",
    )
    print(json.dumps({"case_one": first, "case_two": second}, allow_nan=False))
    print("dme-037: two reproducibility cases passed")


if __name__ == "__main__":
    main()
