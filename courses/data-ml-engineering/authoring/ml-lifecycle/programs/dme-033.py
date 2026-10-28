"""A decision baseline, validation-only threshold selection and held-out cohorts."""

import json

import numpy as np
import plotly.graph_objects as go
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from ds60sqlpy.plot_artifacts import publish_table


def counts(labels, predictions):
    labels, predictions = np.asarray(labels), np.asarray(predictions)
    false_negative = int(np.sum((labels == 1) & (predictions == 0)))
    false_positive = int(np.sum((labels == 0) & (predictions == 1)))
    rows = len(labels)
    assert rows > 0
    return {
        "rows": rows,
        "positives": int(labels.sum()),
        "false_negatives": false_negative,
        "false_positives": false_positive,
        "accuracy": float(np.mean(labels == predictions)),
        "cost_per_row": (9 * false_negative + false_positive) / rows,
    }


def example_one():
    rng = np.random.default_rng(2033)
    groups = rng.integers(0, 2, 2048)
    features = rng.normal(size=(2048, 2))
    features[:, 1] += 0.8 * groups
    logits = 1.6 * features[:, 0] - 0.8 * features[:, 1] - 2.0 + 0.7 * groups
    probabilities = 1 / (1 + np.exp(-logits))
    labels = (rng.random(2048) < probabilities).astype(int)
    order = rng.permutation(len(labels))
    train, validation, test = order[:1024], order[1024:1536], order[1536:]
    assert not set(train) & set(validation) and not set(train) & set(test)
    assert not set(validation) & set(test)
    model = make_pipeline(StandardScaler(), LogisticRegression(random_state=33))
    model.fit(features[train], labels[train])
    baseline = DummyClassifier(strategy="most_frequent").fit(features[train], labels[train])
    validation_probability = model.predict_proba(features[validation])[:, 1]
    curve = []
    for threshold in np.round(np.arange(0.05, 0.96, 0.05), 2):
        metrics = counts(labels[validation], validation_probability >= threshold)
        curve.append({"threshold": float(threshold), **metrics})
    selected = min(curve, key=lambda row: (row["cost_per_row"], row["threshold"]))
    default_validation = next(row for row in curve if row["threshold"] == 0.5)
    assert selected["cost_per_row"] <= default_validation["cost_per_row"]
    test_probability = model.predict_proba(features[test])[:, 1]
    learned = counts(labels[test], test_probability >= selected["threshold"])
    majority = counts(labels[test], baseline.predict(features[test]))
    assert majority["false_positives"] == 0 and majority["false_negatives"] == majority["positives"]
    return {
        "summary": {
            "train_rows": len(train),
            "validation_rows": len(validation),
            "test_rows": len(test),
            "selected_threshold": selected["threshold"],
            "selected_on_validation_only": True,
            "majority_baseline": majority,
            "held_out_learned_decision": learned,
        },
        "curve": curve,
        "test_rows": [
            {"group": int(group), "label": int(label), "probability": float(probability)}
            for group, label, probability in zip(
                groups[test], labels[test], test_probability, strict=True
            )
        ],
    }


def example_two(first=None):
    first = example_one() if first is None else first
    threshold = first["summary"]["selected_threshold"]
    rows = first["test_rows"]
    cohorts = []
    for group in (0, 1):
        selected = [row for row in rows if row["group"] == group]
        metrics = counts(
            [row["label"] for row in selected],
            [row["probability"] >= threshold for row in selected],
        )
        cohorts.append({"cohort": f"group {group}", **metrics})
    assert sum(row["rows"] for row in cohorts) == len(rows)
    reconstructed = sum(row["cost_per_row"] * row["rows"] for row in cohorts) / len(rows)
    original = first["summary"]["held_out_learned_decision"]["cost_per_row"]
    assert np.isclose(reconstructed, original)
    shifted_mix = 0.1 * cohorts[0]["cost_per_row"] + 0.9 * cohorts[1]["cost_per_row"]
    return {
        "cohorts": cohorts,
        "original_cost_per_row": original,
        "reweighted_10_90_cost_per_row": shifted_mix,
        "reweighting_assumes_unchanged_within_group_performance": True,
        "threshold_reselected_on_test": False,
    }


def main():
    first = example_one()
    second = example_two(first)
    curve = first["curve"]
    figure = go.Figure(
        go.Scatter(
            x=[row["threshold"] for row in curve],
            y=[row["cost_per_row"] for row in curve],
            mode="lines+markers",
            name="Validation cost per row",
        )
    )
    figure.update_layout(
        title="Select a decision threshold using validation data only",
        xaxis_title="Probability threshold",
        yaxis_title="Synthetic cost units per validation row",
        meta={
            "description": "Validation cost: false negatives cost nine; false positives cost one.",
            "table": {
                "columns": ["threshold", "false negatives", "false positives", "cost per row"],
                "rows": [
                    [r["threshold"], r["false_negatives"], r["false_positives"], r["cost_per_row"]]
                    for r in curve
                ],
            },
        },
    )
    figure.show()
    columns = ["cohort", "rows", "positives", "false_negatives", "false_positives", "cost_per_row"]
    publish_table(
        columns,
        [[row[column] for column in columns] for row in second["cohorts"]],
        description="Disjoint held-out cohorts at the unchanged validation-selected threshold",
    )
    print(json.dumps({"case_one": first["summary"], "case_two": second}, allow_nan=False))
    print("dme-033: two decision cases passed")


if __name__ == "__main__":
    main()
