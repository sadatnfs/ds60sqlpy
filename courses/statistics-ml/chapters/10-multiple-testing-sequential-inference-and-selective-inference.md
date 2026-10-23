# 10. Multiple Testing, Sequential Inference, and Selective Inference

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-010`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

A laboratory tests one prespecified hypothesis at alpha .05. A dashboard tests 200 metrics every hour and highlights whichever crosses .05. These are different statistical procedures. Multiplicity arises across outcomes, subgroups, model choices and time. The correction must follow the procedure that could generate a reported claim.

For m valid p-values, Bonferroni uses alpha/m. The union bound gives P(any false rejection) no greater than the sum of individual error probabilities, with no independence assumption. Holm improves this by comparing ordered p-values to progressively less stringent thresholds. FDR instead controls an expected proportion among discoveries and is useful for screening, not equivalent to limiting the probability of any mistake.

Sequential evidence must be designed for monitoring. One transparent confidence-sequence construction allocates error alpha_t=alpha/[t(t+1)] at each time. Because the alpha_t values sum to alpha, the probability that any interval misses is at most alpha if each time-specific interval has its advertised coverage. This construction is conservative but makes optional-stopping protection understandable.

## Methods, mechanisms, and limits

### stat-10-01

**Family-wise error rate**

FWER is P(at least one false rejection) in a defined family. Specify the family before seeing results. Subdividing one scientific search into convenient smaller families can conceal the actual error opportunity.

### stat-10-02

**False discovery rate**

FDR is E[V/max(R,1)], where V is false discoveries and R all discoveries. It does not promise a bound on every realized discovery fraction or a per-finding probability of being false.

### stat-10-03

**Bonferroni correction**

Compare each valid p-value with alpha/m or multiply it by m, capped at one. The union-bound guarantee tolerates arbitrary dependence but can be conservative when tests are numerous or strongly correlated.

### stat-10-04

**Holm’s procedure**

Order p-values and test the smallest at alpha/m, then alpha/(m-1), stopping at the first failure. Holm controls FWER under general dependence and never rejects fewer hypotheses than ordinary Bonferroni.

### stat-10-05

**Benjamini–Hochberg procedure**

Find the largest rank k with p_(k)<=q*k/m and reject through k. Its FDR guarantee needs independence or suitable positive dependence; it is not universally valid for arbitrary dependence.

### stat-10-06

**Benjamini–Yekutieli procedure**

Divide the BH target by the harmonic sum of 1/i to obtain a conservative general-dependence correction. Its broader guarantee can substantially reduce power when the family is large.

### stat-10-07

**Adjusted p-values**

An adjusted p-value is the smallest family-level threshold at which a procedure rejects that hypothesis. It is not a posterior false-discovery probability. Preserve the family and correction name with the number.

### stat-10-08

**Simultaneous confidence intervals**

Design intervals to cover every parameter in a family jointly, for example using Bonferroni critical levels. Several separate 95% intervals generally do not give 95% joint coverage.

### stat-10-09

**Hierarchical testing**

Organize related hypotheses into a tree and allocate error according to a justified hierarchical procedure. Simply testing children after a significant parent is not enough unless the full rule has a proven guarantee.

### stat-10-10

**Gatekeeping procedures**

Require primary endpoints or earlier families to pass before later confirmatory tests proceed. This connects scientific priority to error allocation. Report which gates were prespecified and which conclusions remained exploratory.

### stat-10-11

**Alpha spending**

Allocate cumulative Type I error across information times using a spending rule and calibrated boundaries. Spending alpha separately at every look without accounting for previous looks is not alpha spending.

### stat-10-12

**Group sequential designs**

Plan interim analyses and stopping boundaries for efficacy, futility or harm. Correlation between looks matters. Report stage-adjusted inference and recognize that early stopping can exaggerate naive effect estimates.

### stat-10-13

**Sequential probability ratio tests**

Accumulate log likelihood ratios for two hypotheses and compare them with upper and lower boundaries. Classical operating-characteristic formulas assume the specified models and sampling structure; composite hypotheses need additional construction.

### stat-10-14

**Always-valid p-values**

Always-valid p-values satisfy a probability bound over permitted stopping times. They require a suitable sequential construction, not repeated ordinary fixed-sample p-values. Check assumptions about adaptation and data dependence.

### stat-10-15

**Confidence sequences**

A confidence sequence covers a fixed target simultaneously over all times with stated probability. Width shrinks with information, but usually costs some precision compared with a single prescheduled interval.

### stat-10-16

**E-values and e-processes**

A nonnegative e-value has null expectation at most one; an e-process has an appropriate sequential validity property. Ville-type bounds justify threshold crossing for nonnegative test supermartingales. Arbitrary multiplying of dependent e-values is unsafe.

### stat-10-17

**Online false discovery control**

Allocate testing levels as hypotheses arrive using rules tied to prior discoveries or wealth. Online FDR guarantees depend on the procedure's assumptions and ordering, so post-hoc reordering is not innocuous.

### stat-10-18

**Selective inference**

Condition or adjust inference for the selection event that made a result reportable. The selection procedure itself must be specified; unrecorded analyst choices make formal selective adjustment difficult.

### stat-10-19

**Post-selection inference**

After variable selection, ordinary coefficient intervals often ignore that selected variables looked promising by chance. Sample splitting offers a simple separation of selection and inference, at a power cost.

### stat-10-20

**Knockoff methods**

Construct synthetic features that mimic the dependence structure of originals while serving as negative controls. Model-X knockoffs require a valid feature-distribution construction and appropriate statistics; arbitrary shuffled columns are not equivalent.

### stat-10-21

**Winner’s curse**

Selecting the largest observed effect also selects positive noise. Independent replication, shrinkage or selection-aware inference can reduce this bias. Merely enlarging the printed confidence interval without modeling selection may not suffice.

### stat-10-22

**Multiverse analysis**

Run defensible analysis specifications and display their full result distribution or decision pattern. A multiverse reveals analytical fragility; it is not permission to report only the most favorable branch.

<!-- detailed-case-studies:start -->

## Extended case studies and scientific reasoning

### Case study: the probability of at least one lucky result

If 100 independent true null hypotheses are each tested at .05, the probability of no false rejection is .95^100, about .0059. The chance of at least one false rejection is therefore about .994. Independence is used for this exact calculation; dependence changes the number, but it does not eliminate the need to define the family of opportunities.

Bonferroni instead allocates .05/100 to each valid test and uses the union bound to control family-wise error without assuming independence. Holm retains that broad protection while using ordered thresholds more efficiently. These procedures answer a different question from FDR control, which permits some false discoveries in a screening list while controlling an expected proportion.

Under the global null, every discovery is false, so FDR equals the probability of any discovery. In mixed null/alternative families, the distinction becomes important. A discovery list controlled at 5% FDR does not mean each selected item has a 5% posterior probability of being false or that exactly 5% of this particular list is wrong.

### Case study: monitoring changes the experiment

An analyst checks an ordinary fixed-sample p-value every day and stops the first time it falls below .05. On paths where noise fluctuates toward a promising result, the study stops and preserves the favorable fluctuation. Paths with unfavorable fluctuations continue. The final reported sample size is therefore related to the observed evidence, changing the procedure's operating characteristics.

A group sequential design calibrates boundaries for planned information times. Alpha-spending methods specify how cumulative Type I error can be used as information grows. Confidence sequences and e-processes provide other frameworks for permitted ongoing monitoring. They are not interchangeable labels for rerunning a fixed-sample test.

The conservative spending construction alpha_t=alpha/[t(t+1)] is instructive because the sum telescopes to alpha. If each time-specific interval misses with probability at most alpha_t, the probability of any miss is at most alpha. This proves simultaneous protection through a union bound, though more refined methods can be much tighter. The guarantee still depends on each constituent bound's assumptions.

### Case study: likelihood-ratio evidence and optional stopping

For independent Bernoulli observations, compare a specified alternative p1 with null p0. Multiply p1/p0 after a success and (1-p1)/(1-p0) after a failure. Under the null, the expected one-step multiplier is one, so the accumulated likelihood ratio is a nonnegative martingale under the stated model. A threshold crossing can then be controlled using a martingale inequality.

This construction works because the full process, not only its final value, has the required expectation property. Multiplying arbitrary dependent e-values or selecting the most favorable among many unaccounted-for processes can destroy validity. Composite nulls, adaptive alternatives and dependent observations need appropriately designed constructions.

The evidence ratio is not itself a posterior odds statement unless prior model odds and the Bayesian model comparison framework are supplied. Nor is crossing a statistical threshold equivalent to a deployment decision. Effect size, practical consequences and integrity checks remain necessary.

### Case study: selecting a model selects favorable noise

A team screens 500 features, retains the ten with strongest associations, fits a regression and reports ordinary coefficient p-values as if those ten had been prespecified. The selection step already used the same outcomes. Those coefficients were chosen partly because their noise looked favorable, so ordinary post-selection inference can be misleading.

One transparent remedy is sample splitting: use one sample to select features and an independent sample to estimate the prespecified selected model. It sacrifices information but separates the roles. Selective-inference methods model or condition on the selection event; knockoff methods create valid synthetic competitors under specific feature-distribution conditions. Neither is a generic adjustment for undocumented analyst exploration.

A multiverse analysis can reveal how conclusions change across reasonable definitions, controls and exclusions. Show the whole defensible range and explain dependencies among specifications. Reporting only the most favorable branch turns sensitivity analysis into another selection mechanism. The purpose is to expose decision fragility and identify which assumptions deserve more evidence.

<!-- detailed-case-studies:end -->

## Worked Python demonstrations

Complete offline program: [chapter_10.py](../examples/chapter_10.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_10.py
```

### Different error targets lead to different discoveries

For the same four p-values, Holm rejects one hypothesis and BH rejects two at 0.05. Neither method is universally better. The correct choice depends on whether the decision can tolerate some false screening discoveries or needs protection against any false confirmatory claim.

### Build monitoring validity from explicit bounds

The spending sequence telescopes and remains below 0.05 over 100 looks. A Hoeffding radius uses each look's allocated error under independent bounded observations. Separately, an all-success Bernoulli path produces a likelihood ratio above 20 for p=.8 against p=.5. The one-step expected multiplier under the null equals one; the extreme path is evidence, not a statement that the null has 5% posterior probability.

### Complete executable example

```python
import numpy as np
from statsmodels.stats.multitest import multipletests

def multiple_testing():
    p = np.array([.001,.02,.04,.3])
    holm = multipletests(p,alpha=.05,method="holm")[0]
    bh = multipletests(p,alpha=.05,method="fdr_bh")[0]
    assert holm.tolist() == [True,False,False,False]
    assert bh.tolist() == [True,True,False,False]
    print("Holm decisions:",holm,"BH decisions:",bh)

def spending_and_evidence():
    alpha=.05
    t=np.arange(1,101)
    spending=alpha/(t*(t+1))
    assert spending.sum() < alpha
    means=np.full(100,.6)
    radius=np.sqrt(np.log(2/spending)/(2*t))
    assert radius[-1] < radius[0]
    observations=np.ones(8,dtype=int)
    eprocess=np.cumprod(np.where(observations==1,.8/.5,.2/.5))
    assert eprocess[-1] > 20
    null_one_step=.5*(.8/.5)+.5*(.2/.5)
    assert null_one_step == 1
    print("Spent alpha:",spending.sum(),"last Hoeffding radius:",radius[-1],"likelihood ratio:",eprocess[-1])

def main():
    multiple_testing(); spending_and_evidence()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Can you stop an A/B test as soon as p<.05?** Only if the inferential procedure was designed for that monitoring rule. Repeated fixed-sample tests increase opportunities for an accidental crossing. Use prescheduled analyses, calibrated group sequential boundaries or a valid sequential method.

**Interview: Does BH at 5% mean each selected feature has a 5% chance of being false?** No. It controls an expected fraction over repeated uses under its assumptions. It does not assign a posterior error probability to an individual feature.

## Primary sources and official APIs

- [statsmodels multiplicity procedures](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html).

- [Howard et al., Time-uniform, nonparametric, nonasymptotic confidence sequences](https://arxiv.org/abs/1810.08240).

## Reading connections

[Previous chapter](09-hypothesis-tests-and-group-comparisons.md) | [Book contents](../README.md) | [Next chapter](11-regression-and-generalized-linear-models.md)
