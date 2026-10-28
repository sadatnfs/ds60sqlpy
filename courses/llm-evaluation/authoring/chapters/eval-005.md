## Sampling for precision changes the observed mix

Rare but consequential questions deserve enough evaluation cases to reveal failures. A balanced test can therefore oversample a rare stratum relative to future traffic. Its unweighted average describes the balanced sample, not the deployment mixture. This is not a defect in sampling when the estimator and report preserve the distinction.

Let stratum \(h\) have target weight \(W_h\), with nonnegative weights summing to one, and estimated mean correctness \(\bar{C}_h\). The stratified target estimate is

\[
\widehat{\mu}=\sum_h W_h\bar{C}_h.
\]

If the sample draws independently within every stratum, its sampling variance depends on the within-stratum variability and sample sizes. A population weight is not the same as an inverse inclusion-probability weight for an arbitrary sampling design. In particular, overlapping sampling frames or repeated users need more than a two-column weight lookup.

## Worked case A: a balanced sample, an unequal target

The authored test has equal numbers of routine and rare requests. Accuracy is 0.9 in the routine stratum and 0.5 in the rare stratum. Its unweighted mean is 0.7. For a target population that is 90% routine and 10% rare, the target estimate is 0.86. Reporting both numbers is informative: the first describes this test design, and the second applies the specified deployment mixture.

Changing the rare-stratum weight to one half returns 0.7. Neither weight choice should be selected after seeing which produces a favorable model ranking. Fix the target population before comparison, retain stratum-level results, and check whether the intended traffic mix is stable over time.

{{WORKED_A}}

## Worked case B: inclusion weights and overlap

When units have known inclusion probabilities, a Horvitz-Thompson total sums observed outcomes divided by those probabilities. Dividing by a known population size gives an estimated mean. A self-normalized weighted average instead divides by the sum of sampled weights; it generally has a different finite-sample behavior. The example calculates both using tiny enumerated inputs so the denominators remain visible.

A zero inclusion probability for a relevant target unit is an identification problem. No finite weight recovers outcomes never observable under the sampling design. Very small probabilities can produce extreme weights and high variance. The descriptive effective sample size \((\sum_i w_i)^2/\sum_i w_i^2\) diagnoses concentration, but it is not a universal count of independent observations or a replacement for a design-based variance estimator.

{{WORKED_B}}

## Assumptions and uncertainty

To generalize a stratified sample, the observed cases within each stratum must represent the relevant target cases under the stated design or model. If difficult rare requests were excluded during labeling, correct top-level weights do not repair that within-stratum selection. If target weights are estimated rather than known, their uncertainty should be reflected in the final analysis.

Use the same target weights when comparing two systems. Pair their outcomes by eligible request, preserve failures, and then aggregate the paired differences. Evaluating A on one traffic mix and B on another conflates model changes with composition changes. A request, a user and a question family can also have different target weights; name which one your estimator represents.

## Practical diagnosis

Inspect support before calculating weighted metrics. Every positive target stratum needs observed data, and every supplied inclusion probability must be in the interval from zero to one with zero excluded. Print the largest weights and sensitivity to a defensible alternative target mixture. Trimming weights can reduce variance but changes the estimator and may introduce bias; it is a policy requiring explanation rather than a cosmetic cleanup step.

The synthetic examples verify arithmetic and invalid-input behavior. They do not estimate live traffic weights. In a real evaluation, document the sampling frame, exclusions, clustering, known population totals and any model used to fill coverage gaps. Keep separate worst-case or critical-risk criteria when average population utility would underweight rare severe failures.
