"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
from scipy import optimize


def case_05():
    relevance = np.array([3, 2, 0, 1])
    order = np.array([1, 0, 3, 2])
    discount = 1 / np.log2(np.arange(2, 6))
    dcg = ((2 ** relevance[order] - 1) * discount).sum()
    ideal = ((2 ** np.sort(relevance)[::-1] - 1) * discount).sum()
    assert 0 < dcg / ideal < 1
    rng = np.random.default_rng(3205)
    n = 2000
    context = rng.integers(0, 2, n)
    action = rng.binomial(1, 0.2, n)
    reward_probability = np.where(action == context, 0.7, 0.3)
    reward = rng.binomial(1, reward_probability)
    logging_probability = np.where(action == 1, 0.2, 0.8)
    policy = context
    score = (action == policy) * reward / logging_probability
    estimate, se = score.mean(), score.std(ddof=1) / np.sqrt(n)
    assert abs(estimate - 0.7) < 4 * se
    value = np.array([3.0, 1.8, 2.0])
    cost = np.array([2.0, 1.0, 2.0])
    allocation = optimize.linprog(
        -value, A_ub=[cost], b_ub=[3], bounds=[(0, 1)] * 3, method="highs"
    )
    conservative = optimize.linprog(
        -(value - [1.5, 0.2, 0.1]), A_ub=[cost], b_ub=[3], bounds=[(0, 1)] * 3, method="highs"
    )
    assert allocation.success and conservative.success
    assert cost @ allocation.x <= 3 + 1e-8 and not np.allclose(allocation.x, conservative.x)
    result = {
        "ndcg": dcg / ideal,
        "ips_policy_value": estimate,
        "ips_se": se,
        "oracle_policy_value": 0.7,
        "expected_value_allocation": allocation.x.tolist(),
        "conservative_allocation": conservative.x.tolist(),
    }
    print("05 ranking, exposure and constrained action:", result)
    return result


def main():
    case_05()


if __name__ == "__main__":
    main()
