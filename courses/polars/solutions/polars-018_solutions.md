# polars-018: explained reference

Publish a feature artifact with explicit derivation and consumption contracts.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Introduce conflicting duplicates

Compare content per event_id before selecting a record. A version timestamp or authority rule must be justified; arbitrary first/last selection is not a data contract.

**Why it holds here:** Event 2 appears twice with amount 7. If one copy is changed to 8, the rows are no longer identical, so unique on event_id would keep one arbitrarily and the total for customer 10 becomes 12 or 13.

**Plausible wrong approach:** Keeping unique(subset='event_id') unchanged hides the conflict, because it silently keeps one version without saying the copies disagreed.

**How to verify:** Group valid rows by event_id and assert n_unique of amount is 1 for each; with the 8 the check fails for event 2 and the pipeline stops or applies a stated rule.

**Expected:** The pipeline explicitly rejects or resolves the conflict under a stated rule.

## 2. Reconcile the source

Apply classification in a documented order and verify identifiers in each outcome. Ambiguous overlap makes reported quality counts unreliable.

```python
import polars as pl

raw = pl.DataFrame({"event_id": [1, 2, 2, 3, 4], "amount_text": ["5", "7", "7", "bad", "9"]})
parsed = raw.with_columns(pl.col("amount_text").cast(pl.Int64, strict=False).alias("amount"))
invalid = parsed.filter(pl.col("amount").is_null()).height
valid = parsed.filter(pl.col("amount").is_not_null())
accepted = valid.unique(subset="event_id").height
duplicates = valid.height - accepted
assert (raw.height, accepted, invalid, duplicates) == (5, 3, 1, 1)
assert raw.height == accepted + invalid + duplicates
```

**Why it holds here:** Classification runs in order: event 3 with bad is invalid first, then among the four valid rows the second event 2 is a duplicate, leaving 3 accepted, so 5 = 3 + 1 + 1.

**Plausible wrong approach:** Deduplicating before parsing still yields 5 = 3 + 1 + 1 here, but if a duplicate were also invalid it would be counted in two categories.

**How to verify:** Run the answer code and assert (5, 3, 1, 1) and raw.height == accepted + invalid + duplicates.

**Expected:** 5 source rows = 3 accepted unique + 1 invalid + 1 duplicate.

## 3. Check final grain

Validate the final key and compare additive totals with accepted events. This checks both shape and quantity preservation.

**Why it holds here:** The result has customers 10 and 20, one row each, with totals 12 and 9 that sum to 21, the amounts of the three accepted events.

**Plausible wrong approach:** Checking only that totals look reasonable misses a fanout that leaves totals unchanged, such as a duplicated customer row with total 0.

**How to verify:** Assert result['customer'].n_unique() == result.height and result['total'].sum() == clean['amount'].sum() == 21.

**Expected:** Unique customer count equals output height.

## 4. Tamper with an artifact

Recompute and compare before consuming the artifact. A new matching hash written by the same attacker would need an authenticity boundary that this local example does not provide.

```python
import hashlib
import tempfile
from pathlib import Path

import polars as pl

with tempfile.TemporaryDirectory() as d:
    path = Path(d) / "features.parquet"
    pl.DataFrame({"customer": [10, 20], "total": [12, 9]}).write_parquet(path)
    recorded = hashlib.sha256(path.read_bytes()).hexdigest()
    pl.DataFrame({"customer": [10, 20], "total": [12, 10]}).write_parquet(path)
    assert hashlib.sha256(path.read_bytes()).hexdigest() != recorded
```

**Why it holds here:** Changing total for customer 20 from 9 to 10 and rewriting the file changes its bytes, so the new SHA-256 differs from the recorded one.

**Plausible wrong approach:** Trusting the receipt because it sits next to the file fails when the same writer can replace both; a hash only detects change, not who made it.

**How to verify:** Run the answer code and assert the recomputed hash differs; then restore 9, rewrite, and check whether the hash matches again on your Polars version.

**Expected:** The hash check detects the difference.

## 5. Distinguish two equalities

Use hashes for exact artifacts and schema/value checks for a logical transformation contract. Record the writer version when byte reproducibility matters.

**Why it holds here:** Byte identity says two files are the same encoding; logical equality says pl.read_parquet returns equal frames. A different compression or writer version can change bytes with identical tables.

**Plausible wrong approach:** Using a changed hash as proof that the data changed fails when only the encoding or writer version changed.

**How to verify:** Write the same frame with two compression settings, assert the hashes may differ while pl.read_parquet(...).equals holds for both.

**Expected:** The explanation allows equivalent encodings with different hashes.

## 6. Design the next boundary

The consumer should validate its expected version and reject incompatible or temporally invalid features. The ML engineering path carries these checks into training and serving.

**Why it holds here:** A training consumer needs the schema with customer and total types, one row per customer, the cutoff that features were available by, null policy, and the receipt hash for identity.

**Plausible wrong approach:** Checking only that the file opens and has rows accepts a stale or future dated feature set with the right columns.

**How to verify:** Write a consumer test that rejects a wrong schema version, a duplicated customer, a hash mismatch and a feature time after the training cutoff.

**Expected:** It includes schema, grain, availability, missingness and data identity.

## Complete reference

```python
"""polars-018: complete bounded Polars investigation."""

import hashlib
import json
import tempfile
from pathlib import Path

import polars as pl


def example_one():
    raw = pl.DataFrame(
        {
            "event_id": [1, 2, 2, 3, 4],
            "customer": [10, 10, 10, 20, 20],
            "amount_text": ["5", "7", "7", "bad", "9"],
            "time": [1, 2, 2, 3, 4],
        }
    )
    parsed = raw.with_columns(pl.col("amount_text").cast(pl.Int64, strict=False).alias("amount"))
    quarantine = parsed.filter(pl.col("amount").is_null())
    clean = parsed.filter(pl.col("amount").is_not_null()).unique(subset="event_id").sort("event_id")
    result = (
        clean.group_by("customer")
        .agg(pl.col("amount").sum().alias("total"), pl.len().alias("events"))
        .sort("customer")
    )
    assert quarantine["event_id"].to_list() == [3]
    assert clean.height == 3 and result.to_dicts() == [
        {"customer": 10, "total": 12, "events": 2},
        {"customer": 20, "total": 9, "events": 1},
    ]
    assert raw.height == clean.height + quarantine.height + 1
    return {"result": result.to_dicts(), "rejected": 1, "duplicate_rows": 1}


def example_two():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "features.parquet"
        frame = pl.DataFrame({"customer": [10, 20], "total": [12, 9]})
        frame.write_parquet(path)
        receipt = {
            "grain": "one row per customer",
            "rows": 2,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "schema": {k: str(v) for k, v in frame.schema.items()},
        }
        receipt_path = Path(d) / "receipt.json"
        receipt_path.write_text(json.dumps(receipt, sort_keys=True))
        restored = json.loads(receipt_path.read_text())
        assert restored["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
        assert pl.read_parquet(path).equals(frame)
        assert frame["customer"].n_unique() == frame.height
        return {"receipt": restored, "readback_matches": True}


def main():
    print(example_one())
    print(example_two())
    print("polars-018 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Extend the case with a conflicting duplicate and a late-known event, then document why publication is accepted or blocked. Use this result as a foundation for the analytics-engineering and ML-engineering paths rather than assuming a clean-looking table is a complete data product.
