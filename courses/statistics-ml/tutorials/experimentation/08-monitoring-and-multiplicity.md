# Define the procedure that is allowed to stop

Tutorial ID: `statistics-exp-008`. Prerequisites: `statistics-exp-006`, `statistics-010`, `statistics-003`. Complete example: [experiment_08.py](examples/experiment_08.py).

## Key terms

- **Repeated looks:** Testing at many interim sample sizes and stopping at the first favorable crossing, which raised the false rejection rate from about .049 for one final test to about .213 in the simulation.
- **Planned-look Bonferroni:** Spending \(\alpha/K\) at each of \(K\) prespecified looks, which controls the chance of any false crossing by the union bound.
- **Confidence sequence:** A sequence of intervals that covers the target simultaneously at every sample size, so its coverage claim survives monitoring at any time.
- **Nonnegative martingale:** A process whose conditional expected multiplier under the null is one, so it crosses \(1/\alpha\) with probability at most \(\alpha\).
- **Holm procedure:** A step-down multiplicity correction across metrics that tests the smallest p-value at alpha divided by the number of tests and relaxes the threshold for each later one.

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

## Worked example: three multiplicity rules on the same p-values

The example's Holm step applies to four metrics. Compare it with Bonferroni and Benjamini-Hochberg in [experiment_08.py](examples/experiment_08.py), where `multipletests` is already imported.

```python prelude=examples/experiment_08.py
p = [0.001, 0.02, 0.04, 0.3]
for method in ["bonferroni", "holm", "fdr_bh"]:
    reject, adjusted, _, _ = multipletests(p, alpha=0.05, method=method)
    print(
        f"{method:10s} reject={reject.astype(int).tolist()} adjusted={np.round(adjusted, 3).tolist()}"
    )
```

```text
bonferroni reject=[1, 0, 0, 0] adjusted=[0.004, 0.08, 0.16, 1.0]
holm       reject=[1, 0, 0, 0] adjusted=[0.004, 0.06, 0.08, 0.3]
fdr_bh     reject=[1, 1, 0, 0] adjusted=[0.004, 0.04, 0.053, 0.3]
```

Holm trace: the smallest p, .001, is compared with .05/4 and rejects; the next, .02, is compared with .05/3, about .0167, and fails, so Holm stops. Its adjusted values, .06 and .08, are smaller than Bonferroni's .08 and .16, which is why Holm is never less powerful. Benjamini-Hochberg rejects the second metric as well, because it controls the expected share of false discoveries rather than the chance of any false discovery. For a launch decision built on one primary metric and a few guardrails, familywise control is usually the right contract; for screening dozens of exploratory metrics, a false discovery rate can be appropriate if it is declared in advance.

## Worked example: the price of looking at any time

The anytime-valid radius from the derivation above can be compared with a fixed-sample Hoeffding radius at the same \(n\).

```python
for n in [10, 50, 200, 1000]:
    anytime = np.sqrt(np.log(2 / (0.05 / (n * (n + 1)))) / (2 * n))
    fixed_hoeffding = np.sqrt(np.log(2 / 0.05) / (2 * n))
    print(
        f"n={n:4d} anytime radius={anytime:.3f} fixed-n radius={fixed_hoeffding:.3f} "
        f"ratio={anytime / fixed_hoeffding:.2f}"
    )
```

```text
n=  10 anytime radius=0.648 fixed-n radius=0.429 ratio=1.51
n=  50 anytime radius=0.340 fixed-n radius=0.192 ratio=1.77
n= 200 anytime radius=0.189 fixed-n radius=0.096 ratio=1.97
n=1000 anytime radius=0.094 fixed-n radius=0.043 ratio=2.18
```

The anytime interval is wider at every sample size, and the ratio grows slowly because \(\log(n(n+1))\) increases with \(n\). At 200 observations, permission to stop whenever you like costs roughly a doubling of width compared with committing to \(n=200\) in advance. This crude union-bound allocation is conservative; mixture-based confidence sequences from the primary reading are considerably tighter, but they still cost width relative to a single fixed look.

## Diagnosing an invalid monitoring report

Ask three questions of any reported interim result: how many looks were possible, which metrics and segments were eligible, and whether the interval quoted was built for that procedure. A dashboard that refreshes hourly with ordinary .05 intervals implies hundreds of looks, and the simulation above shows that even 19 looks inflate the error rate above four times its nominal value.

Continue to [factorial designs](09-factorial-analysis.md). Primary sources: [always-valid inference](https://arxiv.org/abs/1512.04922), [confidence sequences](https://arxiv.org/abs/1810.08240).
