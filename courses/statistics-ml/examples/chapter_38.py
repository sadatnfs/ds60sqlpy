import numpy as np


def funnel_and_retention():
    stages = np.array([1000, 400, 100])
    step = stages[1:] / stages[:-1]
    overall = stages[-1] / stages[0]
    assert np.allclose(step, [0.4, 0.25]) and np.isclose(np.prod(step), overall)
    cohort_size = np.array([100, 80])
    retained = np.array([60, 56])
    mature = np.array([True, False])
    observed = retained[mature].sum() / cohort_size[mature].sum()
    assert observed == 0.6
    print("Step conversions:", step, "overall:", overall, "mature-cohort retention:", observed)


def carryover_and_saturation():
    spend = np.array([10.0, 0.0, 0.0, 0.0])
    state = 0.0
    adstock = []
    for x in spend:
        state = x + 0.5 * state
        adstock.append(state)
    assert adstock == [10.0, 5.0, 2.5, 1.25]
    exposure = np.array([0.0, 1.0, 2.0, 4.0])
    response = exposure / (1 + exposure)
    assert np.allclose(response, [0.0, 0.5, 2 / 3, 0.8])
    print("Adstock:", adstock, "saturation:", response)


def price_quantity_decomposition():
    p0, q0 = 10.0, 100.0
    p1, q1 = 12.0, 110.0
    change = p1 * q1 - p0 * q0
    price = (p1 - p0) * q0
    quantity = p0 * (q1 - q0)
    interaction = (p1 - p0) * (q1 - q0)
    assert change == 320 and price + quantity + interaction == change
    print("Value change and components:", change, price, quantity, interaction)


def verified_narrative_input():
    numerator, denominator = 100, 1000
    computed = numerator / denominator
    model_claim = 0.25
    assert computed == 0.1 and not np.isclose(model_claim, computed)
    packet = {"numerator": numerator, "denominator": denominator, "conversion": computed}
    print("Code-verified report packet:", packet, "reject unsupported 25-percent narrative")


def main():
    funnel_and_retention()
    carryover_and_saturation()
    price_quantity_decomposition()
    verified_narrative_input()


if __name__ == "__main__":
    main()
