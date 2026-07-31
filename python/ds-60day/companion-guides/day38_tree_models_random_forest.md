# Day 38 — Decision Trees and Random Forests

**Lesson ID:** `python-38` · **Level:** intermediate · **Dependencies:** `data` · **Network:** offline

Decision trees divide feature space through a sequence of rules. Random forests
average many randomized trees to reduce the instability of a single tree.

## Learning objectives

By the end of the lesson, you can:

- fit and compare a decision tree and random forest;
- identify underfitting and overfitting as depth changes;
- control tree complexity with depth and leaf-size settings;
- compare impurity-based and held-out permutation importance; and
- explain why feature importance is not causal importance.

## Prerequisites

- Complete `python-37` (regularized linear models).
- Be able to make a stratified split and interpret accuracy from `python-35`.
- Recall that validation choices must not use the final test set.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Split | Feature threshold that partitions observations at a node |
| Impurity | Measure of class mixing, such as Gini impurity |
| Leaf | Terminal node that produces a prediction |
| Maximum depth | Longest allowed root-to-leaf path |
| Bootstrap sample | Sample drawn with replacement |
| Feature subsampling | Considering only a random subset of features at a split |
| Random forest | Ensemble of decorrelated trees whose predictions are averaged or voted |
| Permutation importance | Score decrease after shuffling one feature in evaluation data |

A deep tree can memorize small idiosyncrasies. A forest reduces variance through
averaging, but it can still learn leakage, bias, and spurious correlations.

## Worked example: compare training and held-out behavior

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, stratify=y, random_state=42
)

for depth in [1, 2, 4, 8, None]:
    tree = DecisionTreeClassifier(max_depth=depth, random_state=42)
    tree.fit(X_train, y_train)
    print(depth, tree.score(X_train, y_train), tree.score(X_test, y_test))
```

The gap between training and held-out accuracy is one diagnostic, not a complete
model-selection procedure. Choose complexity with validation or CV and report a
separate test estimate.

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 38 learner notebook from this guide's **Next
   step** section in VS Code or JupyterLab.
2. Select the `Python (ds60sqlpy)` kernel. Start at the top and use
   **Run All** only after making the written predictions; every added
   worked example is bounded and offline after bootstrap.
3. Keep experiments in new scratch cells. Do not edit the official
   solution while attempting the numbered practice.
4. Restart the kernel and run from the first cell before calling the
   lesson complete. A clean run catches hidden state and stale
   variables.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab
```

macOS/Linux:

```bash
.venv/bin/python -m jupyter lab
```

If the Windows environment uses the documented conda-prefix fallback,
use `.\.venv\python.exe` in place of
`.\.venv\Scripts\python.exe`.

## Concept deep dive — tree splits, ensemble variance reduction, and held-out importance

### The mental model

A decision tree recursively partitions feature space. Each split asks a
threshold question chosen to reduce impurity; each leaf stores a local
prediction. Deep trees can represent fine interactions but also isolate
noise. Depth, leaf size, and pruning control that capacity.

A random forest trains many trees on bootstrapped rows while considering
subsets of features. Averaging decorrelated trees reduces variance.
Impurity importance describes split usage inside the fitted forest;
held-out permutation importance measures score loss when one feature's
association is broken. Neither establishes causality.

### Worked examples and syntax anatomy

- **`DecisionTreeClassifier(max_depth=..., min_samples_leaf=...)`:** sets capacity controls before fitting and exposes tree-specific train/validation gaps.
- **`RandomForestClassifier(n_estimators=..., random_state=...)`:** averages bootstrapped, feature-subsampled trees; enough estimators stabilize rather than deepen the model.
- **`permutation_importance(model, X_valid, y_valid, ...)`:** measures held-out score change under repeated feature shuffles.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — make the depth-versus-generalization gap visible

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

X, y = load_breast_cancer(return_X_y=True)
X_train, X_valid, y_train, y_valid = train_test_split(
    X, y, stratify=y, random_state=3801
)
for depth in (1, 3, 8, None):
    tree = DecisionTreeClassifier(max_depth=depth, random_state=3801)
    tree.fit(X_train, y_train)
    print(depth, {"train": tree.score(X_train, y_train),
                  "valid": tree.score(X_valid, y_valid)})
```

**Expected observation:** Training accuracy rises with capacity; validation accuracy need not, revealing overfitting rather than a syntax error.

**Assumption to name:** The validation split represents future cases and was not used to choose unlimited alternatives.

### Focused example B — test a deliberately useless noise feature

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split

X, y = load_breast_cancer(return_X_y=True)
rng = np.random.default_rng(3802)
X = np.column_stack([X, rng.normal(size=X.shape[0])])
X_train, X_valid, y_train, y_valid = train_test_split(
    X, y, stratify=y, random_state=3802
)
forest = RandomForestClassifier(n_estimators=80, random_state=3802, n_jobs=1)
forest.fit(X_train, y_train)
importance = permutation_importance(
    forest, X_valid, y_valid, n_repeats=5, random_state=3802, n_jobs=1
)
print({"noise_importance": importance.importances_mean[-1],
       "best_importance": importance.importances_mean.max()})
```

**Expected observation:** The random noise feature should have importance near zero, while at least one real feature matters more.

**Assumption to name:** The model's held-out score is good enough that score perturbations are interpretable.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define tree splits, ensemble variance reduction, and held-out importance in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Treating `feature_importances_` as causal effect or as reliable when correlated features can substitute for one another.

**Debug it deliberately:** Compare train/validation scores, tree depth/leaf counts, repeated permutation intervals, and a synthetic noise feature.

**Stop condition:** Do not interpret importance from a poorly performing model or from the same rows used to fit it.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Plot tree depth versus accuracy.

**Verify:** Practice 1 — tree splits, ensemble variance reduction, and held-out importance — for a declared depth grid including an unconstrained tree, print train and validation accuracy mean/std on identical folds and save the labeled depth curve; choose depth from validation evidence only.

2. Inspect feature importances and discuss their reliability.

**Verify:** Practice 2 — tree splits, ensemble variance reduction, and held-out importance — report impurity and seeded held-out permutation importance by feature, including a synthetic noise feature and permutation variability; flag any claim that treats impurity rank as causal or stable without the held-out check.

### Progressive hints

1. Record training and validation accuracy for each depth. Treat `None` as an
   unbounded depth label rather than a numeric x-coordinate.
2. Compare `feature_importances_` with
   `sklearn.inspection.permutation_importance` on held-out data. Preserve feature
   names from `load_breast_cancer().feature_names`.

### Additional mastery practice

Diagnose tree capacity with train/validation evidence and inspect importance with methods that respect held-out data, correlation, and class costs.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

3. **Pruning implementation:** Use a decision tree's cost-complexity pruning path to evaluate candidate `ccp_alpha` values with cross-validation. Freeze the chosen value before final holdout evaluation.
   **Progressive hint:** The path is derived from training data. Treat alpha selection as a hyperparameter search inside the development boundary.

**Verify:** Pruning implementation — print each ccp_alpha, tree size/depth, and cross-validation mean/std; freeze the selected alpha, fit once on all training rows, and report one holdout metric without retuning.

4. **Out-of-bag reasoning:** Enable `oob_score=True` in a RandomForestClassifier and compare the out-of-bag estimate with held-out or cross-validated performance.
   **Progressive hint:** Each tree leaves out about 36.8% of bootstrap rows; aggregate predictions only from trees for which a row was out of bag.

**Verify:** Out-of-bag reasoning — print oob_score_, held-out/cross-validation score, row counts, seed, and their difference; assert bootstrap and oob_score are enabled and avoid presenting OOB as an independent final test.

5. **Imbalance debugging:** Train a tree on a 98:2 dataset, compare accuracy with minority recall and average precision, then test `class_weight='balanced'`.
   **Progressive hint:** A majority-only classifier reaches 98% accuracy. Keep the split stratified and compare confusion matrices at a documented threshold.

**Verify:** Imbalance debugging — on a seeded 98:2 dataset, print class support, accuracy, minority recall, average precision, and confusion counts for default and balanced weights using identical splits.

6. **Correlated-importance edge case:** Duplicate one informative feature, refit the forest, and observe how impurity and single-feature permutation importance change.
   **Progressive hint:** The two columns can substitute for each other, splitting apparent importance and making either single-column permutation look weak.

**Verify:** Correlated-importance edge case — print original/duplicate correlation and before/after impurity plus held-out permutation importance means/std; report how combined credit and individual ranks change under one fixed seed/split.

Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.

## Self-check

- Why does a fully grown tree often have very high training accuracy?
- How do bootstrap sampling and feature subsampling decorrelate trees?
- Why can impurity importance favor continuous or high-cardinality features?
- What happens to permutation importance when two features carry redundant
  information?

Expected behavior: very shallow trees underfit, a random forest is generally
more stable than one tree, and the two importance rankings need not match.

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Consequence | Better practice |
|---|---|---|
| Choosing depth on the test set | Optimistic evaluation | Tune in validation/CV |
| Reporting only impurity importance | Biased ranking | Add held-out permutation importance |
| Treating importance as direction | Magnitude has no sign | Use effect-oriented tools and domain analysis |
| Leaving resource use unbounded | Slow or memory-heavy fit | Start with modest `n_estimators` and `n_jobs` |
| Assuming trees need no preprocessing ever | Missing values/categories still require handling | Use a reproducible preprocessing pipeline |

More trees usually reduce Monte Carlo variation but cost CPU and memory.
`min_samples_leaf` is often a more interpretable smoothness control than depth
alone.

## Next step

- Work in the [Day 38 learner notebook](../notebooks/day38_tree_models_random_forest.ipynb).
- Then consult the
  [Day 38 solution](../solutions/day38_tree_models_random_forest/day38_solutions.md).
- Continue to [Day 39 — Gradient Boosting](day39_gradient_boosting_xgboost_lightgbm.md).

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-38` — Day 38 — Decision Trees and Random Forests.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize tree splits, ensemble variance reduction, and held-out importance. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day38_tree_models_random_forest.md`
- learner artifact: `python/ds-60day/notebooks/day38_tree_models_random_forest.ipynb`

Treat me as a beginner except for these direct catalog prerequisites:
`python-37`. Do not assume knowledge beyond them or skip the
guide's declared setup boundary. Do not open or quote anything under
`solutions/` unless I explicitly ask after an honest attempt. First
explain one concept in plain language and show a tiny example. Then ask
me to predict what happens before I run code.
Give me one bounded task at a time and wait for my code, output, error,
or written reasoning. If I am stuck, reveal only one rung of a
progressive hint ladder at a time.

Run or inspect my learner artifact when safe, distinguish observed
evidence from inference, and help me diagnose tracebacks instead of
replacing my work. Finish with two or three retrieval questions and
one transfer task.

Done when I can explain the core mechanism without notes, complete one
fresh attempt without copied solution code, produce the guide's stated
verification evidence from a clean run, answer the retrieval questions,
and explain how the transfer task changes the assumptions. A cell that
merely ran is not evidence of mastery.
```
