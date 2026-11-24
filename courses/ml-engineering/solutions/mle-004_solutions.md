# mle-004: explained reference

Validate a feature interface structurally and semantically.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Add a missing value

Use a missingness policy that the model and serving interface share. Keep the reason so coverage and model behavior can be interpreted.

Add row 4 with usage None. The current check row["usage"] < 0 raises TypeError on None, so the fixture would crash rather than classify it; test for None first and append "missing_usage" as its own reason. Replacing None with 0.0 would accept the row as a light user, which is the mislabeling the check warns about. Verify that rejected now holds ids 2, 3 and 4 with three different reason lists.

**Expected:** Missing is not mislabeled as a negative value.

## 2. Add a legitimate category

Review encoding and model behavior before accepting the category. A vocabulary update can affect train/serve compatibility.

Adding "east" to the set inside example_one alone is the tempting shortcut: row 3 would still fail because its value is "unknown", while an east row would pass with no record that the vocabulary changed. Change expected["region"] to ["east", "north", "south"], compute the new digest, and confirm it differs from the approved one, so the serving side can refuse a model built on the two-region list.

**Expected:** The change is versioned and tested.

## 3. Check a unit conversion

Apply the conversion explicitly and preserve its source definition. Do not relabel minutes as hours without transforming values.

Example_two shows why the column set cannot catch this: set(expected) == set(changed) is True while the digests differ. For a value of 90 minutes the model should receive 1.5, not 90. Write the conversion as usage_hours = usage_minutes / 60, assert 90 becomes 1.5, and record the unit in the contract text so the hash moves with it.

**Expected:** The converted value matches the declared unit.

## 4. Preserve rejection counts

Choose a classification policy and record all relevant reasons where appropriate. Do not present a partial count as full data quality.

Here 3 rows produce 1 accepted and 2 rejected, and the reason counts are one negative_usage and one unknown_region. Add a row with usage -2.0 and region "west" and the totals become 1 accepted, 3 rejected, but 4 reasons. Summing reasons to get the rejected count would report 4 and break accepted + rejected == 4. Report both tables.

**Expected:** Accepted plus rejected equals the input population.

## 5. Review a hash claim

Use review and a trusted publication mechanism for those additional claims. A changed hash should trigger analysis, not automatic approval.

For this fixture the approved digest proves only that the three-key dictionary serialized with sorted keys is byte-identical to what was reviewed. It says nothing about whether "nonnegative float" was the right rule or whether the data obeys it; row 2 with usage -1.0 is caught by example_one, not by the hash. Treating a matching hash as a passed quality check is the error to avoid.

**Expected:** It establishes exact serialized identity.

## 6. Bind the consumer

Validate the feature interface before inference and fail clearly on incompatible inputs. The artifact lessons implement that boundary.

Store the value returned in "version" next to the model file and compare it with digest(expected) at load time; a mismatch should stop serving before any row is scored. Comparing column names would pass the minutes contract from example_two, which is the case this binding exists to stop.

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

Keep explicit rejection reasons and bind accepted feature meaning to the model artifact. This protects both reproducibility and useful diagnostics when inputs evolve.
