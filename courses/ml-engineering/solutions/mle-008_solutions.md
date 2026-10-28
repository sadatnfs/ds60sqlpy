# mle-008: explained reference

Package and use a single fitted preprocessing/model interface.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Reorder incoming fields

Use explicit named selections or validate a positional interface carefully. A raw array without a recorded order is easy to misuse.

**Expected:** The named-column pipeline preserves the intended values.

## 2. Add a missing numeric value

Retain the fitted imputer with the model and make missingness handling explicit. A successful imputation does not prove that the missingness mechanism is harmless.

**Expected:** The same training-derived policy is used in batch and serving.

## 3. Change a category

Decide whether to reject, map or encode unknown values. Document and test the same policy at training and serving boundaries.

**Expected:** Behavior matches the chosen encoder/API contract.

## 4. Inspect fitted state

Record the relevant pipeline/version with the model artifact. Recomputing those values from a later dataset changes the model.

**Expected:** They come only from training rows.

## 5. Design a parity fixture

Use normal, boundary and rejected cases. Compare errors as well as successful probabilities.

**Expected:** Both execution paths produce matching accepted outputs.

## 6. Separate correctness and quality

Use an appropriate evaluation design and independent data-contract checks in addition to parity. Consistency is necessary but not sufficient.

**Expected:** It does not establish predictive validity.

## Complete reference

```python
"""mle-008: local, bounded ML engineering investigation."""

import numpy as np
import pandas as pd


def dataset():
    rng = np.random.default_rng(17)
    n = 120
    usage = rng.uniform(1, 100, n)
    tickets = rng.poisson(2, n)
    region = np.where(np.arange(n) % 2 == 0, "north", "south")
    logit = 0.9 * tickets - 0.035 * usage + (region == "north") * 0.3
    probability = 1 / (1 + np.exp(-logit))
    label = (rng.random(n) < probability).astype(int)
    cutoff = np.arange(n) + 100
    return pd.DataFrame(
        {
            "id": np.arange(n),
            "customer_id": np.arange(n) % 12,
            "cutoff": cutoff,
            "available_at": cutoff - 2,
            "label_available_at": cutoff + 4,
            "usage": usage,
            "tickets": tickets,
            "region": region,
            "label": label,
        }
    )


def fit_pipeline(frame):
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    numeric = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    transform = ColumnTransformer(
        [
            ("numeric", numeric, ["usage", "tickets"]),
            ("region", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["region"]),
        ]
    )
    model = Pipeline(
        [("features", transform), ("classifier", LogisticRegression(max_iter=200, random_state=17))]
    )
    model.fit(frame[["usage", "tickets", "region"]], frame["label"])
    return model


def example_one():
    frame = dataset()
    train = frame[frame.label_available_at <= 180]
    sample = frame.iloc[[90, 91]]
    model = fit_pipeline(train)
    batch = model.predict_proba(sample[["usage", "tickets", "region"]])[:, 1]
    online = np.array(
        [
            model.predict_proba(pd.DataFrame([r]))[0, 1]
            for r in sample[["usage", "tickets", "region"]].to_dict("records")
        ]
    )
    assert np.allclose(batch, online, atol=1e-12)
    assert np.all((batch >= 0) & (batch <= 1))
    return {"batch_probabilities": batch.tolist(), "single_request_parity": True}


def example_two():
    from sklearn.preprocessing import StandardScaler

    training = np.array([[0.0], [2.0]])
    heldout = np.array([[100.0]])
    fitted = StandardScaler().fit(training)
    correct = fitted.transform(heldout).item()
    leaking = StandardScaler().fit(np.vstack([training, heldout])).transform(heldout).item()
    assert correct == 99.0 and abs(leaking - correct) > 90
    return {
        "training_mean": 1.0,
        "proper_transformed_value": correct,
        "leaking_transformed_value": leaking,
    }


def main():
    print(example_one())
    print(example_two())
    print("mle-008 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Package and use a single fitted preprocessing/model interface. Verify parity on contrasting request fixtures and retain the training population that estimated its state. Then evaluate predictive quality separately under the intended deployment design.
