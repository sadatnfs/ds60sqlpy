"""mle-009: worked starting point; complete the guide's six changes."""

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


if __name__ == "__main__":
    print(example_one())

# TODO 1: Explain what a high AUC would and would not establish.
# TODO 2: Read the sample count in each displayed bin.
# TODO 3: Increase false-positive cost and recompute threshold utilities.
# TODO 4: Describe where thresholds should be selected.
# TODO 5: Remove an outcome and report evaluation coverage.
# TODO 6: Download or inspect the exact figure metadata and table.
