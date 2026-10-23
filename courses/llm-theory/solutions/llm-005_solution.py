from __future__ import annotations

import math


def score_targets(probabilities, mask=None):
    probabilities = list(probabilities)
    if not probabilities:
        raise ValueError("nonempty probability sequence required")
    if any(not math.isfinite(float(p)) or float(p) < 0 or float(p) > 1 for p in probabilities):
        raise ValueError("finite probabilities in [0,1] required")
    if mask is None:
        mask = [True] * len(probabilities)
    mask = list(mask)
    if any(type(value) is not bool for value in mask):
        raise TypeError("mask must be boolean")
    if len(mask) != len(probabilities) or not any(mask):
        raise ValueError("same-length mask with active targets required")
    active = [float(p) for p, include in zip(probabilities, mask, strict=True) if include]
    total = math.inf if 0 in active else math.fsum(-math.log(p) for p in active)
    mean = total / len(active)
    try:
        perplexity = math.exp(mean)
    except OverflowError:
        perplexity = math.inf
    return {
        "total_nll": total,
        "active_targets": len(active),
        "mean_nll": mean,
        "perplexity": perplexity,
    }


def verify():
    # Exercise 1: explicit score fields
    base = score_targets([0.5, 0.25])
    assert base["active_targets"] == 2
    assert math.isclose(base["perplexity"], 2**1.5, rel_tol=0, abs_tol=1e-12)
    # Exercise 2: padding leaves the denominator unchanged
    assert score_targets([0.5, 0.25, 1], [True, True, False]) == base
    # Exercise 3: document and target units
    a, b = score_targets([0.5]), score_targets([0.25] * 3)
    assert math.isclose(
        (a["total_nll"] + b["total_nll"]) / 4, 7 * math.log(2) / 4, rel_tol=0, abs_tol=1e-12
    )
    # Exercise 4: impossible active versus ignored target
    assert math.isinf(score_targets([0.5, 0])["perplexity"])
    assert score_targets([0.5, 0], [True, False])["perplexity"] == 2
    # Exercise 5: invalid scoring requests
    for error, probs, mask in (
        (ValueError, [0.5], [False]),
        (ValueError, [], None),
        (ValueError, [1.1], None),
        (TypeError, [0.5], [1]),
    ):
        try:
            score_targets(probs, mask)
        except error:
            pass
        else:
            raise AssertionError("invalid target score accepted")
    # Exercise 6: incompatible tokenizer units
    assert score_targets([0.25])["perplexity"] == 4 and score_targets([0.5] * 3)["perplexity"] == 2
    assert 0.25 > 0.5**3
    return base


if __name__ == "__main__":
    print(verify())
