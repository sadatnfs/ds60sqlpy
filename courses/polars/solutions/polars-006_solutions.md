# polars-006: explained reference

Enrich a fact table while proving its grain and totals remain valid.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Prove the expected key

Use n_unique and a duplicate-frequency table. The join validator and the independent key check catch related errors through different evidence.

**Why it holds here:** The dimension holds customers 10 and 20 on two rows, so n_unique equals height and each fact row can find at most one region.

**Plausible wrong approach:** Relying only on the fact that the join executed proves nothing about uniqueness; a duplicated dimension joins happily and returns 5 rows.

**How to verify:** Assert dimension['customer'].n_unique() == dimension.height and inspect dimension.group_by('customer').len() for any count above 1.

**Expected:** Unique customer count equals dimension height.

## 2. Reconcile a total

Keep both row and amount checks: some duplicated or dropped zero-valued records can leave a total unchanged.

**Why it holds here:** A valid many to one left join keeps the 3 facts, so amounts 5, 7 and 9 still sum to 21. Checking height as well catches a case where a zero amount row is duplicated or dropped.

**Plausible wrong approach:** Checking only the total misses such cases, and with the duplicated dimension the result already fails at 5 rows and a total of 33.

**How to verify:** Assert joined.height == facts.height == 3 and joined['amount'].sum() == 21 after the join with validate='m:1'.

**Expected:** The total remains 21.

## 3. Make a membership query

A semi join expresses existence directly. Joining and dropping columns afterward still permits fanout.

```python
import polars as pl

facts = pl.DataFrame({"order_id": [1, 2, 3], "customer": [10, 10, 20], "amount": [5, 7, 9]})
dimension = pl.DataFrame({"customer": [10, 20], "region": ["N", "S"]})
known = facts.join(dimension, on="customer", how="semi")
assert known.columns == ["order_id", "customer", "amount"]
assert known.sort("order_id")["order_id"].to_list() == [1, 2, 3]
duplicated = pl.concat([dimension, dimension.head(1)])
assert facts.join(duplicated, on="customer", how="semi").height == 3
```

**Why it holds here:** A semi join keeps each fact whose customer exists in the dimension and adds no columns, so orders 1, 2 and 3 appear once even if the dimension is duplicated.

**Plausible wrong approach:** A left join followed by drop('region') returns 5 rows against the duplicated dimension, because the fanout happens before the column is dropped.

**How to verify:** Run the answer code: known.columns stays order_id, customer, amount and the semi join against the duplicated dimension still has height 3.

**Expected:** Each matching order appears once.

## 4. Audit unmatched rows

The anti join produces a reviewable quarantine set. Decide whether the missing dimension is late, invalid or genuinely outside the domain.

```python
import polars as pl

facts = pl.DataFrame(
    {"order_id": [1, 2, 3, 4], "customer": [10, 10, 20, 30], "amount": [5, 7, 9, 6]}
)
dimension = pl.DataFrame({"customer": [10, 20], "region": ["N", "S"]})
orphans = facts.join(dimension, on="customer", how="anti")
assert orphans.to_dicts() == [{"order_id": 4, "customer": 30, "amount": 6}]
```

**Why it holds here:** An anti join returns facts without a match, so the new order 4 for customer 30 with amount 6 is the only row listed.

**Plausible wrong approach:** An inner join drops order 4 without any trace, and a left join keeps it with a null region that is easy to overlook in a total.

**How to verify:** Run the answer code and assert orphans.to_dicts() equals the single order 4 record.

**Expected:** The new order is explicitly listed.

## 5. Handle duplicate history

A changing dimension may require a time-qualified join. Arbitrarily keeping first or last can attach future information to past facts.

**Why it holds here:** If customer 10 appears twice because its region changed over time, each row is a valid version with its own validity period and the right one depends on the order date.

**Plausible wrong approach:** unique(subset='customer', keep='first') picks whichever version happened to come first, which may attach a region that did not yet apply to an older order.

**How to verify:** Look for valid_from and valid_to columns on the duplicated rows; if they differ, the fix is an as-of or range join rather than deduplication.

**Expected:** The answer distinguishes historical versions from accidental duplicates.

## 6. Define null-key policy

Use a known sentinel only if its meaning is explicitly a shared entity. Otherwise preserve unmatched missing keys for diagnosis.

**Why it holds here:** Polars does not treat two null keys as equal by default, so the semi join keeps only order 1. Setting nulls_equal=True is an explicit choice that also matches order 3.

**Plausible wrong approach:** fill_null(0) on both sides creates a fake customer 0 that matches, and a real customer 0 added later would be confused with it.

**How to verify:** Assert the default semi join returns order ids [1] and the nulls_equal=True version returns [1, 3].

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

Extend the exercise with a legitimate historical dimension, then document the additional temporal rule required. Carry the same reconciliation into dbt tests and ML feature pipelines, where silent fanout can contaminate both training labels and online metrics.
