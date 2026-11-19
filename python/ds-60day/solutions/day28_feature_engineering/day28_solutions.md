# Day 28 Solutions: Feature Engineering with scikit-learn

**Offline teaching data:** The [original synthetic fixtures](../../../fixtures/README.md) replace first-run sample-data downloads. Their values are not historical or observational evidence. Keep numerical conclusions scoped to the declared teaching input.


<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **reproducible feature transformations without information leakage**. Predict each named
result before comparing your attempt with its matching assertions.

A feature is a model input available at the moment a prediction would be
made. Feature engineering changes representation to expose useful
structure: scaling numbers, encoding categories, extracting dates,
binning, or combining fields. It must preserve the time/knowledge
boundary, post-outcome data and target-derived values are leakage.

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

## Exercises 1-2: Worked answers

### Exercise 1: worked answer

**Learner contract:** Add a fare-bin feature using a transformer inside the preprocessing pipeline. **Contract:** thresholds are learned or fixed without evaluation data, bin closure/labels are documented, and missing/out-of-range behavior is defined. **Verify:** inspect fitted thresholds/feature names and test exact boundaries plus one missing value.

**Reasoning:** Putting the binning inside a transformer means the same rule runs during training, evaluation, and inference, and the thresholds `(0, 10, 25, inf)` are fixed in advance, so no evaluation data can influence them. `pd.cut` uses right-closed bins, `(0, 10]`, `(10, 25]`, and `(25, inf)`, and `include_lowest=True` also puts exactly 0 into the first bin, which is why 0 and 10 are `low` and 25 is `medium`. Values outside every bin, such as -1, and missing values both become missing, which the boundary tests check explicitly together with the fitted feature name, `fare_band`.

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
        return (
            pd.cut(
                series,
                bins=self.bins,
                labels=["low", "medium", "high"],
                include_lowest=True,
            )
            .astype("string")
            .to_numpy()
            .reshape(-1, 1)
        )

    def get_feature_names_out(self, input_features=None):
        return np.asarray(["fare_band"])


preprocessing = Pipeline([("fare_bins", FareBinner())])
transformed = preprocessing.fit_transform([[0], [10], [25], [100], [np.nan], [-1]]).ravel().tolist()
assert transformed[:4] == ["low", "low", "medium", "high"]
assert pd.isna(transformed[4]) and pd.isna(transformed[5])
fitted_binner = preprocessing.named_steps["fare_bins"]
assert fitted_binner.bins == (0, 10, 25, np.inf)
assert fitted_binner.get_feature_names_out().tolist() == ["fare_band"]
```

`pd.cut` is right-closed here: `0` and `10` are `low`, `25` is
`medium`, and values above `25` are `high`. Missing or below-zero fares
remain missing instead of being silently assigned a misleading band.

### Exercise 2: worked answer

**Learner contract:** Compare one model pipeline with scaling against the same model pipeline without scaling. **Constraints:** keep split/folds, random state, features, model, and all other transforms identical; fit both only on training data. **Expected behavior:** report held-out or cross-validated scores with uncertainty, not training score. **Verify:** report both score estimates, uncertainty intervals, and their difference; compare that difference with a stated practical threshold and connect the result to the model family's sensitivity to feature scale.

**Reasoning:** A fair comparison changes exactly one thing: both pipelines use the same folds, data, model, and settings, so any score difference comes from scaling alone. Here the difference is 0.0 because every generated feature already has a standard deviation between about 1 and 1.7, so scaling barely changes the problem; the report gives each mean with a rough two-standard-error interval and compares the difference with a stated practical threshold of 0.02. Regularized logistic regression is sensitive to units because the penalty acts on coefficient size: a feature measured in tiny units needs a large coefficient and is suppressed, which the extra check with one shrunken feature shows.

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

import numpy as np

practical_threshold = 0.02  # smallest accuracy change worth acting on here


def interval(scores: np.ndarray) -> tuple[float, float]:
    """Mean plus or minus two standard errors across folds (a rough interval)."""
    half_width = 2 * scores.std(ddof=1) / np.sqrt(len(scores))
    return round(scores.mean() - half_width, 3), round(scores.mean() + half_width, 3)


report = {
    "plain": (round(plain_scores.mean(), 3), interval(plain_scores)),
    "scaled": (round(scaled_scores.mean(), 3), interval(scaled_scores)),
    "difference": round(difference, 3),
    "practically_important": abs(difference) >= practical_threshold,
    "conclusion": conclusion,
}
print(report)

# Regularization penalizes coefficient size, so a feature in tiny units is suppressed.
shrunk = X.copy()
shrunk[:, 0] *= 0.001
shrunk_gap = (
    cross_val_score(scaled, shrunk, y, cv=folds).mean()
    - cross_val_score(plain, shrunk, y, cv=folds).mean()
)
print("scaled minus plain after shrinking feature 0:", round(shrunk_gap, 3))
```

Scaling changes feature units, which can matter to a regularized
distance-sensitive linear model. The conclusion deliberately compares
the mean difference with observed fold variation instead of claiming
that a tiny score change is universally important.

## Exercises 3-7: Expanded mastery answers

### Exercise 3: answer contract

**Learner contract:** **Prediction:** Predict how fitting a scaler or category encoder before the train/test split leaks information from evaluation data. **Progressive hint:** Learned means, scales, and categories become evaluation-derived parameters. **Verify:** Fit both ways on a fixture with an extreme held-out value; record differing learned parameters and assert the pipeline fit uses training rows only.

**Reasoning:** A scaler learns a mean and a standard deviation, and an encoder learns a list of categories, so fitting either on all rows lets evaluation data shape the transformation that is then evaluated. In the shared implementation for Exercises 3-4, the held-out fare of 500 moves the learned mean from 11.0 to 92.5, and the held-out port `C` becomes a known category. Fitting only on the training rows keeps those parameters free of evaluation data, and `handle_unknown="ignore"` deals with categories seen for the first time at evaluation.

### Exercise 4: answer contract

**Learner contract:** **Tracing:** Trace numeric and categorical columns through a `ColumnTransformer` and state the output order/shape. **Progressive hint:** Each branch selects columns, transforms them, then outputs are concatenated. **Verify:** Inspect `get_feature_names_out()` and transformed shape; map every output column back to its numeric or categorical branch in the declared order.

**Reasoning:** A `ColumnTransformer` sends each listed column set to its own branch, transforms it, and concatenates the outputs in the order the branches are declared. With two numeric columns and a port column with three categories, the output has 2 + 3 = 5 columns, and `get_feature_names_out()` prefixes every name with its branch, so `numeric__age` comes from the numeric branch and `category__port_A` from the categorical one. The shared implementation for Exercises 3-4 asserts the names, the shape, and the branch of every output column.

### Exercise 5: answer contract

**Learner contract:** **Implementation:** Add deterministic date features (weekday and month) without retaining the original target or post-outcome timestamp. **Progressive hint:** Validate timezone and the moment at which a feature becomes known. **Verify:** Assert weekday/month values for known timestamps and prove target/post-outcome columns are absent from the transformed feature names.

**Reasoning:** Weekday and month are safe features only if they come from a timestamp known when the prediction is made, so the reference parses it as UTC to avoid local-time ambiguity and drops the original column after deriving the features. The target and any timestamp recorded after the outcome are removed before feature creation, because using them would leak the answer into the inputs. The shared implementation for Exercises 5-7 checks known values, 6 January 2025 is a Monday (0) and 14 February 2025 a Friday (4), and asserts that the target and post-outcome columns are absent from the features.

### Exercise 6: answer contract

**Learner contract:** **Debugging:** Repair a pipeline that scales one-hot indicator columns unnecessarily and fails on an unseen category. **Progressive hint:** Use separate branches and `handle_unknown='ignore'`. **Verify:** Pass an unseen category through the repaired pipeline and assert no failure, expected output shape, and no scaling step applied to one-hot columns.

**Reasoning:** One-hot indicators are already 0 or 1, so scaling them only makes them harder to read, and an encoder with the default `handle_unknown="error"` stops at the first category it has not seen. The repair gives numeric and categorical columns separate branches, scaling only the numeric one, and sets `handle_unknown="ignore"`, so an unseen port becomes a row of zeros. The shared implementation for Exercises 5-7 reproduces the old failure, then asserts that the repaired pipeline returns one row with four columns, that the unseen port produces zeros, and that the categorical branch contains no scaler.

### Exercise 7: answer contract

**Learner contract:** **Edge case and explanation:** Handle a zero-variance numeric feature, unseen category, and missing value at inference; define tests for each. **Progressive hint:** The fitted pipeline, not ad hoc notebook code, owns these policies. **Verify:** Run three inference fixtures, zero variance, unseen category, missing value, through the same fitted pipeline and assert each documented result.

**Reasoning:** Each inference edge case is handled by a fitted step, not by ad hoc notebook code: `StandardScaler` maps a feature that was constant in training to 0 instead of dividing by zero, the encoder ignores unseen categories, and the imputer fills a missing age with the training median. The shared implementation for Exercises 5-7 fits the pipeline once on data with a constant fare and passes the three fixtures through the same fitted object, asserting the documented output for each.

## Expanded mastery lab solutions

Fit learned transformations only on training data and keep every feature inside a reproducible pipeline with explicit unknown/missing behavior.

### Shared implementation for Exercises 3-4: Fit only on training data

Scaling and encoding learn parameters. Fitting before the split lets evaluation
rows influence those parameters. `ColumnTransformer` runs branches in declared
order and concatenates their feature matrices.

```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

fares = pd.DataFrame({"fare": [10.0, 12.0, 11.0, 13.0, 9.0, 500.0]})
train_fares, held_out_fares = fares.iloc[:5], fares.iloc[5:]  # 500 is held out
leaky_scaler = StandardScaler().fit(fares)  # fitted before the split
honest_scaler = StandardScaler().fit(train_fares)  # training rows only
print({"leaky_mean": leaky_scaler.mean_[0], "honest_mean": honest_scaler.mean_[0]})
assert honest_scaler.mean_[0] == train_fares["fare"].mean() == 11.0
assert leaky_scaler.mean_[0] == 92.5  # the held-out 500 shaped the parameter

ports = pd.DataFrame({"port": ["A", "B", "A", "C"]})
leaky_encoder = OneHotEncoder().fit(ports)
honest_encoder = OneHotEncoder(handle_unknown="ignore").fit(ports.iloc[:3])
assert leaky_encoder.categories_[0].tolist() == ["A", "B", "C"]  # learned from evaluation
assert honest_encoder.categories_[0].tolist() == ["A", "B"]

frame = pd.DataFrame(
    {"age": [20.0, 40.0, 30.0], "fare": [5.0, 15.0, 10.0], "port": ["A", "B", "C"]}
)
columns = ColumnTransformer(
    [
        ("numeric", StandardScaler(), ["age", "fare"]),
        ("category", OneHotEncoder(), ["port"]),
    ]
)
output = columns.fit_transform(frame)
names = columns.get_feature_names_out().tolist()
print(names)
assert output.shape == (3, 5)
assert [name.split("__")[0] for name in names] == ["numeric"] * 2 + ["category"] * 3
```

### Shared implementation for Exercises 5-7: Deterministic date features and robust preprocessing

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

train = pd.DataFrame(
    {"age": [20.0, None, 40.0], "fare": [5.0, 10.0, 15.0], "port": ["A", "B", "A"]}
)
test = pd.DataFrame({"age": [30.0], "fare": [10.0], "port": ["NEW"]})
preprocessor.fit(train)  # Evaluation data does not influence parameters.
transformed = preprocessor.transform(test)
assert transformed.shape[0] == 1

events = pd.DataFrame(
    {
        "booked_at": ["2025-01-06T10:00:00Z", "2025-02-14T23:30:00Z"],
        "fare": [10.0, 20.0],
        "target": [1, 0],
        "outcome_recorded_at": ["2025-01-20", None],  # known only after the outcome
    }
)
features = add_calendar_features(
    events.drop(columns=["target", "outcome_recorded_at"]), "booked_at"
)
assert features["booked_at_weekday"].tolist() == [0, 4]  # Monday, Friday
assert features["booked_at_month"].tolist() == [1, 2]
assert {"target", "outcome_recorded_at", "booked_at"}.isdisjoint(features.columns)

# The old design scaled one-hot columns and rejected unseen categories.
broken = Pipeline([("encode", OneHotEncoder(sparse_output=False)), ("scale", StandardScaler())])
broken.fit(train[["port"]])
try:
    broken.transform(test[["port"]])
except ValueError as error:
    print("broken:", str(error).splitlines()[0])
else:
    raise AssertionError("an unseen category should break the old pipeline")
assert transformed.shape == (1, 4)
assert transformed[0, 2:].tolist() == [0.0, 0.0]  # unseen port: all indicators zero
assert "scale" not in preprocessor.named_transformers_["category"].named_steps

# Three inference edge cases through one fitted pipeline.
from sklearn.base import clone

fitted = clone(preprocessor).fit(train.assign(fare=7.0))  # fare has zero variance
edge_cases = {
    "zero variance": pd.DataFrame({"age": [30.0], "fare": [7.0], "port": ["A"]}),
    "unseen category": pd.DataFrame({"age": [30.0], "fare": [7.0], "port": ["NEW"]}),
    "missing value": pd.DataFrame({"age": [float("nan")], "fare": [7.0], "port": ["B"]}),
}
results = {name: fitted.transform(row)[0].tolist() for name, row in edge_cases.items()}
print(results)
assert results["zero variance"][1] == 0.0  # constant feature scales to 0, not NaN
assert results["unseen category"][2:] == [0.0, 0.0]
assert results["missing value"][0] == 0.0  # training median imputed, then centered
```

StandardScaler safely maps a training-set constant feature to zeros; the
imputers and encoder make missing and unseen-value behavior part of the fitted,
testable artifact.
