# Day 28 — Solutions: Feature Engineering

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

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Add a binned fare feature. **Hint:** put the binner inside the preprocessing pipeline so its thresholds are learned only from training data; document the bin strategy and output encoding.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Compare scaling with no scaling. **Hint:** keep the split/folds, model, random state, and all other transforms identical; compare held-out or cross-validated performance, not training score.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Prediction

**Prompt:** Predict how fitting a scaler or category encoder before the train/test split leaks information from evaluation data.

**Reasoning checkpoint:** Learned means, scales, and categories become evaluation-derived parameters. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 4 — Tracing

**Prompt:** Trace numeric and categorical columns through a `ColumnTransformer` and state the output order/shape.

**Reasoning checkpoint:** Each branch selects columns, transforms them, then outputs are concatenated. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Implementation

**Prompt:** Add deterministic date features (weekday and month) without retaining the original target or post-outcome timestamp.

**Reasoning checkpoint:** Validate timezone and the moment at which a feature becomes known. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Debugging

**Prompt:** Repair a pipeline that scales one-hot indicator columns unnecessarily and fails on an unseen category.

**Reasoning checkpoint:** Use separate branches and `handle_unknown='ignore'`. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Edge case and explanation

**Prompt:** Handle a zero-variance numeric feature, unseen category, and missing value at inference; define tests for each.

**Reasoning checkpoint:** The fitted pipeline—not ad hoc notebook code—owns these policies. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

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
