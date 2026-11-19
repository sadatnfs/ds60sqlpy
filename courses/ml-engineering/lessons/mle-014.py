"""mle-014: both worked cases; complete the guide's six changes."""

import hashlib

import numpy as np


def example_one():
    assignments = [
        int(hashlib.sha256(f"entity:{i}".encode()).hexdigest()[:8], 16) % 100 for i in range(100)
    ]
    small = {i for i, bucket in enumerate(assignments) if bucket < 10}
    larger = {i for i, bucket in enumerate(assignments) if bucket < 25}
    assert small <= larger and len(small) > 0 and len(larger) < 100
    assert assignments == [
        int(hashlib.sha256(f"entity:{i}".encode()).hexdigest()[:8], 16) % 100 for i in range(100)
    ]
    return {
        "stable_cohort": True,
        "nested_ramp": True,
        "small_n": len(small),
        "larger_n": len(larger),
    }


def example_two():
    old = np.array([0.1, 0.3, 0.6, 0.9])
    candidate = np.array([0.2, 0.4, 0.7, 0.8])
    disagreement = int(np.sum((old >= 0.5) != (candidate >= 0.5)))
    assert disagreement == 0 and np.max(np.abs(old - candidate)) > 0
    accepted = bool(np.max(np.abs(old - candidate)) <= 0.15)
    assert accepted
    return {
        "shadow_disagreement": disagreement,
        "prediction_change_exists": True,
        "no_causal_effect_claim": True,
    }


if __name__ == "__main__":
    print(example_one())
    print(example_two())

# TODO 1: Compare stable customer assignment with per-request random assignment.
# TODO 2: Add an explicit assignment-version field.
# TODO 3: Compare score deltas even when decisions agree.
# TODO 4: Define acceptable errors and latency for a candidate.
# TODO 5: Explain what shadow predictions cannot establish about outcomes.
# TODO 6: Specify the accepted version and state needed if a ramp stops.
