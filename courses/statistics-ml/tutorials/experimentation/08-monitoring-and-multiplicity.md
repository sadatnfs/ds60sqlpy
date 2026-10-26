# Define the procedure that is allowed to stop

Tutorial ID: `statistics-exp-008`. Prerequisites: `statistics-exp-006`, `statistics-010`, `statistics-003`. Complete example: [experiment_08.py](examples/experiment_08.py).

## Repeated opportunities change the question

A fixed-sample p-value controls its stated error at one specified sample size. Looking repeatedly and preserving the first favorable crossing is another procedure. Dependence between successive looks reduces the number of fully independent opportunities, but does not restore fixed-horizon validity.

The worked simulation draws 4,000 paths of 200 independent standard-normal observations under a zero mean. At each of 19 prespecified sample sizes, it computes the known-variance statistic \(Z_n=\sum_{i=1}^nY_i/\sqrt n\). Using a known variance isolates the stopping issue from variance estimation.

The fixed final test rejects about .049 of paths. Repeated ordinary .05 tests reject about .213. A conservative planned-look Bonferroni procedure rejects about .014. The Monte Carlo SE near the nominal .05 rate is about .00345. These are observed frequencies for this generating process, not universal constants.

## Derive a transparent monitoring guarantee

With \(K\) prespecified looks, assigning each a two-sided error \(\alpha/K\) controls the probability of any false crossing by the union bound. It needs no independence between looks, but each individual test must be valid. More efficient group-sequential designs use the joint distribution of correlated test statistics; their boundaries cannot be created by simply dividing the final critical value by the number of looks.

For an unlimited sequence of independent observations bounded in [0,1], allocate

\[
\alpha_n=\frac{\alpha}{n(n+1)},\qquad
r_n=\sqrt{\frac{\log(2/\alpha_n)}{2n}}.
\]

Hoeffding's inequality bounds each miss by \(\alpha_n\), and the sum of allocated errors is at most \(\alpha\). Therefore the intervals \([\bar Y_n-r_n,\bar Y_n+r_n]\), clipped to [0,1], cover the fixed mean simultaneously with at least \(1-\alpha\) probability under the assumptions. The program constructs these intervals around an actual observed Bernoulli path, not a fabricated constant mean. Their conservatism is visible in the final width.

## Evidence processes and decisions

For a simple Bernoulli null .5 and alternative .6, multiply the likelihood ratio by 1.2 after success and .8 after failure. Its null conditional expected multiplier is one. The product is a nonnegative martingale; a crossing of \(1/\alpha\) can be controlled by a martingale inequality. The example checks whether its observed path crossed 20. The evidence ratio is not a posterior probability that the null is false.

Metrics and subgroups create further multiplicity. Holm applied to [.001,.02,.04,.3] rejects only the first at .05. A sequentially valid p-value for each metric does not automatically control the family across metrics. Specify both time and outcome opportunities.

## What to report at stopping

An early extreme estimate is selected partly for favorable noise. Report the stopping rule, time, information, effect estimate and an interval valid for the allowed monitoring scheme. A confidence sequence supports its time-uniform coverage claim; it does not make the raw stopped estimate unbiased or establish that a practical threshold has been met. Retain exposure maturity and guardrail checks before the action decision.

**Answered discussion: Is a safety stop forbidden?** No. Protecting users can justify stopping operationally. The scientific report must then describe that rule and use valid inference or label ordinary fixed-horizon analysis as descriptive. Safety authority and statistical calibration are separate questions.

Continue to [factorial designs](09-factorial-analysis.md). Primary sources: [always-valid inference](https://arxiv.org/abs/1512.04922), [confidence sequences](https://arxiv.org/abs/1810.08240).
