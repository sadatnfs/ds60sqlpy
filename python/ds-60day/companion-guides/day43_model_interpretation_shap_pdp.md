# Day 43 — Model Interpretation: SHAP, PDP, and Permutation (Companion Guide)

## Learning objectives
- Use permutation importance to assess feature impact
- Plot partial dependence (PDP) and ICE for marginal effects
- Explain predictions with SHAP values; understand limitations

## Why this matters
Interpretability builds trust, surfaces bias, and guides feature work.

## Core concepts and examples
### Permutation importance
```python
from sklearn.inspection import permutation_importance
r = permutation_importance(model, X_valid, y_valid, n_repeats=10, scoring='roc_auc', random_state=0)
```

### PDP/ICE
```python
from sklearn.inspection import PartialDependenceDisplay
PartialDependenceDisplay.from_estimator(model, X_valid, ['age','income'])
```

### SHAP (tree-based example)
```python
import shap
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_valid)
shap.summary_plot(shap_values, X_valid)
```

## Common pitfalls
- Correlated features can distort importance rankings
- PDP assumes feature independence; ICE helps reveal heterogeneity
- SHAP on non-tree models may be slower; use approximate methods

## Practice exercises
1) Compare permutation importance vs model-native importance
2) Generate PDP/ICE for two top features and interpret
3) Create SHAP summary and dependence plots; discuss findings

## Further reading
- sklearn inspection: https://scikit-learn.org/stable/modules/partial_dependence.html
- SHAP: https://shap.readthedocs.io
