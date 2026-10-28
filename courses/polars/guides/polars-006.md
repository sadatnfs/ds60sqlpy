# polars-006: Joins, cardinality and reconciliation

## Level and prerequisites

Beginner. Direct prerequisites: `polars-003`, `polars-004`, `polars-005`

**Outcome:** Enrich a fact table while proving its grain and totals remain valid.

## Question and mechanism

A join matches records using keys; it does not verify that the key represents the intended relationship. A fact table may have many orders for one customer, while a customer dimension should have one row per customer for a many-to-one enrichment. Duplicating a dimension key causes every matching fact to repeat. The result can still look plausible and contain no nulls while its total is inflated.

Declare the expected cardinality where the API supports it, then independently reconcile row counts and additive quantities. The validate="m:1" contract says the left side may contain repeated keys and the right side must have unique matching keys. This protects one part of the data model; it does not prove that region is correct or that the dimension represents the correct historical version.

Semi and anti joins answer membership questions. A semi join keeps matching left rows without appending right-side columns. An anti join keeps unmatched left rows. These are useful for eligibility and quarantine logic because a membership test should not accidentally multiply facts. Null-key matching is a separate policy: a missing customer identifier is not automatically the same entity as another missing identifier.

## Syntax and data contract

join takes a key, join type and optional cardinality validation. A left join preserves unmatched left rows, but may multiply matched rows if right keys repeat. semi and anti return left columns only. nulls_equal=True deliberately allows missing keys to match; use it only when that semantics is justified. Sort by a stable identifier before comparing output records.

## Run the lesson

Open this subject in `/classroom`, then show its code and notes. The prepared `data-engineering` worker runs `main.py` in a fresh temporary directory. The examples use installed packages and synthetic local fixtures; no account, cloud service, network request or package download is required. Save source and notes before switching lessons. Temporary databases, project files and tracking artifacts are recreated by each complete program and removed after the job. The classroom retains the submitted source and bounded output, not an indefinitely running external service. The guide distinguishes this local execution from the deployment decisions that need an owned production environment.



## Worked case 1: Detect dimension fanout

The first case enriches three orders with two customer rows and confirms the original total 21. It then duplicates customer 10 and observes an inflated total 33. The validated join rejects the same bad dimension, demonstrating that a successful unvalidated join is insufficient evidence.

**Expected evidence:** Correct rows 3/total 21; duplicate dimension gives 5 rows/total 33; m:1 validation rejects it.

```python
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


if __name__ == "__main__":
    print(example_one())
```


## Worked case 2: Membership and unknown identity

The second case divides left records into matching and nonmatching sets. It then turns on null equality to show that a missing key can become a match under a different policy. The choice must come from the meaning of the key, not from a desire to eliminate unmatched counts.

**Expected evidence:** Default matching retains id 1; anti retains ids 2 and 3; explicit null matching also retains id 3.

```python
import polars as pl


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


if __name__ == "__main__":
    print(example_two())
```


## Practice

Make each requested change in a saved copy. Compare both the expected result and the deliberately changed assumption. The separate reference explains the answers.


### 1. Prove the expected key

Check the dimension key before enrichment.

**Check:** Unique customer count equals dimension height.

**Hint:** Inspect the right side independently.


### 2. Reconcile a total

Verify that additive order revenue is unchanged by valid enrichment.

**Check:** The total remains 21.

**Hint:** Compare before and after.


### 3. Make a membership query

Return orders whose customers occur in the dimension without adding region.

**Check:** Each matching order appears once.

**Hint:** Use a semi join.


### 4. Audit unmatched rows

Add a customer 30 order and inspect it using an anti join.

**Check:** The new order is explicitly listed.

**Hint:** Use an identifier in the output.


### 5. Handle duplicate history

Explain why dropping duplicate customer rows can be incorrect.

**Check:** The answer distinguishes historical versions from accidental duplicates.

**Hint:** Which row was valid at the order time?


### 6. Define null-key policy

Compare default and nulls_equal behavior for two missing keys.

**Check:** Only the explicit policy matches them.

**Hint:** Missing identity is not a common identity.


## Diagnose errors and misleading results

If the result has too many rows, inspect key multiplicities on both sides and calculate the expected product of counts for one key. If it has too few rows, inspect join type and the unmatched set. A post-join distinct operation can erase evidence while leaving incorrect aggregates; fix the relation and time contract before deduplicating the result.

## Transfer to independent work

Enrich a fact table while proving its grain and totals remain valid. Extend the exercise with a legitimate historical dimension, then document the additional temporal rule required. Carry the same reconciliation into dbt tests and ML feature pipelines, where silent fanout can contaminate both training labels and online metrics.

## Primary references

- [Polars documentation: Joins, cardinality and reconciliation](https://docs.pola.rs/user-guide/transformations/joins/)
- [Polars Python API reference](https://docs.pola.rs/api/python/stable/reference/index.html)

## Tutor guidance

Use the repository learning-companion skill for `polars-006`. Inspect the learner's own source and observations, ask for an explanation of the relevant data or state contract, and give a focused hint. Separate an assertion on this fixture from a claim about an external dataset or deployed service.
