## Sampling weights describe a design

A sample can deliberately over-represent some units to improve information about rare groups or reduce collection costs. An unweighted average then describes the realized sample, which may not represent the target population. Design-based reasoning uses known inclusion probabilities to account for how the sample was selected.

Let \(\pi_i\) be the probability that population unit \(i\) is included, and let \(S_i\) indicate inclusion. For a finite population total \(T=\sum_i y_i\), the Horvitz-Thompson estimator is

\[
\widehat T_{\mathrm{HT}}=\sum_i\frac{S_iy_i}{\pi_i},
\qquad
\mathbb{E}_{\mathrm{design}}[\widehat T_{\mathrm{HT}}]=\sum_i y_i.
\]

The expectation is over the sampling design, with population values held fixed. It is a different argument from treatment propensity weighting or model-based regression. Accurate first-order inclusion probabilities are enough for the unbiasedness statement, while variance estimation generally requires more information about the joint design.

## Worked case 1: distinguish expectation from one realized sample

The population values are 1,2,5,8, with unequal inclusion probabilities .2,.4,.5,.8. The code computes the design expectation of the weighted total and recovers 16 exactly. It then evaluates one particular realized sample containing the second and fourth units. That sample's weighted total is 15, illustrating that unbiasedness does not require every sample to equal the population value.

The program also calculates a ratio or Hajek-style weighted mean for that sample. Its denominator estimates population size through the sum of weights. Ratio estimators can improve practical behavior but do not generally inherit the exact finite-sample unbiasedness of the Horvitz-Thompson total. An attractive value in one sample is not proof of its design properties.

A zero inclusion probability means that the design supplies no information about the excluded unit for this estimator. Calibration weights or a model can add assumptions, but they cannot create a design-based observation that was never possible. The target population and sampling frame should therefore be defined together.

## Worked case 2: derive a cluster design effect

For a cluster of size \(m\) with equal unit variance and common pairwise correlation \(\rho\), the variance of the cluster total reflects both diagonal and off-diagonal covariance. Relative to independent units, the familiar equal-cluster expression is

\[
\operatorname{DEFF}=1+(m-1)\rho.
\]

With five units and correlation .3, the design effect is 2.2. The code constructs the covariance matrix explicitly and verifies that summing its entries produces the same factor. This derivation exposes the assumptions behind the formula rather than treating 2.2 as a generic penalty for clustered data.

Unequal cluster sizes, variable weights, stratification, informative sampling and different estimators can alter the design effect. A universal adjustment based only on the number of rows can be badly misleading. The relevant number of independent primary sampling units may be far smaller than the number of measured individuals.

## Carry the design into analysis

Retain strata, cluster IDs, inclusion probabilities and any replicate weights supplied by the design. Dropping them during cleaning can make a later variance calculation impossible. Missing responses introduce another mechanism: inclusion in the sample is not the same as responding to the survey, and response adjustment needs its own assumptions.

Poststratification and calibration align weighted summaries with known population totals. Their usefulness depends on the calibration variables and population information. Extreme resulting weights can increase variance, and a weighted population estimate should be checked for support and sensitivity. Do not choose calibration targets simply because they produce an appealing outcome.

Model-based and design-based analyses can both be useful. State which source of randomness and which target support the inference. A model that predicts outcomes accurately in the realized sample can still misrepresent the population if the sampling or response process is ignored.

## Answered scientific discussion

**Does a large weighted population count mean we observed that many independent people?** No. Weights represent units in the target under a design or adjustment. Precision still depends on the actual sample, dependence and estimator.

**Should all weights be normalized to mean one?** Some point estimates are invariant to a common rescaling, while totals and some variance procedures are not. Follow the estimator's definition and retain the original weight meaning and population totals.
