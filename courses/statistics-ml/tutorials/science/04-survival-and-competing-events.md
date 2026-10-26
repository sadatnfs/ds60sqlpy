# Censoring changes both the likelihood and the question

Tutorial ID: `statistics-science-004`. Prerequisites: `statistics-028`, `statistics-learning-002`, `statistics-learning-003`. Complete program: [science_04.py](examples/science_04.py).

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

Continue to [target-trial timing](08-longitudinal-regimes-and-target-trials.md). Official API: [statsmodels PHReg](https://www.statsmodels.org/stable/generated/statsmodels.duration.hazard_regression.PHReg.html).
