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

<!-- BEGIN HOW TO RUN -->
## How to run this lesson

Work from the repository root. The rendered HTML lesson is a readable
preview; execute the real notebook in VS Code or JupyterLab.

1. Confirm the course environment before changing it:

   ```powershell
   # Windows PowerShell
   $CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
       (Resolve-Path .\.venv\Scripts\python.exe).Path
   } else {
       (Resolve-Path .\.venv\python.exe).Path
   }
   & $CoursePython scripts\course.py doctor
   ```

   ```bash
   # macOS/Linux
   .venv/bin/python scripts/course.py doctor
   ```

2. Read `python/ds-60day/companion-guides/day28_feature_engineering.md`, then open `python/ds-60day/notebooks/day28_feature_engineering.ipynb` from the repository
   folder in VS Code or JupyterLab.
3. Select **Python (ds60sqlpy)**. Do not run `%pip` in the notebook. If
   an import is missing, use the doctor and the catalog dependency label
   to repair the shared environment.
4. Restart the kernel and run from the first cell downward. Before every
   example, write a prediction; after it runs, compare the actual value,
   type, shape, or side effect with the stated observation.
5. Attempt each numbered exercise in its own work cell. Use the explicit
   verification as part of the task. Keep `solutions/` closed until you
   have a tested attempt or deliberately ask for help.

**Lesson outcome:** use day 28 — feature engineering with scikit-learn to practice reproducible feature transformations without information leakage
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

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

### Vocabulary in plain language

- **feature:** an input value available to a model at prediction time.
- **transformer:** an object that fits parameters and transforms data.
- **fit:** learn transformation/model parameters from training data.
- **transform:** apply already learned parameters to data.
- **pipeline:** an ordered fitted chain of preprocessing and estimation.
- **leakage:** evaluation or future/target information entering training features.

### Syntax anatomy

A `ColumnTransformer` selects named column groups and runs separate
pipelines, then concatenates their outputs. `Pipeline([...])` fits each
preprocessing step only on the training rows passed to `fit` and passes
the transformed output to the estimator. `handle_unknown="ignore"`
defines inference behavior for categories absent during fit.

### Worked example 1 — Fit scaling on training data only

The held-out value is transformed with training parameters. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
import numpy as np
from sklearn.preprocessing import StandardScaler

train = np.array([[1.0], [2.0], [3.0]])
test = np.array([[10.0]])
scaler = StandardScaler().fit(train)
(scaler.mean_.tolist(), scaler.transform(test).round(2).tolist())
```

**Expected observation**

```text
The training mean is `[2.0]`; the held-out value becomes a large positive standardized value. Test data did not influence the mean.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Handle an unseen category explicitly

The encoder's inference contract belongs inside preprocessing. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
from sklearn.preprocessing import OneHotEncoder

encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
encoder.fit([["red"], ["blue"]])
encoded = encoder.transform([["green"], ["red"]])
(encoder.categories_[0].tolist(), encoded.tolist())
```

**Expected observation**

```text
Known levels are `['blue', 'red']`; unseen `green` becomes all zeros while `red` activates its learned column.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Write when every candidate feature becomes known relative to prediction time.
2. Split before fitting any stateful transformation.
3. Inspect transformed feature names, shape, and output ordering.
4. Test missing values, unseen categories, and zero variance through the fitted pipeline—not ad hoc notebook fixes.

### Practice ramp

Work through the numbered exercises in five modes rather than treating all
of them as blank-code prompts:

1. **Prediction:** state the value, type, shape, rows, or side effect before
   execution.
2. **Guided modification:** change one part of a worked example and explain
   which part of the result must change.
3. **Independent application:** implement the same idea with a new input and
   an explicit contract.
4. **Debugging and edge cases:** reproduce a failure, identify the violated
   assumption, and prove the repair at a boundary.
5. **Retrieval:** close the guide and explain the core model from memory
   before moving on.

**Useful alternative:** Stateless arithmetic/date extraction can be a small function transformer; learned preprocessing belongs in fitted pipeline objects.

**Boundary to remember:** Unseen categories, missing values, zero variance, target/time leakage, sparse/dense memory growth, and feature-name drift require tests.
<!-- END BEGINNER DEEP DIVE -->

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

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Add a fare-bin feature using a transformer inside the preprocessing pipeline. **Contract:** thresholds are learned or fixed without evaluation data, bin closure/labels are documented, and missing/out-of-range behavior is defined.
   **Verify:** inspect fitted thresholds/feature names and test exact boundaries plus one missing value.

2. Compare one model pipeline with scaling against the same model pipeline without scaling. **Constraints:** keep split/folds, random state, features, model, and all other transforms identical; fit both only on training data.
   **Expected behavior:** report held-out or cross-validated scores with uncertainty, not training score.
   **Verify:** report both score estimates, uncertainty intervals, and their difference; compare that difference with a stated practical threshold and connect the result to the model family's sensitivity to feature scale.

### Additional mastery practice

Fit learned transformations only on training data and keep every feature inside a reproducible pipeline with explicit unknown/missing behavior.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict how fitting a scaler or category encoder before the train/test split leaks information from evaluation data.
   **Progressive hint:** Learned means, scales, and categories become evaluation-derived parameters.
   **Verify:** Fit both ways on a fixture with an extreme held-out value; record differing learned parameters and assert the pipeline fit uses training rows only.
4. **Tracing:** Trace numeric and categorical columns through a `ColumnTransformer` and state the output order/shape.
   **Progressive hint:** Each branch selects columns, transforms them, then outputs are concatenated.
   **Verify:** Inspect `get_feature_names_out()` and transformed shape; map every output column back to its numeric or categorical branch in the declared order.
5. **Implementation:** Add deterministic date features (weekday and month) without retaining the original target or post-outcome timestamp.
   **Progressive hint:** Validate timezone and the moment at which a feature becomes known.
   **Verify:** Assert weekday/month values for known timestamps and prove target/post-outcome columns are absent from the transformed feature names.
6. **Debugging:** Repair a pipeline that scales one-hot indicator columns unnecessarily and fails on an unseen category.
   **Progressive hint:** Use separate branches and `handle_unknown='ignore'`.
   **Verify:** Pass an unseen category through the repaired pipeline and assert no failure, expected output shape, and no scaling step applied to one-hot columns.
7. **Edge case and explanation:** Handle a zero-variance numeric feature, unseen category, and missing value at inference; define tests for each.
   **Progressive hint:** The fitted pipeline—not ad hoc notebook code—owns these policies.
   **Verify:** Run three inference fixtures—zero variance, unseen category, missing value—through the same fitted pipeline and assert each documented result.

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

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-28`
(Day 28 — Feature Engineering with scikit-learn). Direct catalog prerequisites: `python-27`.
I have completed the direct prerequisites: `python-27`. Emphasize reproducible feature transformations without information leakage.
Read `python/ds-60day/companion-guides/day28_feature_engineering.md` and use the learner notebook
`python/ds-60day/notebooks/day28_feature_engineering.ipynb`. Do not open or quote anything under `solutions/` unless
I explicitly ask after making an honest attempt. Use these visible phases:
Explain, Predict, Attempt, Hint, Evidence, and Retrieval. First explain one
concept in plain language, then ask me to predict a small example and wait
for my attempt. Give only one progressive hint at a time. Help me run or
inspect my actual notebook evidence, adapt commands to my operating system,
and do not treat the rendered HTML preview as executable. Finish with 2-3
retrieval questions and one next step. Done when I can explain the mental
model without the guide, complete one independent exercise, and show the
prompt's verification evidence from my notebook.
```
