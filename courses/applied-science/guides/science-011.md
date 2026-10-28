# science-011: Censoring-aware likelihoods, AFT models and time scales

Tutorial mode. Stage: intermediate. Direct prerequisites: `science-010`.

## Incomplete event times contribute probabilities

A censored observation is not an event occurring at the censoring time. If an event time \(T\) is observed exactly, its likelihood contribution is a density \(f(t)\). If follow-up ends at \(c\) before an event is observed, the contribution is the survival probability \(S(c)=P(T>c)\). These represent different information.

For an exponential model with rate \(\lambda\), \(S(t)=\exp(-\lambda t)\). With event indicator \(\delta_i\), the likelihood and maximum-likelihood estimate are

\[
L(\lambda)=\prod_i\lambda^{\delta_i}\exp(-\lambda t_i),
\qquad \widehat\lambda=\frac{\sum_i\delta_i}{\sum_i t_i}.
\]

The numerator counts observed events and the denominator counts exposure time. A formula based only on the average recorded duration incorrectly treats every censoring time as a failure.

## Worked case 1: use the actual event indicators

The five observed durations are 1,2,4,5,8, with events only at 1,2 and 5. There are three events and 20 exposure units, so the exponential rate estimate is .15. Treating all five durations as event times gives .25. The program checks both values and keeps the naive estimate explicitly labeled as a contrasting incorrect analysis.

The rate has units of events per time. Changing time from years to months should divide the numerical rate by twelve while leaving model probabilities for equivalent durations unchanged. This unit check is useful when combining datasets or interpreting a model's scale parameter.

An exponential model assumes a constant hazard over time. That may be implausible for aging equipment, learning processes or early post-treatment risk. Correct handling of censoring does not make the exponential family appropriate. Model selection requires examining the mechanism and the features of survival that matter for the decision.

## Worked case 2: add delayed entry and a Weibull alternative

For left-truncated observations with entry times \(e_i\), conditioning on survival to entry divides each contribution by \(S(e_i)\). In the exponential model, the estimate becomes observed events divided by \(\sum_i(t_i-e_i)\). The program supplies valid entry times and verifies that the reduced exposure changes the rate. An entry time at or after the observed endpoint is rejected.

A Weibull distribution adds shape \(k>0\) and scale \(s>0\). Its log survival is \(-(t/s)^k\), and its log hazard is \(\log k-\log s+(k-1)(\log t-\log s)\). The code supplies an analytic gradient and fits both positive parameters on a log scale, using the event contribution \(\delta_i\log h(t_i)\) plus log survival for every row. It records optimizer status and gradient norm, and checks that the fitted likelihood is at least as good as the exponential starting point, since the exponential model is the Weibull case \(k=1\).

An **accelerated failure-time** interpretation models how covariates multiply the time scale, often through a linear model for log time. A proportional-hazards interpretation models a hazard multiplier. Some families support relationships between these parameterizations, but their coefficients should not be interchanged without deriving the mapping.

## Diagnostics and numerical safeguards

Positive parameters are represented by exponentiating unconstrained optimization variables. Extreme values can still create overflow or poor conditioning. Use meaningful time units, inspect the objective and check sensitivity to starting values. An optimizer success flag is useful but does not establish a well-identified or scientifically adequate model.

Compare predicted survival with appropriate empirical summaries and examine where discrepancies occur. Early-time agreement can coexist with poor tail behavior, which matters for warranty, retention or reliability decisions. Evaluate uncertainty for the quantity actually used: survival at a horizon, restricted mean time, event probability or another stated target.

The example has five observations and only three events. It is designed to verify likelihood accounting, not to choose a reliable tail model for an external population. With sparse events, priors, simpler models or explicit uncertainty may be more defensible than a highly flexible family. Later Bayesian tutorials revisit the same censoring logic with posterior computation.

## Answered scientific discussion

**Does censoring mean that the missing event time can be imputed by the follow-up duration?** No. The observed information is an inequality. Treating the lower bound as an exact event systematically changes the likelihood.

**Can a lower AIC compensate for an incorrect censoring mechanism?** It compares fitted predictive descriptions under the likelihoods supplied. It cannot validate the observation process or the causal meaning of a covariate. A well-defined likelihood starts with correct data semantics.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import optimize


def exponential_mle(time, event, entry=None):
    t, d = np.asarray(time, float), np.asarray(event, int)
    e = np.zeros_like(t) if entry is None else np.asarray(entry, float)
    if np.any(e >= t) or np.sum(d) == 0:
        raise ValueError("Need positive observed durations and an event")
    return float(np.sum(d) / np.sum(t - e))


def weibull_nll_gradient(theta, time, event):
    t, d = np.asarray(time, float), np.asarray(event, float)
    shape, scale = np.exp(theta)
    ratio = np.log(t) - np.log(scale)
    hazard_integral = np.exp(shape * ratio)
    log_hazard = np.log(shape) - np.log(scale) + (shape - 1) * ratio
    objective = -float(np.sum(d * log_hazard - hazard_integral))
    derivative_shape = -np.sum(d * (1 + shape * ratio) - shape * ratio * hazard_integral)
    derivative_scale = shape * np.sum(d - hazard_integral)
    return objective, np.array([derivative_shape, derivative_scale])


def run_cases():
    t = np.array([1.0, 2.0, 4.0, 5.0, 8.0])
    d = np.array([1, 1, 0, 1, 0])
    rate = exponential_mle(t, d)
    naive = 1 / t.mean()
    assert np.isclose(rate, 0.15) and np.isclose(naive, 0.25)
    entered = exponential_mle(t, d, [0, 0, 1, 2, 3])
    assert entered > rate

    # A Weibull log likelihood includes survival contributions for censored units.
    initial = np.log([1.0, 1 / rate])
    fit = optimize.minimize(
        lambda theta: weibull_nll_gradient(theta, t, d),
        initial,
        jac=True,
        method="BFGS",
        options={"gtol": 1e-7},
    )
    gradient_norm = float(np.linalg.norm(fit.jac))
    assert fit.success and gradient_norm < 1e-5
    assert fit.fun <= weibull_nll_gradient(initial, t, d)[0] + 1e-7
    return dict(
        censored_rate=rate,
        naive_rate=naive,
        left_truncated_rate=entered,
        weibull_shape_scale=np.exp(fit.x).tolist(),
        optimizer_success=bool(fit.success),
        optimizer_message=str(fit.message),
        gradient_norm=gradient_norm,
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-011 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [statsmodels proportional-hazards regression](https://www.statsmodels.org/stable/generated/statsmodels.duration.hazard_regression.PHReg.html)
