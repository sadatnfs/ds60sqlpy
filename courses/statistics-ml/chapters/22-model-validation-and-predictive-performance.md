# 22. Model Validation and Predictive Performance

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-022`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Validation estimates how a complete learning procedure will behave under a specified future use. The split must mimic that use: new customers, future dates, new hospitals or new geographic regions. A random row split answers a different question if related observations appear on both sides. Preprocessing, feature selection, tuning and threshold selection all belong inside the development boundary.

### Separate ranking, probability and action quality

ROC AUC measures the probability that a randomly chosen positive receives a higher score than a randomly chosen negative, with a convention for ties. It does not measure calibration. Log loss and Brier score evaluate probabilities, while threshold metrics evaluate a particular action rule. Precision depends on prevalence: if sensitivity and false-positive rate stay fixed but positives become rarer, positive predictions become less reliable.

For false-positive cost C_FP and false-negative cost C_FN, a calibrated probability p leads to action when \(C_{\mathrm{FP}}\cdot (1-p)<C_{\mathrm{FN}}\cdot p\), or \(p>\frac{C_{\mathrm{FP}}}{C_{\mathrm{FP}}+C_{\mathrm{FN}}}\). Capacity constraints can instead create a top-k policy. Tune that policy on development data, freeze it, then assess final utility and harms on held-out evidence.

### Estimate uncertainty about a comparison

Compare models on the same held-out units and analyze paired loss differences. Resample the independent unit, preserving groups or time blocks as needed. Reusing the final test after every model choice converts it into another validation set. Nested cross-validation separates inner tuning from outer performance estimation; it evaluates the selection procedure, not merely one frozen hyperparameter value.

A metric should be paired with a baseline, subgroup analysis and an operational denominator. A small average gain can conceal worse rare-event recall or a harmful tail. Document what remains unmeasured, including label delay and distribution shift.

## Methods, mechanisms, and limits

### stat-22-01

**Training, validation, and test separation**

Use training for fitting, validation for choices and a final test for an independent assessment. Repeatedly consulting the test contaminates this separation. The split must occur before learned preprocessing or feature selection.

### stat-22-02

**K-fold cross-validation**

Partition independent observations into K folds and average held-out performance. Each row serves in validation once. Fold scores are dependent because training sets overlap, so naive standard errors across folds can be misleading.

### stat-22-03

**Stratified cross-validation**

Maintain class proportions in folds to stabilize evaluation for rare classes. Stratification does not prevent duplicate, group or temporal leakage. Ensure each fold has enough positives for the chosen metric.

### stat-22-04

**Grouped cross-validation**

Keep all records from one person, site or other dependent entity together. The group definition must match deployment generalization. Holding out customers differs from predicting later behavior for already-seen customers.

### stat-22-05

**Nested cross-validation**

Use inner folds to tune and outer folds to estimate the full selection procedure's performance. Report what is refit on all development data afterward. Outer folds should still respect groups or time.

### stat-22-06

**Temporal validation**

Train on earlier observations and evaluate on later information. Use feature availability timestamps and gaps where necessary. Random shuffling can expose future regimes and produce overly optimistic estimates.

### stat-22-07

**Rolling-origin evaluation**

Advance the forecasting cutoff and repeatedly predict future horizons. Match refitting cadence and horizon to deployment. Aggregate losses while accounting for overlapping targets and serial dependence.

### stat-22-08

**Spatial cross-validation**

Hold out spatial regions or buffered locations to test geographic transfer. Nearby observations can leak through spatial dependence. The block size changes the distance and difficulty of the generalization question.

### stat-22-09

**External validation**

Evaluate on independently collected data with clear population and acquisition differences. External validation is stronger evidence for transport only to settings it meaningfully represents. Inspect calibration and subgroup support anew.

### stat-22-10

**Out-of-distribution evaluation**

Stress evaluation on populations or mechanisms outside development support. Label what shifts and why it is plausible. One arbitrary perturbation suite cannot certify robustness to every future change.

### stat-22-11

**Learning curves**

Plot training and validation performance against sample size. A persistent gap can suggest variance or leakage issues; a shared plateau can reflect limited features or irreducible noise. Extrapolated learning curves are uncertain.

### stat-22-12

**Validation curves**

Plot held-out performance across a hyperparameter range using a fixed development protocol. The best observed point is selected with noise. Do not present its validation score as an untouched final estimate.

### stat-22-13

**Ablation studies**

Remove or replace components while preserving an otherwise fair training/evaluation procedure. Interactions can make individual ablations misleading. Compare equivalent tuning budgets and report which question each ablation isolates.

### stat-22-14

**Baseline comparisons**

Compare with trivial, historical and simple statistical baselines under identical splits and metrics. A complex model's absolute score is hard to interpret without the decision-relevant alternative.

### stat-22-15

**Mean absolute error**

MAE averages absolute residuals and is minimized by a conditional median. It remains sensitive to large errors linearly, while treating equal-magnitude errors symmetrically. Use asymmetric loss when consequences differ by direction.

### stat-22-16

**Mean squared error and RMSE**

MSE averages squared residuals and is minimized by the conditional mean; RMSE returns to outcome units. Squaring emphasizes large errors. A few tail failures can dominate, which may be desirable or misleading depending on cost.

### stat-22-17

**R-squared**

R-squared compares squared error with a specified mean baseline. It can be negative on held-out data. Different target distributions or baseline definitions make cross-dataset R-squared values difficult to compare.

### stat-22-18

**Log loss**

Negative log probability assigned to observed classes rewards honest probabilities under the target distribution. Confident mistakes are heavily penalized. Numerical clipping prevents infinity but changes extreme penalties.

### stat-22-19

**Brier score**

Average squared differences between probabilities and binary outcomes. The Brier score evaluates calibration and discrimination jointly. Compare with a prevalence baseline and inspect reliability rather than calling it purely a calibration score.

### stat-22-20

**Precision and recall**

Precision is \(\frac{\mathrm{TP}}{\mathrm{TP}+\mathrm{FP}}\); recall is \(\frac{\mathrm{TP}}{\mathrm{TP}+\mathrm{FN}}\). Precision depends on prevalence and both depend on threshold. Undefined denominators need an explicit reporting policy rather than silently favorable defaults.

### stat-22-21

**Specificity and sensitivity**

Sensitivity is recall among positives; specificity is \(\frac{\mathrm{TN}}{\mathrm{TN}+\mathrm{FP}}\) among negatives. These condition on true class, unlike precision. Their usefulness still depends on representative labels and subgroup behavior.

### stat-22-22

**F-scores**

F-beta combines precision and recall with beta emphasizing recall when greater than one. It ignores true negatives and does not generally encode explicit economic costs. Choose it for a justified retrieval objective.

### stat-22-23

**ROC curves and AUC**

ROC curves vary sensitivity against false-positive rate over thresholds; AUC summarizes ranking. At rare prevalence, apparently small false-positive rates can still create many false alerts. Inspect operational thresholds separately.

### stat-22-24

**Precision–recall curves**

PR curves show precision against recall as the threshold changes. They reflect prevalence and emphasize positive retrieval. Different interpolation or average-precision conventions can yield different summary numbers.

### stat-22-25

**Calibration curves**

Group predictions into probability ranges or use smooth reliability estimates and compare observed frequencies. Small bins are noisy. A calibration curve alone does not assess discrimination or utility.

### stat-22-26

**Threshold optimization**

Select a cutoff using costs, constraints or a prespecified metric on development data. Recalibration or prevalence shifts can change the appropriate cutoff. Final test labels must not choose it.

### stat-22-27

**Top-k and ranking metrics**

Evaluate early-ranked items using precision@k, recall@k, reciprocal rank or discounted gain as appropriate. Define candidate sets and query averaging. A top-k gain can coexist with poor full-list performance.

### stat-22-28

**Business utility evaluation**

Translate outcomes into benefits, costs and resource use at the relevant unit. Include action effects when the model changes behavior. Predictive accuracy alone cannot establish incremental business value.

### stat-22-29

**Paired model comparisons**

Compute per-unit loss differences for models tested on the same observations. This preserves pairing and often reduces variance. Correlated units and model-selection reuse must still be reflected in uncertainty.

### stat-22-30

**Performance uncertainty**

Quantify sample variability through appropriate intervals or resampling, plus scenario variability for changed settings. A narrow test-sample interval does not cover unknown future distribution shifts or label-definition errors.

<!-- detailed-case-studies:start -->

## Extended case studies and scientific reasoning

### Case study: rare events expose the limits of accuracy and ROC

A detector operates on 100,000 requests with 1% true incidents. At sensitivity .9 it catches 900 of 1,000 incidents. At false-positive rate .01 it also flags 990 of 99,000 nonincidents. Precision is \(\frac{900}{900+990}\), about .476. The false-positive rate sounds small, yet more than half the alerts are false because the negative population is large.

If prevalence falls to .1% while sensitivity and false-positive rate remain unchanged, the system catches 90 of 100 incidents and generates 999 false alerts. Precision falls to about .083. Ranking and class-conditional rates may be unchanged, but the operational workload and meaning of an alert change substantially. Calibration and threshold policy should be reassessed for the new prevalence rather than inferred from the original ROC curve.

A precision-recall curve highlights positive retrieval, but its baseline and interpretation also depend on prevalence. Compare models on the same representative evaluation population. If an enriched case-control test set is used for efficient labeling, retain sampling probabilities and avoid presenting its raw precision as production precision. Explicitly reconstruct the deployment denominator when justified.

### Case study: nested validation measures the procedure

Suppose ten model settings are evaluated on one validation set and the best is selected. Each score contains noise, so the winner tends to have favorable noise. Reporting that winning validation score as final performance overestimates the selected procedure's expected generalization. The issue exists even if every individual model fit is implemented correctly.

Nested cross-validation creates outer held-out folds. Within each outer training set, all tuning, feature selection, imputation and preprocessing occur using inner folds. The selected pipeline is then evaluated on the untouched outer fold. The collection of outer results estimates the procedure that includes selection. A final model can be fit on all development data using the chosen selection process, with any final external test kept separate.

If observations are grouped or temporal, both loops must honor those boundaries. Random inner folds can still leak future information even when the outer split is temporal. The tuning budget should be comparable across candidate families, and repeated manual revisions informed by outer results eventually turn the outer layer into another development resource. Record what was tried and reserve truly independent evidence for consequential decisions.

### Case study: evaluate an LLM extraction stage as a measurement instrument

A language model extracts incident start time, affected service and failure category from support notes. Those fields become inputs to a downstream reliability analysis. Evaluate the extractor against a human-reviewed sample with an explicit rubric, including ambiguous and missing cases. Field accuracy, abstention rate, consistency and subgroup error are more informative than whether the generated JSON parses.

Extraction error can be differential. Severe incidents may have longer notes and clearer timestamps, while routine incidents are terse. If the model misses routine records more often, the derived duration distribution and category rates can be biased even when average extraction accuracy is high. Preserve source spans, model/version settings and correction history so each derived field can be audited.

Validate the statistical pipeline separately from the extraction stage. A correct regression on incorrectly extracted labels remains a scientifically flawed result. Use sensitivity analysis or a measurement-error model where appropriate, and route uncertain fields for review. A generated explanation should cite the verified calculations and distinguish measured facts from hypotheses. This is where applied LLM evaluation connects directly to construct validity and data provenance.

### Case study: a small metric gain may not be a useful model gain

Two models are evaluated on the same 5,000 customers. Model A improves average squared error by 1%, but the gain is concentrated in frequent low-value transactions while rare high-cost failures worsen. A single average does not reveal whether the new model improves the decision. Examine paired loss differences, tail behavior, subgroup support and action consequences.

Resample customers, not individual transactions, if transactions within a customer are dependent. If the evaluation horizon is a future month, preserve calendar blocks or use multiple rolling origins. An interval around the paired average estimates sampling uncertainty under that resampling model; it does not account automatically for an unobserved future policy change.

Compare with operational baselines, including the current model and a simple rule. Measure latency, missing-feature behavior, calibration and cost of maintaining additional dependencies. Complexity is justified by reliable decision value, not by the prestige of the algorithm family. Report what the evidence supports and the conditions under which the comparison should be repeated.

<!-- detailed-case-studies:end -->

## Worked Python demonstrations

Complete offline program: [chapter_22.py](../examples/chapter_22.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_22.py
```

### Split the entity and the timeline

Grouped folds are checked for disjoint group identifiers, while temporal folds require every training index to precede every test index. These are different deployment questions. Real timestamp data may additionally need a gap for label maturity or overlapping windows.

### Perfect ranking does not fix probability quality

A monotonic square-root transformation preserves all rankings and hence AUC one, but changes Brier score. The probabilities have changed meaning even though every positive remains above every negative. Threshold decisions and log loss respond to that change.

### Evaluate the chosen action rule

Costs two and eight imply threshold .2 under calibrated probabilities. In the tiny observed fixture this yields one false positive, no false negatives, precision .75 and recall one. This is realized utility on five records, not a reliable population estimate.

### Compare the same cases

The two models' squared-loss difference is computed row by row before averaging, yielding minus .5 in favor of model A. Pairing removes common case difficulty. Four records illustrate the calculation but cannot support a precise superiority claim.

### Complete executable example

```python
import numpy as np
from sklearn.model_selection import GroupKFold, TimeSeriesSplit
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss, confusion_matrix


def splits_match_use():
    groups = np.repeat(np.arange(6), 2)
    x = np.arange(12)[:, None]
    for train, test in GroupKFold(3).split(x, groups=groups):
        assert set(groups[train]).isdisjoint(groups[test])
    for train, test in TimeSeriesSplit(3).split(x):
        assert train.max() < test.min()
    print("Group identities separated; temporal folds preserve order")


def ranking_vs_probability():
    y = np.array([0, 0, 1, 1])
    p = np.array([0.1, 0.4, 0.6, 0.9])
    distorted = np.sqrt(p)
    assert roc_auc_score(y, p) == roc_auc_score(y, distorted) == 1
    assert not np.isclose(brier_score_loss(y, p), brier_score_loss(y, distorted))
    print(
        "AUC stays 1; Brier:",
        brier_score_loss(y, p),
        brier_score_loss(y, distorted),
        "log loss:",
        log_loss(y, p),
    )


def decisions_and_cost():
    y = np.array([0, 1, 0, 1, 1])
    p = np.array([0.1, 0.3, 0.4, 0.7, 0.9])
    threshold = 2 / (2 + 8)
    predicted = (p > threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, predicted, labels=[0, 1]).ravel()
    assert (tn, fp, fn, tp) == (1, 1, 0, 3)
    assert 2 * fp + 8 * fn == 2
    print(
        "Precision:", tp / (tp + fp), "recall:", tp / (tp + fn), "realized cost:", 2 * fp + 8 * fn
    )


def paired_losses():
    y = np.array([0.0, 1.0, 2.0, 3.0])
    a = np.array([0.0, 2.0, 2.0, 4.0])
    b = np.array([1.0, 2.0, 3.0, 4.0])
    difference = (a - y) ** 2 - (b - y) ** 2
    assert np.isclose(difference.mean(), -0.5)
    print("Paired squared-loss differences:", difference, "mean:", difference.mean())


def main():
    splits_match_use()
    ranking_vs_probability()
    decisions_and_cost()
    paired_losses()


if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: AUC improved while business performance worsened. How?** AUC averages ranking across thresholds and ignores calibration, action costs, capacity and prevalence. The operational threshold may lie where performance deteriorated, or the policy may change outcomes. Evaluate the actual decision rule and causal utility.

**Interview: Why nested cross-validation?** Hyperparameter selection exploits validation noise. Outer folds estimate the performance of that entire selection process using observations not used for tuning. Group and time boundaries still apply in both loops.

**Interview: Which error metric should forecast staffing demand?** Tie the metric to consequences. MAE targets a median, MSE a mean, and asymmetric under-staffing costs may call for a quantile or direct utility loss. Compare the resulting decisions, not just interchangeable numerical scores.

## Applied LLM companion

The [structured extraction and contract lesson](../../llm-applied/guides/llm-applied-002.md) applies these measurement boundaries to model-produced fields. The [applied LLM course](../../llm-applied/guides/llm-applied-001.md) develops retrieval, answer evaluation and adaptation. Keep statistical calculations and analysis designs independently verifiable.

## Primary sources and official APIs

- [scikit-learn model evaluation metrics](https://scikit-learn.org/stable/modules/model_evaluation.html).

- [scikit-learn cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html).

## Connected worked tutorial

[Evaluate the complete learning procedure](../tutorials/learning/07-validation-as-a-procedure.md). Contrast identity leakage with grouped evaluation and execute nested preprocessing and model selection.

## Reading connections

[Previous chapter](21-unsupervised-learning-and-multivariate-analysis.md) | [Book contents](../README.md) | [Next chapter](23-uncertainty-quantification-and-distribution-shift.md)
