from __future__ import annotations

import math

TRAIN = [{"id": f"t{i}", "group": f"train-{i}", "x": i, "y": 2 * i} for i in range(1, 4)]
HOLDOUT = [
    {"id": f"h{i}", "group": f"holdout-{i}", "x": i + 3, "y": 2 * (i + 3)} for i in range(1, 5)
]


def mse(predictions, targets):
    predictions, targets = list(predictions), list(targets)
    if not predictions or len(predictions) != len(targets):
        raise ValueError("nonempty equal-length evaluation pairs required")
    pairs = [(float(a), float(b)) for a, b in zip(predictions, targets, strict=True)]
    if not all(math.isfinite(a) and math.isfinite(b) for a, b in pairs):
        raise ValueError("finite evaluation pairs required")
    return sum((a - b) ** 2 for a, b in pairs) / len(pairs)


def validate_split(train, holdout):
    if not train or not holdout:
        raise ValueError("nonempty train and holdout required")
    ids = [{row["id"] for row in part} for part in (train, holdout)]
    groups = [{row["group"] for row in part} for part in (train, holdout)]
    if any(len(keys) != len(part) for keys, part in zip(ids, (train, holdout), strict=True)):
        raise ValueError("duplicate row IDs")
    if ids[0] & ids[1]:
        raise ValueError("row ID overlap")
    if groups[0] & groups[1]:
        raise ValueError("source group overlap")
    return True


def verify():
    # Exercise 1: row and group identities
    assert len(TRAIN) == 3 and len(HOLDOUT) == 4 and validate_split(TRAIN, HOLDOUT)
    # Exercise 2: training-only baseline
    constant = sum(row["y"] for row in TRAIN) / len(TRAIN)
    assert constant == 4 and math.isclose(mse([constant] * 3, [r["y"] for r in TRAIN]), 8 / 3)
    assert mse([constant] * 4, [r["y"] for r in HOLDOUT]) == 54
    # Exercise 3: sum and mean
    assert mse([7, 11], [8, 10]) == 1
    # Exercise 4: grouped leakage
    leaked = [dict(row) for row in HOLDOUT]
    leaked[0]["group"] = TRAIN[0]["group"]
    try:
        validate_split(TRAIN, leaked)
    except ValueError as error:
        assert "group" in str(error)
    else:
        raise AssertionError("group leakage accepted")
    # Exercise 5: empty evaluation
    try:
        mse([], [])
    except ValueError:
        pass
    else:
        raise AssertionError("empty evaluation accepted")
    # Exercise 6: exact published-point claim only
    assert mse([2 * r["x"] for r in HOLDOUT], [r["y"] for r in HOLDOUT]) == 0
    return {"training_rows": 3, "holdout_rows": 4, "constant": constant, "holdout_mse": 54}


if __name__ == "__main__":
    print(verify())
