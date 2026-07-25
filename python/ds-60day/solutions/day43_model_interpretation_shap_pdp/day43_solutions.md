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
