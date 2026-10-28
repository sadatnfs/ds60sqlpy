import numpy as np


def family_difference(rows, weighting="request"):
    ids = [r[0] for r in rows]
    if not rows or len(ids) != len(set(ids)):
        raise ValueError("Requests must be nonempty and uniquely paired.")
    differences = np.array([r[3] - r[2] for r in rows], dtype=float)
    if weighting == "request":
        return float(differences.mean())
    if weighting != "family":
        raise ValueError("Unknown weighting")
    families = sorted({r[1] for r in rows})
    return float(np.mean([np.mean([r[3] - r[2] for r in rows if r[1] == f]) for f in families]))


def decision(gates):
    required = {"quality", "label_coverage", "access_policy"}
    return "go" if set(gates) == required and all(v is True for v in gates.values()) else "no-go"


# === EXAMPLE A ===
def worked_a():
    rows = [
        ("m1", "metrics", 0, 1),
        ("m2", "metrics", 0, 1),
        ("m3", "metrics", 0, 1),
        ("p1", "policy", 1, 0),
    ]
    assert family_difference(rows) == 0.5
    assert family_difference(rows, "family") == 0
    extended = rows + [(f"m{i}", "metrics", 0, 1) for i in range(4, 10)]
    assert family_difference(extended, "family") == 0
    print(
        "Request difference:",
        family_difference(rows),
        "family difference:",
        family_difference(rows, "family"),
    )


# === EXAMPLE B ===
def worked_b():
    labels = [1, 1, None]
    observed = [x for x in labels if x is not None]
    assert np.mean(observed) == 1 and len(observed) / len(labels) == 2 / 3
    gates = {"quality": True, "label_coverage": False, "access_policy": True}
    assert decision(gates) == "no-go"
    gates["label_coverage"] = True
    gates["access_policy"] = None
    assert decision(gates) == "no-go"
    print("Observed accuracy:", np.mean(observed), "label coverage:", len(observed) / len(labels))


# === EXERCISES ===
def exercise_checks():
    rows = [("a", "x", 1, 0), ("b", "y", 0, 1)]
    assert family_difference(rows) == 0
    assert family_difference([("only", "x", 0, 1)]) == 1
    assert family_difference([("only", "x", 1, 0)]) == -1
    assert family_difference([(k, g, b, a) for k, g, a, b in rows]) == 0
    assert decision({"quality": True, "label_coverage": True, "access_policy": True}) == "go"
    assert decision({"quality": True, "label_coverage": True}) == "no-go"
    try:
        family_difference([rows[0], rows[0]])
    except ValueError:
        pass
    else:
        raise AssertionError("Duplicate request accepted")
    try:
        family_difference([])
    except ValueError:
        pass
    else:
        raise AssertionError("Empty population accepted")


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-001: all reference checks passed")


if __name__ == "__main__":
    main()
