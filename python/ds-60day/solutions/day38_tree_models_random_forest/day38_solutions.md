# Day 38 — Solutions: Decision Trees and Random Forests

We train a shallow decision tree and a random forest, control overfitting with depth/leaf parameters, and compare feature importances (impurity vs permutation).

Contents
- Exercise 1: Tree depth vs accuracy
- Exercise 2: Feature importances and their reliability

---

Setup
```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
import numpy as np

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=42)
```

Worked reference for Exercise 1 — Depth vs accuracy
```python
depths = [1, 2, 3, 4, 6, 8, None]
accs = []
for d in depths:
    dt = DecisionTreeClassifier(max_depth=d, random_state=42)
    dt.fit(Xtr, ytr)
    accs.append(dt.score(Xte, yte))
list(zip(depths, accs))
```
Interpretation
- Very shallow trees underfit; very deep trees may overfit; pick a sweet spot via validation

Random forest baseline
```python
rf = RandomForestClassifier(n_estimators=300, min_samples_leaf=2, n_jobs=1, random_state=42)
rf.fit(Xtr, ytr)
rf_acc = rf.score(Xte, yte)
rf_acc
```

Worked reference for Exercise 2 — Feature importances (impurity vs permutation)
```python
# Impurity-based (built-in)
impurity_imp = rf.feature_importances_

# Permutation-based (on held-out data)
perm = permutation_importance(rf, Xte, yte, n_repeats=10, random_state=42, n_jobs=1)
perm_imp = perm.importances_mean

# Compare top features
import numpy as np
order_imp = np.argsort(impurity_imp)[::-1][:10]
order_perm = np.argsort(perm_imp)[::-1][:10]
order_imp, order_perm
```
Notes
- Impurity importances can be biased toward high-cardinality/continuous features
- Prefer permutation importance on a validation set for model-agnostic insight

Takeaways
- Use ensembles (RF) for stronger performance and robustness
- Control overfitting via max_depth/min_samples_leaf and validate choices

---

**Portable worker default:** These reference runs use `n_jobs=1` so they behave predictably on Windows, CI runners, and constrained notebook environments. After correctness is established, benchmark a larger worker count on your own workload rather than assuming `n_jobs=1` is faster.

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **`DecisionTreeClassifier(max_depth=..., min_samples_leaf=...)`:** sets capacity controls before fitting and exposes tree-specific train/validation gaps.
2. **`RandomForestClassifier(n_estimators=..., random_state=...)`:** averages bootstrapped, feature-subsampled trees; enough estimators stabilize rather than deepen the model.
3. **`permutation_importance(model, X_valid, y_valid, ...)`:** measures held-out score change under repeated feature shuffles.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** Capacity diagnostics address overfitting first; held-out perturbation then asks how predictive information is distributed.

**Useful alternative:** Gradient boosting can reduce bias sequentially, while a pruned single tree may be easier to explain.

**Trade-off:** More trees improve stability at computation cost; deeper trees increase interaction capacity and overfitting risk.

**Edge case to test:** Tiny classes, duplicated/correlated features, missing values, and high-cardinality identifiers can distort splits and importance.

**Evidence of correctness:** Report train and held-out scores across capacity settings, set seeds and `n_jobs`, test a noise feature, and include variability for permutation importance.

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

**Prompt:** Plot tree depth versus accuracy.

**How to reason about it:** Plot training and validation accuracy together across depth. An unbounded tree is a distinct setting, and one split is not enough to separate true capacity effects from sampling noise.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 1 — tree splits, ensemble variance reduction, and held-out importance — for a declared depth grid including an unconstrained tree, print train and validation accuracy mean/std on identical folds and save the labeled depth curve; choose depth from validation evidence only.

### Exercise 2 — Original lesson practice

**Prompt:** Inspect feature importances and discuss their reliability.

**How to reason about it:** Impurity importance is fast but biased toward high-cardinality and frequently split features. Compare held-out permutation importance, retain names, and discuss correlated-feature masking.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 2 — tree splits, ensemble variance reduction, and held-out importance — report impurity and seeded held-out permutation importance by feature, including a synthetic noise feature and permutation variability; flag any claim that treats impurity rank as causal or stable without the held-out check.

### Exercise 3 — Pruning implementation

**Prompt:** Use a decision tree's cost-complexity pruning path to evaluate candidate `ccp_alpha` values with cross-validation. Freeze the chosen value before final holdout evaluation.

**Reasoning before implementation:** The path is derived from training data. Treat alpha selection as a hyperparameter search inside the development boundary.

Call `cost_complexity_pruning_path` on the current training fold, fit a tree
for a bounded subset of alphas, and compare mean plus spread of validation
scores. Very small alpha retains a complex tree; sufficiently large alpha
collapses it toward the root.

If the path is computed once using the entire dataset before CV, the candidate
set itself has seen validation rows. A nested search or a fixed, documented
alpha grid provides the cleanest evaluation.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Pruning implementation — print each ccp_alpha, tree size/depth, and cross-validation mean/std; freeze the selected alpha, fit once on all training rows, and report one holdout metric without retuning.

### Exercise 4 — Out-of-bag reasoning

**Prompt:** Enable `oob_score=True` in a RandomForestClassifier and compare the out-of-bag estimate with held-out or cross-validated performance.

**Reasoning before implementation:** Each tree leaves out about 36.8% of bootstrap rows; aggregate predictions only from trees for which a row was out of bag.

OOB evaluation reuses training data efficiently and can support fast iteration,
but it is not a final untouched test. Confirm that bootstrapping is enabled and
use enough trees so each row receives many OOB votes.

Large discrepancies between OOB and held-out results can reveal distribution
shift, grouping leakage, time ordering, or insufficient forest size. Do not
average them into one reassuring number; investigate the boundary mismatch.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Out-of-bag reasoning — print oob_score_, held-out/cross-validation score, row counts, seed, and their difference; assert bootstrap and oob_score are enabled and avoid presenting OOB as an independent final test.

### Exercise 5 — Imbalance debugging

**Prompt:** Train a tree on a 98:2 dataset, compare accuracy with minority recall and average precision, then test `class_weight='balanced'`.

**Reasoning before implementation:** A majority-only classifier reaches 98% accuracy. Keep the split stratified and compare confusion matrices at a documented threshold.

Class weights change the fitting objective, not merely the report. They can
improve minority recall while reducing precision or overall accuracy. Evaluate
both classes and use the metric tied to the real error cost.

If probability quality matters, assess calibration after weighting. Never
oversample or compute weights using the final holdout labels.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Imbalance debugging — on a seeded 98:2 dataset, print class support, accuracy, minority recall, average precision, and confusion counts for default and balanced weights using identical splits.

### Exercise 6 — Correlated-importance edge case

**Prompt:** Duplicate one informative feature, refit the forest, and observe how impurity and single-feature permutation importance change.

**Reasoning before implementation:** The two columns can substitute for each other, splitting apparent importance and making either single-column permutation look weak.

Correlated substitutes let the model recover from permuting only one column.
Use domain-aware grouped permutation, conditional methods, or report the
correlation cluster together. SHAP and impurity scores also require careful
interpretation under dependence.

An importance score answers how this fitted model used available inputs under
a particular perturbation—not what would happen if the real-world feature were
intervened upon.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Correlated-importance edge case — print original/duplicate correlation and before/after impurity plus held-out permutation importance means/std; report how combined credit and individual ranks change under one fixed seed/split.
