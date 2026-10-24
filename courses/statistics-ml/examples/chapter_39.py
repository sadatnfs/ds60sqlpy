import numpy as np


def meta_weights():
    effect = np.array([0.2, 0.5])
    variance = np.array([0.1, 0.2]) ** 2
    weight = 1 / variance
    common = np.sum(weight * effect) / weight.sum()
    se = np.sqrt(1 / weight.sum())
    random_weight = 1 / (variance + 0.04)
    random_mean = np.sum(random_weight * effect) / random_weight.sum()
    assert np.isclose(common, 0.26) and np.isclose(se, np.sqrt(1 / 125))
    assert random_mean > common and random_weight[0] / random_weight[1] < weight[0] / weight[1]
    print(
        "Common-effect mean and SE:", common, se, "illustrative tau-squared=.04 mean:", random_mean
    )


def relative_and_circular():
    composition = np.array([1.0, 2.0, 7.0])
    scaled = 10 * composition
    assert np.allclose(composition / composition.sum(), scaled / scaled.sum())
    ratio = np.log(composition[0] / composition[1])
    assert np.isclose(ratio, np.log(scaled[0] / scaled[1]))
    radians = np.deg2rad([359.0, 1.0])
    circular = np.rad2deg(np.angle(np.mean(np.exp(1j * radians))))
    assert abs(circular) < 1e-10 and np.mean([359.0, 1.0]) == 180.0
    print("Invariant log ratio:", ratio, "circular mean near zero:", circular)


def laplace_ratio():
    epsilon = 1.0
    sensitivity = 1.0
    scale = sensitivity / epsilon

    def density(output, count):
        return np.exp(-abs(output - count) / scale) / (2 * scale)

    ratio = density(7.0, 6.0) / density(7.0, 5.0)
    assert np.isclose(ratio, np.exp(epsilon))
    assert sensitivity / 0.5 > sensitivity / 2.0
    print("Adjacent-count density ratio:", ratio, "bound:", np.exp(epsilon))


def main():
    meta_weights()
    relative_and_circular()
    laplace_ratio()


if __name__ == "__main__":
    main()
