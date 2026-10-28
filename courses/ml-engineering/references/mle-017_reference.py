"""mle-017: local, bounded ML engineering investigation."""


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


def example_two():
    card = {
        "purpose": "optional support prioritization",
        "features": ["usage", "tickets", "region"],
        "excluded": ["email", "free_text"],
        "owner": "learning team",
        "limits": ["synthetic population", "delayed labels"],
        "rollback_version": "v1",
    }
    request = {"usage": 10, "tickets": 2, "region": "north", "email": "learner@example.invalid"}
    allowed = set(card["features"])
    rejected = set(request) - allowed
    assert rejected == {"email"} and card["rollback_version"] == "v1" and card["limits"]
    return {
        "rejected_fields": sorted(rejected),
        "review_card": card,
        "not_a_legal_compliance_certificate": True,
    }


def main():
    print(example_one())
    print(example_two())
    print("mle-017 reference checks passed")


if __name__ == "__main__":
    main()
