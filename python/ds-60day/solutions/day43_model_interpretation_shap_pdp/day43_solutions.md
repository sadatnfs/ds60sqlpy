# Day 43 — Solutions: Model Interpretation (SHAP, PDP, LIME)

We introduce global vs local interpretability, compute SHAP values for a tree model, draw Partial Dependence Plots (PDP), and briefly show how to apply LIME (optional).

Contents
- Exercise 1: SHAP summary for top features (tree model)
- Exercise 2: Partial Dependence for most important feature(s)
- Exercise 3 (optional): LIME on a single prediction

---

Setup
```python
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split
import numpy as np

dataset = load_breast_cancer()
X, y = dataset.data, dataset.target
feature_names = np.asarray(dataset.feature_names)
Xtr, Xte, ytr, yte = train_test_split(
    X,
    y,
    stratify=y,
    random_state=42,
)
rf = RandomForestClassifier(n_estimators=80, random_state=42).fit(Xtr, ytr)
X_explain, y_explain = Xte[:50], yte[:50]
permutation = permutation_importance(
    rf,
    X_explain,
    y_explain,
    scoring="roc_auc",
    n_repeats=5,
    random_state=43,
    n_jobs=1,
)
permutation_order = np.argsort(permutation.importances_mean)[::-1]
most_important = int(permutation_order[0])
print(
    {
        "held_out_accuracy": rf.score(Xte, yte),
        "pdp_feature": feature_names[most_important],
        "permutation_mean": permutation.importances_mean[most_important],
    }
)
```

Worked reference for Exercise 1 — SHAP summary (tree model)
```python
# Missing SHAP is a disclosed capability boundary. Any failure after a
# successful import is a real defect and must remain visible.
try:
    import shap
except ModuleNotFoundError:
    print("SHAP is not installed; complete the permutation/PDP work first.")
else:
    shap_explainer = shap.TreeExplainer(rf)
    shap_values = shap_explainer.shap_values(X_explain)
    # SHAP <0.45 returned one array per class; newer SHAP returns a 3-D array.
    if isinstance(shap_values, list):
        positive_class_values = np.asarray(shap_values[1])
    elif np.asarray(shap_values).ndim == 3:
        positive_class_values = np.asarray(shap_values)[:, :, 1]
    else:
        positive_class_values = np.asarray(shap_values)
    assert positive_class_values.shape == X_explain.shape
    mean_absolute_shap = np.abs(positive_class_values).mean(axis=0)
    shap_order = np.argsort(mean_absolute_shap)[::-1]
    shap_top_five = feature_names[shap_order[:5]].tolist()
    permutation_top_five = feature_names[permutation_order[:5]].tolist()
    print(
        {
            "shap_top_five": shap_top_five,
            "permutation_top_five": permutation_top_five,
            "top_five_overlap": sorted(
                set(shap_top_five) & set(permutation_top_five)
            ),
        }
    )
    shap.summary_plot(
        positive_class_values,
        X_explain,
        feature_names=feature_names,
        max_display=5,
        show=False,
    )
```
Notes
- TreeExplainer supports tree-based models efficiently
- Positive SHAP values push prediction toward the positive class, negative away
- Global importance can be approximated by mean |SHAP| per feature

---

Worked reference for Exercise 2 — Partial Dependence Plots (PDP)
```python
from sklearn.inspection import PartialDependenceDisplay
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6, 4))
PartialDependenceDisplay.from_estimator(
    rf,
    Xtr,
    [most_important],
    feature_names=feature_names,
    ax=ax,
    grid_resolution=20,
)
ax.set_title(
    f"PDP for held-out permutation rank 1: {feature_names[most_important]}"
)
plt.tight_layout()
plt.show()
```
Interpretation
- PDP shows the marginal effect of a feature on predictions
- Interactions: use tuples (i, j) to plot 2D PDPs

---

Worked reference for Exercise 3 (optional) — LIME on a single prediction
```python
try:
    from lime.lime_tabular import LimeTabularExplainer
except ModuleNotFoundError:
    print("LIME is not installed; this optional comparison is skipped.")
else:
    lime_results = []
    for seed in (43, 44, 45):
        explainer = LimeTabularExplainer(
            Xtr,
            feature_names=feature_names,
            class_names=["negative", "positive"],
            discretize_continuous=True,
            random_state=seed,
        )
        explanation = explainer.explain_instance(
            Xte[0],
            rf.predict_proba,
            labels=(1,),
            num_features=5,
        )
        lime_results.append(explanation.as_list(label=1))
    print(lime_results)
```
Caveats
- SHAP is model-aware for trees; kernel SHAP works for general models but is slower
- PDP assumes features are independent; can mislead with strong correlations
- LIME explanations vary with sampling; interpret trends rather than single runs

---

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **`permutation_importance(..., X_valid, y_valid)`:** measures predictive reliance on held-out data with repeated shuffles and a declared scorer.
2. **`PartialDependenceDisplay.from_estimator(...)`:** averages model predictions over a grid while holding the empirical distribution of other features.
3. **`shap.TreeExplainer(model, data=background, ...)`:** allocates model output under an explicit dependence/background convention; output shape is model/version dependent.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** Triangulating local sensitivity, held-out permutation, and global behavior makes method assumptions and disagreements visible.

**Useful alternative:** Coefficients, ALE plots, counterfactual analysis, and model-specific diagnostics answer different questions and may handle correlation differently.

**Trade-off:** Model-agnostic explanations are portable but computationally expensive and assumption-heavy; simpler models can be easier to audit.

**Edge case to test:** Correlated/duplicate features, multiclass output shapes, out-of-range perturbations, and unstable background samples can radically change attributions.

**Evidence of correctness:** Explain only a validated held-out model, report repeated uncertainty, record background/scorer/output class, test plausibility, and state explicitly that predictive explanation is not causality.

When comparing your attempt with the reference, explain which of these
decisions your code made explicitly. If the reference makes a different
choice, compare the contracts and evidence before deciding that one
version is universally better.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Exercise 1 — Original lesson practice

**Prompt:** On the first 50 held-out rows, rank features by mean absolute positive-class SHAP value. Report the five names and values, then compare their ordering with held-out permutation importance from the same fitted model, rows, scorer, and five seeded repeats.

**How to reason about it:** Aggregate absolute SHAP values over a representative held-out sample, preserve feature names, and record the explainer/background choice. Magnitude ranks influence; sign and dependence require separate inspection.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 1 — global versus local explanations, perturbation assumptions, and causal limits — assert that the normalized positive-class SHAP matrix has 50 rows and one column per named feature; report both named top-five lists, their numeric means, the fixed permutation seed/repeat count, and their set/rank overlap on the identical held-out rows and scorer.

### Exercise 2 — Original lesson practice

**Prompt:** Select the feature ranked first by the held-out permutation calculation in Exercise 1, then plot its one-dimensional PDP. Report its name, ranking value, PDP direction/nonlinearity, and where the displayed deciles show weak data support; do not use causal language.

**How to reason about it:** A PDP averages model predictions over counterfactual feature values. Mark regions with little support and prefer conditional/ICE diagnostics when correlated features make those combinations unrealistic.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 2 — global versus local explanations, perturbation assumptions, and causal limits — print the selected feature name, index, and held-out permutation mean; assert that same index enters the PDP call, then retain the labeled curve/deciles plus a numeric direction and sparse-support caveat without causal language.

### Exercise 3 — Original lesson practice

**Prompt:** Optionally explain held-out row 0 with LIME and SHAP using the same positive-class output. Repeat LIME with three declared seeds and compare signs, top-five overlap, and instability; skip only when importing `lime` raises `ModuleNotFoundError`.

**How to reason about it:** LIME is an optional local surrogate whose result depends on neighborhood sampling and kernel choices. Compare repeated explanations and do not treat agreement with SHAP as proof of causal truth.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 3 — global versus local explanations, perturbation assumptions, and causal limits — treat only a missing `lime` import as a skip; when installed, record three seed-specific contribution lists and compare sign, top-five overlap, and instability against SHAP for held-out row 0; let every other exception fail visibly.

### Exercise 4 — Local-versus-global diagnosis

**Prompt:** Construct a case where a feature is globally important but contributes little to one prediction. Explain why those statements do not conflict.

**Reasoning before implementation:** Global importance aggregates across rows; a local explanation is conditioned on one row and its baseline.

A feature can drive predictions for many records while the selected record has
a value near the model's baseline or lies in a region where another feature
dominates. Report the local predicted value, baseline, and contributions, then
separately report how global importance was aggregated.

Do not use one compelling local waterfall plot to summarize an entire
population. Sample representative correct cases, errors, and important slices.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Local-versus-global diagnosis — record the feature's aggregate importance/rank and its signed contribution for the chosen held-out row; show that the global summary is large while that row's local contribution is near zero, and identify the row-specific baseline.

### Exercise 5 — Explanation leakage

**Prompt:** Explain why selecting the 'most important' features with the final test set and then retraining a smaller model contaminates evaluation.

**Reasoning before implementation:** The explanation becomes a supervised feature-selection step. Keep the test set unavailable until the complete selection procedure is frozen.

Importance computed on test rows uses their features and often their labels
through the evaluation choice. If it changes the model, threshold, or feature
set, the test data has entered development.

Perform explanation-guided pruning within training/validation or nested CV,
then evaluate the frozen reduced pipeline on the untouched test once. It is
fine to explain final test errors afterward if no new performance claim is
made from a retrained model.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Explanation leakage — draw the data-access timeline and mark final-test explanations as a feature-selection use of test labels; then show the corrected train/validation-only selection boundary with the final test opened once after the feature set and pipeline are frozen.

### Exercise 6 — Correlated-feature and causality check

**Prompt:** Duplicate or strongly correlate one predictor, compare SHAP, PDP, and permutation results, and write a cautious stakeholder explanation.

**Reasoning before implementation:** Credit can move or split between substitutes; marginal perturbations can create implausible combinations.

State that the model uses a correlated feature group rather than claiming one
member independently causes the outcome. Show the correlation/support evidence
and, when appropriate, grouped permutation or conditional analysis.

Predictive explanation answers how this fitted model behaves under a specified
background and perturbation. A causal claim requires a causal design and
assumptions not supplied by SHAP, PDP, LIME, or permutation importance.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Correlated-feature and causality check — report the original/duplicate correlation, seeded before-and-after SHAP and permutation ranks, and both PDP curves; state that credit may split between substitutes and that none of the three methods establishes a causal effect.
