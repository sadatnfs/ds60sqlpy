import hashlib


def validate_split(rows):
    seen = set()
    groups = {}
    for row in rows:
        if row["id"] in seen:
            raise ValueError("Duplicate ID")
        seen.add(row["id"])
        prior = groups.setdefault(row["family"], row["split"])
        if prior != row["split"]:
            raise ValueError("Family leakage")
    return groups


def training_ids(rows, cutoff):
    return [r["id"] for r in rows if r["event"] <= cutoff and r["label_available"] <= cutoff]


def fingerprint(text):
    normalized = " ".join(text.casefold().split())
    return hashlib.sha256(normalized.encode()).hexdigest()


# === EXAMPLE A ===
def worked_a():
    rows = [
        {"id": "m1", "family": "metrics", "split": "train"},
        {"id": "m2", "family": "metrics", "split": "train"},
        {"id": "p1", "family": "policy", "split": "test"},
    ]
    assert validate_split(rows) == {"metrics": "train", "policy": "test"}
    broken = [dict(r) for r in rows]
    broken[1]["split"] = "test"
    try:
        validate_split(broken)
    except ValueError as error:
        assert str(error) == "Family leakage"
    else:
        raise AssertionError("Leaking split accepted")
    print("Family split accepted; leaking split rejected")


# === EXAMPLE B ===
def worked_b():
    rows = [
        {"id": "a", "event": 8, "label_available": 9},
        {"id": "b", "event": 8, "label_available": 12},
        {"id": "c", "event": 11, "label_available": 11},
    ]
    assert training_ids(rows, 10) == ["a"]
    assert [r["id"] for r in rows if r["event"] <= 10] == ["a", "b"]
    assert fingerprint("  Define  conversion RATE ") == fingerprint("define conversion rate")
    print("Training at day 10:", training_ids(rows, 10))


# === EXERCISES ===
def exercise_checks():
    assert training_ids([{"id": "x", "event": 10, "label_available": 10}], 10) == ["x"]
    assert training_ids([{"id": "x", "event": 9, "label_available": 11}], 10) == []
    assert fingerprint("rate") != fingerprint("rates")
    assert fingerprint("A B") == fingerprint("a\n b")
    try:
        validate_split(
            [
                {"id": "a", "family": "x", "split": "train"},
                {"id": "a", "family": "y", "split": "test"},
            ]
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Duplicate ID accepted")
    assert validate_split([]) == {}


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-002: all reference checks passed")


if __name__ == "__main__":
    main()
