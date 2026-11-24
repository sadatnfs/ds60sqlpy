# polars-018: A validated event-to-feature publication

## Level and prerequisites

Advanced. Direct prerequisites: `polars-006`, `polars-011`, `polars-014`, `polars-017`

**Outcome:** Publish a feature artifact with explicit derivation and consumption contracts.

## Question and mechanism

The final case combines several contracts rather than introducing another table method. Raw events arrive with identifiers, customer keys, textual amounts and event times. One event is repeated and another has an invalid amount. A reliable pipeline should account for both before publishing a customer-level feature table. A final total alone cannot explain which records were rejected or duplicated.

The deduplication in this fixture is justified because the repeated event has identical content. Conflicting versions of one event would require a reviewed ordering or conflict policy; unique(subset=...) must not arbitrarily choose a winner in that situation. The accepted rows then produce one result per customer, with an event count beside the amount total. This makes the change from event grain to customer grain explicit.

The second case writes a typed artifact and a receipt containing its hash, schema, row count and grain. A cryptographic hash establishes byte identity, not correctness or authenticity by itself. Readback checks the published content, while the earlier row accounting checks how it was derived. In a durable system, publication would also need ownership, atomicity, lineage and a retention policy.

## Key terms

- **Data contract:** The declared columns, types, keys and value rules that published rows must satisfy.
- **Deduplication:** Removing repeated events with `unique(subset=...)`, which is justified only when the repeats have identical content.
- **Quarantine:** Holding rows that violate the contract apart with a reason instead of publishing them or silently dropping them.
- **Artifact hash:** A sha256 digest of the written file's bytes, which identifies exact bytes, not logical equality of the data.
- **Readback receipt:** A JSON record of the contract and the file's SHA-256 hash, written after the published file is read back and checked.

## Syntax and data contract

Parse into a new field, isolate invalid rows, apply the declared duplicate rule and only then aggregate. Use a stable sort before publishing an ordered result. write_parquet creates the typed output; hashlib.sha256 records its exact bytes; a JSON receipt makes the contract inspectable. A hash can legitimately change when a library writes an equivalent Parquet encoding, so distinguish byte identity from logical equality.

## Run the lesson

Open `polars-018` in `/classroom`. Its starter `main.py` contains both worked cases, "Account for every event" and "Publish and inspect a typed artifact", and prints the dictionary each case returns. The prepared `data-engineering` worker runs it in a fresh temporary directory. An `AssertionError` means that an observation differs from the case's stated contract. The inputs are small literal tables. Cases that demonstrate Parquet scans write their files into a temporary directory that is removed when the case returns. No account, network request or package download is involved. Save source and notes before switching lessons.

## Worked case 1: Account for every event

The five source rows become three accepted unique events, one malformed event and one duplicate copy. Customer totals are derived only from accepted events. The count equation makes it impossible to describe this as simply cleaning away inconvenient rows.

**Expected evidence:** Customer 10 has total 12 from 2 events; customer 20 has total 9 from 1 event; one malformed and one duplicate row are recorded.

```python
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


if __name__ == "__main__":
    print(example_one())
```

## Worked case 2: Publish and inspect a typed artifact

The second case writes the feature table and a receipt, then reads both back. It verifies the file hash and logical contents independently. This is a local publication mechanism, not a claim that a distributed transactional service has been deployed.

**Expected evidence:** Readback preserves two unique customers, the schema and exact artifact hash.

```python
import hashlib
import json
import tempfile
from pathlib import Path

import polars as pl


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


if __name__ == "__main__":
    print(example_two())
```

## Practice

The starter contains both worked cases, so a task can change either one. Make each change in a saved copy, run it, and compare the printed result with the task's check before opening the separate explained answers.

### 1. Introduce conflicting duplicates

Change one repeated event amount while keeping its id.

**Check:** The pipeline explicitly rejects or resolves the conflict under a stated rule.

**Hint:** Identical retries differ from conflicting versions.

### 2. Reconcile the source

Write the complete row-accounting equation.

**Check:** 5 source rows = 3 accepted unique + 1 invalid + 1 duplicate.

**Hint:** Keep categories mutually exclusive.

### 3. Check final grain

Assert one output row per customer.

**Check:** Unique customer count equals output height.

**Hint:** An aggregate should have a declared key.

### 4. Tamper with an artifact

Change the output bytes after writing its receipt.

**Check:** The hash check detects the difference.

**Hint:** A stored hash describes particular bytes.

### 5. Distinguish two equalities

Explain byte identity versus logical table equality.

**Check:** The explanation allows equivalent encodings with different hashes.

**Hint:** Parquet metadata and encoding choices can differ.

### 6. Design the next boundary

Specify what a model-training consumer must verify.

**Check:** It includes schema, grain, availability, missingness and data identity.

**Hint:** A readable file is not necessarily suitable training input.

## Diagnose errors and misleading results

If counts do not reconcile, inspect classification order and duplicate semantics. If an output hash changes, determine whether bytes changed, the receipt is stale or a different encoding was produced. If a model receives future information, correct the temporal contract before improving model hyperparameters. Preserve rejected evidence and the publication decision.

## Transfer to independent work

Extend the case with a conflicting duplicate and a late-known event, then document why publication is accepted or blocked. Use this result as a foundation for the analytics-engineering and ML-engineering paths rather than assuming a clean-looking table is a complete data product.

## Primary references

- [Polars user guide: Schema](https://docs.pola.rs/user-guide/lazy/schemas/)
- [Polars Python API reference](https://docs.pola.rs/api/python/stable/reference/index.html)

## Tutor guidance

Use the repository's `$guide-ds60sqlpy-learning` skill (`.agents/skills/guide-ds60sqlpy-learning/SKILL.md`) for `polars-018`. Inspect the learner's own source and printed output first. Ask for an explanation of data contract, deduplication, quarantine, artifact hash and readback in their own words, then give one focused hint at a time. Keep an assertion on this synthetic fixture separate from a claim about an external dataset or deployed service.
