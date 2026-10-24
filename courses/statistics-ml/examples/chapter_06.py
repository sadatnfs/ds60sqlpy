import numpy as np
import pandas as pd


def join_cardinality():
    orders = pd.DataFrame({"order": [1, 2], "revenue": [10, 20]})
    lines = pd.DataFrame({"order": [1, 1, 2], "item": ["a", "b", "c"]})
    joined = orders.merge(lines, on="order", validate="one_to_many")
    assert joined.revenue.sum() == 40 and orders.revenue.sum() == 30
    try:
        orders.merge(lines, on="order", validate="one_to_one")
    except pd.errors.MergeError:
        pass
    else:
        raise AssertionError("Cardinality violation was not detected")
    print(
        "Original revenue:", orders.revenue.sum(), "incorrect post-join sum:", joined.revenue.sum()
    )


def composition_and_ecdf():
    a_success, a_count = np.array([9, 20]), np.array([10, 100])
    b_success, b_count = np.array([80, 1]), np.array([100, 10])
    assert np.all(a_success / a_count > b_success / b_count)
    assert a_success.sum() / a_count.sum() < b_success.sum() / b_count.sum()
    x = np.array([1.0, 1.0, 2.0, 9.0])
    assert np.mean(x <= 2) == 0.75
    print("Within-group A rates:", a_success / a_count, "B rates:", b_success / b_count)
    print(
        "Pooled A/B:",
        a_success.sum() / a_count.sum(),
        b_success.sum() / b_count.sum(),
        "ECDF(2):",
        0.75,
    )


def main():
    join_cardinality()
    composition_and_ecdf()


if __name__ == "__main__":
    main()
