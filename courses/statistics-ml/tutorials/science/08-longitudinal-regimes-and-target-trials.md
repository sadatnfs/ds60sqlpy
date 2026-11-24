# When yesterday's treatment changes tomorrow's confounder

Tutorial ID: `statistics-science-008`. Prerequisites: `statistics-science-001`, `statistics-015`, `statistics-017`. Complete program: [science_08.py](examples/science_08.py).

## Key terms

- **Sequential exchangeability:** At each decision time, treatment is independent of the potential outcomes given the observed history so far.
- **G-formula:** Computing a regime mean by averaging the outcome over the covariate distribution that the regime itself would induce.
- **Regime weight:** The inverse of the product of period-specific probabilities of following the regime, taken in time order given the observed history.
- **Target trial emulation:** Specifying the eligibility, treatment strategies, assignment time, follow-up, outcomes, estimand and analysis of a hypothetical randomized trial, then aligning observational data to it.
- **Immortal-time bias:** Bias from crediting pre-adoption follow-up to treatment when treated status is defined by later adoption.

## A two-period intervention

Let baseline condition \(L_0\) affect first treatment \(A_0\). The next condition \(L_1\) depends on both baseline and first treatment. It then affects second treatment \(A_1\) and final outcome Y. For preventive maintenance, current wear can both respond to prior maintenance and determine later maintenance.

Ordinary regression adjustment for \(L_1\) tries to remove confounding for \(A_1\), but can simultaneously block part of \(A_0\)'s effect. The target is therefore essential: a controlled direct coefficient and the total effect of a sustained policy are different quantities.

The synthetic world sets

\[
L_1\sim\operatorname{Bernoulli}\{\sigma(L_0-A_0)\},\qquad
Y=1+2A_0+3A_1+L_0+L_1+\epsilon.
\]

Treatment propensities are known functions of the available history and stay away from zero. Sequential exchangeability, positivity and consistency hold by construction. The program compares the policy treating at both times with the policy never treating.

## Compute the regime mean two ways

For a fixed regime a, the probability of following it is the product of its period-specific assignment probabilities, conditioned on the observed history at each time. The inverse-probability estimator is

\[
\widehat\mu_a=\frac1n\sum_i
\frac{\mathbf1\{A_{i0}=a,A_{i1}=a\}Y_i}
{p(A_{i0}=a\mid L_{i0})p(A_{i1}=a\mid L_{i0},A_{i0},L_{i1})}.
\]

This is a Horvitz-Thompson form, not a normalized weighted mean. The product must follow time order; using a baseline propensity for both decisions ignores changing confounding. Long histories can create extreme products even when each individual probability seems moderate.

The oracle g-formula averages over the baseline distribution and the distribution of \(L_1\) induced by each policy. Its means are approximately 2.116 under never treatment and 6.884 under always treatment, giving total effect 4.769. In 30,000 simulated observations the weighted estimate is about 4.773. The direct coefficient sum is five; the smaller total effect includes treatment's effect on \(L_1\). This sign follows the declared synthetic equations, not a substantive claim about real maintenance.

## Align a target trial before fitting

Define eligibility, treatment strategies, assignment time, follow-up, outcomes, estimand and analysis. Suppose treated users are defined as those who eventually adopt within 30 days, but follow-up begins at enrollment. Those users must remain available long enough to adopt. Crediting their pre-adoption time to treatment can create immortal-time bias.

A valid observational emulation must align time zero and use a strategy definition compatible with available data. Sequential trial emulation or cloning/censoring/weighting can address some delayed or sustained strategies, but requires explicit assumptions and uncertainty methods. This two-period known-propensity example is a foundation for that work, not a complete implementation of every target-trial estimator.

**Answered discussion: Can cross-fitting solve treatment-confounder feedback?** It helps control overfitting in nuisance estimation. It does not change the causal structure or make an ordinary regression coefficient equal a sustained-policy effect. Choose the identified estimand and score before choosing flexible learners.

## Worked example: what regression coefficients estimate here

Fit ordinary least squares to the 30,000 rows from `examples/science_08.py`, once adjusting only for baseline condition and once adding \(L_1\).

```python
import numpy as np
import statsmodels.api as sm
from scipy import special

rng = np.random.default_rng(1708)
n = 30000
l0 = rng.binomial(1, 0.5, n)
a0 = rng.binomial(1, special.expit(-0.4 + 0.8 * l0))
l1 = rng.binomial(1, special.expit(l0 - a0))
a1 = rng.binomial(1, special.expit(-0.4 + l1))
y = 1 + 2 * a0 + 3 * a1 + l0 + l1 + rng.normal(size=n)
for name, cols in (("adjust L0 only", [a0, a1, l0]), ("adjust L0 and L1", [a0, a1, l0, l1])):
    fit = sm.OLS(y, sm.add_constant(np.column_stack(cols))).fit()
    print(
        f"{name}: A0 {fit.params[1]:.3f} A1 {fit.params[2]:.3f} sum {fit.params[1] + fit.params[2]:.3f}"
    )
```

```text
adjust L0 only: A0 1.792 A1 3.227 sum 5.019
adjust L0 and L1: A0 2.010 A1 2.996 sum 5.006
```

Adjusting only for \(L_0\) leaves \(L_1\) as an open confounder of \(A_1\), so the \(A_1\) coefficient is pushed to 3.227 and the \(A_0\) coefficient falls to 1.792. Adding \(L_1\) recovers the structural coefficients, 2.010 and 2.996, whose sum 5.006 is the controlled direct effect. Neither model returns the sustained-policy effect of 4.769, because treating at time zero also lowers \(L_1\), which lowers Y by one unit for those it changes. No choice of adjustment set in a single regression delivers both quantities; the target must be chosen first.

## Worked example: weight diagnostics for each regime

Before trusting the inverse-probability means, inspect how many people follow each regime and how concentrated their weights are. The snippet also compares the Horvitz-Thompson form in the guide with a normalized version.

```python
import numpy as np
from scipy import special

rng = np.random.default_rng(1708)
n = 30000
l0 = rng.binomial(1, 0.5, n)
e0 = special.expit(-0.4 + 0.8 * l0)
a0 = rng.binomial(1, e0)
l1 = rng.binomial(1, special.expit(l0 - a0))
e1 = special.expit(-0.4 + l1)
a1 = rng.binomial(1, e1)
y = 1 + 2 * a0 + 3 * a1 + l0 + l1 + rng.normal(size=n)
for regime in (0, 1):
    follow = (a0 == regime) & (a1 == regime)
    weight = 1 / (np.where(regime, e0, 1 - e0) * np.where(regime, e1, 1 - e1))
    ess = weight[follow].sum() ** 2 / np.sum(weight[follow] ** 2)
    print(
        f"regime {regime}: followers {follow.sum()} max weight {weight[follow].max():.2f} "
        f"effective n {ess:.0f} HT mean {np.mean(follow * weight * y):.3f} "
        f"normalized mean {np.sum(follow * weight * y) / np.sum(follow * weight):.3f}"
    )
```

```text
regime 0: followers 6895 max weight 7.03 effective n 6079 HT mean 2.137 normalized mean 2.109
regime 1: followers 7561 max weight 6.21 effective n 6749 HT mean 6.910 normalized mean 6.895
```

About 6,900 people follow never-treat and 7,600 follow always-treat, and the largest weights are 7.03 and 6.21, so effective sample sizes stay above 6,000. Both versions agree closely: Horvitz-Thompson gives 6.910 minus 2.137, or 4.773, and the normalized means give 4.786, each near the oracle 4.769. With more periods, the product of probabilities would shrink, maximum weights would multiply, and the effective sample size could collapse even though each period looks benign.

## Assumptions to defend in a real analysis

Sequential exchangeability requires that every common cause of each treatment decision and the outcome is measured by that time. Positivity must hold for the regime in every history the population reaches, not just on average. Consistency requires a single well-defined version of treatment. Propensities must be estimated in practice, so their models need the same checks for calibration and overlap that the known functions skip here.

Primary reference: [Hernan and Robins, longitudinal causal inference](https://miguelhernan.org/whatifbook). Related discussion: [survival and censoring](04-survival-and-competing-events.md).
