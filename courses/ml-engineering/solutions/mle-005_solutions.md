# mle-005: explained reference

Design evaluation around the target population and information boundary.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Define the deployment entity

Use grouped separation for an unseen-entity claim and a suitable time design for returning entities. State the population explicitly.

**Expected:** The split follows that question.

## 2. Audit overlap

Retain group identity in the evaluation ledger. A row-only overlap check can miss memorization leakage.

**Expected:** The two overlap questions are reported separately.

## 3. Protect label timing

Physical availability in today's dataset is different from historical eligibility. Preserve the label-availability clock.

**Expected:** The training maturity assertion holds.

## 4. Choose a threshold honestly

Evaluate the whole selected procedure on protected data, or use a resampling design that includes selection. Do not report the best inspected holdout result as an unbiased estimate.

**Expected:** It uses an appropriate development/validation stage.

## 5. Test another fallback

The observed fraction is not a population guarantee. Use a representative evaluation and uncertainty analysis for a real claim.

**Expected:** The cold-start score changes under that policy.

## 6. Record the evaluation contract

Retain the data/source version, groups, cutoffs, label maturity, selection process and uncertainty limits alongside the result.

**Expected:** The record explains the generalization target.

## Complete reference

```python
"""mle-005: local, bounded ML engineering investigation."""

import numpy as np
import pandas as pd


def dataset():
    rng = np.random.default_rng(17)
    n = 120
    usage = rng.uniform(1, 100, n)
    tickets = rng.poisson(2, n)
    region = np.where(np.arange(n) % 2 == 0, "north", "south")
    logit = 0.9 * tickets - 0.035 * usage + (region == "north") * 0.3
    probability = 1 / (1 + np.exp(-logit))
    label = (rng.random(n) < probability).astype(int)
    cutoff = np.arange(n) + 100
    return pd.DataFrame(
        {
            "id": np.arange(n),
            "customer_id": np.arange(n) % 12,
            "cutoff": cutoff,
            "available_at": cutoff - 2,
            "label_available_at": cutoff + 4,
            "usage": usage,
            "tickets": tickets,
            "region": region,
            "label": label,
        }
    )


def example_one():
    customers = np.arange(6)
    labels = np.array([0, 0, 0, 1, 1, 1])
    memory = dict(zip(customers, labels, strict=True))
    repeated_predictions = np.array([memory[int(c)] for c in customers])
    assert float(np.mean(repeated_predictions == labels)) == 1.0
    held_out = {1, 4}
    training = {int(c): int(y) for c, y in zip(customers, labels, strict=True) if c not in held_out}
    cold = np.array([training.get(c, 1) for c in sorted(held_out)])
    actual = labels[sorted(held_out)]
    assert float(np.mean(cold == actual)) == 0.5
    return {
        "repeated_entity_accuracy": 1.0,
        "unseen_entity_accuracy": 0.5,
        "target_population_changed": True,
    }


def example_two():
    frame = dataset()
    cutoff = 180
    train = frame[(frame.cutoff < cutoff) & (frame.label_available_at <= cutoff)]
    test = frame[frame.cutoff >= cutoff]
    assert set(train.id).isdisjoint(test.id)
    assert train.cutoff.max() < test.cutoff.min()
    assert train.label_available_at.max() <= cutoff
    return {
        "training_rows": len(train),
        "test_rows": len(test),
        "training_label_cutoff": int(train.label_available_at.max()),
    }


def main():
    print(example_one())
    print(example_two())
    print("mle-005 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Design evaluation around the target population and information boundary. Demonstrate the difference between repeat-entity, cold-start and future-time questions, and retain the complete selection/evaluation procedure with the resulting metrics.
