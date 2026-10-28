"""Distribution change and matured-label evaluation are different observed quantities."""

from collections import Counter


def total_variation(reference, current):
    if not reference or not current:
        raise ValueError("Compare two nonempty observed populations")
    before, after = Counter(reference), Counter(current)
    return 0.5 * sum(
        abs(before[key] / len(reference) - after[key] / len(current))
        for key in before.keys() | after.keys()
    )


def evaluate(predictions, labels, cutoff, horizon):
    if type(horizon) is not int or horizon < 1:
        raise ValueError("Use a positive declared outcome horizon")
    if len({row["id"] for row in predictions}) != len(predictions) or len(
        {row["id"] for row in labels}
    ) != len(labels):
        raise ValueError("Evaluation requires unique prediction and label identities")
    available = {row["id"]: row for row in labels if row["known_day"] <= cutoff}
    eligible = [row for row in predictions if row["decision_day"] + horizon <= cutoff]
    joined = [
        {**row, "outcome": available[row["id"]]["outcome"] if row["id"] in available else None}
        for row in eligible
    ]
    observed = [row for row in joined if row["outcome"] is not None]
    correct = sum((row["probability"] >= 0.5) == row["outcome"] for row in observed)
    return {
        "eligible": len(eligible),
        "labelled": len(observed),
        "missing": len(joined) - len(observed),
        "coverage": len(observed) / len(eligible) if eligible else None,
        "accuracy_observed": correct / len(observed) if observed else None,
        "population": joined,
    }


def example_one():
    reference = ["north"] * 50 + ["south"] * 50
    current = ["north"] * 90 + ["south"] * 10
    drift = total_variation(reference, current)
    assert abs(drift - 0.4) < 1e-12
    before_correct = [True] * 90 + [False] * 10
    after_correct = [True] * 90 + [False] * 10
    assert (
        sum(before_correct) / len(before_correct) == sum(after_correct) / len(after_correct) == 0.9
    )
    return {
        "categorical_total_variation": drift,
        "reference_accuracy": 0.9,
        "current_accuracy": 0.9,
        "input_change_alone_does_not_prove_quality_loss": True,
        "labels_are_synthetic_observations_not_a_guarantee_about_future_data": True,
    }


def example_two():
    predictions = [
        {"id": str(day), "decision_day": day, "probability": 0.8} for day in range(1, 11)
    ]
    labels = [{"id": str(day), "known_day": day + 2, "outcome": day != 3} for day in range(1, 7)]
    labels += [
        {"id": "7", "known_day": 12, "outcome": False},
        {"id": "8", "known_day": 9, "outcome": True},
    ]
    result = evaluate(predictions, labels, cutoff=10, horizon=3)
    assert result["eligible"] == 7 and result["labelled"] == 6 and result["missing"] == 1
    assert result["coverage"] == 6 / 7 and result["accuracy_observed"] == 5 / 6
    assert result["population"][-1]["outcome"] is None
    naive = [row for row in labels if row["known_day"] <= 10]
    assert sum(row["outcome"] for row in naive) / len(naive) == 6 / 7
    return {
        "matured_cohort": result,
        "naive_available_label_accuracy": 6 / 7,
        "immature_known_label_excluded": "8",
        "late_unknown_label_retained_as_missing": "7",
    }


def main():
    from ds60sqlpy.plot_artifacts import publish_report, publish_table

    first, second = example_one(), example_two()
    print("Input shift without observed quality loss:", first)
    print("Maturity and missing labels define the evaluation population:", second)
    publish_table(
        ["id", "decision_day", "probability", "outcome"],
        [
            [row[name] for name in ["id", "decision_day", "probability", "outcome"]]
            for row in second["matured_cohort"]["population"]
        ],
        description=(
            "Seven eligible matured predictions retain six known labels and "
            "one explicit missing label; an immature known label is excluded."
        ),
    )
    publish_report(
        first,
        description=(
            "A controlled categorical shift of 0.4 accompanies unchanged "
            "observed accuracy of 0.9; drift is not itself a quality verdict."
        ),
    )


if __name__ == "__main__":
    main()
