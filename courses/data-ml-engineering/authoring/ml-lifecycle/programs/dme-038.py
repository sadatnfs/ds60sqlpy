"""Actual grouped evaluation, independent calibration and label-maturity cohorts."""

import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

from ds60sqlpy.plot_artifacts import publish_report


def example_one():
    entities = np.repeat(np.arange(80), 4)
    entity_labels = np.array([0, 1] * 40)
    labels = entity_labels[entities]
    frame = pd.DataFrame({"entity": [f"entity-{value:03}" for value in entities]})
    order = np.random.default_rng(2038).permutation(len(frame))
    random_train, random_test = order[:240], order[240:]
    grouped_train, grouped_test = next(
        GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=38).split(
            frame, labels, groups=entities
        )
    )
    assert not set(entities[grouped_train]) & set(entities[grouped_test])
    assert set(entities[random_train]) & set(entities[random_test])

    def evaluate(train, test):
        model = make_pipeline(
            OneHotEncoder(handle_unknown="ignore"), LogisticRegression(C=10000, random_state=38)
        )
        model.fit(frame.iloc[train], labels[train])
        return float(accuracy_score(labels[test], model.predict(frame.iloc[test])))

    row_score = evaluate(random_train, random_test)
    group_score = evaluate(grouped_train, grouped_test)
    assert row_score > 0.9 and row_score > group_score + 0.2
    return {
        "row_random_accuracy": row_score,
        "unseen_entity_accuracy": group_score,
        "row_random_shared_entities": len(set(entities[random_train]) & set(entities[random_test])),
        "grouped_shared_entities": 0,
        "target_population_for_group_score": "Previously unseen entities",
    }


def reliability(labels, probabilities, family):
    bins = np.digitize(probabilities, np.linspace(0, 1, 6)[1:-1])
    result = []
    for bucket in range(5):
        selected = bins == bucket
        if selected.any():
            result.append(
                {
                    "family": family,
                    "bin": bucket,
                    "rows": int(selected.sum()),
                    "mean_probability": float(probabilities[selected].mean()),
                    "positive_fraction": float(labels[selected].mean()),
                }
            )
    assert sum(row["rows"] for row in result) == len(labels)
    return result


def example_two():
    rng = np.random.default_rng(3038)
    time = np.arange(2000)
    signal = rng.normal(size=len(time))
    true_probability = 1 / (1 + np.exp(-(signal - 0.7)))
    labels = (rng.random(len(time)) < true_probability).astype(int)
    # Deliberately distorted score: calibration uses independent mature labels.
    raw_logit = 2.8 * (signal - 0.7) + 0.9
    raw_probability = 1 / (1 + np.exp(-raw_logit))
    label_available = time + np.where(labels == 1, 30, 1)
    calibration_rows = (time >= 600) & (time < 970) & (label_available <= 1000)
    future_rows = (time >= 1200) & (time < 1800)
    assert label_available[calibration_rows].max() <= 1000
    assert time[future_rows].min() > time[calibration_rows].max()
    assert label_available[future_rows].max() <= 1900
    calibrator = LogisticRegression(C=1000, random_state=38)
    calibrator.fit(raw_logit[calibration_rows, None], labels[calibration_rows])
    calibrated = calibrator.predict_proba(raw_logit[future_rows, None])[:, 1]
    actual, raw = labels[future_rows], raw_probability[future_rows]
    metrics = {
        "raw_brier": float(brier_score_loss(actual, raw)),
        "calibrated_brier": float(brier_score_loss(actual, calibrated)),
        "raw_log_loss": float(log_loss(actual, raw, labels=[0, 1])),
        "calibrated_log_loss": float(log_loss(actual, calibrated, labels=[0, 1])),
        "raw_auc": float(roc_auc_score(actual, raw)),
        "calibrated_auc": float(roc_auc_score(actual, calibrated)),
    }
    assert np.isclose(metrics["raw_brier"], np.mean((raw - actual) ** 2))
    assert all(np.isfinite(value) for value in metrics.values())
    assert calibrator.coef_[0, 0] > 0
    assert np.isclose(metrics["raw_auc"], metrics["calibrated_auc"])
    recent = (time >= 950) & (time < 1000)
    known_recent = recent & (label_available <= 1000)
    pending = int(np.sum(recent & (label_available > 1000)))
    assert pending > 0 and known_recent.sum() < recent.sum()
    rows = reliability(actual, raw, "Raw score") + reliability(
        actual, calibrated, "Calibrated score"
    )
    return {
        "metrics": metrics,
        "calibration_parameters": {
            "slope": float(calibrator.coef_[0, 0]),
            "intercept": float(calibrator.intercept_[0]),
        },
        "reliability": rows,
        "calibration_rows": int(calibration_rows.sum()),
        "future_evaluation_rows": int(future_rows.sum()),
        "recent_total": int(recent.sum()),
        "recent_known": int(known_recent.sum()),
        "recent_pending": pending,
        "observed_recent_positive_fraction": float(labels[known_recent].mean()),
        "eventual_recent_positive_fraction_simulation_oracle": float(labels[recent].mean()),
        "pending_labels_were_not_replaced_with_zero": True,
    }


def main():
    first, second = example_one(), example_two()
    figure = go.Figure()
    for family in ("Raw score", "Calibrated score"):
        rows = [row for row in second["reliability"] if row["family"] == family]
        figure.add_trace(
            go.Scatter(
                x=[r["mean_probability"] for r in rows],
                y=[r["positive_fraction"] for r in rows],
                mode="lines+markers",
                name=family,
            )
        )
    figure.add_trace(
        go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Reference: y = x", line={"dash": "dot"})
    )
    columns = ["family", "bin", "rows", "mean_probability", "positive_fraction"]
    figure.update_layout(
        title="Independent future evaluation with mature labels",
        xaxis_title="Mean predicted probability in a nonempty bin",
        yaxis_title="Observed positive fraction",
        meta={
            "description": "Reliability and row counts; y=x is a reference, not a sample.",
            "table": {
                "columns": columns,
                "rows": [[r[c] for c in columns] for r in second["reliability"]],
            },
        },
    )
    figure.show()
    publish_report(
        {"case_one": first, "case_two": second},
        description="Group-disjoint evaluation, calibration and delayed-label populations",
    )
    print(json.dumps({"case_one": first, "case_two": second}, allow_nan=False))
    print("dme-038: two evaluation cases passed")


if __name__ == "__main__":
    main()
