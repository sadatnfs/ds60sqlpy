"""mle-014: worked starting point; complete the guide's six changes."""

import hashlib


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


if __name__ == "__main__":
    print(example_one())

# TODO 1: Compare stable customer assignment with per-request random assignment.
# TODO 2: Add an explicit assignment-version field.
# TODO 3: Compare score deltas even when decisions agree.
# TODO 4: Define acceptable errors and latency for a candidate.
# TODO 5: Explain what shadow predictions cannot establish about outcomes.
# TODO 6: Specify the accepted version and state needed if a ramp stops.
