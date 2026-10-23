# 5. Sampling, Surveys, and Data Collection

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-005`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Sampling determines which population statements are defensible. Imagine a fleet with many small sites and a few large sites. Sampling equal numbers of sites estimates a different raw average from sampling equal numbers of machines. Inclusion probabilities connect the realized sample to a specified population total or mean.

Weights address known selection mechanisms, not arbitrary gaps in coverage. Variance must reflect the design, including clustering and stratification. The number of stored records is not the effective amount of independent information. Always retain sampling strata, primary sampling units, inclusion probabilities and population totals alongside measurements.

## Methods, mechanisms, and limits

### stat-05-01

**Simple random sampling**

Select every size-n subset with equal probability. The sample mean estimates the finite-population mean without design bias. Sorting then taking the first n records is not random sampling.

### stat-05-02

**Stratified sampling**

Partition the population into nonoverlapping strata and sample within each. Combine stratum estimates using population weights. Oversampling rare strata improves subgroup precision but requires weighting for population summaries.

### stat-05-03

**Cluster sampling**

Select whole groups, then observe their members. Operational cost decreases, but similar members provide redundant information. Variance estimation must preserve clusters instead of treating every member as independently sampled.

### stat-05-04

**Multistage sampling**

Sample sites, then teams, then people. An individual's inclusion probability depends on all stages. Retain stage-specific identifiers because a single final weight does not describe all covariance induced by the design.

### stat-05-05

**Systematic sampling**

Choose a random starting position and every kth record thereafter. This is easy operationally but vulnerable to periodic ordering aligned with k. A daily cycle can make the selected sample unrepresentative.

### stat-05-06

**Probability-proportional-to-size sampling**

Give larger clusters higher selection probabilities, often then sample a fixed number inside each. Some designs approximately equalize individual inclusion probabilities; with-replacement draws and without-replacement inclusion probabilities require different calculations.

### stat-05-07

**Unequal-probability sampling**

Selection probabilities may differ to improve efficiency or cover rare groups. Distinguish a per-draw probability from the probability of appearing at least once; unbiased total estimators require the appropriate inclusion probability.

### stat-05-08

**Survey weights**

Base weights invert inclusion probabilities; later adjustments may address nonresponse or known population composition. Large weights increase variance and sensitivity. Trimming reduces instability but changes bias and must be reported.

### stat-05-09

**Horvitz–Thompson estimation**

Estimate a finite population total by summing observed y_i/pi_i. Design unbiasedness follows because E[I_i]=pi_i. Zero inclusion probability for some population units prevents identification of their contribution.

### stat-05-10

**Hájek estimation**

Normalize inverse-probability weights and compute sum(w*y)/sum(w). This ratio often stabilizes mean estimation but is generally not exactly design unbiased. It differs from dividing a Horvitz-Thompson total by a known population size.

### stat-05-11

**Poststratification**

Use known population cell counts to reweight sample cell means. Empty sampled cells cannot be repaired by weighting alone and require pooling or modeling, with additional assumptions.

### stat-05-12

**Raking**

Iteratively adjust weights to match separate population margins, such as age and region. Matching each margin does not guarantee their joint distribution matches. Extreme or incompatible margins can cause unstable weights.

### stat-05-13

**Calibration weighting**

Choose weights close to base weights while satisfying known auxiliary totals. Useful auxiliaries predict the outcome or response mechanism. Calibration constraints do not create information about unmeasured selection drivers.

### stat-05-14

**Design effects**

Compare the design-based variance with simple-random-sampling variance for the same nominal sample size. For equal clusters, 1+(m-1)*ICC is a useful approximation, not a universal formula for every design.

### stat-05-15

**Finite population correction**

Without-replacement sampling reduces uncertainty as the sampled fraction grows. The variance correction is approximately 1-n/N; use only for an appropriate finite target and design, not an unlimited superpopulation claim.

### stat-05-16

**Coverage error**

A frame omitting offline customers excludes part of the target population. No adjustment based solely on included customers verifies their missing outcomes. Audit frame construction and define the reachable population explicitly.

### stat-05-17

**Nonresponse bias**

Response bias arises when response probabilities and outcomes remain related after adjustment. High response rate does not ensure absence of bias, nor does low response necessarily imply severe bias.

### stat-05-18

**Convenience sampling**

Available respondents may differ from the target population in unmeasured ways. Describe their selection and limit claims. A large convenience sample can have tiny standard errors around a systematically wrong target.

### stat-05-19

**Selection bias**

Conditioning on inclusion can distort associations when inclusion depends on causes of multiple variables. Drawing a selection diagram helps distinguish missing population coverage from collider-induced association bias.

### stat-05-20

**Capture–recapture estimation**

Two lists with sizes n1 and n2 and overlap m suggest population size near n1*n2/m. Dependence between captures or heterogeneous capture probabilities can strongly bias this estimate; tiny overlap is unstable.

### stat-05-21

**Adaptive sampling**

Sampling may expand around detected rare events or high-value regions. Retain the adaptive design probabilities and stopping rules. Ordinary fixed-design estimators can become biased when discovery changes who is observed.

### stat-05-22

**Optimal allocation**

Neyman allocation gives more samples to large, variable strata; unequal costs modify that balance. Optimize for the actual target, since precise population means and precise rare-subgroup contrasts require different allocation.

### stat-05-23

**Measurement study design**

Plan instrument resolution, repeat measurements, timing and validation samples before collection. Repeated measurements separate within-unit noise from between-unit variability only when the repeat process itself is stable.

<!-- detailed-case-studies:start -->

## Extended case studies and scientific reasoning

### Case study: prove an inverse-probability total by enumeration

Consider a finite population with values ten and thirty. The first unit is included independently with probability .5 and the second with probability .25. The Horvitz-Thompson total is I1*10/.5+I2*30/.25, where each I indicates inclusion. The four possible samples yield totals zero, twenty, 120 and 140 with probabilities .375,.375,.125 and .125. Their probability-weighted average is forty, the true population total.

The estimator can be very variable even though it is design unbiased. Its variance in this example is 2,800, because a rarely included high-value unit receives a large weight. Unbiasedness alone is therefore not enough to choose an estimator or sampling plan. Improving inclusion of influential units, stratifying or collecting useful auxiliary information can reduce uncertainty before analysis.

The Hajek ratio divides the weighted outcome total by the estimated population count. It often stabilizes a mean but is not exactly the same as dividing a Horvitz-Thompson total by a known population size. Ratio normalization changes finite-sample properties, and an empty sample creates a denominator problem. State which estimator is used rather than referring vaguely to a weighted average.

### Case study: survey calibration cannot repair an absent population

An online survey matches known population margins for age and region after raking. This corrects those margins, but users without internet access are absent. If their outcomes differ after conditioning on age and region, the weighted survey remains biased for the full population. A large weighted sample can have a narrow interval around the wrong target.

Joint distributions matter as well. Matching age and region margins does not ensure that every age-by-region cell is represented correctly. Poststratification on joint cells can help when cell totals are known and sample information exists. Empty cells require a model, pooling or a narrower target. Weighting cannot manufacture observed outcomes for a cell with zero support.

Report weight ranges, effective sample information and sensitivity to trimming. Trimming extreme weights can reduce variance but introduces bias relative to the original design correction. That tradeoff should be visible, especially when extreme weights represent small or underserved groups. A stable dashboard is not sufficient justification for silently removing their population influence.

### Case study: sampling costs and precision targets

A population contains 800 low-variability units with SD one and 200 high-variability units with SD four. For a population mean with equal collection cost, Neyman allocation is proportional to stratum size times SD. Both strata receive the same allocation because 800*1 equals 200*4. Sampling strictly in proportion to size would devote most observations to the lower-variability stratum.

If the high-variability stratum costs four times as much per observation, a cost-constrained allocation adjusts for the square root of cost. If the objective is instead a precise estimate for the small stratum, the optimal allocation changes again. There is no universally optimal sample independent of the target and budget.

Adaptive sampling can improve discovery of rare clusters, but the selection process changes as observations arrive. Retain the design history and inclusion probabilities needed for valid estimation. Treating the final adaptively selected set as a simple random sample overstates representativeness. Design-based and model-based analyses can both be useful, but their assumptions should not be mixed silently.

### Case study: capture-recapture and list dependence

Suppose one search finds 100 entities, another finds 80 and they overlap in 20. The elementary estimate is 100*80/20=400 entities. If highly visible entities are likely to appear in both lists while hidden entities appear in neither, the overlap can be too large relative to the independent-capture model and the simple estimator can underestimate the population.

If the second search deliberately avoids entities found by the first, overlap can be too small and the estimate can be exaggerated. Heterogeneous capture probabilities and list dependence are therefore central assumptions, not minor corrections. Use additional lists, covariates or sensitivity analysis where appropriate, and communicate uncertainty when overlap is sparse.

A measurement study can sometimes be more valuable than more ordinary observations. Repeated measurements, gold-standard validation or targeted collection in missing strata can identify error mechanisms that routine large-volume logging cannot. Choose additional data by the uncertainty it can reduce in the actual decision.

<!-- detailed-case-studies:end -->

## Worked Python demonstrations

Complete offline program: [chapter_05.py](../examples/chapter_05.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_05.py
```

### Weighting defines the population contribution

An observed value 10 with inclusion probability 0.5 contributes 20 to a population total; a value 30 with probability 0.25 contributes 120. Their normalized weighted mean is 23.3333. In another population, combining cell means 2 and 8 with population shares 0.8 and 0.2 gives 3.2, not the unweighted cell average 5.

### Count independent information and allocate deliberately

With cluster size 10 and intraclass correlation 0.2, a design-effect approximation is 2.8, so 100 records have roughly the precision of 35.7 independent records for that comparison. Neyman allocation assigns equal samples to a large low-variance stratum and a small high-variance stratum in this fixture.

### Complete executable example

```python
import numpy as np

def weights_and_population():
    values = np.array([10., 30.])
    inclusion = np.array([.5, .25])
    total = np.sum(values/inclusion)
    hajek = np.sum(values/inclusion)/np.sum(1/inclusion)
    assert total == 140 and np.isclose(hajek, 70/3)
    sample_cell_mean, population_share = np.array([2., 8.]), np.array([.8, .2])
    standardized = sample_cell_mean @ population_share
    assert np.isclose(standardized, 3.2)
    print("HT total:", total, "Hajek mean:", round(hajek, 4), "poststratified mean:", standardized)

def design_and_allocation():
    cluster_size, icc, nominal_n = 10, .2, 100
    deff = 1+(cluster_size-1)*icc
    effective_n = nominal_n/deff
    assert np.isclose(deff, 2.8) and effective_n < nominal_n
    population = np.array([800., 200.])
    sd = np.array([1., 4.])
    allocation = population*sd/(population @ sd)*100
    assert np.allclose(allocation, [50, 50])
    print("Design effect:", deff, "effective n:", round(effective_n,2), "allocation:", allocation)

def main():
    weights_and_population()
    design_and_allocation()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Can weighting fix an unrepresentative sample?** It can correct specified inclusion or response mechanisms when positivity holds and the relevant adjustment information is adequate. It cannot establish outcomes for a group that never appears or remove unmeasured selection bias by itself.

**Interview: Why might a smaller stratified sample outperform a larger clustered one?** Stratification can remove composition uncertainty, while clustering repeats similar information. Compare estimator variances under each design and the actual collection budget, not only raw record counts.

## Primary sources and official APIs

- [Statistics Canada, Survey Methods and Practices](https://www150.statcan.gc.ca/n1/en/catalogue/12-587-X).

## Reading connections

[Previous chapter](04-probability-distributions-you-should-recognize.md) | [Book contents](../README.md) | [Next chapter](06-measurement-exploratory-analysis-and-data-quality.md)
