import hashlib
import json
from itertools import product

import numpy as np

RECORDS = [
    {
        "request_id": "metrics-1",
        "family_id": "metrics",
        "segment": "routine",
        "split": "train",
        "event_day": 1,
        "label_day": 3,
        "baseline_correct": 1,
        "candidate_correct": 1,
        "candidate_answered": True,
        "candidate_confidence": 0.95,
        "candidate_latency_ms": 100,
        "critical_error": False,
    },
    {
        "request_id": "metrics-2",
        "family_id": "metrics",
        "segment": "routine",
        "split": "train",
        "event_day": 2,
        "label_day": 4,
        "baseline_correct": 1,
        "candidate_correct": 1,
        "candidate_answered": True,
        "candidate_confidence": 0.7,
        "candidate_latency_ms": 120,
        "critical_error": False,
    },
    {
        "request_id": "metrics-3",
        "family_id": "metrics",
        "segment": "routine",
        "split": "train",
        "event_day": 3,
        "label_day": 5,
        "baseline_correct": 1,
        "candidate_correct": 1,
        "candidate_answered": True,
        "candidate_confidence": 0.65,
        "candidate_latency_ms": 140,
        "critical_error": False,
    },
    {
        "request_id": "metrics-4",
        "family_id": "metrics",
        "segment": "routine",
        "split": "train",
        "event_day": 4,
        "label_day": 6,
        "baseline_correct": 0,
        "candidate_correct": 0,
        "candidate_answered": False,
        "candidate_confidence": 0.3,
        "candidate_latency_ms": 160,
        "critical_error": False,
    },
    {
        "request_id": "retrieval-1",
        "family_id": "retrieval",
        "segment": "routine",
        "split": "development",
        "event_day": 1,
        "label_day": 3,
        "baseline_correct": 1,
        "candidate_correct": 1,
        "candidate_answered": True,
        "candidate_confidence": 0.95,
        "candidate_latency_ms": 100,
        "critical_error": False,
    },
    {
        "request_id": "retrieval-2",
        "family_id": "retrieval",
        "segment": "routine",
        "split": "development",
        "event_day": 2,
        "label_day": 4,
        "baseline_correct": 1,
        "candidate_correct": 1,
        "candidate_answered": True,
        "candidate_confidence": 0.7,
        "candidate_latency_ms": 120,
        "critical_error": False,
    },
    {
        "request_id": "retrieval-3",
        "family_id": "retrieval",
        "segment": "routine",
        "split": "development",
        "event_day": 3,
        "label_day": 5,
        "baseline_correct": 0,
        "candidate_correct": 1,
        "candidate_answered": True,
        "candidate_confidence": 0.65,
        "candidate_latency_ms": 140,
        "critical_error": False,
    },
    {
        "request_id": "retrieval-4",
        "family_id": "retrieval",
        "segment": "routine",
        "split": "development",
        "event_day": 4,
        "label_day": 6,
        "baseline_correct": 0,
        "candidate_correct": 0,
        "candidate_answered": False,
        "candidate_confidence": 0.3,
        "candidate_latency_ms": 160,
        "critical_error": False,
    },
    {
        "request_id": "operations-1",
        "family_id": "operations",
        "segment": "rare",
        "split": "test",
        "event_day": 1,
        "label_day": 3,
        "baseline_correct": 1,
        "candidate_correct": 1,
        "candidate_answered": True,
        "candidate_confidence": 0.95,
        "candidate_latency_ms": 100,
        "critical_error": False,
    },
    {
        "request_id": "operations-2",
        "family_id": "operations",
        "segment": "rare",
        "split": "test",
        "event_day": 2,
        "label_day": 4,
        "baseline_correct": 0,
        "candidate_correct": 0,
        "candidate_answered": True,
        "candidate_confidence": 0.7,
        "candidate_latency_ms": 120,
        "critical_error": False,
    },
    {
        "request_id": "operations-3",
        "family_id": "operations",
        "segment": "rare",
        "split": "test",
        "event_day": 3,
        "label_day": 5,
        "baseline_correct": 1,
        "candidate_correct": 0,
        "candidate_answered": True,
        "candidate_confidence": 0.65,
        "candidate_latency_ms": 140,
        "critical_error": True,
    },
    {
        "request_id": "operations-4",
        "family_id": "operations",
        "segment": "rare",
        "split": "test",
        "event_day": 4,
        "label_day": 6,
        "baseline_correct": 0,
        "candidate_correct": 0,
        "candidate_answered": False,
        "candidate_confidence": 0.3,
        "candidate_latency_ms": 160,
        "critical_error": False,
    },
    {
        "request_id": "policy-1",
        "family_id": "policy",
        "segment": "rare",
        "split": "test",
        "event_day": 1,
        "label_day": 3,
        "baseline_correct": 0,
        "candidate_correct": 1,
        "candidate_answered": True,
        "candidate_confidence": 0.95,
        "candidate_latency_ms": 100,
        "critical_error": False,
    },
    {
        "request_id": "policy-2",
        "family_id": "policy",
        "segment": "rare",
        "split": "test",
        "event_day": 2,
        "label_day": 4,
        "baseline_correct": 1,
        "candidate_correct": 1,
        "candidate_answered": True,
        "candidate_confidence": 0.7,
        "candidate_latency_ms": 120,
        "critical_error": False,
    },
    {
        "request_id": "policy-3",
        "family_id": "policy",
        "segment": "rare",
        "split": "test",
        "event_day": 3,
        "label_day": 5,
        "baseline_correct": 0,
        "candidate_correct": 1,
        "candidate_answered": True,
        "candidate_confidence": 0.65,
        "candidate_latency_ms": 140,
        "critical_error": False,
    },
    {
        "request_id": "policy-4",
        "family_id": "policy",
        "segment": "rare",
        "split": "test",
        "event_day": 4,
        "label_day": 6,
        "baseline_correct": 1,
        "candidate_correct": 0,
        "candidate_answered": False,
        "candidate_confidence": 0.3,
        "candidate_latency_ms": 160,
        "critical_error": False,
    },
]


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def gates(packet):
    return {
        "quality": packet["effect_lower"] >= packet["minimum_effect"],
        "coverage": packet["coverage"] >= packet["required_coverage"],
        "critical_cases": packet["critical_failures"] == 0,
        "protocol_frozen": packet["protocol_frozen"] is True,
        "latency": packet["latency_ms"] <= packet["latency_limit_ms"],
    }


def decide(packet):
    checks = gates(packet)
    return {
        "decision": "go" if all(checks.values()) else "no-go",
        "failed": [k for k, v in checks.items() if not v],
    }


def fixture():
    rows = [r for r in RECORDS if r["split"] == "test" and r["event_day"] <= 6]
    if not rows or any(r["label_day"] > 6 for r in rows):
        raise ValueError("Final decision requires mature labels for every eligible request")
    assert len({r["request_id"] for r in rows}) == len(rows)
    families = sorted({r["family_id"] for r in rows})
    means = np.array(
        [
            np.mean(
                [
                    r["candidate_correct"] - r["baseline_correct"]
                    for r in rows
                    if r["family_id"] == family
                ]
            )
            for family in families
        ]
    )
    assert len(families) == 2
    resamples = np.array(
        [np.mean(means[list(indices)]) for indices in product(range(len(means)), repeat=len(means))]
    )
    bounds = np.quantile(resamples, [0.025, 0.975], method="inverted_cdf")
    return {
        "protocol": "desk-eval-v1",
        "system": "candidate-v1",
        "dataset_sha256": digest(rows),
        "eligible_ids": [r["request_id"] for r in rows],
        "families": families,
        "effect_estimate": float(means.mean()),
        "effect_lower": float(bounds[0]),
        "effect_upper": float(bounds[1]),
        "minimum_effect": 0.02,
        "coverage": float(np.mean([r["candidate_answered"] for r in rows])),
        "required_coverage": 0.85,
        "critical_failures": sum(r["critical_error"] for r in rows),
        "protocol_frozen": True,
        "latency_ms": max(r["candidate_latency_ms"] for r in rows),
        "latency_limit_ms": 150,
        "uncertainty_method": (
            "exact empirical family bootstrap, inverse-CDF percentiles; two synthetic families only"
        ),
    }


def verified_packet(packet, expected):
    if digest(packet) != expected:
        raise ValueError("Evidence artifact changed")
    return decide(packet)


def worked_a():
    packet = fixture()
    decision = decide(packet)
    assert decision == {
        "decision": "no-go",
        "failed": ["quality", "coverage", "critical_cases", "latency"],
    }
    assert len(packet["eligible_ids"]) == 8 and packet["coverage"] == 0.75
    assert (
        packet["effect_estimate"] == 0
        and packet["effect_lower"] == -0.25
        and packet["effect_upper"] == 0.25
    )
    assert packet["critical_failures"] == 1
    print("Held-out decision packet:", json.dumps(packet, sort_keys=True))
    print("Decision:", decision)


worked_a()

# Task 1: Raise coverage to 0.9 while keeping the other authored inputs.
# Task 2: Replace protocol_frozen with None.
# Task 3: Set critical_failures to 1.
# Task 4: Explain the positive bound for a separate hypothetical campaign with zero
# failures in 200 trials.
# Task 5: Change coverage after sealing the packet.
# Task 6: Summarize the failed packet in three sentences.

# Implement your six changes below.
