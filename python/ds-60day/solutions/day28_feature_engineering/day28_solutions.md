# Day 28 — Solutions: Feature Engineering

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**reproducible feature transformations without information leakage**.

A feature is a model input available at the moment a prediction would be
made. Feature engineering changes representation to expose useful
structure: scaling numbers, encoding categories, extracting dates,
binning, or combining fields. It must preserve the time/knowledge
boundary—post-outcome data and target-derived values are leakage.

A transformer learns parameters during `fit` and applies them during
`transform`. Split evaluation data before fitting learned means, scales,
bins, imputers, or category vocabularies. A pipeline binds every learned
step to the model and applies identical logic at inference. Define
missing, unseen-category, and zero-variance behavior.

### Vocabulary used in the worked answers

- **feature:** an input value available to a model at prediction time.
- **transformer:** an object that fits parameters and transforms data.
- **fit:** learn transformation/model parameters from training data.
- **transform:** apply already learned parameters to data.
- **pipeline:** an ordered fitted chain of preprocessing and estimation.
- **leakage:** evaluation or future/target information entering training features.

### Reference pattern 1 — Fit scaling on training data only

The held-out value is transformed with training parameters.

```python
import numpy as np
from sklearn.preprocessing import StandardScaler

train = np.array([[1.0], [2.0], [3.0]])
test = np.array([[10.0]])
scaler = StandardScaler().fit(train)
(scaler.mean_.tolist(), scaler.transform(test).round(2).tolist())
```

**Expected observation:** The training mean is `[2.0]`; the held-out value becomes a large positive standardized value. Test data did not influence the mean.

### Reference pattern 2 — Handle an unseen category explicitly

The encoder's inference contract belongs inside preprocessing.

```python
from sklearn.preprocessing import OneHotEncoder

encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
encoder.fit([["red"], ["blue"]])
encoded = encoder.transform([["green"], ["red"]])
(encoder.categories_[0].tolist(), encoded.tolist())
```

**Expected observation:** Known levels are `['blue', 'red']`; unseen `green` becomes all zeros while `red` activates its learned column.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Add a fare-bin feature using a transformer inside the preprocessing pipeline. **Contract:** thresholds are learned or fixed without evaluation data, bin closure/labels are documented, and missing/out-of-range behavior is defined. **Verify:** inspect fitted thresholds/feature names and test exact boundaries plus one missing value.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies reproducible feature transformations without information leakage.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Stateless arithmetic/date extraction can be a small function transformer; learned preprocessing belongs in fitted pipeline objects.

**Edge case:** Unseen categories, missing values, zero variance, target/time leakage, sparse/dense memory growth, and feature-name drift require tests.

**Solution evidence to inspect:** inspect fitted thresholds/feature names and test exact boundaries plus one missing value.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Compare one model pipeline with scaling against the same model pipeline without scaling. **Constraints:** keep split/folds, random state, features, model, and all other transforms identical; fit both only on training data. **Expected behavior:** report held-out or cross-validated scores with uncertainty, not training score. **Verify:** state whether the observed difference is large enough to matter and why the model family may or may not need scaling.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies reproducible feature transformations without information leakage.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Stateless arithmetic/date extraction can be a small function transformer; learned preprocessing belongs in fitted pipeline objects.

**Edge case:** Unseen categories, missing values, zero variance, target/time leakage, sparse/dense memory growth, and feature-name drift require tests.

**Solution evidence to inspect:** state whether the observed difference is large enough to matter and why the model family may or may not need scaling.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict how fitting a scaler or category encoder before the train/test split leaks information from evaluation data. **Progressive hint:** Learned means, scales, and categories become evaluation-derived parameters. **Verify:** Fit both ways on a fixture with an extreme held-out value; record differing learned parameters and assert the pipeline fit uses training rows only.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying reproducible feature transformations without information leakage.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Stateless arithmetic/date extraction can be a small function transformer; learned preprocessing belongs in fitted pipeline objects.

**Edge case:** Unseen categories, missing values, zero variance, target/time leakage, sparse/dense memory growth, and feature-name drift require tests.

**Solution evidence to inspect:** Fit both ways on a fixture with an extreme held-out value; record differing learned parameters and assert the pipeline fit uses training rows only.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace numeric and categorical columns through a `ColumnTransformer` and state the output order/shape. **Progressive hint:** Each branch selects columns, transforms them, then outputs are concatenated. **Verify:** Inspect `get_feature_names_out()` and transformed shape; map every output column back to its numeric or categorical branch in the declared order.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the reproducible feature transformations without information leakage model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Stateless arithmetic/date extraction can be a small function transformer; learned preprocessing belongs in fitted pipeline objects.

**Edge case:** Unseen categories, missing values, zero variance, target/time leakage, sparse/dense memory growth, and feature-name drift require tests.

**Solution evidence to inspect:** Inspect `get_feature_names_out()` and transformed shape; map every output column back to its numeric or categorical branch in the declared order.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Add deterministic date features (weekday and month) without retaining the original target or post-outcome timestamp. **Progressive hint:** Validate timezone and the moment at which a feature becomes known. **Verify:** Assert weekday/month values for known timestamps and prove target/post-outcome columns are absent from the transformed feature names.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies reproducible feature transformations without information leakage.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Stateless arithmetic/date extraction can be a small function transformer; learned preprocessing belongs in fitted pipeline objects.

**Edge case:** Unseen categories, missing values, zero variance, target/time leakage, sparse/dense memory growth, and feature-name drift require tests.

**Solution evidence to inspect:** Assert weekday/month values for known timestamps and prove target/post-outcome columns are absent from the transformed feature names.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair a pipeline that scales one-hot indicator columns unnecessarily and fails on an unseen category. **Progressive hint:** Use separate branches and `handle_unknown='ignore'`. **Verify:** Pass an unseen category through the repaired pipeline and assert no failure, expected output shape, and no scaling step applied to one-hot columns.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in reproducible feature transformations without information leakage.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Stateless arithmetic/date extraction can be a small function transformer; learned preprocessing belongs in fitted pipeline objects.

**Edge case:** Unseen categories, missing values, zero variance, target/time leakage, sparse/dense memory growth, and feature-name drift require tests.

**Solution evidence to inspect:** Pass an unseen category through the repaired pipeline and assert no failure, expected output shape, and no scaling step applied to one-hot columns.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Handle a zero-variance numeric feature, unseen category, and missing value at inference; define tests for each. **Progressive hint:** The fitted pipeline—not ad hoc notebook code—owns these policies. **Verify:** Run three inference fixtures—zero variance, unseen category, missing value—through the same fitted pipeline and assert each documented result.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from reproducible feature transformations without information leakage.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Stateless arithmetic/date extraction can be a small function transformer; learned preprocessing belongs in fitted pipeline objects.

**Edge case:** Unseen categories, missing values, zero variance, target/time leakage, sparse/dense memory growth, and feature-name drift require tests.

**Solution evidence to inspect:** Run three inference fixtures—zero variance, unseen category, missing value—through the same fitted pipeline and assert each documented result.
<!-- END BEGINNER SOLUTION REVIEW -->

We add a binned fare feature, compare scaling vs no scaling, and adjust the sklearn pipeline accordingly.

Contents
- Exercise 1: Binned fare feature
- Exercise 2: Compare scaling vs not scaling

---

Exercise 1 — Add binned fare
```python
import pandas as pd, seaborn as sns
from sklearn.preprocessing import OneHotEncoder, StandardScaler, KBinsDiscretizer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Data
df = sns.load_dataset('titanic').dropna(subset=['sex','class','fare','survived'])
X = df[['sex','class','fare']]
y = df['survived']

# Add fare_binned as a feature via discretizer
pre = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore'), ['sex','class']),
    ('num', StandardScaler(), ['fare']),
    ('bin', KBinsDiscretizer(n_bins=5, encode='onehot-dense', strategy='quantile'), ['fare'])
])

pipe = Pipeline([('pre', pre), ('clf', LogisticRegression(max_iter=1000))])
pipe.fit(X,y)
acc = pipe.score(X,y)
print({'accuracy_with_bins': acc})
```

Exercise 2 — Compare with/without scaling
```python
pre_noscale = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore'), ['sex','class']),
    ('num', 'passthrough', ['fare'])
])

pipe_noscale = Pipeline([('pre', pre_noscale), ('clf', LogisticRegression(max_iter=1000))])
pipe_noscale.fit(X,y)
print({'accuracy_no_scale': pipe_noscale.score(X,y)})
```
Notes
- Scaling helps linear models when numeric ranges differ significantly
- Binning can capture non-linearities; evaluate via CV, not just resubstitution accuracy

---

## Expanded mastery lab solutions

Fit learned transformations only on training data and keep every feature inside a reproducible pipeline with explicit unknown/missing behavior.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Fit only on training data

Scaling and encoding learn parameters. Fitting before the split lets evaluation
rows influence those parameters. `ColumnTransformer` runs branches in declared
order and concatenates their feature matrices.

### Practices 3–5 — Deterministic date features and robust preprocessing

```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def add_calendar_features(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    """Return a copy with UTC weekday/month derived from an available timestamp."""

    result = frame.copy()
    timestamps = pd.to_datetime(result[column], errors="coerce", utc=True)
    result[f"{column}_weekday"] = timestamps.dt.weekday.astype("Int64")
    result[f"{column}_month"] = timestamps.dt.month.astype("Int64")
    return result.drop(columns=[column])


numeric_pipeline = Pipeline(
    [
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ]
)
categorical_pipeline = Pipeline(
    [
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore")),
    ]
)
preprocessor = ColumnTransformer(
    [
        ("numeric", numeric_pipeline, ["age", "fare"]),
        ("category", categorical_pipeline, ["port"]),
    ]
)

train = pd.DataFrame({"age": [20.0, None, 40.0], "fare": [5.0, 10.0, 15.0], "port": ["A", "B", "A"]})
test = pd.DataFrame({"age": [30.0], "fare": [10.0], "port": ["NEW"]})
preprocessor.fit(train)              # Evaluation data does not influence parameters.
transformed = preprocessor.transform(test)
assert transformed.shape[0] == 1
```

StandardScaler safely maps a training-set constant feature to zeros; the
imputers and encoder make missing and unseen-value behavior part of the fitted,
testable artifact.
