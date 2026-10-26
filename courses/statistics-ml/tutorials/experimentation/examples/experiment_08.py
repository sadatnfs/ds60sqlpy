"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests


def case_08():
    rng = np.random.default_rng(808)
    looks = np.arange(20, 201, 10)
    observations = rng.normal(size=(4000, 200))
    z = observations.cumsum(axis=1)[:, looks - 1] / np.sqrt(looks)
    naive = np.mean(np.any(np.abs(z) > stats.norm.ppf(0.975), axis=1))
    fixed = np.mean(np.abs(z[:, -1]) > stats.norm.ppf(0.975))
    planned = np.mean(np.any(np.abs(z) > stats.norm.ppf(1 - 0.05 / (2 * len(looks))), axis=1))
    mc_se = np.sqrt(0.05 * 0.95 / len(z))
    assert naive > fixed + 0.03 and planned < 0.05 + 4 * mc_se
    path = rng.binomial(1, 0.6, 200)
    n = np.arange(1, len(path) + 1)
    allocated_alpha = 0.05 / (n * (n + 1))
    radius = np.sqrt(np.log(2 / allocated_alpha) / (2 * n))
    mean = path.cumsum() / n
    lower, upper = np.maximum(0, mean - radius), np.minimum(1, mean + radius)
    evidence = np.cumprod(np.where(path == 1, 0.6 / 0.5, 0.4 / 0.5))
    holm = multipletests([0.001, 0.02, 0.04, 0.3], method="holm")[0]
    assert allocated_alpha.sum() < 0.05 and holm.sum() == 1
    result = {
        "null_fixed": fixed,
        "null_peeking": naive,
        "null_planned": planned,
        "mc_se_at_alpha": mc_se,
        "observed_cs_final": [lower[-1], upper[-1]],
        "evidence_crossed_20": bool(np.any(evidence >= 20)),
        "holm": holm.tolist(),
    }
    print("08 monitoring procedures:", result)
    return result


def main():
    case_08()


if __name__ == "__main__":
    main()
