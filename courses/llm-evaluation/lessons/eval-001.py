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


worked_a()

# Task 1: Compute B minus A and then A minus B for one success gained by B.
# Task 2: Reweight the worked families to 75% metrics and 25% policy.
# Task 3: Append an existing request with the same ID.
# Task 4: Omit the access-policy result from an otherwise favorable packet.
# Task 5: Add a second unjudged row to case B.
# Task 6: Evaluate no eligible requests.

# Implement your six changes below.
