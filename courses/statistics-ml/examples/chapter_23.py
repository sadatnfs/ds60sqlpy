import numpy as np


def conformal_rank():
    scores = np.arange(1.0, 20.0)
    alpha = 0.1
    n = len(scores)
    k = int(np.ceil((n + 1) * (1 - alpha)))
    q = np.sort(scores)[k - 1] if k <= n else np.inf
    assert k == 18 and q == 18
    possible_new_scores = np.arange(0.5, 20.0, 1.0)
    rank_coverage = np.mean(possible_new_scores <= q)
    assert rank_coverage == 0.9
    print(
        "Calibration n/k/q:",
        n,
        k,
        q,
        "coverage over illustrative equally likely ranks:",
        rank_coverage,
    )


def shift_weighting():
    source = np.array([0.8, 0.2])
    target = np.array([0.2, 0.8])
    outcome = np.array([1.0, 9.0])
    weights = target / source
    target_mean = np.sum(source * weights * outcome)
    assert np.isclose(target_mean, target @ outcome) and np.isclose(target_mean, 7.4)
    assert np.isclose(source @ outcome, 2.6)
    print(
        "Source mean:", source @ outcome, "target reweighted mean:", target_mean, "ratios:", weights
    )


def selective_prediction():
    confidence = np.array([0.55, 0.6, 0.8, 0.95])
    error = np.array([1.0, 1.0, 0.0, 0.0])
    accepted = confidence >= 0.8
    coverage = accepted.mean()
    risk = error[accepted].mean()
    assert coverage == 0.5 and risk == 0 and error.mean() == 0.5
    print(
        "Accepted fraction:",
        coverage,
        "accepted empirical error:",
        risk,
        "all-case error:",
        error.mean(),
    )


def main():
    conformal_rank()
    shift_weighting()
    selective_prediction()


if __name__ == "__main__":
    main()
