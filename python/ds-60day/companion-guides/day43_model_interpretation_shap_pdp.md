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

## Learner exercises and progressive hints

1. Compare a SHAP summary for the top five important features.
2. Plot PDP for the most important feature and interpret it.
3. Optionally use LIME on one prediction and compare it with SHAP.

LIME is installed by the `ml` dependency group but remains an optional lesson
extension. Complete the required work with SHAP and scikit-learn before adding a
second explanation library.

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
5. **Explanation leakage:** Explain why selecting the 'most important' features with the final test set and then retraining a smaller model contaminates evaluation.
   **Progressive hint:** The explanation becomes a supervised feature-selection step. Keep the test set unavailable until the complete selection procedure is frozen.
6. **Correlated-feature and causality check:** Duplicate or strongly correlate one predictor, compare SHAP, PDP, and permutation results, and write a cautious stakeholder explanation.
   **Progressive hint:** Credit can move or split between substitutes; marginal perturbations can create implausible combinations.

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
