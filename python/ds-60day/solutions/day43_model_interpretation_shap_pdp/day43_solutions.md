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
from sklearn.model_selection import train_test_split
import numpy as np

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=42)
rf = RandomForestClassifier(n_estimators=200, random_state=42).fit(Xtr, ytr)
print({'acc': rf.score(Xte, yte)})
```

Exercise 1 — SHAP summary (tree model)
```python
# SHAP can be heavy; limit to a subset to keep it fast
try:
    import shap
    shap_explainer = shap.TreeExplainer(rf)
    X_sample = Xte[:200]
    shap_values = shap_explainer.shap_values(X_sample)
    # SHAP <0.45 returned one array per class; newer SHAP returns a 3-D array.
    if isinstance(shap_values, list):
        positive_class_values = shap_values[1]
    elif shap_values.ndim == 3:
        positive_class_values = shap_values[:, :, 1]
    else:
        positive_class_values = shap_values
    shap.summary_plot(positive_class_values, X_sample, show=False)
except Exception as e:
    print('SHAP unavailable or failed:', e)
```
Notes
- TreeExplainer supports tree-based models efficiently
- Positive SHAP values push prediction toward the positive class, negative away
- Global importance can be approximated by mean |SHAP| per feature

---

Exercise 2 — Partial Dependence Plots (PDP)
```python
from sklearn.inspection import PartialDependenceDisplay
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6,4))
# Plot single feature 0 and interaction (0,1) as an example
PartialDependenceDisplay.from_estimator(rf, Xtr, [0, (0, 1)], ax=ax)
plt.tight_layout(); plt.show()
```
Interpretation
- PDP shows the marginal effect of a feature on predictions
- Interactions: use tuples (i, j) to plot 2D PDPs

---

Exercise 3 (optional) — LIME on a single prediction
```python
try:
    import lime
    from lime.lime_tabular import LimeTabularExplainer
    expl = LimeTabularExplainer(Xtr, feature_names=[f'f{i}' for i in range(X.shape[1])],
                                class_names=['neg','pos'], discretize_continuous=True)
    i = 0
    exp = expl.explain_instance(Xte[i], rf.predict_proba, num_features=5)
    exp.as_list()  # returns a list of feature contributions
except Exception as e:
    print('LIME unavailable. pip install lime to enable.\n', e)
```
Caveats
- SHAP is model-aware for trees; kernel SHAP works for general models but is slower
- PDP assumes features are independent; can mislead with strong correlations
- LIME explanations vary with sampling; interpret trends rather than single runs

---

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Exercise 1 — Original lesson practice

**Prompt:** Compare a SHAP summary for the top five important features.

**How to reason about it:** Aggregate absolute SHAP values over a representative held-out sample, preserve feature names, and record the explainer/background choice. Magnitude ranks influence; sign and dependence require separate inspection.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 2 — Original lesson practice

**Prompt:** Plot PDP for the most important feature and interpret it.

**How to reason about it:** A PDP averages model predictions over counterfactual feature values. Mark regions with little support and prefer conditional/ICE diagnostics when correlated features make those combinations unrealistic.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 3 — Original lesson practice

**Prompt:** Optionally use LIME on one prediction and compare it with SHAP. LIME is installed by the `ml` dependency group but remains an optional lesson extension. Complete the required work with SHAP and scikit-learn before adding a second explanation library.

**How to reason about it:** LIME is an optional local surrogate whose result depends on neighborhood sampling and kernel choices. Compare repeated explanations and do not treat agreement with SHAP as proof of causal truth.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

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
