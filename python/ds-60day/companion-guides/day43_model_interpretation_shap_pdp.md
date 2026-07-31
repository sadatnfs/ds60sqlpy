# Day 43 — Model Interpretation with SHAP, PDP, and Permutation

**Lesson ID:** `python-43` · **Level:** intermediate · **Dependencies:** `ml` · **Network:** offline

Interpretation tools describe how a fitted model behaves under their own
assumptions. They do not make the model causal, fair, correct, or safe.

## Learning objectives

By the end of the lesson, you can:

- distinguish global behavior from a local prediction explanation;
- calculate held-out permutation importance;
- create partial-dependence views and state their independence caveat;
- normalize SHAP output shapes across supported SHAP versions; and
- triangulate an explanation rather than relying on one plot.

## Prerequisites

- Complete `python-42` (unsupervised learning and anomaly detection).
- Recall random forests and correlated features from `python-38`.
- Install the `ml` dependency group during connected setup for SHAP.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Global explanation | Summary of behavior across many observations |
| Local explanation | Attribution for one prediction or small set of predictions |
| Permutation importance | Performance loss after breaking one feature's association with the target |
| Partial dependence (PDP) | Average model response as selected features are varied over a grid |
| ICE | Individual conditional-expectation curve for one observation |
| SHAP value | Game-theoretic attribution relative to an explainer's baseline/background |
| Background distribution | Reference data defining what “missing” or baseline feature information means |

Attributions divide a prediction among inputs under an explainer. Correlated
features can share or substitute attribution in ways that do not match a human
causal story.

## Worked example: handle SHAP classifier shapes

```python
import shap
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, stratify=y, random_state=42
)
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
).fit(X_train, y_train)

sample = X_test[:200]  # bounded for CPU and memory
values = shap.TreeExplainer(model).shap_values(sample)
if isinstance(values, list):          # older SHAP: one array per class
    positive_values = values[1]
elif values.ndim == 3:                # newer SHAP: rows × features × classes
    positive_values = values[:, :, 1]
else:
    positive_values = values
```

The lesson is fully offline after packages are installed. It uses package-bundled
data and a small sample because SHAP can be computationally heavy.

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 43 learner notebook from this guide's **Next
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

## Concept deep dive — global versus local explanations, perturbation assumptions, and causal limits

### The mental model

An explanation describes a fitted model under a chosen data reference;
it does not automatically describe the data-generating process.
**Global** tools summarize behavior across many observations. **Local**
tools allocate one prediction relative to a baseline or nearby cases.

Permutation importance breaks a feature's observed association and
measures score loss. Partial dependence averages predictions while
varying features, potentially creating unrealistic combinations when
features are correlated. SHAP values also require assumptions about
missing-feature dependence and a background distribution.

### Worked examples and syntax anatomy

- **`permutation_importance(..., X_valid, y_valid)`:** measures predictive reliance on held-out data with repeated shuffles and a declared scorer.
- **`PartialDependenceDisplay.from_estimator(...)`:** averages model predictions over a grid while holding the empirical distribution of other features.
- **`shap.TreeExplainer(model, data=background, ...)`:** allocates model output under an explicit dependence/background convention; output shape is model/version dependent.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — measure one local prediction's sensitivity

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X, y = load_breast_cancer(return_X_y=True)
X_train, X_valid, y_train, y_valid = train_test_split(
    X, y, stratify=y, random_state=4301
)
model = RandomForestClassifier(n_estimators=80, random_state=4301, n_jobs=1)
model.fit(X_train, y_train)
row = X_valid[[0]].copy()
baseline = model.predict_proba(row)[0, 1]
changed = row.copy()
changed[0, 0] = np.median(X_train[:, 0])
perturbed = model.predict_proba(changed)[0, 1]
print({"baseline": baseline, "one_feature_changed": perturbed,
       "difference": perturbed - baseline})
```

**Expected observation:** Changing one feature can move the prediction, but the difference is a model sensitivity under an artificial intervention.

**Assumption to name:** The changed feature value combined with all unchanged values represents a plausible input.

### Focused example B — give permutation importance an uncertainty interval

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
from sklearn.inspection import permutation_importance

result = permutation_importance(
    model, X_valid, y_valid, scoring="roc_auc",
    n_repeats=8, random_state=4302, n_jobs=1
)
order = result.importances_mean.argsort()[::-1][:3]
summary = [
    (int(i), float(result.importances_mean[i]), float(result.importances_std[i]))
    for i in order
]
print(summary)
assert all(mean >= -3 * std for _, mean, std in summary)
```

**Expected observation:** Importance is a distribution across shuffles, not one exact ranking; close features may be indistinguishable.

**Assumption to name:** Held-out ROC AUC is a valid model-quality measure and the model performs well enough to explain.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define global versus local explanations, perturbation assumptions, and causal limits in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Writing 'feature X causes outcome Y' beneath a SHAP, PDP, or importance plot.

**Debug it deliberately:** State the explained output, dataset/split, background, scorer, perturbation rule, correlation structure, and whether the input combinations are plausible.

**Stop condition:** Do not explain a poorly validated model or expose sensitive row-level explanations without an access/privacy policy.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Compare a SHAP summary for the top five important features.

**Verify:** For task `Compare a SHAP summary for the top five important features`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.






2. Plot PDP for the most important feature and interpret it.

**Verify:** For task `Plot PDP for the most important feature and interpret it`, show the labeled figure and reconcile it with a numeric summary so appearance is not the only check.






3. Optionally use LIME on one prediction and compare it with SHAP.

LIME is installed by the `ml` dependency group but remains an optional lesson
extension. Complete the required work with SHAP and scikit-learn before adding a
second explanation library.

**Verify:** For task `Optionally use LIME on one prediction and compare it with SHAP`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.







### Progressive hints

1. Rank features with mean absolute SHAP values, preserve the original feature
   names, and then limit the display.
2. Choose importance from held-out permutation or aggregated SHAP, not from a
   single local case. Look for regions with little data support.
3. If you intentionally install LIME during a connected session, fix its random
   seed and compare direction, magnitude, and stability—not just wording.

### Additional mastery practice

Treat explanations as model diagnostics tied to a dataset and baseline. Distinguish global from local behavior and predictive association from causation.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Local-versus-global diagnosis:** Construct a case where a feature is globally important but contributes little to one prediction. Explain why those statements do not conflict.
   **Progressive hint:** Global importance aggregates across rows; a local explanation is conditioned on one row and its baseline.

**Verify:** For task `Local-versus-global diagnosis: Construct a case where a feature is globally important but con...`, use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.







5. **Explanation leakage:** Explain why selecting the 'most important' features with the final test set and then retraining a smaller model contaminates evaluation.
   **Progressive hint:** The explanation becomes a supervised feature-selection step. Keep the test set unavailable until the complete selection procedure is frozen.

**Verify:** For task `Explanation leakage: Explain why selecting the 'most important' features with the final test...`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then produce the requested artifact with every named field/control and walk one allowed plus one rejected scenario through it.







6. **Correlated-feature and causality check:** Duplicate or strongly correlate one predictor, compare SHAP, PDP, and permutation results, and write a cautious stakeholder explanation.
   **Progressive hint:** Credit can move or split between substitutes; marginal perturbations can create implausible combinations.

**Verify:** For task `Correlated-feature and causality check: Duplicate or strongly correlate one predictor, compar...`, record the seed, resampling unit, run count, estimate, and an analytic or hand-worked comparison with a stated tolerance; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.






Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.



## Self-check

- What reference does a SHAP value explain a prediction relative to?
- Why can shuffling one of two redundant features produce low importance?
- Why can PDP evaluate unrealistic feature combinations?
- Which tool tells you whether changing a feature would cause an outcome?

Expected behavior: SHAP output is either a list or an array depending on
version; the compatibility branch should yield one row-by-feature matrix for the
positive class.

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Consequence | Better practice |
|---|---|---|
| Using training data for importance | Optimistic behavior | Compute on held-out representative data |
| Treating SHAP sign as causal direction | Association becomes a false intervention claim | State the model-relative interpretation |
| Ignoring feature correlation in PDP | Unrealistic combinations | Add ICE, conditional analysis, and data-density checks |
| Explaining a poor model beautifully | Explanation creates false confidence | Validate performance and data first |
| Explaining too many rows/features | Slow, unreadable output | Sample deterministically and state scope |

Permutation importance answers a predictive question, PDP answers an averaged
response question, and SHAP allocates prediction differences. Agreement is
reassuring; disagreement is a prompt to investigate assumptions.

## Next step

- Work in the [Day 43 learner notebook](../notebooks/day43_model_interpretation_shap_pdp.ipynb).
- Then consult the
  [Day 43 solution](../solutions/day43_model_interpretation_shap_pdp/day43_solutions.md).
- Continue to [Day 44 — FastAPI Deployment](day44_model_deployment_fastapi.md).

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-43` — Day 43 — Model Interpretation with SHAP, PDP, and Permutation.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize global versus local explanations, perturbation assumptions, and causal limits. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day43_model_interpretation_shap_pdp.md`
- learner artifact: `python/ds-60day/notebooks/day43_model_interpretation_shap_pdp.ipynb`

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
