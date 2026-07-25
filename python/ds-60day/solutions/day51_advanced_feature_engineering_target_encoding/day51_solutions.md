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
