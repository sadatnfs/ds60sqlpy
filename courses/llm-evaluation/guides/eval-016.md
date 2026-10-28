# eval-016: A reproducible evaluation decision packet

## Starting point and outcome

Advanced; approximately 120 minutes. Direct prerequisites: `eval-013`, `eval-015`.

Compute and seal a complete held-out decision packet from the connected synthetic ledger, preserving all failed and unknown conditions.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-016`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## The deliverable is a reconstructable argument

An evaluation report should let another analyst reconstruct the population, data, transformations, estimates and decision. A single leaderboard number cannot explain whether a system met its intended use, which failures occurred or what remains unknown. The Research Support Desk case therefore ends its evaluation sequence with a small decision packet.

The packet records a protocol identity, system versions, dataset identity, eligibility and labeling rules, effect and uncertainty estimates, coverage and operational constraints. Every gate has a named criterion and evidence status. A no-go result can be a complete and useful evaluation when it identifies what failed and what new evidence would support reconsideration.

A content digest binds a serialized artifact to its bytes under a declared encoding. It detects later modification when compared with a trusted recorded digest. It does not establish who created the artifact, whether the protocol was followed or whether the scientific assumptions are valid. Authentication, access control and study validity are separate concerns.

## Worked case A: calculate the packet from the held-out ledger

The complete program embeds the shared synthetic fixture and selects only its operations and policy families, both assigned to the test partition. It requires labels for every eligible held-out request to be available by day 6. If any label is still missing, the program rejects the final packet instead of silently dropping that request. The training and development families do not enter the final calculation. Eight eligible requests remain. The program computes paired correctness differences, averages them within family, enumerates the four empirical family-bootstrap draws and records inverse-CDF percentile endpoints.

The estimated equal-family effect is zero, with an empirical interval from -0.25 to 0.25. Answer coverage is 0.75, one critical failure is present, and the maximum latency is 160 milliseconds. Under the authored thresholds, all four quantitative gates fail. The memo is no-go and preserves each reason. With only two synthetic families, this interval demonstrates the computation and its weakness; it is not reliable population evidence.

```python
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
```

## Worked case B: retain exact evidence through a review

The second program seals the computed packet using canonical JSON and checks it before use. Changing a score without updating the recorded digest is rejected. The original packet remains available. This is a small artifact-integrity mechanism, not a cryptographic signature or a substitute for an experiment registry with controlled access.

```python
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


def worked_b():
    import copy

    original = fixture()
    identity = digest(original)
    assert verified_packet(original, identity)["decision"] == "no-go"
    changed = copy.deepcopy(original)
    changed["coverage"] = 0.95
    try:
        verified_packet(changed, identity)
    except ValueError:
        pass
    else:
        raise AssertionError("Changed evidence accepted")
    assert original["coverage"] == 0.75
    upper = 1 - 0.05 ** (1 / 200)
    assert 0 < upper < 0.02
    print("Original evidence retained; mutation detected; hypothetical zero-of-200 bound:", upper)


worked_b()
```

## What the written decision should contain

State the intended users and request population, system configuration and allowed actions. Describe data selection, group/time splitting, annotation and adjudication. Give effect estimates and uncertainty using the declared sampling unit. Include missing-label coverage, abstention behavior, important slices, retrieval/evidence diagnostics, critical failures, latency and cost where relevant.

Explain the selection history. A final score should identify which choices were frozen before final assessment. If a model was revised after a failed test, identify the new development cycle and the independent evidence used afterward. Keep original failed results rather than replacing them with a later successful summary.

## Limits and follow-up

Small synthetic data can establish arithmetic and software behavior, but not a real product's quality. The effect interval here is actually computed from the held-out family differences, and the packet names its two-family limitation. More resamples would not add independent families. The second case also computes a separate hypothetical one-sided binomial upper bound \(1-\alpha^{1/n}\) for zero failures in 200 independent trials. It is not the failure rate from the main ledger, which has one observed critical failure. This calculation explains why even a hypothetical zero-failure campaign does not establish zero population risk.

A responsible memo identifies which conditions could change the decision: more independent families, mature labels, a corrected access policy, an altered target mix or a different cost assumption. Define monitoring and rollback owners before a rollout. The planned monitoring rule should match the promised decision, including how uncertain and missing signals are handled.

The six investigations ask you to vary a real gate, trace an artifact change and explain an inference limit. They do not ask you to turn every no-go into a go. The objective is a transparent decision that follows its declared evidence, including a decision to withhold deployment.


## Six investigations

### 1. Change one constraint

Raise coverage to 0.9 while keeping the other authored inputs.

**Expected:** Only the coverage gate passes; quality, critical cases and latency still fail.

**Hint:** Recompute each named gate.

### 2. Keep a missing protocol result

Replace protocol_frozen with None.

**Expected:** The protocol gate fails.

**Hint:** Unknown evidence cannot satisfy an explicit True requirement.

### 3. Preserve a critical failure

Set critical_failures to 1.

**Expected:** The critical-case gate fails even if quality improves.

**Hint:** Required constraints are not weighted into an average.

### 4. Interpret zero incidents

Explain the positive bound for a separate hypothetical campaign with zero failures in 200 trials.

**Expected:** Finite observations do not imply zero population risk.

**Hint:** State the binomial and sampling assumptions.

### 5. Detect an artifact edit

Change coverage after sealing the packet.

**Expected:** Verification rejects the old digest.

**Hint:** Recompute canonical serialized bytes.

### 6. Write a bounded memo

Summarize the failed packet in three sentences.

**Expected:** State no-go, all four failing conditions and the independent evidence needed next.

**Hint:** Do not remove unfavorable results.

## Primary references

- [Model cards and reporting](https://arxiv.org/abs/1810.03993)
- [Existing integrated scientific workflow](../../../courses/statistics-ml/tutorials/science/07-integrated-scientific-workflow.md)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
