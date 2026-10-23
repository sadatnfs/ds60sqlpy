from __future__ import annotations

import math


def central_difference(function, point, h):
    point, h = float(point), float(h)
    if not math.isfinite(point) or not math.isfinite(h) or h <= 0:
        raise ValueError("finite point and positive finite h required")
    high, low = float(function(point + h)), float(function(point - h))
    if not math.isfinite(high) or not math.isfinite(low):
        raise ValueError("finite probe values required")
    return (high - low) / (2 * h)


def verify():
    def f(w):
        return (w - 2) ** 2

    # Exercise 1: distinguish local slope from updated state
    assert f(0) == 4 and math.isclose(f(0.4), 2.56, rel_tol=0, abs_tol=1e-12)
    # Exercise 2: three central scales
    for h in (0.1, 0.01, 0.001):
        assert math.isclose(central_difference(f, 0, h), -4, rel_tol=0, abs_tol=1e-10)
    # Exercise 3: explicit forward bias
    for h in (0.1, 0.01, 0.001):
        assert math.isclose((f(h) - f(0)) / h, -4 + h, rel_tol=0, abs_tol=1e-10)
    # Exercise 4: positive slope on the other side
    assert math.isclose(central_difference(f, 3, 0.01), 2, rel_tol=0, abs_tol=1e-10)
    assert math.isclose(f(2.8), 0.64, rel_tol=0, abs_tol=1e-12)
    # Exercise 5: kink and invalid probes
    assert central_difference(abs, 0, 0.01) == 0
    for point, h in ((0, 0), (math.nan, 0.1)):
        try:
            central_difference(f, point, h)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid probe accepted")

    # Exercise 6: a new objective
    def g(w):
        return 3 * (w - 1) ** 2

    assert math.isclose(central_difference(g, 2, 0.01), 6, rel_tol=0, abs_tol=1e-10)
    assert math.isclose(g(1.4), 0.48, rel_tol=0, abs_tol=1e-12)
    return {"derivative_at_zero": -4, "updated_weight": 0.4}


if __name__ == "__main__":
    print(verify())
