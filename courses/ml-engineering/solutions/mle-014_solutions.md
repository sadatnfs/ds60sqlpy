# mle-014: explained reference

Design stable routing and shadow comparisons with bounded conclusions.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Change the assignment key

Choose the unit from the experiment or rollout design and retain it consistently. Do not assume request-level assignment answers an entity-level question.

**Expected:** The cohort interpretation changes.

## 2. Record a salt/version

Changing it can reassign entities. Treat that as a reviewed change rather than an invisible implementation detail.

**Expected:** The routing rule is reproducible.

## 3. Inspect probabilities

Use appropriate numeric and calibration diagnostics alongside action disagreement. A small label difference does not prove equivalent probabilities.

**Expected:** The confidence change remains visible.

## 4. Add operational limits

Use actual service observations and a rollback rule. The local project supplies bounded HTTP/monitoring checks; production capacity needs separate evidence.

**Expected:** The policy names measured quantities and responses.

## 5. Avoid a causal claim

Use an appropriate randomized or otherwise identified design for that question, with interference, exposure and metric assumptions made explicit.

**Expected:** They do not establish the effect of changed actions.

## 6. Plan rollback

Restore model and feature compatibility, reconcile in-flight work and record the reason. A pointer switch alone is not every possible recovery requirement.

**Expected:** A compatible prior bundle is retained.

## Complete reference

```python
"""mle-014: local, bounded ML engineering investigation."""

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


def main():
    print(example_one())
    print(example_two())
    print("mle-014 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Design stable routing and shadow comparisons with bounded conclusions. Separate interface, operational and causal evidence, and retain a compatible rollback target before expanding exposure.
