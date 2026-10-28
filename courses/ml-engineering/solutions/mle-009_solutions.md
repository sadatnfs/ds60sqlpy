# mle-009: explained reference

Evaluate probabilities, ranking and actions with separately interpreted evidence.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Interpret a ranking score

A model can rank well but be poorly calibrated or unsuitable for a chosen action cost. Use evidence matched to the decision.

**Expected:** The answer distinguishes ranking from calibrated probabilities and utility.

## 2. Inspect calibration support

Add an appropriate uncertainty analysis for a real claim and consider subgroup/temporal variation. Do not overinterpret the visual smoothness.

**Expected:** Sparse bins remain visibly uncertain.

## 3. Change utility values

State the new values and compare the resulting actions. The model's ranking can remain unchanged while the useful policy changes.

**Expected:** The preferred action policy can change.

## 4. Protect the evaluation set

Evaluate the selected procedure with protected data or a design that includes selection. Keep the threshold choice in the recorded workflow.

**Expected:** The selection and final evaluation roles are separated.

## 5. Add a missing label

Do not silently evaluate only the easiest mature outcomes without reporting that selection. The monitoring lesson expands this issue.

**Expected:** The denominator and excluded population are explicit.

## 6. Check the figure source

Reconcile the plotted points and sample counts. A rendered chart does not establish that the split, labels or utility assumptions were valid.

**Expected:** The values agree with the underlying metric calculation.

## Complete reference

```python
"""mle-009: local, bounded ML engineering investigation."""

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
    from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score

    frame = dataset()
    train = frame[frame.label_available_at <= 180]
    test = frame[frame.cutoff >= 180]
    model = fit_pipeline(train)
    prob = model.predict_proba(test[["usage", "tickets", "region"]])[:, 1]
    metrics = {
        "brier": float(brier_score_loss(test.label, prob)),
        "log_loss": float(log_loss(test.label, prob)),
        "auc": float(roc_auc_score(test.label, prob)),
    }
    assert 0 <= metrics["brier"] <= 1 and metrics["log_loss"] >= 0 and 0 <= metrics["auc"] <= 1
    assert len(np.unique(test.label)) == 2
    assert int(test.label_available_at.max()) <= 224
    import plotly.graph_objects as go

    bins = np.linspace(0, 1, 6)
    table = []
    for i in range(5):
        selected = (prob >= bins[i]) & (prob <= bins[i + 1] if i == 4 else prob < bins[i + 1])
        if selected.any():
            table.append(
                [
                    float(bins[i]),
                    float(bins[i + 1]),
                    int(selected.sum()),
                    float(prob[selected].mean()),
                    float(test.label.to_numpy()[selected].mean()),
                ]
            )
    assert sum(row[2] for row in table) == len(test)
    figure = go.Figure(
        go.Scatter(
            x=[row[3] for row in table],
            y=[row[4] for row in table],
            mode="markers+lines",
            name="Synthetic held-out bins",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=[0, 1], y=[0, 1], mode="lines", line={"dash": "dash"}, name="Equality reference"
        )
    )
    figure.update_layout(
        title="Descriptive calibration after label maturity",
        xaxis_title="Mean predicted probability",
        yaxis_title="Observed positive share",
        meta={
            "description": (
                "Calibration bins for 40 synthetic future rows, all labels "
                "known by cutoff 224. No sampling interval is "
                "claimed."
            ),
            "table": {
                "columns": ["Lower", "Upper", "Rows", "Mean prediction", "Observed share"],
                "rows": table,
            },
        },
    )
    figure.show()
    return {"rows": len(test), "metrics": metrics, "not_a_deployment_decision_alone": True}


def example_two():
    y = np.array([0, 0, 1, 1])
    prob = np.array([0.1, 0.4, 0.6, 0.9])

    def utility(threshold):
        chosen = prob >= threshold
        return int(5 * np.sum(chosen & (y == 1)) - 2 * np.sum(chosen & (y == 0)))

    assert utility(0.3) == 8 and utility(0.5) == 10 and utility(0.8) == 5
    import plotly.graph_objects as go

    values = [[threshold, utility(threshold)] for threshold in (0.3, 0.5, 0.8)]
    figure = go.Figure(
        go.Bar(
            x=[str(row[0]) for row in values], y=[row[1] for row in values], name="Declared utility"
        )
    )
    figure.update_layout(
        title="Threshold utility on a fixed teaching fixture",
        xaxis_title="Decision threshold",
        yaxis_title="Utility units",
        meta={
            "description": (
                "Four labeled examples under benefit 5 and false-positive "
                "cost 2; these are declared teaching costs, not estimated "
                "business effects."
            ),
            "table": {"columns": ["Threshold", "Utility"], "rows": values},
        },
    )
    figure.show()
    return {
        "utilities": {str(t): utility(t) for t in (0.3, 0.5, 0.8)},
        "costs_are_declared_not_inferred": True,
    }


def main():
    print(example_one())
    print(example_two())
    print("mle-009 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Evaluate probabilities, ranking and actions with separately interpreted evidence. Retain the cohort, maturity cutoff, selected procedure and decision costs, and make figures auditable through their exact values. Use a broader design before making an external deployment claim.
