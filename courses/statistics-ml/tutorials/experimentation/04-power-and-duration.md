# Turn a practical effect into an information budget

Tutorial ID: `statistics-exp-004`. Prerequisites: `statistics-008`, `statistics-009`, `statistics-exp-002`. Complete example: [experiment_04.py](examples/experiment_04.py).

## State the alternative before collecting outcomes

Power is the probability that a specified procedure rejects under a specified alternative. It depends on the outcome distribution, effect, allocation, sample size and decision rule. The minimum detectable effect is the effect targeted by that planning calculation. It is not the smallest possible significant observed estimate.

For total sample size \(N\), treatment fraction \(q\), and independent arm variances \(\sigma_T^2,\sigma_C^2\),

\[
\operatorname{Var}(\bar Y_T-\bar Y_C)
=\frac{1}{N}\left(\frac{\sigma_T^2}{q}+\frac{\sigma_C^2}{1-q}\right).
\]

A useful normal planning approximation is

\[
N\approx\frac{(z_{1-\alpha/2}+z_{1-\beta})^2}{\delta^2}
\left(\frac{\sigma_T^2}{q}+\frac{\sigma_C^2}{1-q}\right).
\]

It targets one tail of a two-sided test under the positive alternative; the exact normal power includes the small opposite tail as well. Small samples, rare events and unknown variance warrant a more specific calculation or simulation.

## Work continuous and binary cases

With SD two in both arms, effect one, 80% power and two-sided alpha .05, the approximation gives 126 total users after rounding. Halving the effect quadruples the required information. Allocating 80% to treatment increases the requirement to 197 with equal variances. Equal allocation minimizes variance only under equal costs and appropriate variance conditions; operational risk can justify a different allocation.

For conversion rising from .20 to .24, the Bernoulli variances are .16 and .1824. Substitution gives about 3,360 total users. This is an absolute four-percentage-point change, or a 20% relative increase. Confusing those scales changes the study size drastically. The program displays power at several per-arm sample sizes rather than presenting a single magic threshold.

## Information is not elapsed time

At 300 arrivals per day with 80% eligibility, enrollment supplies 240 users daily. The binary example needs 14 enrollment days, then seven days for the final cohort's outcome to mature, giving 21 days. This simplified calculation assumes stable traffic, no repeat enrollment, no attrition and a seven-day outcome. Day-of-week variation or a novelty period can require longer observation even after nominal enrollment is sufficient.

If groups contain 12 correlated units with ICC .1, the familiar equal-cluster design effect is \(1+11(.1)=2.1\). Multiplying an independent-unit size by 2.1 is a rough variance adjustment, not a guarantee for a study with only a few clusters. Unequal sizes, treatment-effect heterogeneity and small-cluster reference distributions need explicit design analysis.

## How simulation extends the calculation

Generate assignment and complete outcomes under plausible baseline, effect, tail and dependence scenarios; run the planned analysis in each replicate; record rejection, bias, coverage and failure. If 800 of 1,000 simulations reject, estimated power is .8 with Monte Carlo SE \(\sqrt{.8(.2)/1000}\), about .0126. Increasing simulation count reduces simulation uncertainty, not real-study uncertainty. Unit 08 provides a complete repeated-procedure simulation; unit 11 changes the independent unit.

**Answered discussion: Can we resize using the observed effect?** Doing so can make the final sample size depend on favorable noise. Use a prespecified adaptation with valid inference or a new independent study. Do not label observed-effect power as new evidence beyond the same estimate and p-value.

Continue to [integrity checks](05-aa-and-integrity.md). Reference: [NIST experimental design](https://www.itl.nist.gov/div898/handbook/pri/section3/pri3.htm).
