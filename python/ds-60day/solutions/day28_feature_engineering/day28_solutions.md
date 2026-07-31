# Day 28 — Solutions: Feature Engineering

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **reproducible feature transformations without information leakage**. Predict each named
result before comparing your attempt with its matching assertions.

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

### How to compare an answer

For this lesson's **reproducible feature transformations without information leakage** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–2 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Add a fare-bin feature using a transformer inside the preprocessing pipeline. **Contract:** thresholds are learned or fixed without evaluation data, bin closure/labels are documented, and missing/out-of-range behavior is defined. **Verify:** inspect fitted thresholds/feature names and test exact boundaries plus one missing value.

**Reasoning:** Implement this exact contract as written: Add a fare-bin feature using a transformer inside the preprocessing pipeline. Contract: thresholds are learned or fixed without evaluation data, bin closure/labels are documented, and missing/out-of-range behavior is defined. Keep the prompt's named data and constraints visible in the code, then establish this specific result: inspect fitted thresholds/feature names and test exact boundaries plus one missing value. That connects the answer to reproducible feature transformations without information leakage.

```python
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline


class FareBinner(BaseEstimator, TransformerMixin):
    def __init__(self, bins: tuple[float, ...] = (0, 10, 25, np.inf)):
        self.bins = bins

    def fit(self, values, target=None):
        self.feature_names_in_ = np.asarray(["fare"])
        return self

    def transform(self, values):
        series = pd.Series(np.asarray(values).ravel())
        return pd.cut(
            series,
            bins=self.bins,
            labels=["low", "medium", "high"],
            include_lowest=True,
        ).astype("string").to_numpy().reshape(-1, 1)

    def get_feature_names_out(self, input_features=None):
        return np.asarray(["fare_band"])

preprocessing = Pipeline([("fare_bins", FareBinner())])
transformed = preprocessing.fit_transform(
    [[0], [10], [25], [100], [np.nan], [-1]]
).ravel().tolist()
assert transformed[:4] == ["low", "low", "medium", "high"]
assert pd.isna(transformed[4]) and pd.isna(transformed[5])
fitted_binner = preprocessing.named_steps["fare_bins"]
assert fitted_binner.bins == (0, 10, 25, np.inf)
assert fitted_binner.get_feature_names_out().tolist() == ["fare_band"]
```

`pd.cut` is right-closed here: `0` and `10` are `low`, `25` is
`medium`, and values above `25` are `high`. Missing or below-zero fares
remain missing instead of being silently assigned a misleading band.

**Verification evidence:** inspect fitted thresholds/feature names and test exact boundaries plus one missing value.

### Exercise 2 — worked answer

**Learner contract:** Compare one model pipeline with scaling against the same model pipeline without scaling. **Constraints:** keep split/folds, random state, features, model, and all other transforms identical; fit both only on training data. **Expected behavior:** report held-out or cross-validated scores with uncertainty, not training score. **Verify:** report both score estimates, uncertainty intervals, and their difference; compare that difference with a stated practical threshold and connect the result to the model family's sensitivity to feature scale.

**Reasoning:** Implement this exact contract as written: Compare one model pipeline with scaling against the same model pipeline without scaling. Constraints: keep split/folds, random state, features, model, and all other transforms identical; fit both only on training data. Expected behavior: report held-out or cross-validated scores with uncertainty, not training score. Keep the prompt's named data and constraints visible in the code, then establish this specific result: report both score estimates, uncertainty intervals, and their difference; compare that difference with a stated practical threshold and connect the result to the model family's sensitivity to feature scale. That connects the answer to reproducible feature transformations without information leakage.

```python
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = make_classification(
    n_samples=180,
    n_features=6,
    n_informative=4,
    class_sep=0.8,
    random_state=42,
)
folds = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
plain = LogisticRegression(max_iter=1_000)
scaled = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1_000))
plain_scores = cross_val_score(plain, X, y, cv=folds)
scaled_scores = cross_val_score(scaled, X, y, cv=folds)
assert plain_scores.shape == scaled_scores.shape == (3,)
difference = scaled_scores.mean() - plain_scores.mean()
uncertainty = max(plain_scores.std(), scaled_scores.std())
conclusion = (
    "difference exceeds one observed fold standard deviation"
    if abs(difference) > uncertainty
    else "difference is small relative to fold variation"
)
assert conclusion
```

Scaling changes feature units, which can matter to a regularized
distance-sensitive linear model. The conclusion deliberately compares
the mean difference with observed fold variation instead of claiming
that a tiny score change is universally important.

**Verification evidence:** report both score estimates, uncertainty intervals, and their difference; compare that difference with a stated practical threshold and connect the result to the model family's sensitivity to feature scale.

## Exercises 3–7 — Expanded mastery answers

### Exercise 3 — answer contract

**Learner contract:** **Prediction:** Predict how fitting a scaler or category encoder before the train/test split leaks information from evaluation data. **Progressive hint:** Learned means, scales, and categories become evaluation-derived parameters. **Verify:** Fit both ways on a fixture with an extreme held-out value; record differing learned parameters and assert the pipeline fit uses training rows only.

**Reasoning:** Predict this named state change before running it: Prediction: Predict how fitting a scaler or category encoder before the train/test split leaks information from evaluation data. Progressive hint: Learned means, scales, and categories become evaluation-derived parameters. Then compare the prediction with this proof target: Fit both ways on a fixture with an extreme held-out value; record differing learned parameters and assert the pipeline fit uses training rows only. This makes reproducible feature transformations without information leakage observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Fit both ways on a fixture with an extreme held-out value; record differing learned parameters and assert the pipeline fit uses training rows only.

### Exercise 4 — answer contract

**Learner contract:** **Tracing:** Trace numeric and categorical columns through a `ColumnTransformer` and state the output order/shape. **Progressive hint:** Each branch selects columns, transforms them, then outputs are concatenated. **Verify:** Inspect `get_feature_names_out()` and transformed shape; map every output column back to its numeric or categorical branch in the declared order.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace numeric and categorical columns through a `ColumnTransformer` and state the output order/shape. Progressive hint: Each branch selects columns, transforms them, then outputs are concatenated. Record the named value, shape, label, or iterator position needed to establish: Inspect `get_feature_names_out()` and transformed shape; map every output column back to its numeric or categorical branch in the declared order. The trace exposes reproducible feature transformations without information leakage directly.

**Evidence to locate in the grouped implementation:** Inspect `get_feature_names_out()` and transformed shape; map every output column back to its numeric or categorical branch in the declared order.

### Exercise 5 — answer contract

**Learner contract:** **Implementation:** Add deterministic date features (weekday and month) without retaining the original target or post-outcome timestamp. **Progressive hint:** Validate timezone and the moment at which a feature becomes known. **Verify:** Assert weekday/month values for known timestamps and prove target/post-outcome columns are absent from the transformed feature names.

**Reasoning:** Implement this exact contract as written: Implementation: Add deterministic date features (weekday and month) without retaining the original target or post-outcome timestamp. Progressive hint: Validate timezone and the moment at which a feature becomes known. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert weekday/month values for known timestamps and prove target/post-outcome columns are absent from the transformed feature names. That connects the answer to reproducible feature transformations without information leakage.

**Evidence to locate in the grouped implementation:** Assert weekday/month values for known timestamps and prove target/post-outcome columns are absent from the transformed feature names.

### Exercise 6 — answer contract

**Learner contract:** **Debugging:** Repair a pipeline that scales one-hot indicator columns unnecessarily and fails on an unseen category. **Progressive hint:** Use separate branches and `handle_unknown='ignore'`. **Verify:** Pass an unseen category through the repaired pipeline and assert no failure, expected output shape, and no scaling step applied to one-hot columns.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair a pipeline that scales one-hot indicator columns unnecessarily and fails on an unseen category. Progressive hint: Use separate branches and `handle_unknown='ignore'`. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Pass an unseen category through the repaired pipeline and assert no failure, expected output shape, and no scaling step applied to one-hot columns. The diagnosis depends on reproducible feature transformations without information leakage.

**Evidence to locate in the grouped implementation:** Pass an unseen category through the repaired pipeline and assert no failure, expected output shape, and no scaling step applied to one-hot columns.

### Exercise 7 — answer contract

**Learner contract:** **Edge case and explanation:** Handle a zero-variance numeric feature, unseen category, and missing value at inference; define tests for each. **Progressive hint:** The fitted pipeline—not ad hoc notebook code—owns these policies. **Verify:** Run three inference fixtures—zero variance, unseen category, missing value—through the same fitted pipeline and assert each documented result.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Handle a zero-variance numeric feature, unseen category, and missing value at inference; define tests for each. Progressive hint: The fitted pipeline—not ad hoc notebook code—owns these policies. Values below, at, and above the named boundary must produce the evidence Run three inference fixtures—zero variance, unseen category, missing value—through the same fitted pipeline and assert each documented result. Those cases show how reproducible feature transformations without information leakage behaves at its edge.

**Evidence to locate in the grouped implementation:** Run three inference fixtures—zero variance, unseen category, missing value—through the same fitted pipeline and assert each documented result.

## Expanded mastery lab solutions

Fit learned transformations only on training data and keep every feature inside a reproducible pipeline with explicit unknown/missing behavior.

### Shared implementation for Exercises 3–4 — Fit only on training data

Scaling and encoding learn parameters. Fitting before the split lets evaluation
rows influence those parameters. `ColumnTransformer` runs branches in declared
order and concatenates their feature matrices.

### Shared implementation for Exercises 5–7 — Deterministic date features and robust preprocessing

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
