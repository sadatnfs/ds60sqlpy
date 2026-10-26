# Evaluate everything that learns from data

Tutorial ID: `statistics-learning-007`. Prerequisites: `statistics-learning-003`, `statistics-learning-004`, `statistics-learning-006`, `statistics-022`. Complete program: [learning_06.py](examples/learning_06.py).

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

Continue to [learning theory](08-learning-theory-and-bounds.md). Existing implementation practice: [Python Day 40](../../../../python/ds-60day/companion-guides/day40_model_tuning_searchcv.md). Reference: [ISLP resampling labs](https://islp.readthedocs.io/en/stable/labs.html).
