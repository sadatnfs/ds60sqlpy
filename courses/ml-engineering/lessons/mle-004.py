"""mle-004: worked starting point; complete the guide's six changes."""


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


if __name__ == "__main__":
    print(example_one())

# TODO 1: Define a separate outcome for unavailable usage.
# TODO 2: Introduce a new region under a revised contract.
# TODO 3: Convert minutes to hours before applying an hours-based model.
# TODO 4: Report each reason and the original denominator.
# TODO 5: Explain what the contract digest establishes.
# TODO 6: State how a serving bundle identifies its expected feature contract.
