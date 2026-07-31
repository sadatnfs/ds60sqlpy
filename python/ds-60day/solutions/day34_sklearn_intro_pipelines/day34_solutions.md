# Day 34 — Solutions: scikit-learn Intro and Pipelines

We build a basic preprocessing + model pipeline, then swap models (Ridge) and inspect coefficients, emphasizing reproducibility and leak-free evaluation.

Contents
- Exercise 1: Build a pipeline (scaler + LinearRegression) with train/test split
- Exercise 2: Swap in Ridge and compare scores
- Exercise 3: Inspect coefficients and discuss the impact of scaling

---

Worked reference for Exercise 1 — Pipeline with scaler + LinearRegression
```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.datasets import load_diabetes

X, y = load_diabetes(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)

pipe = Pipeline([
    ('sc', StandardScaler()),
    ('lr', LinearRegression())
])
pipe.fit(Xtr, ytr)
score_lr = pipe.score(Xte, yte)
score_lr
```
Line-by-line
- StandardScaler is inside the Pipeline, so fit is performed only on training data
- R² score on the test split is returned by `score`

---

Worked reference for Exercise 2 — Swap to Ridge and compare
```python
from sklearn.linear_model import Ridge

pipe_ridge = Pipeline([
    ('sc', StandardScaler()),
    ('ridge', Ridge(alpha=1.0, random_state=42))
])
pipe_ridge.fit(Xtr, ytr)
score_ridge = pipe_ridge.score(Xte, yte)
{'linear': score_lr, 'ridge': score_ridge}
```
Notes
- Ridge adds L2 regularization which can improve generalization, especially with correlated features
- Tune `alpha` via cross-validation for best results

---

Worked reference for Exercise 3 — Inspect coefficients with and without scaling
```python
# With scaling
pipe.fit(Xtr, ytr)
coefs_scaled = pipe.named_steps['lr'].coef_

# Without scaling (not recommended generally for linear models)
from sklearn.linear_model import LinearRegression
lr_noscale = LinearRegression().fit(Xtr, ytr)
coefs_noscale = lr_noscale.coef_

coefs_scaled, coefs_noscale
```
Interpretation
- Coefficient magnitudes are not directly comparable across features without scaling
- Scaling stabilizes optimization and makes coefficients more interpretable (relative impact per standardized feature)

Takeaways
- Always put preprocessing inside pipelines to avoid leakage
- Try regularized models (Ridge/Lasso) and select hyperparameters via CV

---

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **`Pipeline([('scale', ...), ('model', ...)])`:** names ordered steps so nested parameters and learned attributes remain inspectable.
2. **`.fit(X_train, y_train)`:** fits every transformer on training rows, transforms those rows, then fits the final estimator.
3. **`.predict(X_new)`:** uses already learned preprocessing and model state; it must not refit on new data.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** The unified estimator contract makes training boundaries repeatable and allows model selection tools to clone the full workflow.

**Useful alternative:** Manual preprocessing can be valid when it uses an explicit fitted object and tests prove train-only state, but it is easier to misuse.

**Trade-off:** Pipelines add naming and inspection overhead while sharply reducing inconsistent preprocessing and leakage risk.

**Edge case to test:** Unknown categories, missing columns, changed column order, and sparse/dense output expectations must be part of the input contract.

**Evidence of correctness:** Inspect fitted step attributes, prove test rows did not enter learned preprocessing, verify feature shape/order, and execute prediction on an unknown-category boundary.

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

**Prompt:** Swap `LinearRegression` for `Ridge` and compare test scores.

**How to reason about it:** Change only the final estimator while keeping the split and preprocessing fixed. Compare held-out metrics and coefficient magnitude; one score does not establish that regularization is universally better.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 1 — the scikit-learn estimator contract and leakage-safe pipelines — use one frozen train/test split and one preprocessing pipeline; report Ridge alpha, baseline and Ridge R² plus RMSE, and assert model selection never reads the test labels.

### Exercise 2 — Original lesson practice

**Prompt:** Inspect the coefficients and discuss how feature scaling changes their numeric values and interpretation.

**How to reason about it:** A coefficient after StandardScaler describes a one-standard-deviation change in that fitted training feature. Preserve transformed feature names and avoid causal language when predictors are correlated.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 2 — the scikit-learn estimator contract and leakage-safe pipelines — print feature names in coefficient order and both scaled-space coefficients and coefficients converted back to original units; verify the two representations produce equal predictions within 1e-10.

### Exercise 3 — Leakage prediction

**Prompt:** Predict how cross-validation scores can change when a scaler is fit on the complete dataset before `cross_val_score`, then explain why the code still runs without warning.

**Reasoning before implementation:** The globally fitted mean and scale contain information from each validation fold. A Pipeline refits them using only the fold's training rows.

The global transform lets every held-out row influence preprocessing
statistics, so validation is no longer a simulation of unseen data. The score
may be optimistically biased even though shapes and types are valid.

Pass raw `X` and a `Pipeline([("scale", StandardScaler()), ("model", ...)])`
to cross-validation. scikit-learn clones and fits the entire pipeline inside
each training fold. This same rule applies to imputation, feature selection,
target encoding, and learned dimensionality reduction.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Leakage prediction — on one seeded dataset, print fold scores for a scaler fitted globally and for Pipeline(StandardScaler(), model); show the global fit has seen validation statistics and retain the score difference without treating its direction as guaranteed.

### Exercise 4 — Mixed-type implementation

**Prompt:** Build a `ColumnTransformer` for numeric imputation/scaling and categorical imputation/one-hot encoding, followed by LogisticRegression. Use a tiny DataFrame containing a missing value.

**Reasoning before implementation:** Use separate nested pipelines and `handle_unknown='ignore'`; keep column lists explicit so schema drift is visible.

```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

numeric = ["age", "income"]
categorical = ["region"]
preprocess = ColumnTransformer(
    [
        (
            "num",
            Pipeline(
                [("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
            ),
            numeric,
        ),
        (
            "cat",
            Pipeline(
                [
                    ("impute", SimpleImputer(strategy="most_frequent")),
                    ("encode", OneHotEncoder(handle_unknown="ignore")),
                ]
            ),
            categorical,
        ),
    ]
)
model = Pipeline(
    [("preprocess", preprocess), ("model", LogisticRegression(max_iter=1_000))]
)
```

Fit this object only after the split. Median and most-frequent values are
learned state, not harmless cleanup constants.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Mixed-type implementation — fit the mixed pipeline on a tiny DataFrame with named numeric/categorical columns and one missing value; assert output row count, transformed feature names, finite values, and a prediction for a row containing an unseen category.

### Exercise 5 — Unknown-category debugging

**Prompt:** Fit on regions `north` and `south`, then predict a row with region `west`. Compare `OneHotEncoder` default behavior with `handle_unknown='ignore'` and explain the resulting representation.

**Reasoning before implementation:** The default raises on an unseen category. Ignore maps the unknown to all zeros for that feature block, which is operationally safe but lossy.

With `handle_unknown="ignore"`, the transformed categorical block for `west`
contains zeros in both known-region columns. The model can score the row, but
it cannot distinguish “unknown” from the baseline implied by that zero vector.

Monitor unknown-category rates and consider an explicit rare/unknown bucket
when the distinction matters. Do not fit the encoder again during prediction;
that would change the feature schema and invalidate fitted coefficients.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Unknown-category debugging — capture the default OneHotEncoder unknown-category ValueError for region='west'; with handle_unknown='ignore', assert prediction succeeds and the west one-hot block is all zeros in the documented feature order.

### Exercise 6 — Inspection and schema contract

**Prompt:** After fitting the mixed-type pipeline, recover transformed feature names, pair them with coefficients, and assert that an inference DataFrame has the required columns in a safe order.

**Reasoning before implementation:** Use `get_feature_names_out()` from the fitted ColumnTransformer. Select by column name rather than trusting an incoming positional order.

```python
required = numeric + categorical

def validate_inference_frame(frame: pd.DataFrame) -> pd.DataFrame:
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f"missing required columns: {missing}")
    return frame.loc[:, required].copy()

# After `model.fit(train_frame, target)`:
# names = model.named_steps["preprocess"].get_feature_names_out()
# coefs = model.named_steps["model"].coef_[0]
# assert len(names) == len(coefs)
```

Extra columns may be rejected or deliberately ignored, but the policy should
be explicit. Persist the fitted pipeline and its input schema together so
serving code cannot silently invent another column order.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Inspection and schema contract — print get_feature_names_out() paired one-to-one with coefficients; assert required input columns are present, reject missing/extra columns under the chosen policy, reorder safely, and match a fixed prediction.
