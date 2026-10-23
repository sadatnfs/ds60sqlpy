from __future__ import annotations

import math


def sequence_score(probabilities):
    probabilities = list(probabilities)
    if not probabilities:
        raise ValueError("nonempty probability sequence required")
    if any(isinstance(p, bool) for p in probabilities):
        raise TypeError("probabilities must be real numbers, not boolean")
    probabilities = [float(p) for p in probabilities]
    if any(not math.isfinite(p) or p < 0 or p > 1 for p in probabilities):
        raise ValueError("finite probabilities in [0,1] required")
    nll = math.inf if 0 in probabilities else math.fsum(-math.log(p) for p in probabilities)
    return {
        "probability": math.prod(probabilities),
        "nll": nll,
        "targets": len(probabilities),
        "mean_nll": nll / len(probabilities),
    }


def verify():
    # Exercise 1: conditional chain
    result = sequence_score([0.5, 0.25, 0.8])
    assert math.isclose(result["probability"], 0.1, rel_tol=0, abs_tol=1e-12)
    assert (
        math.isclose(result["nll"], math.log(10), rel_tol=0, abs_tol=1e-12)
        and result["targets"] == 3
    )
    # Exercise 2: a different conditional table
    assert sequence_score([0.5, 0.5, 0.5])["probability"] == 0.125
    # Exercise 3: underflow without infinite log loss
    long = sequence_score([0.01] * 1000)
    assert long["probability"] == 0 and math.isfinite(long["nll"])
    assert math.isclose(long["nll"], 1000 * math.log(100), rel_tol=0, abs_tol=1e-9)
    # Exercise 4: certain and impossible events
    assert sequence_score([1, 1])["nll"] == 0 and math.isinf(sequence_score([0.5, 0])["nll"])
    # Exercise 5: invalid probability contracts
    for values in ([], [-0.1], [1.1], [math.nan]):
        try:
            sequence_score(values)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid probabilities accepted")
    # Exercise 6: aggregation units
    a, b = sequence_score([0.5]), sequence_score([0.25] * 3)
    assert math.isclose((a["nll"] + b["nll"]) / 4, 7 * math.log(2) / 4, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(
        (a["mean_nll"] + b["mean_nll"]) / 2, 3 * math.log(2) / 2, rel_tol=0, abs_tol=1e-12
    )
    return result


if __name__ == "__main__":
    print(verify())
