"""mle-017: worked starting point; complete the guide's six changes."""


def example_one():
    groups = {"A": {"tp": 8, "fn": 2, "fp": 1, "tn": 9}, "B": {"tp": 2, "fn": 3, "fp": 1, "tn": 4}}
    report = {}
    for name, c in groups.items():
        n = sum(c.values())
        report[name] = {
            "n": n,
            "tpr": c["tp"] / (c["tp"] + c["fn"]),
            "accuracy": (c["tp"] + c["tn"]) / n,
        }
    assert report["A"]["tpr"] == 0.8 and report["B"]["tpr"] == 0.4
    assert report["A"]["n"] == 20 and report["B"]["n"] == 10
    return {"slice_metrics": report, "metric_parity_alone_is_not_fairness": True}


if __name__ == "__main__":
    print(example_one())

# TODO 1: Identify the denominator of true-positive rate for each slice.
# TODO 2: Describe an appropriate uncertainty analysis for the slice comparison.
# TODO 3: State which decision the model is intended to support.
# TODO 4: Remove a field with no justified role in the interface.
# TODO 5: Identify who can accept a model and initiate rollback in a real setting.
# TODO 6: Explain why this card is not a compliance certificate.
