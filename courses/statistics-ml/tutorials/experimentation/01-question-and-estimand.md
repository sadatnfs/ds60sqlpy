# Assignment, exposure and the question an experiment answers

Tutorial ID: `statistics-exp-001`. Prerequisites: `statistics-001`, `statistics-003`, `statistics-015`. Complete worked example: [experiment_01.py](examples/experiment_01.py). Reading requires no runtime; the Python example uses the ordinary scientific profile. All discussions below are answered.

## Key terms

- **Estimand:** The precisely defined target quantity, here the average, over all assigned eligible users, of the seven-day outcome under the redesign minus the outcome under control.
- **Counterfactual outcome:** A user's outcome under an assignment the user did not receive; a real experiment observes only one of \(Y_i(1)\) and \(Y_i(0)\) for each user.
- **All-user effect:** The average effect across every assigned user, 1.6 points here, which answers whether to assign the redesign to all eligible users.
- **Opportunity user:** A user whose relevant opportunity, recorded by `trigger` before assignment, makes benefit possible; the effect among these users is two.
- **Dilution:** The shrinking of the all-user effect by users who cannot benefit, so it equals the opportunity-user effect times the opportunity rate.

## Start with a decision

A product team proposes a redesigned activity page. The operational choice is whether to assign the redesign to all eligible users. The primary outcome is total value points per assigned user over seven days. A value point is a synthetic measure of useful activity, not currency. The assignment unit is a user; events are repeated measurements within that user. The intervention is assignment to the new page, including users who never reach it.

The shared fixture has 240 users, 120 assigned to each arm. Four out of five users have a relevant opportunity, defined before assignment by `trigger`. The baseline activity covariate also precedes assignment. Each user has several events. The [fixture specification](README.md) explains how those tables join. All first seven units reconstruct these same records from the same seed; no file download or external state is needed.

## Define the counterfactual target

Let \(Y_i(0)\) be user \(i\)'s seven-day outcome under control and let \(T_i\) indicate a pretreatment opportunity. The teaching world defines

\[
Y_i(1)=Y_i(0)+2T_i,
\qquad \tau=\frac{1}{240}\sum_{i=1}^{240}\{Y_i(1)-Y_i(0)\}.
\]

There are 192 opportunity users. Therefore \(\tau=2(192/240)=1.6\) points per assigned user. Among opportunity users, the effect is two. Both numbers are correct, but they answer different rollout questions. The all-user effect includes dilution by users who cannot benefit.

Only \(Y_i=A_iY_i(1)+(1-A_i)Y_i(0)\) would be observed in a real experiment. The synthetic generator retains both worlds only to provide an oracle for explanation and checks. Knowing the oracle here does not make individual counterfactual outcomes observable in a real product.

## Work the observed comparison

The program aggregates no events yet because it already has one outcome per assigned user. It subtracts the control mean from the treatment mean, then calculates independent-arm uncertainty. The observed contrast is about 1.584 with standard error 0.623 and an approximate 95% Welch interval from 0.356 to 2.812. The estimate need not equal the finite-population effect exactly: random assignment creates chance imbalance in baseline outcomes.

The interval is a model-based approximation treating user outcomes as independent sampling units. Complete randomization in a fixed finite population supports a distinct design-based analysis; the observed sample variance estimate is generally conservative for its difference-in-means variance because individual effect variability is not observed. Do not call a Welch interval an exact finite-population randomization interval.

## Change the inclusion rule

A valid triggered comparison can condition on the recorded pretreatment opportunity because assignment did not cause it. An exposed-only comparison conditioned on whether a user successfully loaded the new page can select different populations: the treatment could itself prevent loading. Removing those failures changes the intervention question and can introduce bias. Unit 03 constructs exactly that failure.

**Answered discussion: Why not report two points as the rollout lift?** Two points describes users with a relevant opportunity. A policy assigning everyone yields 1.6 in this world. Forecasting total benefit requires the target population's opportunity rate, not just the most responsive subset. If deployment changes who reaches the opportunity, even the dilution calculation needs a new causal argument.

## Worked example: the all-user and triggered contrasts side by side

Append this block to [experiment_01.py](examples/experiment_01.py) after its helper functions. It reuses `experiment_fixture` and `welch_summary` and estimates both targets from the same randomized records.

```python prelude=examples/experiment_01.py
users, _, untreated, effect = experiment_fixture()
for label, rows in [("all assigned", users), ("triggered only", users[users.trigger])]:
    est, se, ci = welch_summary(
        rows.loc[rows.assigned == 1, "value"], rows.loc[rows.assigned == 0, "value"]
    )
    print(f"{label:15s} n={len(rows):3d} estimate={est:.3f} se={se:.3f}")
print("opportunity rate:", users.trigger.mean())
```

```text
all assigned    n=240 estimate=1.584 se=0.623
triggered only  n=192 estimate=1.373 se=0.692
opportunity rate: 0.8
```

The oracle says the triggered effect is 2 and the all-user effect is 1.6, yet the realized triggered estimate, 1.373, is smaller than the all-user estimate. That is not a contradiction. Dropping the 48 users who cannot benefit raises the target from 1.6 to 2, but it removes little noise, because baseline activity, not the trigger, drives most outcome variation. The triggered subset loses 48 users, so its standard error rises from 0.623 to 0.692, and the chance baseline imbalance inside those 192 users happens to pull the estimate down. With a different seed the ordering could reverse. Triggering helps precision mainly when untriggered users contribute variance but no effect, for example when they generate zero value in both arms.

## Worked example: what the interval is uncertain about

The oracle lets you hold every user's two potential outcomes fixed and redraw only the assignment, which is exactly the variation complete randomization creates.

```python
users, _, untreated, effect = experiment_fixture()
treated_world = untreated + effect
rng = np.random.default_rng(1)
draws = []
for _ in range(4000):
    a = rng.permutation(users.assigned.to_numpy())
    draws.append(treated_world[a == 1].mean() - untreated[a == 0].mean())
draws = np.array(draws)
print("mean over re-randomizations:", round(draws.mean(), 3))
print("randomization SD:", round(draws.std(ddof=1), 3))
print("share within 0.5 of 1.6:", round(np.mean(np.abs(draws - 1.6) < 0.5), 3))
```

```text
mean over re-randomizations: 1.618
randomization SD: 0.624
share within 0.5 of 1.6: 0.581
```

The mean of 1.618 sits within two Monte Carlo standard errors (about 0.010 each) of the finite-population target 1.6, which is the unbiasedness that randomization buys. The spread across assignments, 0.624, nearly equals the single-sample Welch SE of 0.623 because every opportunity user has the same effect, so the unobservable effect variance is close to the dilution term alone. If individual effects varied widely, the Welch SE would exceed the true randomization SD, which is the conservativeness noted above. Only about 58% of assignments land within half a point of 1.6, a concrete reminder that one experiment can easily report 1.1 or 2.1 for the same truth.

## Assumptions this unit relies on

The calculation assumes no interference between users, one version of the redesign, and a trigger recorded identically in both arms before assignment. If the redesign changed whether `trigger` gets logged, conditioning on it becomes the exposure-selection failure described above. If a user's outcome depended on a friend's arm, the potential outcomes \(Y_i(1)\) and \(Y_i(0)\) would not be well defined, and unit 10 shows how the estimand must change.

Continue to [metric definitions](02-metric-contracts.md). Related chapter: [causal targets](../../chapters/15-causal-inference-foundations.md). Primary reading: [Hernan and Robins](https://miguelhernan.org/whatifbook).
