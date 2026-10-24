import math


def recommend(current, observed, target, minimum=1, maximum=2):
    if observed is None:
        raise ValueError("metric unavailable")
    if current < 1 or observed < 0 or target <= 0:
        raise ValueError("invalid model input")
    ideal = math.ceil(current * observed / target)
    return ideal, min(maximum, max(minimum, ideal))


def main():
    assert 50 / 100 * 100 == 50 and 50 / 200 * 100 == 25
    assert recommend(1, 80, 50) == (2, 2)
    assert recommend(2, 20, 50) == (1, 1)
    assert recommend(1, 200, 50) == (4, 2)
    try:
        recommend(1, None, 50)
    except ValueError:
        pass
    else:
        raise AssertionError("missing metric was converted to zero")
    print("k8s-033 complete-data proportional model passed; real HPA timing is not simulated")


if __name__ == "__main__":
    main()
