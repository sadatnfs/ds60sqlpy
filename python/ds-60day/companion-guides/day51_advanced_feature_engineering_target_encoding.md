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

## Learner exercises and progressive hints

1. Add K-fold target encoding to a scikit-learn pipeline through a custom
   transformer or `FunctionTransformer`.
2. Add an appropriate prior and smoothing; experiment with `n_splits`.
3. Compare ROC AUC with one-hot encoding across multiple seeded train/test
   splits.

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
5. **Unknown and missing categories:** Define distinct policies for a missing category, an unseen category, and a known category with one observation. Write tests for all three.
   **Progressive hint:** Normalize missing values to an explicit sentinel if missingness is a category; unseen categories generally receive the training global prior.
6. **Temporal leakage:** Design target encoding for timestamped events where later labels cannot inform earlier rows. Compare random K-fold encoding with an expanding-time implementation.
   **Progressive hint:** Sort by event time and compute each row's category statistics from strictly earlier labeled rows; handle ties deliberately.

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
