"""Complete offline worked example. See the matching tutorial for assumptions."""

from itertools import product

import numpy as np


def case_10():
    # Two disconnected pairs. A unit's neighbor is its pair partner.
    neighbor = np.array([1, 0, 3, 2])
    baseline = np.arange(4, dtype=float)
    estimates = []
    for assignment in product([0, 1], repeat=4):
        a = np.array(assignment)
        g = a[neighbor]
        y = baseline + 2 * a + 3 * g
        # Bernoulli(1/2) assignment gives probability 1/4 to each (a,g) cell.
        means = {
            (own, other): np.mean(((a == own) & (g == other)) * y / 0.25)
            for own, other in product([0, 1], repeat=2)
        }
        estimates.append(
            [means[1, 0] - means[0, 0], means[0, 1] - means[0, 0], means[1, 1] - means[0, 0]]
        )
    direct, spillover, rollout = np.mean(estimates, axis=0)
    assert np.allclose([direct, spillover, rollout], [2, 3, 5])
    cluster = []
    for assignments in product([0, 1], repeat=2):
        a = np.repeat(assignments, 2)
        y = baseline + 2 * a + 3 * a[neighbor]
        cluster.append(np.mean(a * y / 0.5 - (1 - a) * y / 0.5))
    assert np.isclose(np.mean(cluster), rollout)
    result = {
        "mean_direct_estimator": direct,
        "mean_spillover_estimator": spillover,
        "mean_rollout_estimator": rollout,
        "cluster_policy_effect": np.mean(cluster),
        "individual_design_assignments": len(estimates),
        "cluster_assignments": len(cluster),
    }
    print("10 interference targets:", result)
    return result


def main():
    case_10()


if __name__ == "__main__":
    main()
