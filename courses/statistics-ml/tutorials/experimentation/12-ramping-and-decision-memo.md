# From a trustworthy result to a bounded rollout

Tutorial ID: `statistics-exp-012`. Prerequisites: `statistics-exp-006`, `statistics-exp-007`, `statistics-exp-008`, `statistics-exp-010`, `statistics-exp-011`. Complete example: [experiment_12.py](examples/experiment_12.py).

## Ramping changes exposure, not the rules of evidence

A rollout can start with a small eligible population to inspect reliability and measurement, then increase exposure through prespecified stages. State who can enter each stage, how assignments persist, which data belong to the estimand, and which safety signals stop exposure. Operational ramping is not automatically a statistically valid sequential efficacy test.

If early stages have different traffic sources or eligibility, pooling them without accounting for those differences can change the target. If assignment probabilities change, analysis may need stage-specific estimates and explicit weighting. A treatment effect calculated on an outcome-selected final stage does not inherit validity from the initial randomization.

## Mature every outcome

For a seven-day outcome, a user enrolled yesterday has not supplied a seven-day observation. The shared fixture has 198 users with at least seven days of follow-up out of 240 assigned users. The example counts this difference. It does not silently mark the remaining users as failures or zeros.

A mature-cohort analysis can be defined using enrollment dates and observation cutoff that do not depend on outcomes. Censoring methods may be appropriate for a different target, but require their own assumptions. Calendar age and time since first exposure are different clocks; novelty analyses need the latter as well as a concurrent control.

## Contrast novelty with persistence

The second teaching world defines an age-specific effect

\[
\tau(t)=0.2+1.8\exp\{-(t-1)/7\}.
\]

The effect is two on day one but about .238 at day 28. This formula is a declared synthetic mechanism, not a fitted extrapolation. It shows why a precise first-day gain does not establish a durable gain. Follow comparable randomized cohorts to the same exposure ages; avoid comparing selected long-staying treated users with a different control population.

## Four complete decision cases

The decision helper uses a practical benefit margin .5 and an upper acceptable guardrail deterioration .1. Its inputs are assumed already valid intervals from the chosen analysis; the helper itself does not create valid statistical evidence.

| Benefit interval | Guardrail upper bound | Integrity/maturity | Explained decision |
| --- | --- | --- | --- |
| [.7,1.3] | .08 | Passed | Eligible for a bounded rollout under the stated utility rule |
| [.7,1.3] | .08 | Integrity failed | Investigate; the numerical interval cannot repair corrupted measurement |
| [-.2,1.3] | .08 | Passed | Inconclusive against the practical benefit threshold |
| [.7,1.3] | .15 | Passed | Guardrail unresolved despite a favorable primary estimate |

These are explicit operational rules, not a universal launch policy. A severe harm might require a different constraint. A portfolio of endpoints needs a prespecified multiplicity policy, especially when interpreting simultaneous benefit and safety claims.

## A worked memo for the shared experiment

The raw seven-day value estimate is 1.584 points with interval [.356,2.812], which does not establish benefit above .5. Prespecified baseline adjustment gives approximately 1.504 with interval [1.194,1.813] under its robust regression assumptions. The adjusted result supports the benefit threshold in the synthetic complete dataset. A real recommendation still requires the separate logging/integrity and guardrail evidence, mature outcomes, and a credible account of interference. The logging-corrupted version in unit 03 fails this chain and must not inherit the clean dataset's recommendation.

**Answered discussion: Does a successful experiment prove permanent rollout value?** It supports the intervention, population, horizon and environment actually studied. Persistent holdouts and follow-up can reveal adaptation or cumulative harms. Replication and monitoring extend evidence; they do not retroactively make a short experiment a long-term study.

Return to the [route contents](README.md). Primary scope reference: [Trustworthy Online Controlled Experiments](https://assets.cambridge.org/97811087/24265/toc/9781108724265_toc.pdf).
