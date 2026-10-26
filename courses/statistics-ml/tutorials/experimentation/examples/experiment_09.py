"""Complete offline worked example. See the matching tutorial for assumptions."""

from itertools import product

import numpy as np
import statsmodels.api as sm


def case_09():
    # Two replications per factorial cell give residual degrees of freedom.
    cells = np.array(list(product([-1.0, 1.0], repeat=2)))
    factors = np.repeat(cells, 2, axis=0)
    a, b = factors.T
    noise = np.tile([-0.5, 0.5], 4)
    design = np.column_stack([np.ones(8), a, b, a * b])
    y = 10 + 2 * a + 3 * b + 4 * a * b + noise
    fit = sm.OLS(y, design).fit()
    assert np.allclose(fit.params, [10, 2, 3, 4]) and fit.df_resid == 4
    effects = {
        "A_average": 2 * fit.params[1],
        "A_at_B_low": 2 * (fit.params[1] - fit.params[3]),
        "A_at_B_high": 2 * (fit.params[1] + fit.params[3]),
    }
    alias = np.column_stack([design, a * b])
    assert np.linalg.matrix_rank(alias) == 4
    result = {
        **effects,
        "A_mean_ci95": (2 * fit.conf_int()[1]).tolist(),
        "interaction_difference": 4 * fit.params[3],
        "alias_rank": int(np.linalg.matrix_rank(alias)),
    }
    print("09 factorial effects:", result)
    return result


def main():
    case_09()


if __name__ == "__main__":
    main()
