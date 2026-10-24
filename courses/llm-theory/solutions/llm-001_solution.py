from __future__ import annotations


def evaluate(rows):
    rows = list(rows)
    if not rows:
        raise ValueError("nonempty question evaluation required")
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("duplicate question ID")
    if any(type(row["correct"]) is not bool for row in rows):
        raise TypeError("correct must be boolean")
    groups = {}
    for row in rows:
        groups.setdefault(row["family"], []).append(row["correct"])
    record = sum(row["correct"] for row in rows) / len(rows)
    family = sum(sum(values) / len(values) for values in groups.values()) / len(groups)
    return {
        "records": len(rows),
        "families": len(groups),
        "record_accuracy": record,
        "family_accuracy": family,
    }


def verify():
    # Exercise 1: bounded evidence classes
    classes = ["mechanism", "empirical", "unsupported", "empirical", "unsupported", "mechanism"]
    assert classes.count("unsupported") == 2
    # Exercise 2: distinct evaluation units
    rows = [
        {"id": "q1", "family": "A", "correct": True},
        {"id": "q2", "family": "A", "correct": True},
        {"id": "q3", "family": "B", "correct": False},
    ]
    result = evaluate(rows)
    assert result["record_accuracy"] == 2 / 3 and result["family_accuracy"] == 0.5
    # Exercise 3: a fluent counterexample
    assert 7 + 8 == 15 and 13 != 15
    # Exercise 4: repeated IDs
    try:
        evaluate(rows + [dict(rows[0])])
    except ValueError as error:
        assert "duplicate" in str(error)
    else:
        raise AssertionError("duplicate question accepted")
    # Exercise 5: absent evidence
    try:
        evaluate([])
    except ValueError:
        pass
    else:
        raise AssertionError("empty evaluation accepted")
    # Exercise 6: changed family balance
    more = rows[:2] + [{"id": "q4", "family": "A", "correct": True}, rows[2]]
    transfer = evaluate(more)
    assert transfer["record_accuracy"] == 0.75 and transfer["family_accuracy"] == 0.5
    return result


if __name__ == "__main__":
    print(verify())
