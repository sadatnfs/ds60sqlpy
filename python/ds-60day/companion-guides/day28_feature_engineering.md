# Day 28 — Feature Engineering with scikit-learn

**Level:** Intermediate

Feature engineering turns raw columns into model inputs. Any transformation
that learns from data must be fit on training data only and reused unchanged on
validation/test data.

## Learning objectives

By the end of this lesson, you can:

- distinguish learned transforms from fixed row-wise transforms;
- encode categorical fields while handling unseen categories;
- scale, bin, and add missingness indicators;
- route column groups with `ColumnTransformer`;
- compare feature choices inside a reproducible `Pipeline`.

## Prerequisites

Complete Day 27 (`python-27`), pandas preprocessing (`python-18`), and data
validation concepts from prior lessons. scikit-learn is in the `data` group.

## Vocabulary and mental model

- **Feature:** model input derived from raw data.
- **Fit:** learn parameters such as means, scales, bins, or categories.
- **Transform:** apply already learned parameters.
- **One-hot encoding:** one indicator column per learned category.
- **Scaling:** recenter/rescale numeric features.
- **Binning:** map continuous values to intervals.
- **Leakage:** training uses information unavailable at prediction time.
- **Pipeline:** ordered estimators sharing fit/transform lifecycle.

## Worked example

```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

train = pd.DataFrame(
    {"city": ["SF", "NY", "SF"], "age": [20.0, 40.0, 30.0]}
)
preprocessor = ColumnTransformer(
    [
        ("category", OneHotEncoder(handle_unknown="ignore"), ["city"]),
        ("number", StandardScaler(), ["age"]),
    ]
)
transformed = preprocessor.fit_transform(train)
```

In real evaluation, `fit_transform` belongs on training data; validation/test
data receives only `transform`.

## Dataset note

The notebook uses Seaborn's Titanic sample, with the same first-use cache
behavior as earlier lessons. A constructed DataFrame keeps practice offline.

## Exercises and progressive hints

1. Add a binned fare feature. **Hint:** put the binner inside the preprocessing
   pipeline so its thresholds are learned only from training data; document the
   bin strategy and output encoding.
2. Compare scaling with no scaling. **Hint:** keep the split/folds, model,
   random state, and all other transforms identical; compare held-out or
   cross-validated performance, not training score.

### Additional mastery practice

Fit learned transformations only on training data and keep every feature inside a reproducible pipeline with explicit unknown/missing behavior.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict how fitting a scaler or category encoder before the train/test split leaks information from evaluation data.
   **Progressive hint:** Learned means, scales, and categories become evaluation-derived parameters.
4. **Tracing:** Trace numeric and categorical columns through a `ColumnTransformer` and state the output order/shape.
   **Progressive hint:** Each branch selects columns, transforms them, then outputs are concatenated.
5. **Implementation:** Add deterministic date features (weekday and month) without retaining the original target or post-outcome timestamp.
   **Progressive hint:** Validate timezone and the moment at which a feature becomes known.
6. **Debugging:** Repair a pipeline that scales one-hot indicator columns unnecessarily and fails on an unseen category.
   **Progressive hint:** Use separate branches and `handle_unknown='ignore'`.
7. **Edge case and explanation:** Handle a zero-variance numeric feature, unseen category, and missing value at inference; define tests for each.
   **Progressive hint:** The fitted pipeline—not ad hoc notebook code—owns these policies.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.


## Self-check

- Which preprocessing steps learn parameters from data?
- Why must categories and scale values be learned on training data only?
- What should happen when inference contains an unseen category?
- Why might scaling affect one model family more than another?

Expected behavior: the pipeline accepts raw columns, handles an unseen
category, and compares alternatives on the same evaluation data.

## Common pitfalls and diagnosis

- **Preprocessing happens before the split:** move learned steps into a pipeline
  fit only on training folds.
- **Inference rejects a new category:** configure the encoder's unknown-category
  policy and test it.
- **Feature matrices unexpectedly become dense:** inspect sparse/dense output
  before converting; dense one-hot data can consume large memory.
- **A bin edge changes between train/test:** reuse the fitted transformer,
  never fit again on test data.
- **Training accuracy is presented as evidence:** use held-out evaluation or
  cross-validation and report uncertainty/limitations.

## Continue

- [Open the learner notebook](../notebooks/day28_feature_engineering.ipynb)
- [Check the separate solution](../solutions/day28_feature_engineering/day28_solutions.md)
- [Next: Day 29 — Data validation schemas](day29_data_validation_schemas.md)
