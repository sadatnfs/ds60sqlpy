# 6. Measurement, Exploratory Analysis, and Data Quality

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-006`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Exploration starts with the meaning of a row. Suppose an order table is joined to line items and then averaged. Revenue may be duplicated, customers may receive unintended weights, and missing dimension keys may silently disappear. These are statistical errors created before any statistical model runs.

A reliable exploratory analysis moves from contracts to distributions to conditional relationships: validate keys and units, inspect missingness and tails, compare subgroups, and investigate surprising patterns. A chart is a diagnostic tool whose construction decisions matter. Its bins, scales, aggregation and conditioning can change what appears salient.

## Methods, mechanisms, and limits

### stat-06-01

**Measurement scales**

Nominal values identify categories; ordinal values also have order; interval scales have meaningful differences; ratio scales have meaningful zero and ratios. Arithmetic on arbitrary category codes manufactures unsupported distances.

### stat-06-02

**Operational definitions**

Define concepts with executable rules, such as a failure occurring within 24 hours of deployment. Version the rule and specify time zones, denominators and exclusions. Otherwise metric changes can masquerade as behavior changes.

### stat-06-03

**Data provenance**

Record source versions, extraction time, transformations and ownership. Provenance lets reviewers reconstruct a result and distinguish a changed input from changed code. A filename alone rarely identifies immutable data.

### stat-06-04

**Data grain**

State whether a row represents an event, entity or time interval. Aggregating at the wrong grain changes implicit weights. One customer appearing in 100 events does not become 100 independent customers.

### stat-06-05

**Uniqueness and duplicate analysis**

Test unique keys before counting. Distinguish duplicate ingestion from legitimate repeated events using business identifiers and timing. Blindly dropping identical rows can delete real repeated purchases.

### stat-06-06

**Referential integrity**

Check that foreign keys refer to valid parent records and investigate orphaned records. A missing customer dimension can bias an inner join toward older or better-documented customers.

### stat-06-07

**Join cardinality analysis**

Declare one-to-one, many-to-one or one-to-many expectations and verify them. A many-to-many join can multiply both values and apparent sample size without creating any information.

### stat-06-08

**Missingness profiling**

Summarize missing rates by feature, time, group and outcome availability. Co-missingness may reveal system outages or eligibility rules. A uniform missing percentage does not identify the missingness mechanism.

### stat-06-09

**Distribution profiling**

Check support, units, multimodality and tail values before fitting. A maximum of 10,000 seconds may be an outage, unit conversion error or legitimate long task; statistical rarity alone cannot choose among them.

### stat-06-10

**Quantiles and percentiles**

Quantiles summarize ordered values and are robust to some extremes. Finite-sample interpolation conventions differ across software. State the convention when exact agreement matters, especially for small samples.

### stat-06-11

**Skewness and kurtosis**

Skewness measures standardized third moments; kurtosis concerns standardized fourth moments and may be reported with or without subtracting three. Both are highly tail-sensitive and unstable in small or heavy-tailed samples.

### stat-06-12

**Empirical cumulative distribution functions**

The empirical CDF at x is the fraction of observations no larger than x. It requires no bin choice and supports quantile reasoning. Ties create jumps rather than evidence of a smooth underlying density.

### stat-06-13

**Histograms and density estimates**

Histograms trade resolution against noise through bin width; kernel density estimates use bandwidth. Excess smoothing hides modes and insufficient smoothing invents them. Respect bounded or discrete support when choosing a smoother.

### stat-06-14

**Box plots and violin plots**

Box plots compress distributions into quantiles and outlier rules; violins add estimated density. A box-plot outlier is a plotting convention, not a proven data error. Report sample counts beside group comparisons.

### stat-06-15

**Quantile–quantile plots**

Pair sample quantiles with reference quantiles. Curvature or tail departure suggests distributional mismatch. Estimated reference parameters alter formal testing calibration, even though the visual diagnostic remains informative.

### stat-06-16

**Scatterplots and conditional plots**

Plot relationships at the unit of analysis, then condition on plausible grouping variables. Transparency, binning and small multiples reduce overplotting. A marginal straight line may conceal nonlinear subgroup patterns.

### stat-06-17

**Correlation analysis**

Inspect scatterplots along with a correlation coefficient. Pearson correlation targets linear association; rank correlations address monotonic ordering. Neither rules out confounding, reverse causation or dependence among observations.

### stat-06-18

**Partial correlation**

Residualize two variables on specified controls and correlate residuals for linear partial correlation. Adjusting for a mediator or collider can change the scientific question or introduce bias instead of removing it.

### stat-06-19

**Simpson’s paradox**

Group composition can reverse a pooled comparison relative to each stratum. Identify the target population and causal role of strata before choosing pooled or adjusted estimates. Neither version is automatically the correct causal answer.

### stat-06-20

**Ecological fallacy**

Group-level relationships do not determine individual-level relationships. A region with high income and high purchase rates may contain no within-region income association. Individual claims require appropriate individual data or strong modeling assumptions.

### stat-06-21

**Aggregation bias**

Aggregation changes weighting and can erase nonlinear or heterogeneous relationships. Report the grain and compare reasonable aggregation levels. Averaging customer rates differs from dividing total events by total exposure.

### stat-06-22

**Data leakage**

Exclude future labels, post-outcome measurements and duplicates crossing evaluation folds. Even preprocessing can leak when fit on all data. Every feature requires an availability time, not merely an event time.

### stat-06-23

**Measurement invariance**

A questionnaire or sensor should measure the same latent construct comparably across groups or periods. Apparent group differences can reflect changed loadings or thresholds rather than changed underlying attributes.

### stat-06-24

**Interrater reliability**

Agreement metrics compare labelers beyond or alongside raw agreement. Cohen's kappa depends on marginal category frequencies, so prevalence changes can change kappa without a similar change in raw agreement.

### stat-06-25

**Test–retest reliability**

Repeated measurement should yield consistent scores when the construct is stable. High correlation can coexist with a systematic shift between tests; examine differences and agreement as well as rank stability.

<!-- detailed-case-studies:start -->

## Extended case studies and scientific reasoning

### Case study: audit a metric before interpreting its movement

A weekly failure rate rises from 2% to 3%. Begin with the numerator definition: are retries counted as separate failures, are canceled attempts included, and did an error-code mapping change? Then inspect the denominator: eligible attempts, completed attempts, customers or active devices? A new logging release can change either side without a change in underlying reliability.

Reconcile counts at each transformation step. Validate uniqueness of event keys, check foreign-key coverage, and compare join cardinality with the intended grain. If a one-to-many dimension join duplicates numerator events, a final aggregation can produce plausible but inflated rates. A deduplication rule should identify the underlying event, not merely drop rows whose current displayed fields happen to match.

Version the operational definition and retain provenance. A metric trend spanning two definitions should either be reconstructed consistently or clearly labeled. Otherwise a statistical model may confidently detect a structural break created by the measurement pipeline. Data quality and statistical interpretation are one continuous responsibility.

### Case study: use several views of a skewed distribution

A service-duration distribution has a central mass near one second and rare multi-minute delays. A histogram with wide bins can hide the central structure; narrow bins can make random noise look multimodal. A log scale reveals multiplicative spread but changes visual emphasis. An ECDF supports direct statements about the fraction below a service threshold without selecting bins.

Compare median, upper quantiles, mean and tail exceedance probability because they answer different operational questions. The mean reflects aggregate resource consumption and is sensitive to long delays. A high quantile describes a service-level target, but its sample uncertainty can be large when few observations populate the tail. A maximum is especially sample-size dependent and should not be compared across periods with radically different exposure without context.

A QQ plot compares ordered quantiles to a reference family. Straight central behavior with tail departures suggests that a normal approximation may describe typical values while missing rare risk. A normality-test rejection with millions of records can be statistically certain but operationally unimportant for a robust mean estimate. Conversely, a small sample may fail to reject a tail misspecification that matters greatly. Diagnose the method's sensitivity to the departure.

### Case study: aggregation creates and removes associations

A region-level scatterplot shows higher customer spending in regions with higher average income. This does not imply that higher-income individuals within each region spend more. Region composition, prices, availability and demographics can generate the aggregate association. An ecological conclusion becomes an individual claim only with additional data or assumptions.

Likewise, a pooled treatment comparison can reverse after stratification because group proportions differ. The numerical reversal should trigger a causal and estimand review, not an automatic instruction to use whichever result seems intuitive. A pretreatment confounder can justify adjustment; a treatment-affected mediator or selection variable may not.

Partial correlation removes linear relationships with selected controls. It does not remove arbitrary nonlinear confounding and can introduce bias if the controls include a collider. The word adjusted describes a computation, not a guarantee of a scientifically improved comparison. State which variable roles justify the adjustment.

### Case study: labels produced by people or models need a measurement study

Two reviewers label incident severity. High raw agreement can occur simply because almost all incidents are low severity, so compare class-specific disagreements and a chance-adjusted statistic where useful. Cohen's kappa depends on marginal prevalences, making comparisons across populations delicate. Weighted agreement can reflect the ordering and consequence of disagreements, but its weights embed judgments.

A language model used as a labeler is also a measurement instrument. Evaluate it on representative, independently reviewed examples, including ambiguous cases and source formats. Preserve supporting text spans and abstain when the evidence is insufficient. Agreement with one noisy reviewer is not automatically ground truth, and repeated prompting does not create independent labels if the same model repeats the same bias.

Test-retest reliability asks whether the same construct remains stable under repeated measurement, while construct validity asks whether the measurement represents the intended concept. A perfectly repeatable extraction rule can consistently measure the wrong date. Validate both the implementation and the meaning before using the resulting labels in regression or causal analysis.

<!-- detailed-case-studies:end -->

## Worked Python demonstrations

Complete offline program: [chapter_06.py](../examples/chapter_06.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_06.py
```

### A valid join can produce an invalid aggregate

The one-to-many join is structurally legitimate, but summing order-level revenue after expansion yields 40 instead of 30. `validate` catches a false one-to-one claim; it does not decide which post-join statistic answers the question. Keep measures at their intended grain or aggregate line items first.

### Composition reverses a comparison

A has success rates 0.9 and 0.2, exceeding B's 0.8 and 0.1 in both strata. Yet A mostly occurs in the harder stratum, so its pooled rate is lower. The ECDF example separately shows that ties and a large tail value do not prevent an exact statement that 75% of observations are at most two.

### Complete executable example

```python
import numpy as np
import pandas as pd

def join_cardinality():
    orders = pd.DataFrame({"order":[1,2], "revenue":[10,20]})
    lines = pd.DataFrame({"order":[1,1,2], "item":["a","b","c"]})
    joined = orders.merge(lines, on="order", validate="one_to_many")
    assert joined.revenue.sum() == 40 and orders.revenue.sum() == 30
    try:
        orders.merge(lines, on="order", validate="one_to_one")
    except pd.errors.MergeError:
        pass
    else:
        raise AssertionError("Cardinality violation was not detected")
    print("Original revenue:", orders.revenue.sum(), "incorrect post-join sum:", joined.revenue.sum())

def composition_and_ecdf():
    a_success, a_count = np.array([9, 20]), np.array([10, 100])
    b_success, b_count = np.array([80, 1]), np.array([100, 10])
    assert np.all(a_success/a_count > b_success/b_count)
    assert a_success.sum()/a_count.sum() < b_success.sum()/b_count.sum()
    x = np.array([1., 1., 2., 9.])
    assert np.mean(x <= 2) == .75
    print("Within-group A rates:", a_success/a_count, "B rates:", b_success/b_count)
    print("Pooled A/B:", a_success.sum()/a_count.sum(), b_success.sum()/b_count.sum(), "ECDF(2):", .75)

def main():
    join_cardinality()
    composition_and_ecdf()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Your dashboard doubled after a join. What do you inspect first?** Compare row counts and measure totals before and after each join, validate key uniqueness and cardinality, and identify whether the measure belongs to parent or child grain. Do not repair the result with a final DISTINCT without understanding which rows multiplied.

**Interview: Does Simpson's paradox mean you should always stratify?** No. Stratification is appropriate when it matches the estimand or a valid adjustment set. Conditioning on treatment-affected variables or colliders can create another bias. The data-generating story determines which comparison matters.

## Primary sources and official APIs

- [pandas merge API and relationship validation](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html).

- [NIST exploratory data analysis](https://www.itl.nist.gov/div898/handbook/eda/eda.htm).

## Reading connections

[Previous chapter](05-sampling-surveys-and-data-collection.md) | [Book contents](../README.md) | [Next chapter](07-missing-data-measurement-error-and-robust-statistics.md)
