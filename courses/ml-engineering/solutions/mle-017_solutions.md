# mle-017: explained reference

Write a model card that is grounded in actual data, metrics and operational decisions.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Compute a denominator

Use tp+fn and retain the underlying counts. Accuracy uses a different denominator and can tell a different story.

**Expected:** It counts actual positives, not all rows.

## 2. Add uncertainty

Use a method appropriate to the cohort and dependence structure, with the original denominators. Avoid a universal fairness conclusion from one noisy metric.

**Expected:** It acknowledges small samples and the sampling/design assumptions.

## 3. Review the purpose

Name the population, action, alternatives and limitations. Changes in intended use require fresh evaluation rather than reusing the same card automatically.

**Expected:** The intended use is concrete.

## 4. Minimize inputs

Review feature necessity and potential harms. Preserve the decision and test rejected fields, rather than accepting arbitrary payloads.

**Expected:** The accepted schema remains explicit.

## 5. Record operational ownership

Connect it to actual procedures, permissions and retained evidence. Do not describe this synthetic label as an implemented organizational process.

**Expected:** The responsibility is acknowledged outside the fixture.

## 6. Bound the claim

Use qualified governance processes and appropriate expertise for the real context. Keep this lesson's technical and statistical observations explicit.

**Expected:** The answer separates documentation from external requirements and review.

## Complete reference

```python
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
```

## Interpretation

Write a model card that is grounded in actual data, metrics and operational decisions. Retain slice denominators, stated limitations and a minimal input contract, and identify which external governance claims require separate review.
