import numpy as np


def weights_and_population():
    values = np.array([10.0, 30.0])
    inclusion = np.array([0.5, 0.25])
    total = np.sum(values / inclusion)
    hajek = np.sum(values / inclusion) / np.sum(1 / inclusion)
    assert total == 140 and np.isclose(hajek, 70 / 3)
    sample_cell_mean, population_share = np.array([2.0, 8.0]), np.array([0.8, 0.2])
    standardized = sample_cell_mean @ population_share
    assert np.isclose(standardized, 3.2)
    print("HT total:", total, "Hajek mean:", round(hajek, 4), "poststratified mean:", standardized)


def design_and_allocation():
    cluster_size, icc, nominal_n = 10, 0.2, 100
    deff = 1 + (cluster_size - 1) * icc
    effective_n = nominal_n / deff
    assert np.isclose(deff, 2.8) and effective_n < nominal_n
    population = np.array([800.0, 200.0])
    sd = np.array([1.0, 4.0])
    allocation = population * sd / (population @ sd) * 100
    assert np.allclose(allocation, [50, 50])
    print("Design effect:", deff, "effective n:", round(effective_n, 2), "allocation:", allocation)


def main():
    weights_and_population()
    design_and_allocation()


if __name__ == "__main__":
    main()
