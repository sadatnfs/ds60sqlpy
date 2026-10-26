"""Complete offline worked example. See the matching tutorial for assumptions."""

import numpy as np
from scipy import optimize, stats
from statsmodels.duration.hazard_regression import PHReg


def cumulative_incidence(time, cause):
    survival, cif = 1.0, 0.0
    for at in np.unique(time):
        risk = np.sum(time >= at)
        d1 = np.sum((time == at) & (cause == 1))
        all_events = np.sum((time == at) & (cause != 0))
        cif += survival * d1 / risk
        survival *= 1 - all_events / risk
    return cif


def case_04():
    rng = np.random.default_rng(2804)
    n = 400
    x = rng.binomial(1, 0.5, n)
    event = rng.exponential(scale=1 / (0.12 * np.exp(np.log(1.7) * x)))
    censor = rng.exponential(scale=15, size=n)
    observed = np.minimum(event, censor)
    status = event <= censor
    cox = PHReg(observed, x[:, None], status=status).fit()
    assert np.isfinite(cox.params[0]) and cox.bse[0] > 0
    # Separate lognormal AFT generating model, fitted with censoring likelihood.
    true_log_time = 1 + 0.5 * x + rng.normal(scale=0.6, size=n)
    lifetime = np.exp(true_log_time)
    limit = rng.exponential(scale=8, size=n)
    t, died = np.minimum(lifetime, limit), lifetime <= limit

    def objective(parameters):
        location = parameters[0] + parameters[1] * x
        sigma = np.exp(parameters[2])
        z = (np.log(t) - location) / sigma
        contribution = np.where(
            died, stats.norm.logpdf(z) - np.log(t) - np.log(sigma), stats.norm.logsf(z)
        )
        return -contribution.sum()

    aft = optimize.minimize(objective, [1, 0, np.log(0.8)], method="BFGS", options={"gtol": 1e-4})
    assert aft.success and abs(aft.x[1] - 0.5) < 0.2
    times, causes = np.array([1, 2, 3, 4]), np.array([2, 1, 2, 1])
    cif = cumulative_incidence(times, causes)
    naive_survival = (1 - 1 / 3) * (1 - 1 / 1)
    assert np.isclose(cif, 0.5) and 1 - naive_survival > cif
    result = {
        "cox_hazard_ratio": np.exp(cox.params[0]),
        "cox_hr_ci95": np.exp(cox.conf_int()[0]).tolist(),
        "aft_time_ratio": np.exp(aft.x[1]),
        "true_aft_time_ratio": np.exp(0.5),
        "event_fraction": status.mean(),
        "cause1_cif": cif,
        "incorrect_cause1_km_risk": 1 - naive_survival,
    }
    print("04 censoring and competing events:", result)
    return result


def main():
    case_04()


if __name__ == "__main__":
    main()
