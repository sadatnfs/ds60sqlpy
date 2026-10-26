# When yesterday's treatment changes tomorrow's confounder

Tutorial ID: `statistics-science-008`. Prerequisites: `statistics-science-001`, `statistics-015`, `statistics-017`. Complete program: [science_08.py](examples/science_08.py).

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

Primary reference: [Hernan and Robins, longitudinal causal inference](https://miguelhernan.org/whatifbook). Related discussion: [survival and censoring](04-survival-and-competing-events.md).
