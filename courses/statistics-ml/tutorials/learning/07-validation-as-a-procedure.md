# Evaluate everything that learns from data

Tutorial ID: `statistics-learning-007`. Prerequisites: `statistics-learning-003`, `statistics-learning-004`, `statistics-learning-006`, `statistics-022`. Complete program: [learning_07.py](examples/learning_07.py).

## Key terms

- **Grouped cross-validation:** Folds that hold out whole groups such as customers, so no identity appears in both training and evaluation.
- **Leakage:** Information from the evaluation side reaching training, such as a memorized customer identity, which inflates scores beyond what transfers to new cases.
- **Nested cross-validation:** An inner search that tunes hyperparameters inside each outer training set, with outer folds estimating the behavior of the whole selection procedure.
- **Pipeline:** Preprocessing steps and an estimator fitted together, so each scaler or encoder learns only from the training rows inside the current boundary.
- **Paired loss difference:** The per-user difference \(L_i(A)-L_i(B)\) between two frozen models on the same held-out users, whose mean and user-level uncertainty exploit pairing.

## What does the split represent?

Predicting another visit from a known customer differs from predicting a new customer's outcome. A random row split can mix customer histories across both sides. High accuracy then may reflect memorized identity rather than transferable signal.

The first fixture contains 60 customer identities, each repeated four times. Each customer receives a random binary label shared by all four rows. There is no feature that predicts a new customer's label. A one-hot customer encoding plus logistic regression performs well under shuffled stratified row folds because the same identities appear in training and evaluation. Grouped folds hold entire customers out, making unseen categories map to the explicit unknown-category policy and removing that shortcut.

The complete program measures both procedures. The row score exceeds the new-customer score by more than .2 in this fixture. This is a deliberate leakage counterexample, not a universal size of optimism. The appropriate score depends on the deployment question; using known customers is not inherently wrong when their prior information really is available and the future outcome boundary is respected.

## Fit preprocessing within each boundary

The second fixture has numeric predictors and a noisy linear response. For each outer grouped split, create an inner grouped grid search over ridge strength. Each candidate is a pipeline containing a scaler and estimator. The scaler fits on the inner training data each time, and the selected pipeline is refit on the outer training set before predicting its untouched outer test fold.

The program checks the fitted scaler's mean against the outer training rows, then reports the three outer MSEs. A scaler fitted globally before the search would fail this data-boundary interpretation even if it never read labels. Feature selection, target encoding, imputation, dimension reduction and threshold choice belong inside their appropriate learning boundary too.

## Interpret the resulting scores

Nested CV estimates the behavior of a selection procedure under the chosen split scheme. It does not evaluate a magically fixed final estimator independent of selection. Outer scores are dependent because training sets overlap, so taking their standard deviation divided by the square root of fold count is not automatically a valid confidence interval.

For two frozen models evaluated on the same held-out independent users, compute paired loss differences \(D_i=L_i(A)-L_i(B)\). A mean difference and its user-level uncertainty exploit pairing. If each user has multiple transactions, resample or aggregate users, preserving the relevant weighting. A procedure-level uncertainty claim must additionally account for retraining/selection and its sampling target.

## A repeated manual search consumes the holdout

If an analyst sees an outer result, changes features, and repeats until the score improves, the outer evidence has become development information. Preserve an independent final evaluation or clearly describe repeated reuse. A frozen seed does not make this selection disappear.

**Answered discussion: Do we need one split strategy for every model?** Candidate models should face the same decision-relevant evaluation boundary. Their internal preprocessing may differ, but a random split for one model and a future-month split for another is not an interpretable model comparison. Comparable tuning budgets also matter.

## Worked example: fold scores tell the leakage story

Aggregated means hide how stark the customer-identity shortcut in `examples/learning_07.py` is. Printing every fold makes it plain.

```python
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold, StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

rng = np.random.default_rng(2206)
groups = np.repeat(np.arange(60), 4)
x, y = groups[:, None], np.repeat(rng.binomial(1, 0.5, 60), 4)
model = make_pipeline(
    OneHotEncoder(handle_unknown="ignore", sparse_output=False), LogisticRegression(C=10)
)
rows = cross_val_score(model, x, y, cv=StratifiedKFold(4, shuffle=True, random_state=6))
new = cross_val_score(model, x, y, cv=GroupKFold(4), groups=groups)
print("row folds:  ", np.round(rows, 3))
print("group folds:", np.round(new, 3), " share of label 1:", y.mean().round(3))
```

```text
row folds:   [1. 1. 1. 1.]
group folds: [0.467 0.733 0.6   0.467]  share of label 1: 0.567
```

Every shuffled row fold scores 1.0: three of each customer's four rows train the model, and the fourth is recognized by its one-hot column. Under grouped folds the held-out customers map to the all-zero unknown encoding, so the model can only use its intercept and predicts the majority label. Fold scores of 0.467 to 0.733 average 0.567, which matches the 0.567 share of label 1, exactly the no-information baseline. A gap from 1.0 to the base rate is not overfitting in the usual sense; it is the difference between two deployment questions.

## Worked example: paired comparison with repeated users

Compare two frozen ridge models, one with all three features and one with only the first, on 30 held-out users who each contribute three rows with similar features.

```python
import numpy as np
from sklearn.linear_model import Ridge

rng = np.random.default_rng(77)
users = np.repeat(np.arange(80), 3)
x = np.repeat(rng.normal(size=(80, 3)), 3, axis=0) + 0.3 * rng.normal(size=(240, 3))
y = x @ np.array([2.0, -1.0, 0.5]) + np.repeat(rng.normal(size=80), 3) + rng.normal(size=240)
train, test = users < 50, users >= 50
full = Ridge(alpha=1).fit(x[train], y[train])
one = Ridge(alpha=1).fit(x[train][:, :1], y[train])
d = (y[test] - full.predict(x[test])) ** 2 - (y[test] - one.predict(x[test][:, :1])) ** 2
per_user = np.bincount(users[test] - 50, d) / 3
print(f"mean loss difference={d.mean():.3f}")
print(
    f"naive row SE={d.std(ddof=1) / np.sqrt(d.size):.3f}  "
    f"user SE={per_user.std(ddof=1) / np.sqrt(per_user.size):.3f}"
)
```

```text
mean loss difference=-1.653
naive row SE=0.406  user SE=0.525
```

The full model lowers squared loss by 1.653 per row on average. Treating the 90 rows as independent gives a standard error of 0.406; averaging within each user first and using the 30 user means gives 0.525, about 30% larger. Rows from the same user share feature values, so their loss differences move together and supply less independent information than their count suggests. The comparison is paired because both models score the same rows, which already removes outcome noise common to both.

## Diagnostics for a validation design

Count entities that appear on both sides of every split; the number should be zero when deployment targets new entities. Inspect per-fold scores and their spread rather than a single mean. Recompute standard errors at the unit that was sampled. Log every analysis decision made after seeing an outer score, since each one spends holdout information.

Continue to [learning theory](08-learning-theory-and-bounds.md). Existing implementation practice: [Python Day 40](../../../../python/ds-60day/companion-guides/day40_model_tuning_searchcv.md). Reference: [ISLP resampling labs](https://islp.readthedocs.io/en/stable/labs.html).
