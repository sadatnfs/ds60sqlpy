# Turn a practical effect into an information budget

Tutorial ID: `statistics-exp-004`. Prerequisites: `statistics-008`, `statistics-009`, `statistics-exp-002`. Complete example: [experiment_04.py](examples/experiment_04.py).

## Key terms

- **Power:** The probability that a specified procedure rejects under a specified alternative, which depends on the outcome distribution, effect, allocation, sample size and decision rule.
- **Minimum detectable effect:** The effect a planning calculation targets for the chosen power, error rate and sample size; it is not the smallest observed estimate that can be significant.
- **Treatment fraction:** The share \(q\) of units assigned to treatment, which enters the variance of the difference in means through \(\sigma_T^2/q+\sigma_C^2/(1-q)\).
- **Outcome maturation:** The follow-up each enrolled unit needs before its outcome is complete, which adds seven days after the last enrollment day in the example.
- **Design effect:** The variance inflation from correlated units within equal clusters, one plus the cluster size minus one times the ICC, which is 2.1 for clusters of 12 with ICC .1.

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

## Worked example: required size as a function of the target effect

Paste after `normal_total_size` in [experiment_04.py](examples/experiment_04.py) to trace the inverse-square law.

```python prelude=examples/experiment_04.py
for delta in [2.0, 1.0, 0.5, 0.25]:
    n = normal_total_size(2, 2, delta)
    print(f"delta={delta:4.2f} total users={int(np.ceil(n)):5d}")
```

```text
delta=2.00 total users=   32
delta=1.00 total users=  126
delta=0.50 total users=  503
delta=0.25 total users= 2010
```

Each halving of the target effect multiplies the requirement by four, apart from rounding: 32, 126, 503, 2010. The function holds outcome SD fixed at two, so the table is really indexed by the standardized effect \(\delta/\sigma\), from 1 down to 0.125. Two practical readings follow. First, a team that cannot afford 2,010 users should not plan for a quarter-point effect and hope; it should either accept a larger minimum detectable effect or reduce variance, as unit 07 does with a baseline covariate. Second, the 32-user row is where the normal approximation is least trustworthy, because the t reference distribution and any skew in the outcome matter most for small samples.

## Worked example: check the formula with a simulation

The planning formula promised about 80% power with 126 users. Simulating the actual Welch test checks that claim under the assumed normal outcome.

```python
rng = np.random.default_rng(404)
per_arm, reps = 63, 2000
control = rng.normal(0, 2, size=(reps, per_arm))
treated = rng.normal(1, 2, size=(reps, per_arm))
p = stats.ttest_ind(treated, control, axis=1, equal_var=False).pvalue
power = np.mean(p < 0.05)
print(
    "simulated power:",
    round(power, 3),
    "Monte Carlo SE:",
    round(np.sqrt(power * (1 - power) / reps), 3),
)
```

```text
simulated power: 0.786 Monte Carlo SE: 0.009
```

The estimate, 0.786, sits about 1.5 Monte Carlo SEs below 0.8. A small shortfall is expected: the formula uses normal quantiles, whereas the Welch test with about 124 degrees of freedom uses a slightly wider t critical value. Replacing `rng.normal` with a skewed generator, adding a novelty decay, or clustering users would change this number in ways the closed form cannot show, which is why the simulation should run the exact analysis you plan to report.

## Failure modes in planning

The most common errors are planning with a variance taken from a different population, quoting a relative lift where the formula expects an absolute one, and ignoring the outcome maturation window when converting users into calendar days. Each one produces a confident number that answers a different question. For the conversion case, planning for a 20% relative lift while the formula reads 0.20 as an absolute change would cut the required sample by a factor of about 25.

Continue to [integrity checks](05-aa-and-integrity.md). Reference: [NIST experimental design](https://www.itl.nist.gov/div898/handbook/pri/section3/pri3.htm).
