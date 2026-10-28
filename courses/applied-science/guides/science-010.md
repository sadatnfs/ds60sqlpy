# science-010: Survival risk sets, delayed entry and partial likelihood

Tutorial mode. Stage: intermediate. Direct prerequisites: `statistics-science-004`.

## Follow-up creates changing comparison sets

Survival analysis studies the time to an event while accounting for incomplete observation. At each event time, the relevant comparison is among units that have entered observation and have not yet failed or been censored. This **risk set** is a scientific data object, not simply every row in a table.

For a Cox proportional-hazards model, \(h(t\mid x)=h_0(t)\exp(\beta x)\). With distinct event times, a partial log likelihood is

\[
\ell(\beta)=\sum_{i:\delta_i=1}
\left[\beta x_i-\log\left\{\sum_{j\in R(t_i)}\exp(\beta x_j)\right\}\right].
\]

Here \(\delta_i\) indicates an observed event and \(R(t_i)\) contains units observed just before that event. The baseline hazard cancels from the conditional comparison. This does not make censoring or entry assumptions disappear. Ties require a specified method, and time-varying covariates require an appropriate interval representation.

## Worked case 1: calculate the likelihood by hand

Four units are observed at times 1,2,3,4, with events at 1,2 and 4. At \(\beta=0\), all risk scores equal one. The event at time one contributes \(-\log(4)\), the event at time two contributes \(-\log(3)\), and the final event contributes zero because only one unit remains at risk. The program checks this exact result.

The binary covariates are 1,0,1,0. A dense grid and a scalar optimizer both examine the likelihood. The optimum can also be derived analytically: writing \(r=\exp(\beta)\), the score equation gives \(r^2=2\), hence \(\widehat\beta=\frac{1}{2}\log(2)\). Agreement with this independent value checks the implementation rather than merely trusting an optimizer's status.

A hazard ratio is not a ratio of cumulative event probabilities, and it is not a difference in expected survival times. The baseline hazard and covariate distribution are needed to obtain many absolute-risk quantities. Interpretation should therefore begin with the target measure rather than ending with an exponentiated coefficient.

## Worked case 2: delayed entry changes the risk set

One unit now enters observation at time 2.5. It must not appear in the denominators for events at times one or two. At zero coefficient, the log likelihood becomes \(-\log(3)-\log(2)\). The code verifies this separately from the ordinary risk-set calculation.

This is **left truncation** or delayed entry, not right censoring. Right censoring says that an observed unit's event time exceeds its last follow-up. Delayed entry says that inclusion requires remaining event-free until entry. Ignoring it can over-represent longer survivors and put impossible comparisons into early risk sets.

The example uses `entry <= event_time` and has no entry/event ties, avoiding a convention-dependent boundary. Real interval data require clear definitions for open and closed endpoints and a tie-handling strategy. Sorting timestamps without documenting those conventions is insufficient when events and updates can share a recorded time.

## What the calculation assumes

The proportional-hazards assumption states that the covariate multiplier is constant over time in the specified model. It can fail even when a fitted coefficient is statistically precise. Investigate time interactions, residual patterns and whether the underlying scientific mechanism plausibly supports proportional hazards.

Independent censoring is conditional on the variables and structure used in the analysis. Administrative study ending can be easier to justify than loss to follow-up related to prognosis. Neither is automatically harmless. The event definition, time origin, entry criteria and censoring process should be recorded before fitting.

The tiny fixture provides an exact likelihood check, not a reliable standard error or a general-purpose implementation of Cox regression. Production analysis should use a reviewed fitting library, validate its tie and entry options, examine the design matrix and retain diagnostics. The earlier survival tutorial supplies fitted-library examples; this unit explains the risk-set mechanism underneath them.

## Answered scientific discussion

**Why exclude censored times from the numerator but keep those units in earlier denominators?** A censored unit has not supplied an event time, yet it was known to be event-free before censoring. That information defines its participation in prior risk sets.

**Does a partial likelihood avoid modeling assumptions?** It avoids directly parameterizing a baseline hazard for this coefficient calculation. It still relies on a model for relative hazards and on a defensible observation process. A simpler-looking objective should not be confused with assumption-free inference.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import optimize, special


def cox_loglik(beta, time, event, x, entry=None):
    time, event, x = np.asarray(time), np.asarray(event), np.asarray(x, float)
    entry = np.zeros(len(time)) if entry is None else np.asarray(entry)
    total = 0.0
    for i in np.flatnonzero(event):
        risk = (entry <= time[i]) & (time >= time[i])
        total += beta * x[i] - special.logsumexp(beta * x[risk])
    return float(total)


def run_cases():
    t = np.array([1.0, 2.0, 3.0, 4.0])
    d = np.array([1, 1, 0, 1])
    x = np.array([1.0, 0.0, 1.0, 0.0])
    zero = cox_loglik(0, t, d, x)
    assert np.isclose(zero, -np.log(4) - np.log(3))
    entry = np.array([0.0, 0.0, 2.5, 0.0])
    delayed = cox_loglik(0, t, d, x, entry)
    assert np.isclose(delayed, -np.log(3) - np.log(2))
    grid = np.linspace(-2, 2, 401)
    scores = np.array([cox_loglik(b, t, d, x) for b in grid])
    best = float(grid[scores.argmax()])
    assert scores.max() >= zero
    fit = optimize.minimize_scalar(
        lambda b: -cox_loglik(b, t, d, x), bounds=(-3, 3), method="bounded"
    )
    assert fit.success and np.isclose(fit.x, 0.5 * np.log(2), atol=1e-5)
    return dict(
        zero_log_partial_likelihood=zero,
        delayed_entry_log_partial_likelihood=delayed,
        grid_beta=best,
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-010 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [statsmodels proportional-hazards regression](https://www.statsmodels.org/stable/generated/statsmodels.duration.hazard_regression.PHReg.html)
