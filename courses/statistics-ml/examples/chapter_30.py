import numpy as np


def moran_and_variogram():
    y = np.array([1.0, 1.0, 3.0, 3.0])
    w = np.zeros((4, 4))
    for i in range(3):
        w[i, i + 1] = w[i + 1, i] = 1.0
    z = y - y.mean()
    moran = len(y) / w.sum() * (z @ w @ z) / (z @ z)
    semivariance = 0.5 * np.mean(np.diff(y) ** 2)
    assert np.isclose(moran, 1 / 3) and np.isclose(semivariance, 2 / 3)
    print("Chain Moran I:", moran, "lag-one semivariance:", semivariance)


def ordinary_kriging():
    locations = np.array([0.0, 2.0])
    target = 1.0
    observed = np.array([1.0, 3.0])
    covariance = np.exp(-np.abs(locations[:, None] - locations[None, :]))
    k = np.exp(-np.abs(locations - target))
    system = np.block([[covariance, np.ones((2, 1))], [np.ones((1, 2)), np.zeros((1, 1))]])
    solution = np.linalg.solve(system, np.r_[k, 1.0])
    weights = solution[:2]
    prediction = weights @ observed
    variance = 1 - weights @ k - solution[2]
    assert np.allclose(weights, [0.5, 0.5]) and np.isclose(prediction, 2.0) and variance > 0
    print("Kriging weights, prediction, conditional variance:", weights, prediction, variance)


def aggregation_support():
    individual = np.array([1.0, 1.0, 3.0, 3.0])
    neighboring = np.array([individual[:2].mean(), individual[2:].mean()])
    mixed = np.array([individual[[0, 2]].mean(), individual[[1, 3]].mean()])
    assert neighboring.tolist() == [1.0, 3.0] and mixed.tolist() == [2.0, 2.0]
    assert neighboring.mean() == mixed.mean() == 2.0
    print("Two boundary choices:", neighboring, mixed, "same global mean")


def main():
    moran_and_variogram()
    ordinary_kriging()
    aggregation_support()


if __name__ == "__main__":
    main()
