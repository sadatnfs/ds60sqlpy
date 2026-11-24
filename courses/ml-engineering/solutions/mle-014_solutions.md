# mle-014: explained reference

Design stable routing and shadow comparisons with bounded conclusions.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Change the assignment key

Choose the unit from the experiment or rollout design and retain it consistently. Do not assume request-level assignment answers an entity-level question.

With the sha256 rule on f"entity:{i}", the 10 percent ramp selects 8 of 100 entities (0, 27, 35, 43, 60, 77, 89 and 92) and the 25 percent ramp selects 19, and every repeat gives the same sets. Per-request random.random() < 0.10 would put the same customer in both arms across requests, so no customer has a single experience to measure.

**Expected:** The cohort interpretation changes.

## 2. Record a salt/version

Changing it can reassign entities. Treat that as a reviewed change rather than an invisible implementation detail.

Prefixing the key with "v2:" changes the 10 percent cohort to 15 entities, only 2 of which were in the original 8. Recording assignment_version beside each prediction makes that reassignment visible; without it, a jump in the cohort's metrics could be mistaken for a model effect.

**Expected:** The routing rule is reproducible.

## 3. Inspect probabilities

Use appropriate numeric and calibration diagnostics alongside action disagreement. A small label difference does not prove equivalent probabilities.

In example_two every probability moves by exactly 0.1, so disagreement is 0 while the first customer's score doubles from 0.1 to 0.2. Reporting only the 0 disagreement would hide that change. Print np.abs(old - candidate) and confirm the maximum is 0.1, under the 0.15 acceptance limit.

**Expected:** The confidence change remains visible.

## 4. Add operational limits

Use actual service observations and a rollback rule. The local project supplies bounded HTTP/monitoring checks; production capacity needs separate evidence.

Write limits as quantities the local checker can measure, for example the fraction of 5xx responses and p95 latency over a fixed number of requests, each with the action taken when exceeded. The 0.15 score-delta limit in example_two is a prediction check and says nothing about latency. A limit such as "be careful with errors" cannot fail, so it cannot trigger a pause either.

**Expected:** The policy names measured quantities and responses.

## 5. Avoid a causal claim

Use an appropriate randomized or otherwise identified design for that question, with interference, exposure and metric assumptions made explicit.

Shadow scoring never changes an action, so the outcomes observed are those produced by the old model's decisions. Even if the candidate would have offered support to someone, their outcome without the offer is what was recorded.

**Expected:** They do not establish the effect of changed actions.

## 6. Plan rollback

Restore model and feature compatibility, reconcile in-flight work and record the reason. A pointer switch alone is not every possible recovery requirement.

Keep the previous model, its feature contract and the assignment version together. Rolling back only the model while the 19-entity cohort's feature version remains newer could reintroduce a train/serve mismatch. Test the rollback by scoring the same four rows from example_two after reverting and confirming the old probabilities 0.1, 0.3, 0.6 and 0.9 come back exactly.

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

Separate interface, operational and causal evidence, and retain a compatible rollback target before expanding exposure.
