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
