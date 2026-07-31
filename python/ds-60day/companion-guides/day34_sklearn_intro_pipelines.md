# Day 34 — scikit-learn Estimators and Pipelines

**Lesson ID:** `python-34` · **Level:** intermediate · **Dependencies:** `data` · **Network:** offline

scikit-learn uses a deliberately consistent API. Once you understand estimators,
transformers, and pipelines, you can change models without rewriting the whole
evaluation workflow.

## Learning objectives

By the end of the lesson, you can:

- distinguish `fit`, `transform`, `fit_transform`, `predict`, and `score`;
- make a reproducible train/test split;
- combine preprocessing and a model in a `Pipeline`;
- swap `LinearRegression` for `Ridge` without leaking test information; and
- inspect named steps and interpret standardized coefficients cautiously.

## Prerequisites

- Complete `python-33` (linear algebra and matrices).
- Recall train/validation/test roles from `python-30`.
- Be comfortable with keyword arguments and object methods.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Estimator | Object that learns parameters in `fit` |
| Transformer | Estimator that maps data through `transform` |
| Predictor | Estimator that produces outputs through `predict` |
| Pipeline | Ordered chain whose preprocessing and final estimator share one `fit` call |
| Learned parameter | Value estimated from data, such as `mean_` or `coef_` |
| Hyperparameter | Configuration chosen before fitting, such as Ridge `alpha` |
| Data leakage | Information unavailable at prediction time influencing training or evaluation |
| \(R^2\) | Regression score comparing squared error with a mean-target baseline |

Treat a fitted pipeline as the deployable unit. It preserves the exact
preprocessing learned from training data together with the model.

## Worked example: preprocessing stays inside the boundary

```python
from sklearn.datasets import load_diabetes
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_diabetes(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = Pipeline(
    [
        ("scale", StandardScaler()),
        ("ridge", Ridge(alpha=1.0)),
    ]
)
model.fit(X_train, y_train)
print(model.score(X_test, y_test))
```

`StandardScaler.fit` sees only `X_train`. Calling `fit_transform` on the entire
dataset before splitting would leak global means and variances into the test
evaluation.

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 34 learner notebook from this guide's **Next
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

## Concept deep dive — the scikit-learn estimator contract and leakage-safe pipelines

### The mental model

Scikit-learn separates **learning state** from **using learned state**.
`fit` estimates parameters from training data. `transform` applies a
fitted representation, and `predict` applies a fitted predictor.
Attributes ending in an underscore, such as `mean_` or `coef_`, are
commonly learned during fitting.

A `Pipeline` is a single estimator whose fit sequence keeps every
learned preprocessing step inside the training boundary. During
cross-validation, each fold receives a newly fitted pipeline. This
prevents validation data from influencing means, encodings, feature
selection, or other learned state.

### Worked examples and syntax anatomy

- **`Pipeline([('scale', ...), ('model', ...)])`:** names ordered steps so nested parameters and learned attributes remain inspectable.
- **`.fit(X_train, y_train)`:** fits every transformer on training rows, transforms those rows, then fits the final estimator.
- **`.predict(X_new)`:** uses already learned preprocessing and model state; it must not refit on new data.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — prove that the scaler learned only training data

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

X_train = np.array([[0.0], [2.0], [4.0]])
y_train = np.array([0.0, 2.0, 4.0])
X_test = np.array([[100.0]])
pipe = Pipeline([("scale", StandardScaler()), ("model", LinearRegression())])
pipe.fit(X_train, y_train)

learned_mean = pipe.named_steps["scale"].mean_[0]
prediction = pipe.predict(X_test)[0]
print({"training_mean": learned_mean, "prediction": prediction})
assert learned_mean == X_train.mean()
```

**Expected observation:** The scaler mean is `2.0`; the extreme test row never influenced fitted preprocessing.

**Assumption to name:** Train/test membership was decided before any learned transformation.

### Focused example B — handle an unseen category at prediction time

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
import numpy as np
from sklearn.preprocessing import OneHotEncoder

encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
train = np.array([["red"], ["blue"], ["red"]])
encoder.fit(train)
transformed = encoder.transform(np.array([["green"], ["red"]]))
print(encoder.categories_, transformed)
assert transformed.shape == (2, 2)
assert transformed[0].sum() == 0
```

**Expected observation:** The unknown `green` row becomes all zeros instead of crashing or inventing a learned category.

**Assumption to name:** An all-zero encoded unknown has an acceptable, documented meaning for the downstream model.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define the scikit-learn estimator contract and leakage-safe pipelines in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Calling `fit_transform` on the entire dataset before splitting or cross-validation.

**Debug it deliberately:** Inspect every learned underscore attribute and ask which row IDs contributed to it; wrap all learned preprocessing in the pipeline.

**Stop condition:** Do not report evaluation results until the split happened before fitting and the complete feature pipeline was evaluated.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Swap `LinearRegression` for `Ridge` and compare test scores.

**Verify:** For task `Swap LinearRegression for Ridge and compare test scores`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.






2. Inspect the coefficients and discuss how feature scaling changes their
   numeric values and interpretation.

**Verify:** For task `Inspect the coefficients and discuss how feature scaling changes their`, demonstrate the concrete requirement “2. Inspect the coefficients and discuss how feature scaling changes their numeric values and interpretation” with explicit inputs, observable output, and one counterexample.







### Progressive hints

1. Keep the split and scaler fixed; change only the final named step. Start with
   `alpha=1.0`, then record both models rather than declaring a winner from one
   unexplained number.
2. Reach the fitted model through `pipeline.named_steps`. A coefficient from
   standardized inputs represents a one-standard-deviation feature change, but
   correlated features still complicate causal interpretation.

### Additional mastery practice

Make preprocessing and estimation one fitted object. Data boundaries, feature names, and unknown-category behavior are part of the model contract.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

3. **Leakage prediction:** Predict how cross-validation scores can change when a scaler is fit on the complete dataset before `cross_val_score`, then explain why the code still runs without warning.
   **Progressive hint:** The globally fitted mean and scale contain information from each validation fold. A Pipeline refits them using only the fold's training rows.

**Verify:** For task `Leakage prediction: Predict how cross-validation scores can change when a scaler is fit on th...`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.







4. **Mixed-type implementation:** Build a `ColumnTransformer` for numeric imputation/scaling and categorical imputation/one-hot encoding, followed by LogisticRegression. Use a tiny DataFrame containing a missing value.
   **Progressive hint:** Use separate nested pipelines and `handle_unknown='ignore'`; keep column lists explicit so schema drift is visible.

**Verify:** For task `Mixed-type implementation: Build a ColumnTransformer for numeric imputation/scaling and categ...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then record the exact command/input, terminal result or returned value, and repeat the critical check from a clean process or fresh state.







5. **Unknown-category debugging:** Fit on regions `north` and `south`, then predict a row with region `west`. Compare `OneHotEncoder` default behavior with `handle_unknown='ignore'` and explain the resulting representation.
   **Progressive hint:** The default raises on an unseen category. Ignore maps the unknown to all zeros for that feature block, which is operationally safe but lossy.

**Verify:** For task `Unknown-category debugging: Fit on regions north and south, then predict a row with region we...`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.







6. **Inspection and schema contract:** After fitting the mixed-type pipeline, recover transformed feature names, pair them with coefficients, and assert that an inference DataFrame has the required columns in a safe order.
   **Progressive hint:** Use `get_feature_names_out()` from the fitted ColumnTransformer. Select by column name rather than trusting an incoming positional order.

**Verify:** For task `Inspection and schema contract: After fitting the mixed-type pipeline, recover transformed fe...`, report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels; then assert exact names, order, types/nullability or versions and prove one mismatch is rejected rather than silently coerced.






Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.



## Self-check

- Which methods are called on each pipeline step during `fit` and `predict`?
- Why does a fixed `random_state` aid comparison without eliminating sampling
  uncertainty?
- What baseline does a negative test \(R^2\) fail to beat?
- If you save only the final Ridge object, what information is missing?

Expected behavior: both models run from package-bundled data with no network
access. Their test scores may be close; regularization is not guaranteed to win
on one split.

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Diagnostic | Better practice |
|---|---|---|
| Scaling before splitting | Scaler was fit on all rows | Put scaling inside the pipeline |
| Comparing different random splits | Models received different examples | Reuse one split or use controlled cross-validation |
| Reading `score` as universal quality | Metric depends on estimator type | Name and interpret the metric explicitly |
| Interpreting coefficients as causal effects | Observational correlations and collinearity remain | Use domain assumptions and uncertainty analysis |
| Mutating a fitted pipeline while experimenting | Results become hard to reproduce | Build fresh pipelines from explicit configurations |

Pipelines add structure and prevent common mistakes, but they do not choose the
right split, metric, or causal assumptions for you.

## Next step

- Work in the [Day 34 learner notebook](../notebooks/day34_sklearn_intro_pipelines.ipynb).
- Then review the
  [Day 34 solution](../solutions/day34_sklearn_intro_pipelines/day34_solutions.md).
- Continue to [Day 35 — Model Evaluation](day35_model_evaluation_cv.md).

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-34` — Day 34 — scikit-learn Estimators and Pipelines.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize the scikit-learn estimator contract and leakage-safe pipelines. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day34_sklearn_intro_pipelines.md`
- learner artifact: `python/ds-60day/notebooks/day34_sklearn_intro_pipelines.ipynb`

Assume only the prerequisites declared in the guide. Do not open or
quote anything under `solutions/` unless I explicitly ask after an
honest attempt. First explain one concept in plain language and show a
tiny example. Then ask me to predict what happens before I run code.
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
