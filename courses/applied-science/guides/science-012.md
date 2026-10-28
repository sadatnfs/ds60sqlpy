# science-012: Competing risks and proportional-hazards diagnostics

Tutorial mode. Stage: intermediate. Direct prerequisites: `science-010`, `science-011`.

## Competing events change the meaning of risk

A competing event prevents the event of interest from occurring in the same way. For example, two mutually exclusive failure modes may terminate a component's lifetime. The probability of one cause depends on survival from all causes up to each event time, not only on that cause's hazard.

For event time \(t_j\), let \(d_{kj}\) count events from cause \(k\), and let \(n_j\) be the risk set. A cumulative-incidence increment is

\[
\Delta F_k(t_j)=S(t_j^-)\frac{d_{kj}}{n_j},
\qquad
S(t_j)=S(t_j^-)\left(1-\frac{\sum_k d_{kj}}{n_j}\right).
\]

The previous survival factor includes every failure cause. A cause-specific hazard describes an instantaneous rate among units still event-free; cumulative incidence describes an absolute probability. They answer related but different questions.

## Worked case 1: reconcile cause probabilities

Four units fail sequentially from causes 1,2,1,2, with no censoring. The program accumulates each cause's incidence while updating survival for all failures. The result is .5 for each cause and zero remaining survival. These values agree with the observed proportions because follow-up is complete, giving a simple independent oracle.

Now treat cause-two events as censoring and compute one minus a cause-one Kaplan-Meier survival curve. The result is .625, larger than the actual .5 cumulative incidence. This calculation estimates a different hypothetical quantity under additional assumptions. It is not the observed probability of cause-one failure in the presence of the competing event.

Cause-specific regression can still be useful, but predicted risks must combine the relevant cause-specific hazards. A subdistribution-hazard model uses a different risk-set construction and parameter interpretation. Choosing between them should follow the target and scientific assumptions, not a rule that one software command is always preferable.

## Worked case 2: diagnose a time pattern in relative hazards

The final fixture contains a sequence of residual-like values that falls systematically with event time. The code calculates their strong negative correlation with time. These are deliberately constructed values, labeled `schoenfeld_style_trend`, rather than residuals from a fitted external dataset.

In a Cox model, Schoenfeld residual diagnostics investigate whether the observed covariate contribution at event times differs from what the fitted risk-set model predicts. A systematic time pattern can challenge the constant-coefficient proportional-hazards assumption. A formal diagnostic needs the actual fitted residuals, their scaling and a suitable reference distribution; a simple correlation in this toy sequence is only a mechanism illustration.

A lack of a visible pattern does not prove proportional hazards, especially with few events. It may be useful to estimate time interactions, stratify an appropriate variable or choose another model. Each alternative changes what can be interpreted directly. Stratification, for example, can allow different baseline hazards while sacrificing a single coefficient for the stratifying variable.

## Model evaluation follows the target

Discrimination, calibration and utility are distinct. Ranking event times correctly does not guarantee accurate cause-specific risk at a horizon. A model may be well calibrated overall while performing poorly in an important subgroup. Evaluate censoring-aware metrics with assumptions appropriate to their estimators and report the horizon and population.

Competing events also complicate causal questions. An intervention may affect the event of interest and the competing event simultaneously. An apparent reduction in one cause can arise through a change in competing-event occurrence. Controlled direct effects, separable effects and total effects require distinct definitions and assumptions. This tutorial establishes probability accounting, not identification of every intervention contrast.

Keep the event dictionary explicit. A terminal event, temporary loss of observation and a change of state that allows later transitions are different objects. If units can move through several states and return, a multi-state model may describe the process more faithfully than a single competing-risk endpoint.

## Answered scientific discussion

**Why must cause incidences and survival be reviewed together?** Their relationship checks whether probabilities describe mutually exclusive outcomes coherently. An impossible sum can reveal a data, risk-set or modeling error before any scientific interpretation is attempted.

**Does a significant proportional-hazards diagnostic tell us which model is correct?** It identifies evidence against a particular restriction. It does not select the replacement mechanism automatically. Use the scientific time process, observed patterns, validation and the desired prediction or effect target to choose a defensible continuation.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def competing_incidence(time, cause):
    t, c = np.asarray(time), np.asarray(cause)
    survival = 1.0
    incidence = np.zeros(2)
    for value in np.unique(t):
        risk = int(np.sum(t >= value))
        events = np.array([np.sum((t == value) & (c == k)) for k in (1, 2)])
        incidence += survival * events / risk
        survival *= 1 - events.sum() / risk
    return incidence, survival


def run_cases():
    incidence, survival = competing_incidence([1, 2, 3, 4], [1, 2, 1, 2])
    assert np.allclose(incidence, [0.5, 0.5]) and survival == 0
    # Censoring the competing cause estimates a different hypothetical quantity.
    km = 1.0
    for i, cause in enumerate([1, 2, 1, 2]):
        if cause == 1:
            km *= 1 - 1 / (4 - i)
    naive = 1 - km
    assert naive > 0.5
    ph_residuals = np.array([1.0, 0.8, 0.4, -0.2, -0.8, -1.0])
    trend = float(np.corrcoef(np.arange(6), ph_residuals)[0, 1])
    assert trend < -0.95
    return dict(
        cause_incidence=incidence.tolist(), naive_one_minus_km=naive, schoenfeld_style_trend=trend
    )


if __name__ == "__main__":
    evidence = run_cases()
    print("science-012 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
```

## Primary references

- [statsmodels proportional-hazards regression](https://www.statsmodels.org/stable/generated/statsmodels.duration.hazard_regression.PHReg.html)
