# polars-006: explained reference

Enrich a fact table while proving its grain and totals remain valid.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Prove the expected key

Use n_unique and a duplicate-frequency table. The join validator and the independent key check catch related errors through different evidence.

**Expected:** Unique customer count equals dimension height.

## 2. Reconcile a total

Keep both row and amount checks: some duplicated or dropped zero-valued records can leave a total unchanged.

**Expected:** The total remains 21.

## 3. Make a membership query

A semi join expresses existence directly. Joining and dropping columns afterward still permits fanout.

**Expected:** Each matching order appears once.

## 4. Audit unmatched rows

The anti join produces a reviewable quarantine set. Decide whether the missing dimension is late, invalid or genuinely outside the domain.

**Expected:** The new order is explicitly listed.

## 5. Handle duplicate history

A changing dimension may require a time-qualified join. Arbitrarily keeping first or last can attach future information to past facts.

**Expected:** The answer distinguishes historical versions from accidental duplicates.

## 6. Define null-key policy

Use a known sentinel only if its meaning is explicitly a shared entity. Otherwise preserve unmatched missing keys for diagnosis.

**Expected:** Only the explicit policy matches them.

## Complete reference

```python
"""polars-006: complete bounded Polars investigation."""

import polars as pl


def example_one():
    facts = pl.DataFrame({"order_id": [1, 2, 3], "customer": [10, 10, 20], "amount": [5, 7, 9]})
    dimension = pl.DataFrame({"customer": [10, 20], "region": ["N", "S"]})
    joined = facts.join(dimension, on="customer", how="left", validate="m:1")
    assert joined.height == 3 and joined["amount"].sum() == 21
    bad = pl.concat([dimension, dimension.head(1)])
    inflated = facts.join(bad, on="customer", how="left")
    assert inflated.height == 5 and inflated["amount"].sum() == 33
    try:
        facts.join(bad, on="customer", how="left", validate="m:1")
    except pl.exceptions.ComputeError:
        rejected = True
    else:
        rejected = False
    assert rejected
    return {"correct_total": 21, "fanout_total": 33, "validation_rejected_duplicate": rejected}


def example_two():
    left = pl.DataFrame({"id": [1, 2, 3], "key": [10, 20, None]})
    right = pl.DataFrame({"key": [10, None]})
    assert left.join(right, on="key", how="semi")["id"].to_list() == [1]
    assert left.join(right, on="key", how="anti").sort("id")["id"].to_list() == [2, 3]
    assert left.join(right, on="key", how="semi", nulls_equal=True).sort("id")["id"].to_list() == [
        1,
        3,
    ]
    return {"known": [1], "unmatched_or_missing": [2, 3], "explicit_null_matching": [1, 3]}


def main():
    print(example_one())
    print(example_two())
    print("polars-006 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Enrich a fact table while proving its grain and totals remain valid. Extend the exercise with a legitimate historical dimension, then document the additional temporal rule required. Carry the same reconciliation into dbt tests and ML feature pipelines, where silent fanout can contaminate both training labels and online metrics.
