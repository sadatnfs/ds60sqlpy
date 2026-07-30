from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import TypedDict

import nbformat

REPO_ROOT = Path(__file__).resolve().parents[2]
COURSE_ROOT = REPO_ROOT / "python" / "ds-60day"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from build_solution_notebooks import generate, markdown_to_cells  # noqa: E402
from normalize_notebooks import normalize_notebook  # noqa: E402


class Exercise(TypedDict):
    kind: str
    prompt: str
    hint: str
    answer: str


class PracticeSpec(TypedDict):
    focus: str
    original_reviews: list[str]
    exercises: list[Exercise]


def exercise(kind: str, prompt: str, hint: str, answer: str) -> Exercise:
    return {"kind": kind, "prompt": prompt, "hint": hint, "answer": answer}


PRACTICE: dict[int, PracticeSpec] = {}

PRACTICE.update(
    {
        31: {
            "focus": (
                "Move between probability models, seeded simulation, and diagnostics. "
                "A simulation is useful only when its sample space and uncertainty are explicit."
            ),
            "original_reviews": [
                (
                    "A Binomial draw is a count, so the possible values are the integers "
                    "0 through n. Use integer-centered bins, a seeded generator, and compare "
                    "the empirical mean and variance with n*p and n*p*(1-p); a visually "
                    "smooth histogram alone does not validate the simulation."
                ),
                (
                    "A density histogram must use density=True before its height can be "
                    "compared with a probability-density curve. Check the sample mean and "
                    "variance numerically as well, and state whether variance uses the "
                    "population convention (ddof=0) or an unbiased sample estimate."
                ),
                (
                    "Bayes' denominator includes both true positives and false positives. "
                    "Write every term with a conditional-probability label before inserting "
                    "numbers; this prevents confusing specificity with the false-positive rate."
                ),
            ],
            "exercises": [
                exercise(
                    "Prediction and uncertainty",
                    (
                        "For an event with probability 0.002 observed in 1,000 independent "
                        "trials, predict the chance of at least one occurrence, simulate it "
                        "20,000 times, and quantify Monte Carlo uncertainty."
                    ),
                    (
                        "Compute 1-(1-p)**n first. Treat each simulated experiment as one "
                        "Bernoulli outcome and use sqrt(p_hat*(1-p_hat)/runs) for its standard error."
                    ),
                    """
The complement is easier to model: “at least one” is one minus “zero.”
Keeping the analytic and simulated calculations separate gives an immediate
reasonableness check.

```python
import math
import numpy as np

event_probability = 0.002
trials = 1_000
runs = 20_000
expected = 1.0 - (1.0 - event_probability) ** trials

rng = np.random.default_rng(3104)
event_counts = rng.binomial(trials, event_probability, size=runs)
estimate = float(np.mean(event_counts >= 1))
monte_carlo_se = math.sqrt(estimate * (1.0 - estimate) / runs)

assert abs(estimate - expected) < 4 * monte_carlo_se
```

The four-standard-error comparison is a simulation diagnostic, not a proof
that every seeded run must match the analytic value exactly. Independence is
an assumption; clustered events would require another model.
""",
                ),
                exercise(
                    "Implementation",
                    (
                        "Estimate P(A|B) from two Boolean arrays without using a probability "
                        "library. Return both the estimate and the denominator so a caller can "
                        "judge support."
                    ),
                    (
                        "Count rows where B is true, then count rows where A and B are both "
                        "true. Decide explicitly what happens when B never occurs."
                    ),
                    """
Conditional probability is a ratio over the rows satisfying the condition.
Returning support prevents a precise-looking fraction based on almost no data.

```python
import numpy as np


def empirical_conditional(
    event_a: np.ndarray, event_b: np.ndarray
) -> tuple[float, int]:
    if event_a.shape != event_b.shape:
        raise ValueError("event arrays must have identical shapes")
    denominator = int(np.count_nonzero(event_b))
    if denominator == 0:
        raise ValueError("P(A|B) is undefined because B never occurs")
    numerator = int(np.count_nonzero(event_a & event_b))
    return numerator / denominator, denominator


estimate, support = empirical_conditional(
    np.array([True, False, True, True]),
    np.array([True, True, False, True]),
)
assert (estimate, support) == (2 / 3, 3)
```

Returning NaN is an alternative for vectorized reporting, but silently
returning zero would incorrectly claim evidence of no association.
""",
                ),
                exercise(
                    "Debugging and boundaries",
                    (
                        "Design and test a Binomial-parameter validator. Include n=0, p=0, "
                        "p=1, a negative n, a fractional n, and probabilities just outside "
                        "the valid interval."
                    ),
                    (
                        "n is a nonnegative integer and p is a finite number in [0, 1]. "
                        "Remember that bool is a subclass of int in Python."
                    ),
                    """
The degenerate cases `n=0`, `p=0`, and `p=1` are valid; they should not be
rejected merely because their distributions have no spread.

```python
import math


def validate_binomial(n: int, p: float) -> tuple[int, float]:
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    if isinstance(p, bool) or not isinstance(p, (int, float)):
        raise ValueError("p must be numeric")
    probability = float(p)
    if not math.isfinite(probability) or not 0.0 <= probability <= 1.0:
        raise ValueError("p must be finite and within [0, 1]")
    return n, probability


assert validate_binomial(0, 0) == (0, 0.0)
assert validate_binomial(4, 1) == (4, 1.0)
```

Use targeted exception tests for `-1`, `2.5`, `True`, `-1e-9`, `1.000000001`,
and NaN. Clipping invalid probabilities would hide upstream data errors.
""",
                ),
            ],
        },
        32: {
            "focus": (
                "Separate effect estimation from decision thresholds. Report uncertainty, "
                "assumptions, and practical magnitude rather than treating a p-value as a verdict."
            ),
            "original_reviews": [
                (
                    "Welch's t-test does not assume equal group variances, but it still "
                    "assumes independent observations and reasonably stable means. Report "
                    "sample sizes, the signed mean difference, a confidence interval, and "
                    "the test result; significance alone does not describe importance."
                ),
                (
                    "A chi-square test consumes counts, not raw category labels or "
                    "percentages. Inspect expected cell counts and combine levels or choose "
                    "an exact method when sparse cells make the asymptotic approximation weak."
                ),
                (
                    "For the same data and method, a 99% interval is wider than a 90% "
                    "interval because it must cover the parameter under more repeated "
                    "samples. The center should stay the same; only the critical value changes."
                ),
            ],
            "exercises": [
                exercise(
                    "Prediction",
                    (
                        "Hold the true mean difference and variance fixed, then predict how "
                        "increasing each group's sample size from 20 to 200 affects standard "
                        "error, confidence-interval width, power, and effect size."
                    ),
                    (
                        "Standard error shrinks approximately with 1/sqrt(n); the underlying "
                        "standardized effect does not grow merely because more rows were collected."
                    ),
                    """
Larger samples generally narrow the interval and increase power because the
sampling distribution of the mean becomes tighter. The population difference
and standardized effect remain unchanged. A tiny effect can therefore become
statistically detectable without becoming practically important.

Simulate many datasets at both sizes with one seeded generator, but summarize
the distribution of rejection rates rather than selecting a convenient run.
Also verify that the observations are independent; duplicated customers would
inflate the apparent sample size.
""",
                ),
                exercise(
                    "Implementation",
                    (
                        "Build a seeded percentile-bootstrap confidence interval for a "
                        "median difference. Validate empty groups and expose the number of "
                        "resamples as a parameter."
                    ),
                    (
                        "Resample each group independently with replacement, compute one "
                        "median difference per resample, then take symmetric quantiles."
                    ),
                    """
The bootstrap approximates the estimator's sampling distribution without
assuming that the raw values are Normal.

```python
import numpy as np


def bootstrap_median_difference(
    left: np.ndarray,
    right: np.ndarray,
    *,
    confidence: float = 0.95,
    resamples: int = 5_000,
    seed: int = 32,
) -> tuple[float, float]:
    if left.size == 0 or right.size == 0:
        raise ValueError("both groups must contain observations")
    if not 0.0 < confidence < 1.0 or resamples < 100:
        raise ValueError("invalid confidence or too few resamples")
    rng = np.random.default_rng(seed)
    differences = np.empty(resamples)
    for index in range(resamples):
        a = rng.choice(left, size=left.size, replace=True)
        b = rng.choice(right, size=right.size, replace=True)
        differences[index] = np.median(a) - np.median(b)
    tail = (1.0 - confidence) / 2.0
    low, high = np.quantile(differences, [tail, 1.0 - tail])
    return float(low), float(high)
```

This percentile interval is a useful teaching baseline. Strong skew, tiny
samples, dependence, or clustered observations call for a more suitable
resampling design or a BCa/analytic interval.
""",
                ),
                exercise(
                    "Multiple-comparison reasoning",
                    (
                        "You test 20 unrelated null hypotheses at alpha=0.05. Estimate the "
                        "chance of at least one false positive, then compare Bonferroni and "
                        "false-discovery-rate control for a planned analysis."
                    ),
                    (
                        "Under independent true nulls, use 1-(1-alpha)**20. Bonferroni "
                        "controls family-wise error; Benjamini-Hochberg targets the expected "
                        "false-discovery proportion among rejections."
                    ),
                    """
The chance of at least one false positive is about
`1 - 0.95**20`, or 64%, under the simplified independence assumption.
Bonferroni would compare each p-value with `0.05/20`; it is conservative and
fits a small set of confirmatory claims. Benjamini-Hochberg is often more
powerful for exploratory discovery, but answers a different error question.

Choose the hypothesis family and correction before inspecting results. Tests
that were added after seeing the data should be labeled exploratory rather
than quietly folded into the confirmatory analysis.
""",
                ),
            ],
        },
        33: {
            "focus": (
                "Treat shapes, rank, and conditioning as part of every matrix contract. "
                "Prefer stable solvers to symbolic formulas that require an explicit inverse."
            ),
            "original_reviews": [
                (
                    "Adding a ones column changes X from (rows, features) to "
                    "(rows, features+1). Decide which coefficient is the intercept and "
                    "verify predictions by multiplying the augmented matrix by the full "
                    "coefficient vector."
                ),
                (
                    "scikit-learn stores intercept_ separately when fit_intercept=True. "
                    "Compare both predictions and aligned coefficients on the same inputs; "
                    "matching rounded coefficients alone can hide a column-order error."
                ),
                (
                    "The normal equation magnifies numerical problems when columns are "
                    "nearly dependent and requires a costly inverse. Use condition number "
                    "as a warning and `lstsq`/QR/SVD-based solvers as the default."
                ),
            ],
            "exercises": [
                exercise(
                    "Shape tracing",
                    (
                        "For X with shape (120, 8), beta with shape (8,), and y with shape "
                        "(120,), trace the shapes of X.T, X.T @ X, X @ beta, and residuals. "
                        "Then explain what changes if beta is shaped (8, 1)."
                    ),
                    (
                        "Write shapes beside every operand before multiplying. A column "
                        "vector preserves a trailing dimension that can trigger broadcasting."
                    ),
                    """
`X.T` is `(8, 120)`, `X.T @ X` is `(8, 8)`, `X @ beta` is `(120,)`,
and `(X @ beta) - y` is `(120,)`. With `beta` shaped `(8, 1)`,
the prediction is `(120, 1)`. Subtracting a `(120,)` target from it broadcasts
to `(120, 120)`, a severe bug that can still produce numeric output.

Use `assert prediction.shape == y.shape` at the modeling boundary. Reshape
deliberately with `ravel()` only when a one-dimensional target is truly the
contract.
""",
                ),
                exercise(
                    "Rank-deficiency debugging",
                    (
                        "Construct a design matrix whose third column equals the sum of "
                        "the first two. Compare `np.linalg.solve(X.T @ X, X.T @ y)` with "
                        "`np.linalg.lstsq(X, y, rcond=None)` and interpret the rank."
                    ),
                    (
                        "The dependent column makes X.T @ X singular. `lstsq` returns a "
                        "minimum-norm solution plus rank information without forming an inverse."
                    ),
                    """
An exact linear dependency means multiple coefficient vectors make identical
predictions. A direct solve can raise `LinAlgError` or become unstable, while
least squares reports the deficient rank.

```python
import numpy as np

x1 = np.array([0.0, 1.0, 2.0, 3.0])
x2 = np.array([1.0, 0.0, 1.0, 2.0])
X = np.column_stack([x1, x2, x1 + x2])
y = np.array([1.0, 2.0, 4.0, 6.0])
coefficients, residuals, rank, singular_values = np.linalg.lstsq(
    X, y, rcond=None
)
assert rank == 2
assert np.allclose(X @ coefficients, y, atol=1.0)
```

The coefficient values are not uniquely identifiable. Remove redundant
features, regularize with a documented purpose, or interpret predictions
rather than inventing meaning for unstable individual coefficients.
""",
                ),
                exercise(
                    "Robust vector operation",
                    (
                        "Implement cosine similarity for two one-dimensional vectors. "
                        "Validate equal shapes and define behavior for a zero vector."
                    ),
                    (
                        "Compute dot(a,b)/(norm(a)*norm(b)); a zero norm makes the angle "
                        "undefined, so do not quietly add an epsilon without documenting it."
                    ),
                    """
```python
import numpy as np


def cosine_similarity(left: np.ndarray, right: np.ndarray) -> float:
    if left.ndim != 1 or right.ndim != 1 or left.shape != right.shape:
        raise ValueError("vectors must be one-dimensional with equal length")
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    if denominator == 0.0:
        raise ValueError("cosine similarity is undefined for a zero vector")
    return float(np.dot(left, right) / denominator)


assert np.isclose(
    cosine_similarity(np.array([1.0, 0.0]), np.array([0.0, 1.0])),
    0.0,
)
```

Clipping a computed result into `[-1, 1]` can protect a later `arccos` from
tiny floating-point overshoot, but it must not conceal incorrect shapes or a
zero denominator.
""",
                ),
            ],
        },
        34: {
            "focus": (
                "Make preprocessing and estimation one fitted object. Data boundaries, "
                "feature names, and unknown-category behavior are part of the model contract."
            ),
            "original_reviews": [
                (
                    "Change only the final estimator while keeping the split and "
                    "preprocessing fixed. Compare held-out metrics and coefficient magnitude; "
                    "one score does not establish that regularization is universally better."
                ),
                (
                    "A coefficient after StandardScaler describes a one-standard-deviation "
                    "change in that fitted training feature. Preserve transformed feature "
                    "names and avoid causal language when predictors are correlated."
                ),
            ],
            "exercises": [
                exercise(
                    "Leakage prediction",
                    (
                        "Predict how cross-validation scores can change when a scaler is fit "
                        "on the complete dataset before `cross_val_score`, then explain why "
                        "the code still runs without warning."
                    ),
                    (
                        "The globally fitted mean and scale contain information from each "
                        "validation fold. A Pipeline refits them using only the fold's training rows."
                    ),
                    """
The global transform lets every held-out row influence preprocessing
statistics, so validation is no longer a simulation of unseen data. The score
may be optimistically biased even though shapes and types are valid.

Pass raw `X` and a `Pipeline([("scale", StandardScaler()), ("model", ...)])`
to cross-validation. scikit-learn clones and fits the entire pipeline inside
each training fold. This same rule applies to imputation, feature selection,
target encoding, and learned dimensionality reduction.
""",
                ),
                exercise(
                    "Mixed-type implementation",
                    (
                        "Build a `ColumnTransformer` for numeric imputation/scaling and "
                        "categorical imputation/one-hot encoding, followed by LogisticRegression. "
                        "Use a tiny DataFrame containing a missing value."
                    ),
                    (
                        "Use separate nested pipelines and `handle_unknown='ignore'`; keep "
                        "column lists explicit so schema drift is visible."
                    ),
                    """
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
""",
                ),
                exercise(
                    "Unknown-category debugging",
                    (
                        "Fit on regions `north` and `south`, then predict a row with region "
                        "`west`. Compare `OneHotEncoder` default behavior with "
                        "`handle_unknown='ignore'` and explain the resulting representation."
                    ),
                    (
                        "The default raises on an unseen category. Ignore maps the unknown "
                        "to all zeros for that feature block, which is operationally safe but lossy."
                    ),
                    """
With `handle_unknown="ignore"`, the transformed categorical block for `west`
contains zeros in both known-region columns. The model can score the row, but
it cannot distinguish “unknown” from the baseline implied by that zero vector.

Monitor unknown-category rates and consider an explicit rare/unknown bucket
when the distinction matters. Do not fit the encoder again during prediction;
that would change the feature schema and invalidate fitted coefficients.
""",
                ),
                exercise(
                    "Inspection and schema contract",
                    (
                        "After fitting the mixed-type pipeline, recover transformed feature "
                        "names, pair them with coefficients, and assert that an inference "
                        "DataFrame has the required columns in a safe order."
                    ),
                    (
                        "Use `get_feature_names_out()` from the fitted ColumnTransformer. "
                        "Select by column name rather than trusting an incoming positional order."
                    ),
                    """
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
""",
                ),
            ],
        },
        35: {
            "focus": (
                "Match metrics and resampling to the decision being modeled. Keep thresholds, "
                "groups, time, and hyperparameter selection inside honest validation boundaries."
            ),
            "original_reviews": [
                (
                    "Accuracy and F1 use thresholded labels, while ROC AUC uses ranking "
                    "scores. Keep folds identical and report class prevalence so readers can "
                    "understand why the metrics may disagree."
                ),
                (
                    "Five and ten folds trade training-set size against compute and fold "
                    "variance. Compare the paired fold procedure across repeated seeds rather "
                    "than announcing a universal winner from one split."
                ),
                (
                    "Any transform learned before cross-validation leaks validation-fold "
                    "information. A pipeline causes preprocessing to be cloned and refit "
                    "inside every fold, but it cannot repair leakage already baked into features."
                ),
            ],
            "exercises": [
                exercise(
                    "Threshold analysis",
                    (
                        "Using one fixed validation score vector, compare confusion matrices "
                        "at thresholds 0.2, 0.5, and 0.8. Explain which errors increase as the "
                        "threshold rises and why ROC AUC stays unchanged."
                    ),
                    (
                        "A higher positive threshold generally reduces predicted positives: "
                        "false positives fall while false negatives rise. Ranking scores do not change."
                    ),
                    """
Build the matrix with an explicit label order such as `[0, 1]` and record
support beside rates. Threshold selection is a policy decision; choose it on
validation data using error costs or a documented constraint, then evaluate
that frozen threshold once on the final holdout.

ROC AUC is unchanged because it considers ranking across all possible
thresholds. Precision, recall, F1, and the confusion matrix do change because
they consume the thresholded labels.
""",
                ),
                exercise(
                    "Grouped resampling",
                    (
                        "Design cross-validation for repeated measurements from the same "
                        "patient or customer. Demonstrate how ordinary StratifiedKFold can "
                        "place one entity in both training and validation."
                    ),
                    (
                        "Use `StratifiedGroupKFold` when both label balance and entity "
                        "separation matter; assert that train and validation group sets are disjoint."
                    ),
                    """
Rows from one entity are correlated, so random row-level folds can let the
model recognize entity-specific patterns rather than generalize to new
entities.

```python
from sklearn.model_selection import StratifiedGroupKFold

splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=35)
for train_index, valid_index in splitter.split(X, y, groups=entity_ids):
    train_groups = set(entity_ids[train_index])
    valid_groups = set(entity_ids[valid_index])
    assert train_groups.isdisjoint(valid_groups)
```

If deployment predicts future rows for already-known entities, a different
split may be appropriate; align the split with that real decision explicitly.
""",
                ),
                exercise(
                    "Selection-bias debugging",
                    (
                        "Explain why reporting `GridSearchCV.best_score_` as final performance "
                        "is optimistic. Sketch a nested cross-validation design and distinguish "
                        "it from out-of-fold predictions for one fixed model."
                    ),
                    (
                        "The same inner folds both select and report the best candidate. "
                        "Nested CV puts the complete search inside an outer held-out fold."
                    ),
                    """
`best_score_` is the highest noisy estimate among tried configurations, so
selection favors candidates that benefited from sampling noise. In nested CV:

1. the inner splitter selects hyperparameters using only the outer-training rows;
2. the selected pipeline predicts the untouched outer-validation rows;
3. outer scores summarize the complete model-selection procedure.

`cross_val_predict` can generate out-of-fold predictions for a fixed estimator,
but it is not automatically nested. Passing the entire search object to the
outer loop is what repeats selection honestly.
""",
                ),
            ],
        },
    }
)


GUIDE_EXERCISE_HEADING = re.compile(
    r"^## Learner exercises.*$",
    flags=re.MULTILINE | re.IGNORECASE,
)
NOTEBOOK_EXERCISE_HEADING = re.compile(
    r"^## Exercises.*$",
    flags=re.MULTILINE | re.IGNORECASE,
)


def _section_span(text: str, heading_pattern: re.Pattern[str]) -> tuple[int, int, str]:
    heading = heading_pattern.search(text)
    if heading is None:
        raise RuntimeError("could not find the expected exercise section")
    following = re.search(r"^## ", text[heading.end() :], flags=re.MULTILINE)
    end = heading.end() + following.start() if following else len(text)
    return heading.start(), end, text[heading.start() : end].rstrip()


def _numbered_items(section: str) -> list[str]:
    body = section.split("\n", maxsplit=1)[1] if "\n" in section else ""
    prompt_body = re.split(
        r"^### Progressive hints.*$",
        body,
        maxsplit=1,
        flags=re.MULTILINE | re.IGNORECASE,
    )[0]
    matches = list(re.finditer(r"(?m)^(\d+)\.\s+", prompt_body))
    items: list[str] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(prompt_body)
        items.append(prompt_body[match.end() : end].strip())
    if not items:
        raise RuntimeError("exercise section has no numbered learner prompts")
    return items


def _guide_section(
    spec: PracticeSpec,
    original_section: str,
    original_count: int,
) -> str:
    original_body = original_section.split("\n", maxsplit=1)[1].strip()
    lines = [
        "## Learner exercises and progressive hints",
        "",
        original_body,
        "",
        "### Additional mastery practice",
        "",
        spec["focus"],
        "",
        "Predict or plan before you run code. Use the hint only after an honest",
        "attempt, and record the evidence that would prove your result correct.",
        "",
    ]
    for number, item in enumerate(spec["exercises"], start=original_count + 1):
        lines.extend(
            [
                f"{number}. **{item['kind']}:** {item['prompt']}",
                f"   **Progressive hint:** {item['hint']}",
            ]
        )
    lines.extend(
        [
            "",
            "Before opening the reference solution, explain the relevant assumption,",
            "failure mode, and validation check for every answer.",
        ]
    )
    return "\n".join(lines)


def _scratch_cell(spec: PracticeSpec, original_count: int) -> str:
    lines = [
        "# Expanded mastery lab scratch space",
        "#",
        "# Keep the official solution closed until you have attempted each task.",
        "# Add small assertions, shape checks, or metric comparisons as evidence.",
        "",
    ]
    for number, item in enumerate(spec["exercises"], start=original_count + 1):
        lines.extend([f"# Practice {number} — {item['kind']}", "", ""])
    return "\n".join(lines).rstrip() + "\n"


def _solution_section(
    spec: PracticeSpec,
    original_items: list[str],
) -> str:
    lines = [
        "",
        "---",
        "",
        "## Exercise-by-exercise reasoning map",
        "",
        "This map connects every learner prompt to a reasoning path. Read the",
        "explanation before copying code: the goal is to understand the assumptions,",
        "the evidence that validates the result, and the edge cases that can make an",
        "apparently correct implementation fail.",
        "",
    ]
    for number, (prompt, review) in enumerate(
        zip(original_items, spec["original_reviews"], strict=True),
        start=1,
    ):
        compact_prompt = " ".join(prompt.split())
        lines.extend(
            [
                f"### Exercise {number} — Original lesson practice",
                "",
                f"**Prompt:** {compact_prompt}",
                "",
                f"**How to reason about it:** {review}",
                "",
                "Use the worked reference earlier in this file, then change one boundary",
                "condition and rerun the stated checks. A copied output is not evidence",
                "unless you can explain why that output follows from the inputs.",
                "",
            ]
        )

    for number, item in enumerate(spec["exercises"], start=len(original_items) + 1):
        lines.extend(
            [
                f"### Exercise {number} — {item['kind']}",
                "",
                f"**Prompt:** {item['prompt']}",
                "",
                f"**Reasoning before implementation:** {item['hint']}",
                "",
                item["answer"].strip(),
                "",
                "**Why this matters:** The result should survive a fresh-kernel rerun and",
                "a deliberately chosen boundary case. If it does not, revisit the",
                "assumption or data boundary rather than hiding the failure.",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _write_notebook(path: Path, notebook: nbformat.NotebookNode) -> None:
    relative = path.relative_to(REPO_ROOT)
    normalized, _ = normalize_notebook(notebook, relative_path=relative)
    path.write_text(
        nbformat.writes(normalized, version=4),
        encoding="utf-8",
        newline="\n",
    )


def _replace_or_append_learner_section(
    notebook: nbformat.NotebookNode,
    section: str,
) -> None:
    for cell in notebook.cells:
        if cell.cell_type != "markdown":
            continue
        source = str(cell.source)
        heading = NOTEBOOK_EXERCISE_HEADING.search(source)
        if heading is None:
            continue
        following = re.search(r"^## ", source[heading.end() :], flags=re.MULTILINE)
        end = heading.end() + following.start() if following else len(source)
        cell.source = (
            source[: heading.start()].rstrip()
            + ("\n\n" if source[: heading.start()].strip() else "")
            + section
            + ("\n\n" + source[end:].lstrip() if source[end:].strip() else "")
        ).rstrip() + "\n"
        return
    notebook.cells.append(
        nbformat.v4.new_markdown_cell(
            section,
            metadata={"tags": ["exercise", "answer-free"]},
        )
    )


def enrich_day(day: int, spec: PracticeSpec, target: int) -> None:
    guide = next((COURSE_ROOT / "companion-guides").glob(f"day{day:02d}_*.md"))
    learner = next((COURSE_ROOT / "notebooks").glob(f"day{day:02d}_*.ipynb"))
    solution_markdown = next(
        (COURSE_ROOT / "solutions").glob(
            f"day{day:02d}_*/day{day:02d}_solutions.md"
        )
    )
    solution_notebook = solution_markdown.with_suffix(".ipynb")

    guide_text = guide.read_text(encoding="utf-8")
    if "### Additional mastery practice" in guide_text:
        raise RuntimeError(f"guide is already enriched: {guide}")
    start, end, original_section = _section_span(
        guide_text,
        GUIDE_EXERCISE_HEADING,
    )
    original_items = _numbered_items(original_section)
    original_count = len(original_items)
    if len(spec["original_reviews"]) != original_count:
        raise RuntimeError(
            f"Day {day}: {len(spec['original_reviews'])} reviews for "
            f"{original_count} original prompts"
        )
    if original_count + len(spec["exercises"]) != target:
        raise RuntimeError(
            f"Day {day}: {original_count} originals + {len(spec['exercises'])} "
            f"new prompts does not equal target {target}"
        )

    combined_section = _guide_section(spec, original_section, original_count)
    guide.write_text(
        (
            guide_text[:start].rstrip()
            + "\n\n"
            + combined_section
            + "\n\n"
            + guide_text[end:].lstrip()
        ).rstrip()
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    learner_notebook = nbformat.read(learner, as_version=4)
    if any(
        "### Additional mastery practice" in str(cell.source)
        for cell in learner_notebook.cells
    ):
        raise RuntimeError(f"learner notebook is already enriched: {learner}")
    _replace_or_append_learner_section(learner_notebook, combined_section)
    learner_notebook.cells.append(
        nbformat.v4.new_code_cell(
            _scratch_cell(spec, original_count),
            metadata={"tags": ["exercise", "answer-free"]},
        )
    )
    _write_notebook(learner, learner_notebook)

    solution_text = solution_markdown.read_text(encoding="utf-8")
    if "## Exercise-by-exercise reasoning map" in solution_text:
        raise RuntimeError(f"solution is already enriched: {solution_markdown}")
    addition = _solution_section(spec, original_items)
    solution_markdown.write_text(
        solution_text.rstrip() + "\n" + addition,
        encoding="utf-8",
        newline="\n",
    )

    if day <= 45:
        solution_notebook_payload = nbformat.read(solution_notebook, as_version=4)
        addition_cells = markdown_to_cells(addition)
        for cell in addition_cells:
            tags = set(cell.metadata.get("tags", []))
            tags.add("expanded-solution")
            cell.metadata["tags"] = sorted(tags)
        solution_notebook_payload.cells.extend(addition_cells)
        _write_notebook(solution_notebook, solution_notebook_payload)


def main() -> None:
    if set(PRACTICE) != set(range(31, 61)):
        raise RuntimeError("practice specification must cover exactly Days 31-60")
    baseline = json.loads(
        (REPO_ROOT / "curriculum" / "practice_baseline.json").read_text(
            encoding="utf-8"
        )
    )["lessons"]
    for day, spec in PRACTICE.items():
        target = int(baseline[f"python-{day:02d}"]["target"])
        enrich_day(day, spec, target)

    changed, checked = generate(
        repo_root=REPO_ROOT,
        check=False,
        days=range(46, 61),
    )
    print(
        "Enriched Python core Days 31-60; "
        f"generated solution notebooks checked={checked}, changed={changed}."
    )


if __name__ == "__main__":
    main()
