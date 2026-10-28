## Time zero belongs to the scientific definition

A target-trial specification aligns eligibility, treatment assignment and the start of follow-up. If a person must survive long enough to be classified as treated, but follow-up starts earlier, the treated category can contain guaranteed survival time. An estimator cannot repair this simply by adding more covariates after the categories have been defined incorrectly.

This tutorial combines a timing audit with sequential inverse-probability weighting. The scientific setup has two binary decisions. The first treatment is assigned with probability .5. An intermediate state becomes more likely after treatment, and the probability of the second treatment depends on that state. The final outcome depends on both decisions and the intermediate state.

For a deterministic policy \(d\), a path receives weight only when its observed actions agree with the policy. The denominator is the product of the conditional probabilities of those observed actions:

\[
\widehat V(d)=\frac{1}{n}\sum_i
\frac{I\{A_{i0}=d_0,\ A_{i1}=d_1(L_{i1})\}Y_i}
{P(A_{i0})P(A_{i1}\mid A_{i0},L_{i1})}.
\]

The exact conditional history must match the assumed assignment process. In a richer problem, omitting relevant prior variables from either denominator can invalidate the weighting argument. Sequential exchangeability, positivity and consistency remain identification assumptions, not numerical validations.

## Worked case 1: verify the policy value by exact summation

The program enumerates all eight possible treatment/intermediate-state paths. Each row contains its population probability, observed actions, outcome and the two assignment probabilities. It multiplies the inverse-probability score by the path's known population mass, so this is an exact expectation rather than a noisy sample average.

The always-treated policy has value 7.2. Under that regime, the intermediate state has probability .6 and contributes 1.2 outcome units; the two direct treatment contributions add five to the intercept one. The weighting calculation independently returns the same value. The total probability across the eight enumerated paths is one, checking that the joint mechanism is coherent.

This exact oracle is useful when implementing a longitudinal estimator. An implementation can be tested on a finite mechanism before being trusted on a complex dataset. It should also be tested when an action has zero probability, when treatment is missing and when the requested policy depends on information unavailable at the decision time. A division-by-zero workaround is not a substitute for a positivity policy.

## Worked case 2: detect an unavailable baseline record

The timing fixture stores eligibility, assignment, event and availability times. One record describes an event after assignment that only becomes available later. It cannot be used as a baseline predictor for that assignment, even if today's warehouse places it on the same person-level row. The program asserts that the proposed baseline contract is violated.

Event time alone is insufficient. A laboratory result may refer to a sample collected before treatment but be reported afterward. Conversely, a value can be available before treatment yet describe a different target horizon or an outcome affected by previous interventions. A valid analysis needs substantive timing semantics as well as timestamp comparisons.

A complete target-trial table records eligibility criteria, strategies, assignment, follow-up, outcomes, causal contrast and analysis plan. Cloning, censoring and weighting may be appropriate for some strategy-emulation designs, but each step needs its own interpretation. Creating multiple rows from one participant does not create independent participants; uncertainty and weighting must respect their shared origin.

## Weight diagnostics and uncertainty

Products of several assignment probabilities can become small even when each individual probability appears reasonable. Inspect path support, extreme cumulative weights and effective sample sizes by follow-up time. Stabilized weights change the numerator to reduce variation under a specified model; they should be derived with the target model rather than introduced as an unexplained normalization.

The finite example contains no estimation error. In observational analysis, assignment models, censoring mechanisms and outcome measurements are estimated or imperfectly observed. A bootstrap should resample the appropriate independent units and repeat the fitted procedure. It does not address all identification uncertainty. Report sensitivity to unsupported histories, model choices and weight handling separately.

## Answered scientific discussion

**Does successful balance after weighting prove sequential exchangeability?** It supports balance of measured histories under the fitted procedure. Unmeasured determinants of treatment and outcome can remain, and an incorrectly aligned time zero can invalidate the design before weighting begins.

**Why store availability time in a scientific dataset?** It permits reconstruction of the information available at a historical decision. Without it, an apparently prospective model may unknowingly use a revised or future record. The same principle connects causal emulation, forecasting and production feature engineering.
