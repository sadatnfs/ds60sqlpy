# 23. Uncertainty Quantification and Distribution Shift

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-023`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

A point prediction hides at least two uncertainties: variability in future outcomes even if the model were known, and uncertainty about the model itself. Which component can be reduced depends on the intervention. More training data can reduce some parameter uncertainty; improved sensors may reduce apparent outcome noise. The decomposition is conditional on what information the model observes.

### Split conformal prediction by ranks

Fit a prediction model on training data. On n fresh calibration observations, compute nonconformity scores, such as absolute residuals \(s_i=|y_i-f(x_i)|\). For desired miscoverage alpha, take \(k=\left\lceil(n+1)(1-\alpha)\right\rceil\) and the kth smallest calibration score q. If k exceeds n, use an unbounded interval rather than quietly substituting the largest observed score. Predict \([f(x)-q,f(x)+q]\). Under exchangeability of calibration and new observations, conditional on the training fit, the new score's rank among n+1 scores provides finite-sample marginal coverage of at least 1-alpha, with suitable handling of ties.

This is marginal coverage across new observations, not a promise of 90% coverage at every exact x or within every subgroup. A model can meet overall coverage while systematically under-covering a rare region. Conformalized quantile regression uses scores max(lower(x)-y,y-upper(x)) to adapt interval width to heteroskedasticity, then applies an analogous rank correction. Better base models can improve efficiency, while the calibration argument supplies coverage under its assumptions.

### Shift changes the guarantee

Covariate shift changes p(x) while preserving p(y|x); importance weights p_target(x)/p_source(x) can adjust target expectations when support overlaps. Label shift changes class priors while preserving p(x|y), enabling a different correction. Concept drift changes the outcome mechanism itself. These assumptions are distinct and cannot be established by one generic drift score. Once calibration exchangeability fails, an old conformal guarantee no longer automatically applies.

Selective prediction trades coverage of cases against error among accepted cases. Abstaining on uncertain inputs can be valuable, but the human or fallback path has its own accuracy, cost and fairness constraints. Evaluate the entire decision system.

## Methods, mechanisms, and limits

### stat-23-01

**Aleatoric uncertainty**

Aleatoric uncertainty is residual outcome variation conditional on the modeled information. It is not always permanently irreducible: richer measurements may explain part of it. Specify the conditioning information when using the term.

### stat-23-02

**Epistemic uncertainty**

Epistemic uncertainty reflects unknown parameters, functions or model structure. It can shrink with informative data but remain large outside support. Agreement among misspecified models can create false confidence.

### stat-23-03

**Uncertainty propagation**

Propagate joint input and parameter uncertainty through a calculation using derivatives or simulation. Preserve dependence among uncertain inputs. Plugging independent marginal draws into a dependent system can misstate tail risk.

### stat-23-04

**Predictive distributions**

Represent possible outcomes with probabilities, densities or samples. Evaluate both calibration and sharpness using proper scores and relevant diagnostics. A narrow distribution is useful only when it assigns plausible mass to actual outcomes.

### stat-23-05

**Quantile prediction**

Estimate conditional quantiles through pinball loss or distributional models. Quantiles can describe asymmetric risk and heterogeneous spread. Separately fitted quantiles may cross and do not automatically supply joint coverage guarantees.

### stat-23-06

**Prediction set construction**

Return a set whose inclusion rule targets a coverage criterion. Set size measures informativeness but must be considered alongside coverage. Trivially returning every outcome covers perfectly while supporting few decisions.

### stat-23-07

**Conformal prediction**

Calibrate scores using exchangeability or another explicitly justified validity framework. The classical guarantee is finite-sample marginal coverage, not universal conditional coverage or immunity to distribution change.

### stat-23-08

**Split conformal prediction**

Separate model fitting from calibration and use the finite-sample corrected order statistic. Reusing calibration data to tune many model choices can invalidate the simple argument. Very small calibration sets limit attainable finite intervals.

### stat-23-09

**Conformalized quantile regression**

Start with lower and upper quantile predictions and calibrate their worst signed boundary error. This can adapt width to local noise while preserving a marginal conformal guarantee under the relevant assumptions.

### stat-23-10

**Conditional versus marginal coverage**

Marginal coverage averages over the target population, while conditional coverage holds within specified conditions or at each covariate value. The latter is harder and cannot generally be obtained distribution-free with informative intervals everywhere.

### stat-23-11

**Distribution-free inference**

Distribution-free means no specified parametric distribution within the stated class. It still requires assumptions such as exchangeability, boundedness or design validity. The phrase is not shorthand for assumption-free inference.

### stat-23-12

**Deep ensembles**

Train multiple neural models and examine their predictive mixture or disagreement. Diversity depends on seeds, data and architecture. Ensembles can all fail similarly under shared misspecification or novel inputs.

### stat-23-13

**Bayesian neural networks**

Place distributions over weights or related components and integrate predictions. Computational approximations and priors affect uncertainty. Bayesian terminology alone does not establish empirical calibration or protection against shift.

### stat-23-14

**Selective prediction**

Accept only predictions satisfying an uncertainty or utility criterion and route others elsewhere. Report accepted-case error and acceptance rate together. Abstention can concentrate difficult cases in an overloaded fallback system.

### stat-23-15

**Covariate shift**

Assume predictor distribution changes while the conditional outcome law remains stable. Importance weighting can then target a new population with overlap. If p(y|x) changes too, this correction is insufficient.

### stat-23-16

**Label shift**

Assume class prevalence changes but class-conditional feature distributions remain stable. Adjust class-prior odds or estimate new priors under identifiability conditions. Misclassification and feature shift can complicate prior estimation.

### stat-23-17

**Concept drift**

The relation between inputs and outcomes changes, potentially through policy, behavior or measurement. Input histograms can stay stable while performance deteriorates. Mature labels or independent mechanisms are needed to detect some drift.

### stat-23-18

**Importance weighting**

Reweight source observations by target-to-source density ratios. Large weights increase variance and reveal poor support. Clipping improves stability at the cost of bias and a changed approximation.

### stat-23-19

**Distributionally robust prediction**

Optimize against a specified set of plausible distributions. The uncertainty set determines what protection exists and how conservative the result becomes. Robustness against that set is not robustness to every possible shift.

### stat-23-20

**Out-of-distribution detection**

Score novelty relative to development data or learned representations. A detector can miss harmful semantic shifts and flag benign changes. Evaluate false alarms, missed shifts and downstream performance consequences separately.

<!-- detailed-case-studies:start -->

## Extended case studies and scientific reasoning

### Case study: derive the rank guarantee without a parametric error model

Condition on a predictor trained independently of calibration data. Suppose the n calibration scores and one future score are exchangeable. Ignoring ties for the moment, each of the n+1 ranks is equally likely for the future score. Choosing the kth calibration order statistic as a threshold accepts at least k of those n+1 rank positions. Setting \(k=\left\lceil(n+1)(1-\alpha)\right\rceil\) therefore gives coverage at least 1-alpha.

With \(n=19\) and \(\alpha=0.1\), \(k=18\). Using an ordinary interpolated .9 sample quantile without the finite-sample correction can choose a different threshold. If alpha is so small that \(k=n+1\), there is no finite calibration order statistic supporting that requested bound in the simple construction. Returning infinity is honest; silently using the maximum calibration residual weakens the stated guarantee.

Ties can make coverage conservative with the usual nonrandomized threshold. Randomized tie-breaking can produce more exact rank behavior under suitable construction, but the implementation and interpretation must be explicit. The core result concerns marginal prediction coverage, not the accuracy of the point model or the conditional coverage of every subgroup.

### Case study: overall coverage hides a difficult subgroup

Suppose 90% of observations belong to an easy group with nearly deterministic outcomes and 10% to a noisy group. A constant-width interval calibrated to 90% marginal coverage can cover almost every easy case while failing most noisy cases. The aggregate target may be met even though the system is least reliable for the group where uncertainty matters most.

A quantile model can adapt interval width to predictors of noise, and conformalized quantile regression calibrates its remaining boundary errors. Group-specific calibration can target coverage within prespecified groups if each has enough calibration data. Both approaches introduce design choices and finite-sample limits. Tiny intersections may require wide intervals, pooling assumptions or an explicit abstention policy.

Measure interval width as well as coverage. An interval spanning every possible operational outcome is calibrated but not useful. Evaluate proper scores or quantile losses, coverage by meaningful group, and the downstream action. Avoid choosing the narrowest of many interval methods on the same calibration labels and then claiming the original split-conformal guarantee without accounting for that selection.

### Case study: distinguish three shifts before reweighting

A model predicts incident severity from diagnostic features. A new product mix changes feature frequencies while severity conditional on features remains unchanged: this is covariate shift. If all target feature regions are represented in training, target-to-source density ratios can reweight evaluation or learning. Extremely large ratios reveal that target performance depends on a small number of source examples.

Alternatively, severity prevalence changes while each severity class retains the same feature distribution: this is label shift. Prior-odds correction follows a different model and can change calibrated probabilities without changing some class-conditional patterns. If a new software architecture changes how the same diagnostic features map to severity, the conditional mechanism itself has changed: concept drift. Neither simple covariate weights nor prior-odds correction is sufficient in general.

Observed data rarely prove one shift model perfectly. Use domain changes, label feedback and diagnostics to assess plausibility. A classifier that distinguishes source from target shows distributional difference in the observed inputs, not which correction is valid. A model can also suffer concept drift with unchanged input distributions, so input monitoring alone misses some failures.

### Case study: uncertainty must reach the final decision

A demand model outputs a predictive distribution, then a staffing optimizer treats its mean as certain. The uncertainty has disappeared at the interface between components. If understaffing is costly, optimize against the predictive distribution, quantiles or explicitly defined scenarios rather than only the average. Preserve correlation across locations when shared shocks affect all of them.

Monte Carlo propagation can sample model parameters and future outcomes jointly, then compute the decision outcome for each draw. Distinguish posterior or parameter uncertainty from process variability, and preserve shared latent effects. Sampling each location independently can drastically understate the probability of simultaneous overload.

An abstention policy similarly needs a complete fallback model. If difficult cases are routed to people, evaluate reviewer capacity, error, delay and consistency. A model with excellent accepted-case accuracy may produce a worse system if it sends an unmanageable fraction to review. Report coverage, conditional risk and end-to-end utility together.

<!-- detailed-case-studies:end -->

## Worked Python demonstrations

Complete offline program: [chapter_23.py](../examples/chapter_23.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_23.py
```

### The finite-sample correction matters

Nineteen calibration residuals and alpha .1 require the eighteenth ordered residual. Twenty illustrative equally likely new-score ranks give coverage .9. The program checks the rank arithmetic, not real-world calibration. A real guarantee needs the exchangeability argument and a predictor fitted without calibration leakage.

### Reweight the target, not the narrative

Two strata have unchanged conditional outcomes one and nine, but their shares reverse from \(\frac{0.8}{0.2}\) to \(\frac{0.2}{0.8}\). The mean changes from 2.6 to 7.4. Density ratios .25 and four recover the target mean exactly. If the conditional outcomes also changed, these weights alone would not suffice.

### Zero accepted error can hide low coverage

Accepting only the two high-confidence cases produces zero errors on accepted cases but processes only half the population. The other two cases still need a decision. Four observations are a mechanism illustration, not evidence that the policy is reliably error-free.

### Complete executable example

```python
import numpy as np

def conformal_rank():
    scores=np.arange(1.,20.)
    alpha=.1;n=len(scores);k=int(np.ceil((n+1)*(1-alpha)))
    q=np.sort(scores)[k-1] if k<=n else np.inf
    assert k==18 and q==18
    possible_new_scores=np.arange(.5,20.,1.)
    rank_coverage=np.mean(possible_new_scores<=q)
    assert rank_coverage==.9
    print("Calibration n/k/q:",n,k,q,"coverage over illustrative equally likely ranks:",rank_coverage)

def shift_weighting():
    source=np.array([.8,.2]);target=np.array([.2,.8]);outcome=np.array([1.,9.])
    weights=target/source
    target_mean=np.sum(source*weights*outcome)
    assert np.isclose(target_mean,target@outcome) and np.isclose(target_mean,7.4)
    assert np.isclose(source@outcome,2.6)
    print("Source mean:",source@outcome,"target reweighted mean:",target_mean,"ratios:",weights)

def selective_prediction():
    confidence=np.array([.55,.6,.8,.95]);error=np.array([1.,1.,0.,0.])
    accepted=confidence>=.8
    coverage=accepted.mean();risk=error[accepted].mean()
    assert coverage==.5 and risk==0 and error.mean()==.5
    print("Accepted fraction:",coverage,"accepted empirical error:",risk,"all-case error:",error.mean())

def main():
    conformal_rank();shift_weighting();selective_prediction()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Does 90% conformal coverage mean every subgroup gets 90%?** No. Standard split conformal provides marginal coverage under exchangeability. Rare subgroups can have poor coverage. Group-conditional methods need sufficient calibration data and a clearly specified grouping scheme.

**Interview: Can an ensemble be confidently wrong?** Yes. Shared training data, architecture or objective can produce similar predictions under shared misspecification. Disagreement is one signal, not a complete measure of uncertainty.

**Interview: Which shift can importance weighting fix?** For ordinary covariate-shift correction, the conditional outcome mechanism must stay stable and target support must be covered by the source. Different forms of shift require different assumptions and methods.

## Primary sources and official APIs

- [Angelopoulos and Bates, conformal prediction tutorial](https://arxiv.org/abs/2107.07511).

- [Romano et al., Conformalized Quantile Regression](https://arxiv.org/abs/1905.03222).

## Reading connections

[Previous chapter](22-model-validation-and-predictive-performance.md) | [Book contents](../README.md) | [Next chapter](24-explainability-fairness-and-model-robustness.md)
