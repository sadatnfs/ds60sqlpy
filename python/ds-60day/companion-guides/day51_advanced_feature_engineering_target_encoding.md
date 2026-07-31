# Day 51 — Target Encoding and Leakage-Safe Features

**Lesson ID:** `python-51` · **Level:** advanced · **Dependencies:** `data` · **Network:** first-run Seaborn cache

Target encoding replaces a category with a statistic derived from the target.
It can represent high-cardinality categories compactly, but a naive
implementation leaks the answer into its own feature.

## Learning objectives

By the end of the lesson, you can:

- explain why full-data target means leak target information;
- produce out-of-fold encodings for training rows;
- apply training-only maps and a prior to unseen test categories;
- reason about smoothing and split count; and
- compare target encoding with one-hot encoding across controlled splits.

## Prerequisites

- Complete `python-50` (time-safe model evaluation).
- Recall pipelines, cross-validation, and category handling.
- Cache Seaborn's Titanic dataset once while connected before offline study.

## Dataset and offline contract

The notebook calls `seaborn.load_dataset("titanic")`, which may download the
small dataset on first use and cache it locally. That connected first run is
accepted. Subsequent study can be offline on the same machine.

The reference solution uses deterministic synthetic categories, so it remains a
useful fully local comparison even without the Titanic cache.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Target encoding | Replaces a category with a target statistic such as the mean |
| Out-of-fold encoding | Each training row receives a mapping learned without its fold |
| Global prior | Training-target average used for smoothing or unknown categories |
| Smoothing | Shrinks noisy category estimates toward the prior |
| High cardinality | Many distinct category levels relative to observations |
| Unknown category | Level encountered at transform time but absent during map fitting |
| Feature hashing | Stateless mapping of categories into a fixed sparse dimension |

There are two mappings:

1. training rows need out-of-fold encodings; and

2. validation/test/inference rows need a map learned from all available training
   rows.

Using the first procedure for both, or the second procedure on training rows,
creates subtle errors.

## Worked example: inspect support before trusting a mean

```python
import pandas as pd

training = pd.DataFrame(
    {
        "category": ["a", "a", "a", "b", "b", "rare"],
        "target": [1, 0, 1, 0, 1, 1],
    }
)
summary = training.groupby("category")["target"].agg(["mean", "count"])
print(summary)
```

The rare category has an extreme mean based on one row. Smoothing combines its
estimate with the global training mean, with the count determining how strongly
to trust the category-specific value.

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 51 learner notebook from this guide's **Next
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

## Concept deep dive — out-of-fold target encoding, smoothing, and transform-time unknowns

### The mental model

Target encoding replaces a category with a statistic of the target.
Computing that statistic from the row's own target leaks the answer.
Training rows therefore need **out-of-fold** encodings: each row is
transformed by a map learned from other folds only.

Validation/test rows use a map learned from the corresponding training
data. Rare categories are noisy, so smoothing shrinks their mean toward
the training prior. Missing and unseen categories need an explicit
fallback. Temporal or grouped data requires a compatible split rather
than ordinary shuffled folds.

### Worked examples and syntax anatomy

- **`groupby(category)[target].agg(['mean', 'count'])`:** builds category evidence only from the allowed training subset.
- **`(count * mean + strength * prior) / (count + strength)`:** smooths low-support categories toward the training-wide prior.
- **out-of-fold transform:** fits one map per training fold and writes values only to that fold's held-out rows.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — show why a one-row category leaks perfectly

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
import pandas as pd

category = pd.Series(["common", "common", "only_zero", "only_one"])
target = pd.Series([0, 1, 0, 1], dtype=float)
full_map = target.groupby(category).mean()
leaked = category.map(full_map)
print(pd.DataFrame({"category": category, "target": target, "leaked": leaked}))
assert leaked.iloc[2] == target.iloc[2]
assert leaked.iloc[3] == target.iloc[3]
```

**Expected observation:** Singleton categories receive their own targets exactly, creating a feature that memorizes training labels.

**Assumption to name:** Category identity is available at prediction time, but the current row's target is not.

### Focused example B — smooth known categories and fall back for unknowns

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
import pandas as pd

train_category = pd.Series(["a", "a", "a", "b"])
train_target = pd.Series([1, 1, 0, 1], dtype=float)
prior = train_target.mean()
stats = train_target.groupby(train_category).agg(["mean", "count"])
strength = 3.0
smoothed = (
    stats["mean"] * stats["count"] + prior * strength
) / (stats["count"] + strength)
new_category = pd.Series(["a", "b", "unseen", None])
encoded = new_category.map(smoothed).fillna(prior)
print({"prior": prior, "map": smoothed.to_dict(),
       "encoded": encoded.tolist()})
assert encoded.iloc[2] == prior and encoded.iloc[3] == prior
```

**Expected observation:** The low-support `b` estimate is pulled toward the prior; unseen and missing values use the declared prior.

**Assumption to name:** Using one shared prior for missing/unseen categories matches the model contract.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define out-of-fold target encoding, smoothing, and transform-time unknowns in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Building one full-training target map and applying it back to those same training rows.

**Debug it deliberately:** Attach source fold and map-training row IDs to a tiny example; assert every encoded training row is absent from its map's target aggregation.

**Stop condition:** Do not use target encoding until the split unit, unseen fallback, smoothing strength, and fit/transform boundaries are testable.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Add K-fold target encoding to a scikit-learn pipeline through a custom
   transformer or `FunctionTransformer`.

**Verify:** Practice 1 — out-of-fold target encoding, smoothing, and transform-time unknowns — produce one out-of-fold encoded value per training row, assert that row's target was excluded from its category statistic, and test missing/unseen categories through the fitted pipeline without NaN or leakage.

2. Add an appropriate prior and smoothing; experiment with `n_splits`.

**Verify:** Practice 2 — out-of-fold target encoding, smoothing, and transform-time unknowns — print global prior, smoothing formula, n_splits, category count/support, and encoded values for rare/common/unseen categories; compare at least three n_splits values on identical folds.

3. Compare ROC AUC with one-hot encoding across multiple seeded train/test
   splits.

**Verify:** Practice 3 — out-of-fold target encoding, smoothing, and transform-time unknowns — over multiple declared seeded splits, print ROC-AUC pairs for target encoding and one-hot encoding plus mean/std/difference; keep all encoding fits inside each training fold.

### Progressive hints

1. A robust custom transformer needs distinct fitting and transform behavior.
   During training, generate out-of-fold values; for new rows, use a mapping fit
   only on training data. Write down index-alignment rules first.
2. Blend a category mean with the global prior using its support count. Test an
   unseen category and a one-row category deliberately.
3. Reuse each split for both methods and report score differences per seed, not
   only the best run.

The notebook's `kfold_target_encode` is an instructional utility, not a
drop-in production transformer. Its Series indexes and positional fold indexes
must remain aligned.

### Additional mastery practice

Implement target-derived features with row-level lineage. Training encodings must be out-of-fold; validation, test, and future rows use mappings fitted only on prior data.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

4. **Out-of-fold invariant:** Create a unique category for every training row and show that a leaky full-data target mean reproduces each label. Then prove that your out-of-fold encoder falls back to the prior instead.
   **Progressive hint:** For a category absent from the fold's training partition, there is no valid category statistic; use the fold training prior.

**Verify:** Out-of-fold invariant — on unique-per-row categories, assert full-data encoding equals each label while every out-of-fold value equals the training-fold prior; print row, fold, label, leaky value, and OOF value.

5. **Unknown and missing categories:** Define distinct policies for a missing category, an unseen category, and a known category with one observation. Write tests for all three.
   **Progressive hint:** Normalize missing values to an explicit sentinel if missingness is a category; unseen categories generally receive the training global prior.

**Verify:** Unknown and missing categories — assert missing, unseen, one-observation-known, and well-supported-known fixtures return their separately documented prior/smoothed values without NaN; print support and mapping source for each.

6. **Temporal leakage:** Design target encoding for timestamped events where later labels cannot inform earlier rows. Compare random K-fold encoding with an expanding-time implementation.
   **Progressive hint:** Sort by event time and compute each row's category statistics from strictly earlier labeled rows; handle ties deliberately.

**Verify:** Temporal leakage — print each event timestamp, training cutoff, category support, and encoded value under expanding time; assert no source label timestamp is later than the row cutoff and compare with random-K-fold leakage.

Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.

## Self-check

- Why does grouping the entire training target by category leak each row?
- Which prior should fill a category seen only in the test set?
- How does stronger smoothing affect rare and frequent categories differently?
- Why can one-hot encoding outperform target encoding on low-cardinality data?

Expected behavior: every training row receives a finite out-of-fold value,
unseen categories map to the training prior, and no test target is referenced.

## Pitfalls, diagnostics, and tradeoffs

| Pitfall | Consequence | Better practice |
|---|---|---|
| Full-data means assigned to training rows | Direct target leakage | Generate out-of-fold training encodings |
| Validation target used in mapping | Inflated CV | Fit encoder inside each training fold |
| No smoothing for rare levels | High-variance extreme values | Shrink toward training prior |
| Pandas indexes silently misalign | Wrong targets paired with categories | Assert lengths/indexes and use explicit positions |
| One favorable split reported | Unstable conclusion | Compare paired results across seeds/folds |

Target encoding is compact and potentially powerful. One-hot encoding is easier
to audit, while hashing is stateless and bounded but has collisions. Choose
based on cardinality, leakage risk, runtime, and validated evidence.

## Next step

- Work in the [Day 51 learner notebook](../notebooks/day51_advanced_feature_engineering_target_encoding.ipynb).
- Then consult the
  [Day 51 solution](../solutions/day51_advanced_feature_engineering_target_encoding/day51_solutions.md).
- Continue to [Day 52 — Dask](day52_scalability_dask.md).

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-51` — Day 51 — Target Encoding and Leakage-Safe Features.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize out-of-fold target encoding, smoothing, and transform-time unknowns. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day51_advanced_feature_engineering_target_encoding.md`
- learner artifact: `python/ds-60day/notebooks/day51_advanced_feature_engineering_target_encoding.ipynb`

Treat me as a beginner except for these direct catalog prerequisites:
`python-50`. Do not assume knowledge beyond them or skip the
guide's declared setup boundary. Do not open or quote anything under
`solutions/` unless I explicitly ask after an honest attempt. First
explain one concept in plain language and show a tiny example. Then ask
me to predict what happens before I run code.
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
