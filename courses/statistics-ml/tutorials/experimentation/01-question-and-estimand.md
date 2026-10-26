# Assignment, exposure and the question an experiment answers

Tutorial ID: `statistics-exp-001`. Prerequisites: `statistics-001`, `statistics-003`, `statistics-015`. Complete worked example: [experiment_01.py](examples/experiment_01.py). Reading requires no runtime; the Python example uses the ordinary scientific profile. All discussions below are answered.

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

Continue to [metric definitions](02-metric-contracts.md). Related chapter: [causal targets](../../chapters/15-causal-inference-foundations.md). Primary reading: [Hernan and Robins](https://miguelhernan.org/whatifbook).
