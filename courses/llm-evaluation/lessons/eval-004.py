import numpy as np


def agreement(a, b):
    if len(a) != len(b) or not a:
        raise ValueError("Paired nonempty labels required")
    categories = sorted(set(a) | set(b))
    n = len(a)
    table = np.zeros((len(categories), len(categories)), dtype=int)
    positions = {c: i for i, c in enumerate(categories)}
    for x, y in zip(a, b, strict=True):
        table[positions[x], positions[y]] += 1
    observed = float(np.trace(table) / n)
    expected = float((table.sum(0) / n) @ (table.sum(1) / n))
    if np.isclose(expected, 1):
        raise ValueError("Kappa undefined without marginal variation")
    return observed, (observed - expected) / (1 - expected), table


def ordinal_disagreement(a, b, levels=3):
    if levels < 2 or len(a) != len(b) or not a:
        raise ValueError("Invalid ordinal design")
    if any(type(x) is not int or not 0 <= x < levels for x in a + b):
        raise ValueError("Invalid category")
    return float(np.mean([(x - y) ** 2 / (levels - 1) ** 2 for x, y in zip(a, b, strict=True)]))


def worked_a():
    observed, kappa, table = agreement([1, 1, 0, 0], [1, 0, 0, 0])
    assert observed == 0.75 and kappa == 0.5
    assert table.tolist() == [[2, 0], [1, 1]]
    _, balanced, _ = agreement([0] * 5 + [1] * 5, [0] * 4 + [1] * 6)
    _, rare, _ = agreement([0] * 9 + [1], [0] * 10)
    assert np.isclose(balanced, 0.8) and np.isclose(rare, 0)
    print("Observed agreement:", observed, "kappa:", kappa, "table:", table.tolist())


worked_a()

# Task 1: Rebuild the table in case A by counting label pairs.
# Task 2: Use labels 0,1 from both annotators.
# Task 3: Pair 0,1 with 1,0.
# Task 4: Give both reviewers only label 1.
# Task 5: Compare observed ordinal disagreement to weighted kappa.
# Task 6: Annotate ten paraphrases from each of two families.

# Implement your six changes below.
