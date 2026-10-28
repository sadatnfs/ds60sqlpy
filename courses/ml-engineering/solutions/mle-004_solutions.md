# mle-004: explained reference

Validate a feature interface structurally and semantically.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Add a missing value

Use a missingness policy that the model and serving interface share. Keep the reason so coverage and model behavior can be interpreted.

**Expected:** Missing is not mislabeled as a negative value.

## 2. Add a legitimate category

Review encoding and model behavior before accepting the category. A vocabulary update can affect train/serve compatibility.

**Expected:** The change is versioned and tested.

## 3. Check a unit conversion

Apply the conversion explicitly and preserve its source definition. Do not relabel minutes as hours without transforming values.

**Expected:** The converted value matches the declared unit.

## 4. Preserve rejection counts

Choose a classification policy and record all relevant reasons where appropriate. Do not present a partial count as full data quality.

**Expected:** Accepted plus rejected equals the input population.

## 5. Review a hash claim

Use review and a trusted publication mechanism for those additional claims. A changed hash should trigger analysis, not automatic approval.

**Expected:** It establishes exact serialized identity.

## 6. Bind the consumer

Validate the feature interface before inference and fail clearly on incompatible inputs. The artifact lessons implement that boundary.

**Expected:** The version or digest is retained with the model.

## Complete reference

```python
"""mle-004: local, bounded ML engineering investigation."""

import hashlib
import json


def digest(data):
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def example_one():
    rows = [
        {"id": 1, "usage": 10.0, "tickets": 2, "region": "north"},
        {"id": 2, "usage": -1.0, "tickets": 1, "region": "south"},
        {"id": 3, "usage": 4.0, "tickets": 0, "region": "unknown"},
    ]
    valid = []
    rejected = []
    for row in rows:
        reasons = []
        if row["usage"] < 0:
            reasons.append("negative_usage")
        if row["region"] not in {"north", "south"}:
            reasons.append("unknown_region")
        (rejected if reasons else valid).append({**row, "reasons": reasons})
    assert [r["id"] for r in valid] == [1]
    assert [r["reasons"] for r in rejected] == [["negative_usage"], ["unknown_region"]]
    assert len(valid) + len(rejected) == len(rows)
    return {
        "accepted_ids": [1],
        "rejections": [{k: r[k] for k in ("id", "reasons")} for r in rejected],
    }


def example_two():
    expected = {
        "usage": "nonnegative float",
        "tickets": "nonnegative integer",
        "region": ["north", "south"],
    }
    approved = digest(expected)
    changed = {**expected, "usage": "minutes instead of hours"}
    assert digest(changed) != approved
    assert set(expected) == set(changed)
    return {"same_column_names": True, "semantic_contract_changed": True, "version": approved}


def main():
    print(example_one())
    print(example_two())
    print("mle-004 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Validate a feature interface structurally and semantically. Keep explicit rejection reasons and bind accepted feature meaning to the model artifact. This protects both reproducibility and useful diagnostics when inputs evolve.
