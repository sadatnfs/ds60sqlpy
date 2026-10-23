from __future__ import annotations

import math


def chain_trace(weight, scale=2):
    weight, scale = float(weight), float(scale)
    if not math.isfinite(weight) or not math.isfinite(scale):
        raise ValueError("finite weight and scale required")
    z = scale * weight
    activation = z * z
    loss = (activation - 1) ** 2
    gradient = 2 * (activation - 1) * 2 * z * scale
    return {"z": z, "activation": activation, "loss": loss, "gradient": gradient}


def verify():
    # Exercise 1: all local factors
    first = chain_trace(1)
    assert first == {"z": 2.0, "activation": 4.0, "loss": 9.0, "gradient": 48.0}
    # Exercise 2: changed inner scale
    assert chain_trace(1, 3)["gradient"] == 288 and chain_trace(1, 3)["loss"] == 64
    # Exercise 3: an independent whole-path probe
    h = 1e-5
    slope = (chain_trace(1 + h)["loss"] - chain_trace(1 - h)["loss"]) / (2 * h)
    assert math.isclose(slope, 48, rel_tol=0, abs_tol=1e-7)

    # Exercise 4: a kink does not have one classical derivative
    def relu(z):
        return max(0, z)

    assert (relu(-1), relu(1)) == (0, 1)
    assert (relu(h) - relu(-h)) / (2 * h) == 0.5

    # Exercise 5: a frozen path has a different derivative
    def frozen(w):
        return (4.0 - 1) ** 2

    assert frozen(1) == first["loss"] and (frozen(1 + h) - frozen(1 - h)) / (2 * h) == 0
    # Exercise 6: missing factor diagnosis
    assert first["gradient"] == 24 * 2 and chain_trace(1, 3)["gradient"] == 96 * 3
    return first


if __name__ == "__main__":
    print(verify())
