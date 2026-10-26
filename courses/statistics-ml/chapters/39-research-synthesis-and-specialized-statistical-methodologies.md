# 39. Research Synthesis and Specialized Statistical Methodologies

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-039`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Specialized methods become useful when the observational object or evidence structure violates the assumptions of a familiar table of independent unconstrained numbers. Studies arrive with different precision and populations; survey items measure latent traits; percentages share a total; directions wrap around a circle; curves contain many related points. The appropriate representation is part of the statistical question, not a preprocessing detail to be standardized away.

### Synthesize compatible evidence before averaging it

A meta-analysis combines study estimates only after defining a common estimand or a meaningful distribution of effects. If study i estimates theta_i with sampling variance v_i, a common-effect inverse-variance mean weights by \(\frac{1}{v_{i}}\). A random-effects model adds between-study variance tau_squared, using weights \(\frac{1}{v_{i}+\tau^2}\) in a basic formulation. This changes both interpretation and relative weights. More precise aggregation cannot repair biased studies or incompatible outcome definitions.

A systematic review therefore begins before the model: search strategy, eligibility, duplicate-study handling, risk-of-bias assessment and extraction protocol. Publication and selective-reporting mechanisms can distort the available evidence. An LLM can help locate candidate passages or draft an extraction table, but a human-reviewed source record should establish study identity, design, sample size, effect scale and uncertainty. Unsupported extracted numbers would contaminate the analysis before any estimator is fitted.

### Respect the geometry of the data

A composition such as shares [0.1,0.2,0.7] has a fixed sum. Increasing one component necessarily changes others, so raw covariance can reflect closure rather than a meaningful independent relationship. Log ratios represent relative information, but zeros require a measurement-aware policy rather than arbitrary tiny-value replacement. Angles have another geometry: 359 and 1 degrees are close, and their ordinary arithmetic mean 180 is misleading. A circular mean uses unit-vector directions.

Functional observations, tensors and graphs likewise require representations that preserve their structure. More elaborate mathematics is justified when it addresses that structure and improves the target analysis, not because it produces sophisticated terminology. Diagnostics should test whether the representation and regularization actually support the scientific interpretation.

### Measurement and inference are distinct layers

A psychometric score estimates a latent attribute from observed responses under a model. Item difficulty, discrimination and group invariance determine whether scores can be compared meaningfully. A high reliability coefficient is not proof that the scale measures the intended construct. Similarly, a sparse precision matrix identifies conditional associations under a Gaussian graphical model, not automatically causal edges.

### Privacy is a property of a release mechanism

Disclosure control and differential privacy concern what a released output can reveal about people. Differential privacy specifies neighboring datasets and bounds how much the output distribution can change between them. The guarantee depends on the privacy unit, sensitivity, randomization and composition across releases. Adding arbitrary noise or removing names does not automatically provide that guarantee. The demonstration below checks one Laplace likelihood-ratio identity on synthetic counts; it is not a production privacy implementation or approval to release sensitive data.

## Methods, mechanisms, and limits

### stat-39-01

**Systematic reviews**

A systematic review uses a prespecified search, screening and extraction procedure to assemble evidence for a defined question. Eligibility rules and duplicate publications affect which studies enter the synthesis. Document excluded studies and risk-of-bias judgments. Automation can assist retrieval or extraction, but source verification and a reproducible protocol remain necessary; a fluent narrative review cannot substitute for systematic evidence selection.

### stat-39-02

**Meta-analysis**

Meta-analysis statistically combines study-level or individual-level evidence while respecting effect scales, uncertainty and dependence. Multiple outcomes or estimates from one study are not independent replications. Harmonize the estimand and extraction before selecting a model. A pooled estimate can be precise while misleading if studies share bias, differ in incompatible ways or omit unpublished unfavorable findings.

### stat-39-03

**Fixed-effect meta-analysis**

A fixed-effect or common-effect meta-analysis assumes eligible studies estimate one shared underlying effect, with differences arising from sampling error. Inverse-variance weighting gives more influence to precise studies. The assumption is about the effect, not the absence of study-level covariates. If meaningful heterogeneity exists, a narrow common-effect interval can answer an overly restrictive question rather than the desired population question.

### stat-39-04

**Random-effects meta-analysis**

A random-effects meta-analysis models study-specific effects as varying around a mean with between-study variance. Adding tau_squared to sampling variance typically reduces the dominance of the largest studies. Estimating heterogeneity is uncertain when few studies exist. A confidence interval for the mean effect differs from a prediction interval for a future study effect, and neither eliminates study bias.

### stat-39-05

**Meta-regression**

Meta-regression relates study effect estimates to study characteristics while accounting for their sampling uncertainty and residual heterogeneity. Study-level associations can differ from individual-level relationships, creating ecological interpretation risks. With few studies, many moderators invite overfitting and selective findings. Prespecify plausible moderators and distinguish exploratory explanation from a causal effect of changing a study characteristic.

### stat-39-06

**Network meta-analysis**

Network meta-analysis combines direct and indirect comparisons among multiple interventions. Its validity depends on transitivity and consistency assumptions linking the study populations and comparisons. A treatment ranking can appear precise despite sparse or inconsistent evidence. Examine the network structure, effect modifiers and disagreement between direct and indirect evidence before using a ranked list for a decision.

### stat-39-07

**Publication bias assessment**

Publication-bias assessment asks whether available studies differ systematically from missing studies, often using funnel plots, selection models or sensitivity analyses. Funnel asymmetry can also reflect heterogeneity or small-study differences, so it is not a unique diagnostic of publication bias. With few studies the tests are weak. Report how conclusions change under plausible missing-evidence mechanisms rather than declaring the problem solved.

### stat-39-08

**Evidence grading**

Evidence grading evaluates confidence in a body of evidence using design quality, bias, consistency, directness, precision and reporting concerns under a defined framework. It is not equivalent to a p-value or a pooled sample size. A large set of similarly biased studies can remain weak evidence. Explain which limitation changes the decision and what new evidence would most reduce uncertainty.

### stat-39-09

**Reproducibility**

Reproducibility asks whether the same data and computational procedure yield the same results. It requires accessible inputs or appropriate controlled access, code, environment and configuration. A fixed random seed alone is insufficient when data or dependencies change. Reproducibility supports inspection but does not establish validity: a consistently reproduced leakage error remains an error.

### stat-39-10

**Replicability**

Replicability asks whether new data support comparable findings under a relevant design. Differences in population, measurement and implementation can make exact numeric agreement inappropriate. Define the effect or prediction claim to be replicated and a meaningful tolerance or decision criterion. A failed replication should prompt analysis of uncertainty and context rather than automatic attribution to fraud or an invalid original result.

### stat-39-11

**Structural equation modeling**

Structural equation modeling represents a system of observed and latent relationships through equations and covariance restrictions. Identification depends on constraints and sufficient information; a model can fit covariance well without being uniquely determined or causally correct. Equivalent models may imply different directional stories. Assess measurement and structural components separately and justify causal arrows through design and substantive assumptions.

### stat-39-12

**Path analysis**

Path analysis is a structural-equation approach among observed variables, often decomposing direct and indirect associations. The proposed direction of arrows is not identified merely because a regression can be fitted. Omitted variables and measurement error can alter path coefficients. A product of coefficients has a causal mediation interpretation only under additional assumptions about confounding and intervention definitions.

### stat-39-13

**Item response theory**

Item response theory models response probability through latent ability or trait and item parameters such as difficulty and discrimination. It separates the measurement model from a raw total score. Local independence and parameter invariance are important assumptions. Differential item functioning can make group score comparisons misleading, and a fitted latent scale needs substantive validation of what it measures.

### stat-39-14

**Rasch models**

The Rasch model is a constrained item-response model in which a binary response probability depends on person ability minus item difficulty through a logistic link. Equal discrimination is a strong restriction that supports useful measurement properties when appropriate. Model fit and item functioning should be checked rather than assumed from the scale name. Poorly fitting items can undermine comparisons.

### stat-39-15

**Generalizability theory**

Generalizability theory decomposes measurement variation across facets such as persons, items, raters and occasions. A generalizability study estimates variance components, while a decision study examines designs with different numbers of observations or raters. The relevant error component depends on whether decisions are relative rankings or absolute levels. More repeated measurement helps only the error sources the design actually samples.

### stat-39-16

**Psychometrics**

Psychometrics studies the validity, reliability and interpretation of measurements of latent attributes. Reliability concerns consistency under specified conditions; validity concerns whether evidence supports the intended interpretation and use. High internal consistency can reflect redundant items rather than broad construct coverage. Evaluate response processes, group invariance and external relationships instead of reducing measurement quality to one coefficient.

### stat-39-17

**Compositional data analysis**

Compositional data analysis treats vectors of positive relative parts whose total is arbitrary or constrained. Ratios carry the meaningful information, and multiplying all parts by a common scale should not change interpretation. Raw correlations can be induced by closure. The sampling and zero-generation mechanisms matter, especially when values are rounded, below detection limits or structurally absent.

### stat-39-18

**Log-ratio transformations**

Log-ratio transformations express compositions using logarithms of component ratios, with additive, centered or isometric variants. Choice of denominator or coordinate basis affects interpretation and numerical geometry, while relative information is preserved appropriately. Zeros make logs undefined and require a justified model or replacement strategy. Do not insert an arbitrary small constant without checking how it changes conclusions.

### stat-39-19

**Functional data analysis**

Functional data analysis treats entire curves as observational units, often representing them through smooth basis functions or functional principal components. Dense sampling within one curve does not create many independent subjects. Alignment, smoothing and measurement noise affect inferred modes of variation. Hold out whole subjects or trajectories during validation and distinguish amplitude variation from timing variation.

### stat-39-20

**Circular statistics**

Circular statistics analyzes periodic directions using geometry on the circle. The circular mean is the angle of the average unit vector, and resultant length measures concentration. Opposing directions can cancel, making the mean poorly defined. Specify degrees or radians and the wrap interval. Ordinary linear averages and distances can be wrong near the boundary even when arithmetic is correct.

### stat-39-21

**Directional statistics**

Directional statistics extends circular ideas to directions on spheres or other directional spaces. A vector's orientation, not arbitrary coordinate representation, is the object of interest. Axial data, where opposite directions are equivalent, require different models from oriented vectors. Coordinate-system choices, concentration and multimodality affect summaries, so avoid forcing every directional distribution into one mean direction.

### stat-39-22

**Symbolic and interval-valued data analysis**

Symbolic and interval-valued data analysis models observations represented by ranges, sets or structured summaries. An interval can express within-unit variability, uncertainty or censoring, and these meanings are not interchangeable. Replacing each interval by its midpoint discards width and can bias downstream relationships. Specify how the summary was generated before choosing a likelihood or distance between observations.

### stat-39-23

**High-dimensional inference**

High-dimensional inference addresses settings where the number of candidate variables is large relative to observations. Regularization helps estimation but changes bias and invalidates naive post-selection p-values. Sparsity, design conditions and target definition determine what inference is possible. Distinguish prediction accuracy from valid coefficient or variable-selection claims, and account for the complete selection procedure.

### stat-39-24

**Sparse precision-matrix estimation**

A precision matrix is the inverse covariance matrix. Under a multivariate Gaussian model, zero off-diagonal precision entries correspond to conditional independence given the other variables. Estimating it in high dimensions requires structure or regularization. Outside the Gaussian setting, zeros need not imply the same independence statement, and conditional association is not automatically a causal graph.

### stat-39-25

**Graphical lasso**

Graphical lasso estimates a sparse precision matrix by penalizing off-diagonal entries in a Gaussian likelihood. The penalty controls sparsity and estimation bias; feature scaling and sample size matter. Cross-validation for predictive likelihood may choose a graph different from one suited to scientific edge discovery. Assess stability and uncertainty before interpreting each nonzero edge as a robust relationship.

### stat-39-26

**Tensor decomposition**

Tensor decomposition factors multidimensional arrays into lower-dimensional components, using constructions such as CP or Tucker models. Different forms impose different rank and interaction structures. Identifiability, scaling and permutation ambiguities affect component interpretation. Missing entries and noisy dimensions require appropriate objectives. A compact reconstruction can be useful without its components representing unique physical factors.

### stat-39-27

**Topological data analysis**

Topological data analysis studies connectivity, loops and other shape properties across representations or scales. It can reveal structure missed by linear summaries, but results depend on distance, sampling density and preprocessing. A visually interesting topological feature is not automatically a statistically reliable signal. Compare with suitable null models or perturbations and connect the feature to a concrete analytical question.

### stat-39-28

**Persistent homology**

Persistent homology tracks when topological features appear and disappear as a scale parameter changes. Long persistence can indicate structure robust to small perturbations under appropriate conditions, but persistence alone is not a universal significance test. Distance geometry, noise and finite sampling affect diagrams. Downstream summaries should preserve the uncertainty and invariance assumptions relevant to the application.

### stat-39-29

**Statistical disclosure control**

Statistical disclosure control reduces re-identification or attribute-disclosure risk in released data or statistics through methods such as suppression, aggregation and perturbation. Removing direct identifiers is rarely sufficient when records can be linked through other attributes. Risk depends on the release context and external information. Evaluate utility and residual disclosure risk under an explicit threat model rather than using a generic anonymized label.

### stat-39-30

**Differential privacy**

Differential privacy bounds how much a randomized output distribution can change between neighboring datasets, with parameters epsilon and possibly delta. The privacy unit and adjacency definition determine whose contribution is protected. Noise calibration uses sensitivity, and multiple releases consume a combined privacy budget. A single noisy count example illustrates one mechanism; production guarantees additionally require correct implementation, accounting, access boundaries and review.

## Worked Python demonstrations

Complete offline program: [chapter_39.py](../examples/chapter_39.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_39.py
```

### See how heterogeneity changes relative study weights

Effects 0.2 and 0.5 with standard errors 0.1 and 0.2 receive common-effect weights 100 and 25, giving mean 0.26 and standard error \(\sqrt{\frac{1}{125}}\). Adding an illustrative between-study variance 0.04 produces weights 20 and 12.5, moving the mean toward the second study. The fixed tau-squared is a teaching input, not an estimated heterogeneity result.

### Preserve relative and circular geometry

Multiplying [1,2,7] by ten leaves its composition and log ratio \(\log(\frac{1}{2})\) unchanged. Angles 359 and 1 degrees have arithmetic mean 180 but a circular mean near zero. These checks show why the correct representation changes the result even before any sophisticated model is fitted.

### Inspect one privacy-mechanism identity

For a count with add/remove-one sensitivity one and epsilon one, Laplace scale is one. At output seven, the density ratio for adjacent true counts six and five is \(\exp(1)\), matching the theoretical bound in this case. This is synthetic algebra, not a complete privacy implementation; composition, random-number generation and data access remain outside the demonstration.

### Complete executable example

```python
import numpy as np


def meta_weights():
    effect = np.array([0.2, 0.5])
    variance = np.array([0.1, 0.2]) ** 2
    weight = 1 / variance
    common = np.sum(weight * effect) / weight.sum()
    se = np.sqrt(1 / weight.sum())
    random_weight = 1 / (variance + 0.04)
    random_mean = np.sum(random_weight * effect) / random_weight.sum()
    assert np.isclose(common, 0.26) and np.isclose(se, np.sqrt(1 / 125))
    assert random_mean > common and random_weight[0] / random_weight[1] < weight[0] / weight[1]
    print(
        "Common-effect mean and SE:", common, se, "illustrative tau-squared=.04 mean:", random_mean
    )


def relative_and_circular():
    composition = np.array([1.0, 2.0, 7.0])
    scaled = 10 * composition
    assert np.allclose(composition / composition.sum(), scaled / scaled.sum())
    ratio = np.log(composition[0] / composition[1])
    assert np.isclose(ratio, np.log(scaled[0] / scaled[1]))
    radians = np.deg2rad([359.0, 1.0])
    circular = np.rad2deg(np.angle(np.mean(np.exp(1j * radians))))
    assert abs(circular) < 1e-10 and np.mean([359.0, 1.0]) == 180.0
    print("Invariant log ratio:", ratio, "circular mean near zero:", circular)


def laplace_ratio():
    epsilon = 1.0
    sensitivity = 1.0
    scale = sensitivity / epsilon

    def density(output, count):
        return np.exp(-abs(output - count) / scale) / (2 * scale)

    ratio = density(7.0, 6.0) / density(7.0, 5.0)
    assert np.isclose(ratio, np.exp(epsilon))
    assert sensitivity / 0.5 > sensitivity / 2.0
    print("Adjacent-count density ratio:", ratio, "bound:", np.exp(epsilon))


def main():
    meta_weights()
    relative_and_circular()
    laplace_ratio()


if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Does random-effects meta-analysis solve study heterogeneity?** It models a distribution of effects under assumptions and changes the target to its mean. It does not explain all heterogeneity, repair biased studies or make incompatible outcomes comparable. Prediction intervals and sensitivity analyses may be more relevant than one pooled mean.

**Interview: Why can a composition create misleading correlations?** The fixed total couples components: increasing one share forces others down even without an independent substantive relationship. Ratios and an appropriate compositional geometry better represent relative information, with a separate policy for zeros.

**Interview: Is adding noise enough to claim differential privacy?** No. The mechanism needs a defined privacy unit and neighboring-dataset relation, bounded sensitivity, calibrated randomization and accounting across releases. A numerical example or an anonymized label cannot establish those end-to-end guarantees.

## Primary sources and official APIs

- [Cochrane Handbook: meta-analysis methods](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-10)

- [SciPy circular mean definition](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.circmean.html)

- [Dwork and Roth, The Algorithmic Foundations of Differential Privacy](https://www.nowpublishers.com/articles/foundations-and-trends-in-theoretical-computer-science/TCS-042)

- [NIST guidelines for evaluating differential privacy guarantees](https://csrc.nist.gov/pubs/sp/800/226/final)

## Connected worked tutorial

[A complete research synthesis calculation](../tutorials/science/06-research-synthesis.md). Harmonize effect scales, estimate heterogeneity, distinguish mean and prediction intervals, and inspect leave-one-out sensitivity.

## Reading connections

[Previous chapter](38-product-customer-marketing-and-business-analytics.md) | [Book contents](../README.md) | [Next chapter](40-production-methodology-governance-and-senior-scientific-judgment.md)
