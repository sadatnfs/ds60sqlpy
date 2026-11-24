# Censoring changes both the likelihood and the question

Tutorial ID: `statistics-science-004`. Prerequisites: `statistics-028`, `statistics-learning-002`, `statistics-learning-003`. Complete program: [science_04.py](examples/science_04.py).

## Key terms

- **Right censoring:** Follow-up ends before the event is observed, so the record shows only that the event time exceeds the censoring time.
- **Hazard ratio:** The ratio of instantaneous event rates among those still at risk; it is not a ratio of survival times or cumulative risks.
- **Proportional hazards:** The Cox model assumption that covariates multiply a shared baseline hazard by a factor that is constant over time.
- **Accelerated failure time model:** A model in which covariates stretch or compress the time scale, so an exponentiated coefficient is a time ratio.
- **Cumulative incidence:** The probability of a specific event cause occurring by a given time when competing events can also occur.

## An unfinished duration is not a completed long duration

Observe \(T_i=\min(T_i^*,C_i)\) and an event indicator \(D_i=\mathbf1\{T_i^*\le C_i\}\). For right censoring, an event contributes a density and a censored observation contributes survival probability. Under an appropriate conditional independent-censoring assumption,

\[
L_i=f(T_i\mid X_i)^{D_i}S(T_i\mid X_i)^{1-D_i}.
\]

Discarding censored observations selects those with observed early events. Treating censoring time as the event time invents events. Neither operation is repaired by increasing sample size.

## Work a proportional-hazards model

The first synthetic world uses an exponential baseline hazard .12 and hazard multiplier 1.7 for a binary feature. Independent exponential censoring produces incomplete follow-up. The program fits a Cox proportional-hazards model with `statsmodels.PHReg`, reports the exponentiated coefficient and its interval, and preserves the censor indicator.

The fitted hazard ratio is approximately 1.902 with interval [1.502,2.407] for this seed. A hazard ratio compares instantaneous event rates among those still at risk; it is not a ratio of survival times or cumulative event probabilities. Proportional hazards is a model assumption. Inspect time dependence of effects, residual diagnostics, covariate functional form and censoring plausibility before using a real fit.

## Change to an accelerated-time question

A separate fixture generates log duration as \(1+.5X+\epsilon\), with normal noise SD .6. The code directly minimizes the censored lognormal negative log likelihood, including `logsf` for censored rows and the density's time/scale terms for observed events. The estimated time ratio is about 1.734; the synthetic target is \(e^{.5}\), about 1.649.

This AFT coefficient stretches the time scale. It is a different interpretation from a proportional hazard coefficient. Similar predictor names and outcome units do not make the model families interchangeable. The direct likelihood demonstrates what a library must account for, but a complete real analysis also needs uncertainty, diagnostics and sensitivity to the chosen survival distribution.

## A competing event is not ordinary independent censoring

Four individuals fail at times 1,2,3,4 with causes 2,1,2,1. At each time, update all-cause survival using all events, then add the pre-event survival multiplied by the cause-one event fraction. This Aalen-Johansen calculation gives cause-one cumulative incidence .5.

If the two cause-two events are instead censored and one reports one minus cause-one Kaplan-Meier survival as observed cause-one risk, the result is one. The latter corresponds to a different hypothetical interpretation and overstates the actual cumulative incidence here. Cause-specific hazard modeling can legitimately censor competing events for hazard estimation; the error is interpreting its survival complement as the competing-risk probability without the other hazards.

**Answered discussion: Does complete follow-up identify a causal treatment effect?** It improves observation, but causal identification still depends on assignment, consistency and appropriate comparisons. In an observational target trial, defining treated groups using future treatment can introduce immortal-time bias before the survival model is fitted.

## Worked example: three wrong answers and one right one

Reuse the exponential event and censoring rates from `examples/science_04.py` without the binary feature, so the true mean time to event is known to be \(1/0.12\).

```python
import numpy as np

rng = np.random.default_rng(2804)
event = rng.exponential(scale=1 / 0.12, size=400)
censor = rng.exponential(scale=15, size=400)
t, d = np.minimum(event, censor), event <= censor
print(f"true mean time to event: {1 / 0.12:.2f}; events observed: {d.sum()} of 400")
print(f"mean of observed event times only: {t[d].mean():.2f}")
print(f"mean treating censoring as events: {t.mean():.2f}")
print(f"exponential MLE (total time / events): {t.sum() / d.sum():.2f}")
```

```text
true mean time to event: 8.33; events observed: 256 of 400
mean of observed event times only: 4.84
mean treating censoring as events: 5.03
exponential MLE (total time / events): 7.86
```

Only 256 of 400 events are observed. Averaging those event times gives 4.84, little more than half of the true 8.33, because long durations are exactly the ones censoring cuts off. Treating every censoring time as an event barely helps, 5.03, since it invents events at times that are only lower bounds. The exponential maximum likelihood estimate, total follow-up divided by the number of events, uses each censored row as time at risk without an event and gives 7.86, close to the truth. The likelihood in the guide is what makes that division correct.

## Worked example: Aalen-Johansen with a censored row

Extend the four-person competing-risk example with a fifth individual and a censoring at time 2, and print every step of the cumulative incidence calculation.

```python
import numpy as np

time = np.array([1, 2, 3, 4, 5])
cause = np.array([2, 0, 1, 2, 1])
survival, cif = 1.0, 0.0
print("time at_risk cause cif1   survival")
for at, c in zip(time, cause):
    risk = np.sum(time >= at)
    cif += survival * (c == 1) / risk
    survival *= 1 - (c != 0) / risk
    print(f"{at:4d} {risk:7d} {c:5d} {cif:.3f}  {survival:.3f}")
```

```text
time at_risk cause cif1   survival
   1       5     2 0.000  0.800
   2       4     0 0.000  0.800
   3       3     1 0.267  0.533
   4       2     2 0.267  0.267
   5       1     1 0.533  0.000
```

At time 1 a cause-two event lowers all-cause survival to 0.800 but leaves the cause-one incidence at zero. The censoring at time 2 changes neither quantity; it only shrinks the risk set from four to three. At time 3 the cause-one event adds \(0.800\times1/3=0.267\). At time 4 a competing event lowers survival again, so the final cause-one event at time 5 adds only \(0.267\times1/1\), reaching 0.533. Every increment is scaled by the probability of still being event-free, which is how competing events reduce the chance of observing cause one.

## Checks before trusting a survival analysis

Tabulate events and censorings over time and by group; censoring that differs by arm hints at informative dropout. Examine whether the hazard ratio changes over follow-up, for example by fitting separate periods. Define time zero identically for every group. When competing events exist, report cumulative incidence for each cause, not one minus a Kaplan-Meier curve.

Continue to [target-trial timing](08-longitudinal-regimes-and-target-trials.md). Official API: [statsmodels PHReg](https://www.statsmodels.org/stable/generated/statsmodels.duration.hazard_regression.PHReg.html).
