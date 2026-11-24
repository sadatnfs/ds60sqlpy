# mle-017: explained reference

Write a model card that is grounded in actual data, metrics and operational decisions.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Compute a denominator

Use tp+fn and retain the underlying counts. Accuracy uses a different denominator and can tell a different story.

Slice A has tp 8 and fn 2, so TPR is 8/10 = 0.8; slice B has tp 2 and fn 3, so TPR is 2/5 = 0.4. Dividing by n (20 and 10) would give 0.4 and 0.2, which are positive counts over all rows rather than recall. Accuracy is 17/20 = 0.85 for A and 6/10 = 0.6 for B. Notice that accuracy and TPR both rank A above B here, but they need not: a slice with many true negatives can have high accuracy and poor recall.

**Expected:** It counts actual positives, not all rows.

## 2. Add uncertainty

Use a method appropriate to the cohort and dependence structure, with the original denominators. Avoid a universal fairness conclusion from one noisy metric.

With only 10 and 5 actual positives, 95 percent Wilson intervals are roughly 0.49 to 0.94 for A and 0.12 to 0.77 for B, so they overlap substantially. A bootstrap over rows or an exact interval are reasonable choices, as long as the counts are reported.

**Expected:** It acknowledges small samples and the sampling/design assumptions.

## 3. Review the purpose

Name the population, action, alternatives and limitations. Changes in intended use require fresh evaluation rather than reusing the same card automatically.

The card names "optional support prioritization": the model ranks who might be offered help. Using the same scores to deny service would be a different decision with different harms and needs its own evaluation. Check the card against each proposed use and record a new review when the action changes.

**Expected:** The intended use is concrete.

## 4. Minimize inputs

Review feature necessity and potential harms. Preserve the decision and test rejected fields, rather than accepting arbitrary payloads.

Example_two compares request keys with card["features"] and gets {"email"}. Keep the allowlist in the card and the API schema and test that email is refused; quietly dropping it would hide that clients are sending it.

**Expected:** The accepted schema remains explicit.

## 5. Record operational ownership

Connect it to actual procedures, permissions and retained evidence. Do not describe this synthetic label as an implemented organizational process.

The card says owner "learning team" and rollback_version "v1". In a real setting name the role that may approve activation and the one that may roll back, and where that decision is logged. Writing "learning team" into a production card would imply an on-call rota and approval process that this fixture never implemented.

**Expected:** The responsibility is acknowledged outside the fixture.

## 6. Bound the claim

Use qualified governance processes and appropriate expertise for the real context. Keep this lesson's technical and statistical observations explicit.

The card records purpose, features, limits and a rollback version. Nothing in it shows legal review, consent or regulatory scope, so it supports review but does not replace it. A reader who sees a tidy card might assume approval happened; the field "not_a_legal_compliance_certificate" in example_two exists to block that reading, and the final report should repeat it in prose.

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

Retain slice denominators, stated limitations and a minimal input contract, and identify which external governance claims require separate review.
