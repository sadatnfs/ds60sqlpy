# mle-005: explained reference

Design evaluation around the target population and information boundary.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Define the deployment entity

Use grouped separation for an unseen-entity claim and a suitable time design for returning entities. State the population explicitly.

In example_one the same six customers give 1.0 when they are all seen in training and 0.5 when customers 1 and 4 are held out; neither number is wrong, but each answers a different question. Reporting 1.0 for a launch to new customers would describe a lookup table, not a model.

**Expected:** The split follows that question.

## 2. Audit overlap

Retain group identity in the evaluation ledger. A row-only overlap check can miss memorization leakage.

In example_two the id sets are disjoint, yet test ids 80 to 119 cover all 12 customer_id values, every one of which also appears in train. So row overlap is 0 while customer overlap is 12 of 12. Print both: set(train.id) & set(test.id) is empty and set(train.customer_id) & set(test.customer_id) has 12 members.

**Expected:** The two overlap questions are reported separately.

## 3. Protect label timing

Physical availability in today's dataset is different from historical eligibility. Preserve the label-availability clock.

The filter must keep both terms. Dropping label_available_at <= cutoff gives 80 training rows instead of 77, adding ids 77, 78 and 79 whose labels arrive at 181 to 183. The assertion train.label_available_at.max() <= cutoff then fails, which is the signal that future knowledge entered training.

**Expected:** The training maturity assertion holds.

## 4. Choose a threshold honestly

Evaluate the whole selected procedure on protected data, or use a resampling design that includes selection. Do not report the best inspected holdout result as an unbiased estimate.

Picking the threshold on the 40 test rows and reporting accuracy on the same 40 makes the reported number optimistic by construction. Split the 77 training rows by time, choose on the later part, then score the frozen threshold once on the 40.

**Expected:** It uses an appropriate development/validation stage.

## 5. Test another fallback

The observed fraction is not a population guarantee. Use a representative evaluation and uncertainty analysis for a real claim.

Try training.get(c, 0): customers 1 and 4 have labels 0 and 1, so a constant 0 also scores 0.5, just as constant 1 did. That is a useful surprise: with one positive and one negative held out, any constant fallback scores 0.5. To see the score move, hold out {1, 2}, whose labels are both 0; fallback 1 then scores 0.0 and fallback 0 scores 1.0, showing how little two held-out customers can support.

**Expected:** The cold-start score changes under that policy.

## 6. Record the evaluation contract

Retain the data/source version, groups, cutoffs, label maturity, selection process and uncertainty limits alongside the result.

For this lesson the record needs the generator seed 17, the 120-row dataset, the cutoff 180, the label rule cutoff + 4, the 77/40 split sizes, the held-out customer set and the fallback value. Missing any one of those makes 0.5 or 1.0 impossible to reproduce.

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

Demonstrate the difference between repeat-entity, cold-start and future-time questions, and retain the complete selection/evaluation procedure with the resulting metrics.
