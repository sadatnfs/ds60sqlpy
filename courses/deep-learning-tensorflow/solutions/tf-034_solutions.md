# tf-034: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A robustness report records which conditions were actually tested and which failures occurred. It does not convert a finite list of successful checks into a guarantee. Group metrics need counts, because zero errors among one rare-group observation is very weak evidence. Perturbations should preserve the intended label when interpreted as robustness tests; otherwise they define a new task. Duplicate records can make a score look more certain without adding independent evidence. Privacy claims require their own mechanisms and analysis. The absence of names in a synthetic fixture, or a successful perturbation test, is not proof of differential privacy or production safety.

**Robustness:** Behavior under specified changes to inputs or conditions.

**Subgroup:** A declared subset whose performance is evaluated separately.

**Model card:** A structured account of intended use, evidence and limitations.

## Reading the implementation

Represent each result with a stable record ID, group, expected label and prediction. Aggregate integer errors and counts before calculating rates. Compare the set of unique IDs with row count to detect exact repetitions. Keep a model-card dictionary with intended use, evaluated units and untested conditions. A model card summarizes evidence; it is not itself a validation method.

## Exercise 1: Count errors for three groups

The question is: Use rows (ID, group, truth, prediction): a A 1 1, b A 0 1, c B 1 1, d B 0 0, e C 1 0, f C 0 1, g C 1 1.

Each group keeps its own numerator and denominator, so the small groups remain visibly small. Group C has the most errors but also the most rows; the pair, not a pooled accuracy, is the report.

```python
rows3 = [
    ("a", "A", 1, 1),
    ("b", "A", 0, 1),
    ("c", "B", 1, 1),
    ("d", "B", 0, 0),
    ("e", "C", 1, 0),
    ("f", "C", 0, 1),
    ("g", "C", 1, 1),
]
report3 = {
    g: (sum(t != p for i, k, t, p in rows3 if k == g), sum(k == g for i, k, t, p in rows3))
    for g in ["A", "B", "C"]
}
assert report3 == {"A": (1, 2), "B": (0, 2), "C": (2, 3)}
```

**Expected:** group A 1/2, group B 0/2, group C 2/3 errors.

**Verify:** In a fresh process, the exercise checks confirm `report3 == {'A': (1, 2), 'B': (0, 2), 'C': (2, 3)}`.

## Exercise 2: Deduplicate before reporting

The question is: Append three more copies of row g, then compare group C counts by row and by unique ID.

Duplicated correct rows enlarge the denominator without adding evidence, halving the apparent error rate. Counting by unique ID restores the unit of evaluation.

```python
padded = rows3 + [rows3[-1]] * 3
unique = list({r[0]: r for r in padded}.values())
assert sum(k == "C" for i, k, t, p in padded) == 6 and sum(k == "C" for i, k, t, p in unique) == 3
assert sum(t != p for i, k, t, p in padded if k == "C") == 2
assert sum(t != p for i, k, t, p in unique if k == "C") == 2
```

**Expected:** C has 6 rows but 3 unique IDs; the row-level error rate 2/6 understates the 2/3 rate by ID.

**Verify:** In a fresh process, the exercise checks confirm `sum((k == 'C' for i, k, t, p in padded)) == 6`; `sum((k == 'C' for i, k, t, p in unique)) == 3`; `sum((t != p for i, k, t, p in padded if k == 'C')) == 2` and `sum((t != p for i, k, t, p in unique if k == 'C')) == 2`.

## Exercise 3: Evaluate fixed perturbations

The question is: Use f(x)=x>=0 with base 1 and perturbations -0.1, -0.9, -1.1.

The last perturbation crosses the defined decision boundary. Whether it is a robustness failure depends on whether the label is supposed to remain unchanged under that shift.

```python
base = 1.0
shifts = [-0.1, -0.9, -1.1]
pred = [int(base + s >= 0) for s in shifts]
assert pred == [1, 1, 0]
```

**Expected:** first two retain class 1; final perturbation changes to 0.

**Verify:** In a fresh process, the exercise checks confirm `pred == [1, 1, 0]`.

## Exercise 4: Keep severities separate

The question is: Record one severe failure and nine minor passes; count severe failures independently of total pass rate.

A high average can hide a rare unacceptable outcome. The decision rule should state whether a severe failure blocks release regardless of the aggregate rate.

```python
severity = ["minor"] * 9 + ["severe"]
passed = [True] * 9 + [False]
assert sum(passed) / len(passed) == 0.9
assert sum(s == "severe" and not p for s, p in zip(severity, passed)) == 1
```

**Expected:** 90 percent passes and 1 severe failure.

**Verify:** In a fresh process, the exercise checks confirm `sum(passed) / len(passed) == 0.9` and `sum((s == 'severe' and (not p) for s, p in zip(severity, passed))) == 1`.

## Exercise 5: Write bounded claims

The question is: Create a model card naming the three unique units and untested conditions.

Explicit limitations constrain how the results may be used. Declaring a missing guarantee is more informative than an unqualified claim that the model was checked.

```python
card = {
    "evaluation_units": 3,
    "intended_use": "synthetic teaching",
    "untested": ["future population", "private training data"],
    "privacy_guarantee": False,
}
assert (
    card["evaluation_units"] == 3
    and "future population" in card["untested"]
    and card["privacy_guarantee"] is False
)
```

**Expected:** card includes count 3 and an untested future-population condition.

**Verify:** In a fresh process, the exercise checks confirm `card['evaluation_units'] == 3`, `'future population' in card['untested']` and `card['privacy_guarantee'] is False`.

## Exercise 6: Reject an empty group rate

The question is: Compute a rate only when its group has observations.

No observations and zero observed failures are different states. Mapping both to zero would make an untested group look perfectly reliable.

```python
def rate(errors, count):
    return None if count == 0 else errors / count


assert rate(0, 0) is None and rate(0, 1) == 0
```

**Expected:** empty group produces None, not 0.

**Verify:** In a fresh process, the exercise checks confirm `rate(0, 0) is None` and `rate(0, 1) == 0`.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
