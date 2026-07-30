# Day 51 — Solutions: Advanced Feature Engineering (Target Encoding, Hashing, Groups)

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
from sklearn.model_selection import KFold, train_test_split
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

Exercise 1 — K‑fold target encoding
```python
kf = KFold(n_splits=5, shuffle=True, random_state=0)
train_target_encoded = pd.Series(index=train_df.index, dtype=float)

for fit_indices, validation_indices in kf.split(train_df):
    fold_fit = train_df.iloc[fit_indices]
    category_means = fold_fit.groupby("cat")["y"].mean()
    fold_global_mean = fold_fit["y"].mean()
    train_target_encoded.iloc[validation_indices] = (
        train_df.iloc[validation_indices]["cat"]
        .map(category_means)
        .fillna(fold_global_mean)
    )

# The holdout is transformed only with statistics learned from all training rows.
training_category_means = train_df.groupby("cat")["y"].mean()
training_global_mean = train_df["y"].mean()
test_target_encoded = (
    test_df["cat"].map(training_category_means).fillna(training_global_mean)
)

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
- For each fold, compute category→mean strictly on training indices, then map to validation
- Fill unknowns with global mean from training fold
- Learn the holdout mapping from training data only; never use holdout targets in encoding
- `sparse_output=True` is the supported scikit-learn parameter (`sparse` was renamed)

---

Exercise 2 — Feature hashing
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

Exercise 3 — Rolling group means in time without leakage
```python
# Add a time column and group id
T = len(df)
df = df.sample(frac=1.0, random_state=0).reset_index(drop=True)
df["ts"] = pd.date_range("2020-01-01", periods=T, freq="h")
df["group"] = rng.choice(list("ABC"), size=T)

# Sort by group then time for leakage‑safe transforms
df = df.sort_values(["group", "ts"]).reset_index(drop=True)
df["grp_roll_mean_y"] = df.groupby("group")["y"].transform(
    lambda values: values.shift(1).rolling(24, min_periods=5).mean()
)

print(df[["group", "ts", "y", "grp_roll_mean_y"]].head(30))
```
Explanation
- shift(1) ensures the rolling window uses only past observations
- Sort by group, ts so rolling is chronological within each group
- `min_periods=5` intentionally leaves early rows as NaN until enough history exists

---

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Exercise 1 — Original lesson practice

**Prompt:** Add K-fold target encoding to a scikit-learn pipeline through a custom transformer or `FunctionTransformer`.

**How to reason about it:** A target encoder needs distinct training and inference behavior. Training rows receive out-of-fold values; unseen rows receive a mapping fit on all allowed training rows, with index alignment tested explicitly.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 2 — Original lesson practice

**Prompt:** Add an appropriate prior and smoothing; experiment with `n_splits`.

**How to reason about it:** Smoothing blends category evidence with a global prior based on support. Test singleton, dominant, missing, and unseen categories and document the formula rather than treating library defaults as universal.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 3 — Original lesson practice

**Prompt:** Compare ROC AUC with one-hot encoding across multiple seeded train/test splits.

**How to reason about it:** Compare one-hot and target encoding on exactly paired splits and multiple seeds. Target encoding may help high-cardinality features but adds leakage risk and operational state that score alone does not capture.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 4 — Out-of-fold invariant

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

### Exercise 5 — Unknown and missing categories

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

### Exercise 6 — Temporal leakage

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
