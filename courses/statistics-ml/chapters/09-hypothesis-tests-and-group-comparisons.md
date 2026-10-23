# 9. Hypothesis Tests and Group Comparisons

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-009`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

A hypothesis test evaluates a procedure under a specified null model. It does not assign a probability to the null hypothesis and does not establish that an effect matters. The design determines which observations can be compared, which permutations are legal, and which error rate has meaning.

For an independent two-group mean comparison, estimate delta=mean(A)-mean(B). Welch's standard error is sqrt(sA^2/nA+sB^2/nB), with an approximate degrees-of-freedom correction. For paired measurements, form each within-pair difference first and test its mean. Pairing removes stable person-level variability; pretending pairs are independent groups discards that information.

Choose the null to match the decision. Superiority asks whether an effect differs from or exceeds zero. Equivalence asks whether it lies entirely inside a meaningful interval, commonly through two one-sided tests. Failure to reject zero is not evidence that two options are sufficiently similar.

## Methods, mechanisms, and limits

### stat-09-01

**Null and alternative hypotheses**

Specify the parameter, null region, alternative direction and analysis population before looking at outcomes. A null can be composite, containing many parameter values; the reference procedure must control error across the relevant null.

### stat-09-02

**P-values**

A p-value is the null-model probability of a test statistic at least as extreme as observed. It is neither P(null given data) nor the probability that the result occurred by chance.

### stat-09-03

**Type I error**

Type I error is rejecting a true null under the testing procedure. Alpha controls its repeated-use probability under assumptions. Repeated looks or selective reporting change the procedure and can invalidate nominal alpha.

### stat-09-04

**Type II error**

Type II error is failing to reject for a specified alternative. It depends on effect size, variability, sample size and design. Nonsignificance can reflect low information rather than absence of effect.

### stat-09-05

**Statistical power**

Power is one minus Type II error for a specified alternative. Compute it before collection using realistic variance and design effects. Post-hoc power computed from the observed effect adds little beyond the p-value.

### stat-09-06

**Minimum detectable effect**

MDE is the effect size a planned design detects with chosen power and alpha. It is not the smallest possible significant observed effect. Include allocation, clustering and multiplicity in its calculation.

### stat-09-07

**One-sample t-test**

Standardize the sample mean minus a reference by its estimated SE. Exact small-sample t calibration uses normal independent errors; large-sample approximations need finite variance and appropriate dependence handling.

### stat-09-08

**Paired t-test**

Apply a one-sample test to within-pair differences. Independence is required between pairs, not within each pair. Analyze the difference distribution rather than demanding that both original measurements be separately normal.

### stat-09-09

**Welch’s t-test**

Use separate group variances rather than pooling them. This is often a sensible default for independent means, especially with unequal group sizes. It does not correct nonindependence or extreme tail instability.

### stat-09-10

**Proportion tests**

Compare observed success fractions using binomial-based uncertainty. Sparse events or extreme proportions may make normal approximations poor. Match independent, paired and clustered designs to different procedures.

### stat-09-11

**Chi-square independence test**

Compare cell counts with counts expected under row-column independence. Expected counts and independent observational units govern approximation quality. A significant table does not identify which mechanism caused the association.

### stat-09-12

**Fisher’s exact test**

Condition on fixed margins and evaluate exact contingency-table probabilities. This is useful for sparse two-by-two tables. Exactness refers to the null reference distribution and conditioning assumptions, not immunity to selection bias.

### stat-09-13

**McNemar’s test**

Use discordant pairs in paired binary outcomes to test marginal equality. Concordant pairs contribute no information about change direction. Treating paired outcomes as independent proportions wastes or misstates their covariance.

### stat-09-14

**Analysis of variance**

ANOVA decomposes variation into between-group and residual components in a linear model. A global rejection says at least one modeled mean differs, not that every pair differs. Follow-up contrasts require appropriate control.

### stat-09-15

**Welch’s ANOVA**

Allow group-specific variances when comparing several means. Welch's adjustment avoids the common-variance assumption but still requires independent groups and an adequate approximation for the group mean distributions.

### stat-09-16

**Analysis of covariance**

ANCOVA adjusts group comparisons using additional predictors. In randomized studies, pretreatment covariates can improve precision. Treatment-affected covariates may alter the estimand or introduce bias rather than improve comparability.

### stat-09-17

**Multivariate analysis of variance**

MANOVA evaluates group differences in a vector of outcomes using covariance structure. Its global result does not directly identify a practically relevant individual outcome. Sample size and covariance assumptions become more demanding.

### stat-09-18

**Mann–Whitney U test**

Rank comparisons estimate probabilistic ordering, with ties handled appropriately. A median-shift interpretation requires comparable distribution shapes. Different spreads alone can affect rank behavior even when medians agree.

### stat-09-19

**Wilcoxon signed-rank test**

Rank the absolute paired differences and attach their signs. Symmetry of the difference distribution supports the usual location interpretation. Ties and zeros require explicitly specified handling.

### stat-09-20

**Sign test**

Count positive versus negative nonzero differences using a binomial reference. It requires weaker shape assumptions than signed ranks but discards magnitude information. Excluding zero differences changes the effective sample size.

### stat-09-21

**Kruskal–Wallis test**

Compare ranks across independent groups. It detects distributional differences under its assumptions and is not automatically a pure median test. Unequal shapes complicate a location-only interpretation.

### stat-09-22

**Friedman test**

Rank conditions within each matched block and compare rank totals. Blocks must be independent. It accommodates repeated conditions without assuming ordinary normal errors, while still relying on the block design.

### stat-09-23

**Kolmogorov–Smirnov test**

The KS statistic is the maximum absolute CDF gap. Standard one-sample calibration assumes a fully specified continuous reference distribution. Estimating its parameters from the same data changes the null distribution.

### stat-09-24

**Anderson–Darling test**

Anderson-Darling weights distributional discrepancies strongly in the tails. Critical values depend on the reference family and parameter estimation. Choose the diagnostic because tail adequacy matters, not simply because it rejects more often.

### stat-09-25

**Shapiro–Wilk test**

Shapiro-Wilk checks compatibility with a normal family. Small samples have limited diagnostic power and huge samples detect harmless deviations. The relevant question is whether a method's inference is sensitive to the departure.

### stat-09-26

**Levene’s and Brown–Forsythe tests**

Compare absolute deviations from group centers. Median-centered Brown-Forsythe is less sensitive to nonnormal tails than mean-centered Levene. Variance testing should not become an unplanned switch that distorts subsequent inference.

### stat-09-27

**Likelihood-ratio test**

Compare maximized nested-model log likelihoods using twice their difference. A chi-square reference is asymptotic and can fail at boundaries or under nonidentifiability, as in some mixture comparisons.

### stat-09-28

**Wald test**

Evaluate parameter restrictions using estimates and their covariance. Wald approximations can be poor near boundaries and depend on parameterization. A reported standard error is useful only if its covariance assumptions hold.

### stat-09-29

**Score test**

Evaluate the likelihood slope under the null, scaled by information. It can avoid fitting the unrestricted alternative. Like other asymptotic tests, it needs a valid model and appropriate regularity.

### stat-09-30

**Permutation tests**

Rearrange data only under transformations justified by the null. Exchanging labels requires exchangeability; a paired design allows within-pair swaps. An arbitrary shuffle can destroy the dependence structure it should preserve.

### stat-09-31

**Randomization inference**

Generate treatment assignments using the actual randomization design and recompute a statistic under a sharp null. This uses design probabilities rather than a superpopulation error model; weaker average-effect nulls need additional care.

### stat-09-32

**Equivalence testing**

Set meaningful lower and upper margins, then reject both one-sided nonequivalence nulls. At alpha .05, an appropriate 90% two-sided interval inside the margins establishes TOST equivalence under the model.

### stat-09-33

**Noninferiority testing**

Prespecify the largest acceptable disadvantage and test against that margin. Choosing the margin after results defeats the decision interpretation. Treatment adherence and missing outcomes can particularly distort noninferiority conclusions.

## Worked Python demonstrations

Complete offline program: [chapter_09.py](../examples/chapter_09.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_09.py
```

### Respect the pair

Each person improves by one or two units but baseline levels vary enormously. The paired test isolates those changes and rejects zero; the independent comparison is highly uncertain because it incorporates between-person spread. This is a design distinction, not a contest to find whichever test produces the preferred p-value.

### Enumerate the actual experiment

Four units with two assigned treatment yield exactly six assignments. The observed mean contrast is two. Two assignments have absolute contrast at least two, giving a two-sided randomization p-value of one-third. Tiny experiments cannot produce arbitrary precision.

### Show similarity against an operational margin

An estimate 0.1 with SE 0.1 has an approximate 90% interval entirely within minus 0.5 and plus 0.5. That supports the defined equivalence claim under normal approximation. A much wider interval containing zero would fail the equivalence criterion.

### Complete executable example

```python
import numpy as np
from scipy import stats
from itertools import combinations

def paired_and_welch():
    before = np.array([10.,30.,50.,70.,90.,110.])
    changes = np.array([1.,2.,1.,2.,1.,2.])
    after = before+changes
    paired = stats.ttest_rel(after,before)
    independent = stats.ttest_ind(after,before,equal_var=False)
    assert paired.pvalue < .01 and independent.pvalue > .8
    print("Paired p:", paired.pvalue, "unpaired p:", independent.pvalue)

def exact_randomization():
    y = np.array([1.,2.,3.,4.])
    observed = y[2:].mean()-y[:2].mean()
    contrasts=[]
    for treated in combinations(range(4),2):
        mask=np.zeros(4,dtype=bool);mask[list(treated)]=True
        contrasts.append(y[mask].mean()-y[~mask].mean())
    p = np.mean(np.abs(contrasts)>=abs(observed))
    assert np.isclose(p,1/3)
    print("Six valid assignments, exact two-sided p:", p)

def equivalence():
    delta, se, margin = .1, .1, .5
    lower, upper = delta+np.array([-1,1])*stats.norm.ppf(.95)*se
    assert lower > -margin and upper < margin
    print("90% equivalence interval:", lower, upper, "inside +/-", margin)

def main():
    paired_and_welch(); exact_randomization(); equivalence()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Which test should compare before and after measurements?** First determine whether the same units were measured. Pairing permits analysis of differences; time trends, attrition and lack of a concurrent control still limit causal interpretation. A paired test alone does not identify the intervention effect.

**Interview: What does p=.03 prove?** It reports a tail probability under the stated null and procedure. It does not quantify effect importance, probability of the null or protection against undisclosed selection. Inspect the estimate, interval, design and multiplicity.

**Interview: Why is a nonsignificant result insufficient for equivalence?** An imprecise interval can include both zero and consequential harm. Equivalence requires enough precision to exclude all effects outside prespecified practical margins.

## Primary sources and official APIs

- [SciPy independent t-test and Welch option](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html).

- [SciPy permutation test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html).

## Reading connections

[Previous chapter](08-estimation-and-statistical-inference.md) | [Book contents](../README.md) | [Next chapter](10-multiple-testing-sequential-inference-and-selective-inference.md)
