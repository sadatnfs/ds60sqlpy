# Day 51: Solutions: Advanced Feature Engineering (Target Encoding, Hashing, Groups)

**Offline teaching data:** The [original synthetic fixtures](../../../fixtures/README.md) replace first-run sample-data downloads. Their values are not historical or observational evidence. Keep numerical conclusions scoped to the declared teaching input.


We implement K‑fold target encoding without leakage, feature hashing for high‑cardinality categories, and rolling group statistics in time order.

Contents
- Exercise 1: K‑fold target encoding vs one‑hot
- Exercise 2: Feature hashing for IDs
- Exercise 3: Rolling group means in time without leakage

---

Setup
```python
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# Synthetic data
rng = np.random.default_rng(0)
df = pd.DataFrame(
    {
        "cat": rng.choice([f"c{i}" for i in range(100)], size=5_000),
        "num": rng.normal(size=5_000),
        "y": (rng.random(5_000) < 0.2).astype(int),
    }
)
train_df, test_df = train_test_split(
    df,
    test_size=0.2,
    random_state=0,
    stratify=df["y"],
)
train_df = train_df.reset_index(drop=True)
test_df = test_df.reset_index(drop=True)
```

Worked reference for Exercise 1; K‑fold target encoding
```python
def fit_target_map(cat: pd.Series, y: pd.Series, smoothing=10):
    """Fit smoothed category means and a prior using only these training rows."""
    if not cat.index.equals(y.index):
        raise ValueError("Category and target indexes must match in row order.")
    if len(y) == 0 or not np.isfinite(y.to_numpy(dtype=float)).all():
        raise ValueError("Training targets must be nonempty and finite.")
    if not np.isfinite(smoothing) or smoothing < 0:
        raise ValueError("Smoothing must be finite and nonnegative.")
    prior = float(y.mean())
    # Ignore unused levels; missing categories use the prior at transform time.
    stats = y.groupby(cat, observed=True, dropna=True).agg(["mean", "count"])
    mapping = (stats["mean"] * stats["count"] + prior * smoothing) / (stats["count"] + smoothing)
    return mapping, prior


def transform_target_encode(cat: pd.Series, mapping: pd.Series, prior: float):
    """Apply fitted statistics without reading targets for these new rows."""
    # Mapping a Categorical can retain its dtype. Convert before filling a prior.
    encoded = cat.map(mapping).astype(float).fillna(prior)
    if not np.isfinite(encoded.to_numpy()).all():
        raise ValueError("Encoded values must be finite.")
    return encoded


def kfold_target_encode(cat: pd.Series, y: pd.Series, n_splits=5, smoothing=10):
    """Return OOF features in source order; this is not an sklearn transformer."""
    if not cat.index.equals(y.index):
        raise ValueError("Category and target indexes must match in row order.")
    if len(y) == 0 or not np.isfinite(y.to_numpy(dtype=float)).all():
        raise ValueError("Training targets must be nonempty and finite.")
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    out = pd.Series(index=cat.index, dtype=float)
    for fit_positions, validation_positions in skf.split(cat, y):
        mapping, fold_prior = fit_target_map(
            cat.iloc[fit_positions], y.iloc[fit_positions], smoothing=smoothing
        )
        # Positional assignment preserves row order even for a shuffled index.
        out.iloc[validation_positions] = transform_target_encode(
            cat.iloc[validation_positions], mapping, fold_prior
        ).to_numpy()
    if not np.isfinite(out.to_numpy()).all():
        raise ValueError("Every training row must receive a finite OOF value.")
    return out


train_target_encoded = kfold_target_encode(train_df["cat"], train_df["y"], n_splits=5, smoothing=10)

# The holdout uses the same smoothing policy fitted on all training rows only.
training_mapping, training_prior = fit_target_map(train_df["cat"], train_df["y"], smoothing=10)
test_target_encoded = transform_target_encode(test_df["cat"], training_mapping, training_prior)

X_train_target = np.column_stack([train_df["num"], train_target_encoded])
X_test_target = np.column_stack([test_df["num"], test_target_encoded])
target_model = LogisticRegression(max_iter=1_000)
target_model.fit(X_train_target, train_df["y"])
target_auc = roc_auc_score(
    test_df["y"],
    target_model.predict_proba(X_test_target)[:, 1],
)

# A ColumnTransformer + Pipeline keeps one-hot fitting inside the training split.
one_hot_model = Pipeline(
    steps=[
        (
            "features",
            ColumnTransformer(
                transformers=[
                    (
                        "category",
                        OneHotEncoder(
                            handle_unknown="ignore",
                            sparse_output=True,
                        ),
                        ["cat"],
                    ),
                ],
                remainder="passthrough",
            ),
        ),
        ("classifier", LogisticRegression(max_iter=1_000)),
    ]
)
one_hot_model.fit(train_df[["cat", "num"]], train_df["y"])
one_hot_auc = roc_auc_score(
    test_df["y"],
    one_hot_model.predict_proba(test_df[["cat", "num"]])[:, 1],
)
print({"AUC_target_encoding": target_auc, "AUC_one_hot": one_hot_auc})
```
Explanation
- For each fold, fit both category statistics and the prior strictly on its training rows, then map its validation rows.
- Use `(count * mean + smoothing * prior) / (count + smoothing)` for both OOF and holdout mappings.
- Set `observed=True` to exclude unused categorical levels and `dropna=True` so missing values use the prior, as do unknown levels.
- Convert mapped categories to float before filling the prior; pandas may otherwise preserve categorical dtype and reject the fallback.
- Require aligned category/target indexes; assign folds by position and preserve source order and index.
- Learn the holdout mapping from training data only; never use holdout targets in encoding.
- `sparse_output=True` is the supported scikit-learn parameter (`sparse` was renamed)

The helpers are not a drop-in scikit-learn transformer. A fitted estimator must
produce OOF values during `fit_transform`, store the full-training map and prior,
and apply only that stored state during `transform`. Wrapping these functions
in `FunctionTransformer` alone does not establish that fitting contract.

OOF construction over a whole dataset before outer cross-validation is not
automatically leak-free: outer validation labels can enter other rows' maps or
priors. Recompute OOF features within each outer training partition, then fit
its validation mapping from that partition alone. Use an inner CV loop for
smoothing or split-choice tuning when reporting an outer CV score.

---

Worked reference for Exercise 2; Feature hashing
```python
from sklearn.feature_extraction import FeatureHasher

hasher = FeatureHasher(n_features=2**12, input_type="string")
train_categories = [[value] for value in train_df["cat"].astype(str)]
test_categories = [[value] for value in test_df["cat"].astype(str)]
X_train_hash = hasher.transform(train_categories)
X_test_hash = hasher.transform(test_categories)
X_train_hashed = sparse.hstack(
    [sparse.csr_matrix(train_df[["num"]].to_numpy()), X_train_hash],
    format="csr",
)
X_test_hashed = sparse.hstack(
    [sparse.csr_matrix(test_df[["num"]].to_numpy()), X_test_hash],
    format="csr",
)

hash_model = LogisticRegression(max_iter=1_000)
hash_model.fit(X_train_hashed, train_df["y"])
hash_auc = roc_auc_score(
    test_df["y"],
    hash_model.predict_proba(X_test_hashed)[:, 1],
)
print({"AUC_hashing": hash_auc})
```
Notes
- Hashing is stateless and memory‑safe; expect collisions but often acceptable
- With `input_type="string"`, give each sample an iterable of feature strings
- Adjust n_features to control dimensionality and collision rate

---

Worked reference for Exercise 3; Rolling group means in time without leakage
```python
# Add a time column and group id
T = len(df)
df = df.sample(frac=1.0, random_state=0).reset_index(drop=True)
df["ts"] = pd.date_range("2020-01-01", periods=T, freq="h")
df["group"] = rng.choice(list("ABC"), size=T)

# Sort by group then time for leakage‑safe transforms
df = df.sort_values(["group", "ts"]).reset_index(drop=True)
df["grp_roll_mean_y"] = df.groupby("group", observed=True)["y"].transform(
    lambda values: values.shift(1).rolling(24, min_periods=5).mean()
)

print(df[["group", "ts", "y", "grp_roll_mean_y"]].head(30))
```
Explanation
- shift(1) ensures the rolling window uses only past observations
- Sort by group, ts so rolling is chronological within each group
- `min_periods=5` intentionally leaves early rows as NaN until enough history exists

---

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **`groupby(category)[target].agg(['mean', 'count'])`:** builds category evidence only from the allowed training subset.
2. **`(count * mean + strength * prior) / (count + strength)`:** smooths low-support categories toward the training-wide prior.
3. **out-of-fold transform:** fits one map per training fold and writes values only to that fold's held-out rows.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** Out-of-fold construction prevents self-label leakage, while smoothing and the prior make low-support and unknown categories explicit.

**Useful alternative:** One-hot, hashing, count/frequency encoding, or learned embeddings avoid direct target statistics with different dimension and information trade-offs.

**Trade-off:** Target encoding is compact for high cardinality but adds leakage, split, smoothing, and drift risks.

**Edge case to test:** Singletons, all-missing categories, unseen values, multiclass targets, time-dependent meaning, and grouped duplicates need explicit policy.

**Evidence of correctness:** Prove each training row is excluded from its map, compare against one-hot on identical folds, test unseen/missing categories, and report category support plus smoothing.

When comparing your attempt with the reference, explain which of these
decisions your code made explicitly. If the reference makes a different
choice, compare the contracts and evidence before deciding that one
version is universally better.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Exercise 1: Original lesson practice

**Prompt:** Add K-fold target encoding to a scikit-learn pipeline through a custom transformer or `FunctionTransformer`.

**How to reason about it:** A target encoder needs distinct training and inference behavior. Training rows receive out-of-fold values; unseen rows receive a mapping fit on all allowed training rows, with index alignment tested explicitly.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 1; out-of-fold target encoding, smoothing, and transform-time unknowns; produce one out-of-fold encoded value per training row, assert that row's target was excluded from its category statistic, and test missing/unseen categories through the fitted pipeline without NaN or leakage.

### Exercise 2: Original lesson practice

**Prompt:** Add an appropriate prior and smoothing; experiment with `n_splits`.

**How to reason about it:** Smoothing blends category evidence with a global prior based on support. Test singleton, dominant, missing, and unseen categories and document the formula rather than treating library defaults as universal.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 2; out-of-fold target encoding, smoothing, and transform-time unknowns; print global prior, smoothing formula, n_splits, category count/support, and encoded values for rare/common/unseen categories; compare at least three n_splits values on identical folds.

### Exercise 3: Original lesson practice

**Prompt:** Compare ROC AUC with one-hot encoding across multiple seeded train/test splits.

**How to reason about it:** Compare one-hot and target encoding on exactly paired splits and multiple seeds. Target encoding may help high-cardinality features but adds leakage risk and operational state that score alone does not capture.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** Practice 3; out-of-fold target encoding, smoothing, and transform-time unknowns; over multiple declared seeded splits, print ROC-AUC pairs for target encoding and one-hot encoding plus mean/std/difference; keep all encoding fits inside each training fold.

### Exercise 4: Out-of-fold invariant

**Prompt:** Create a unique category for every training row and show that a leaky full-data target mean reproduces each label. Then prove that your out-of-fold encoder falls back to the prior instead.

**Reasoning before implementation:** For a category absent from the fold's training partition, there is no valid category statistic; use the fold training prior.

This is a powerful unit test: if unique-category training encodings equal the
targets, the implementation leaked. For each fold, fit category sums/counts and
the global prior on the other folds only, transform the held-out fold, and
restore original row order by index.

After generating all training encodings, fit a separate full-training mapping
for future validation/test/inference rows. Never replace the out-of-fold
training column with that full mapping.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Out-of-fold invariant; on unique-per-row categories, assert full-data encoding equals each label while every out-of-fold value equals the training-fold prior; print row, fold, label, leaky value, and OOF value.

### Exercise 5: Unknown and missing categories

**Prompt:** Define distinct policies for a missing category, an unseen category, and a known category with one observation. Write tests for all three.

**Reasoning before implementation:** Normalize missing values to an explicit sentinel if missingness is a category; unseen categories generally receive the training global prior.

Do not conflate missing with unseen unless that is the documented contract.
A missing sentinel can learn a smoothed value when present during training;
an unseen value has no support and should receive the fitted prior (and
optionally set an `is_unknown` indicator).

The singleton known category should be strongly shrunk toward the prior. Save
normalization, mapping, support counts, prior, and smoothing parameters in the
fitted transformer.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Unknown and missing categories; assert missing, unseen, one-observation-known, and well-supported-known fixtures return their separately documented prior/smoothed values without NaN; print support and mapping source for each.

### Exercise 6: Temporal leakage

**Prompt:** Design target encoding for timestamped events where later labels cannot inform earlier rows. Compare random K-fold encoding with an expanding-time implementation.

**Reasoning before implementation:** Sort by event time and compute each row's category statistics from strictly earlier labeled rows; handle ties deliberately.

Random folds can allow future outcomes to shape past features even though each
row is technically out of fold. Use forward-chaining splits or cumulative
category sums/counts shifted by one time block. Rows sharing a timestamp should
not leak into one another unless ordering within that timestamp is genuinely
known at prediction time.

Evaluate with a forward time split and preserve label-availability delay;
event time and label-arrival time may differ.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** Temporal leakage; print each event timestamp, training cutoff, category support, and encoded value under expanding time; assert no source label timestamp is later than the row cutoff and compare with random-K-fold leakage.
