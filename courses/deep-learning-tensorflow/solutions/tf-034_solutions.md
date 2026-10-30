# tf-034: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A robustness report records which conditions were actually tested and which failures occurred. It does not convert a finite list of successful checks into a guarantee. Group metrics need counts, because zero errors among one rare-group observation is very weak evidence. Perturbations should preserve the intended label when interpreted as robustness tests; otherwise they define a new task. Duplicate records can make a score look more certain without adding independent evidence. Privacy claims require their own mechanisms and analysis. The absence of names in a synthetic fixture, or a successful perturbation test, is not proof of differential privacy or production safety.

**Robustness:** Behavior under specified changes to inputs or conditions.

**Subgroup:** A declared subset whose performance is evaluated separately.

**Model card:** A structured account of intended use, evidence and limitations.

## Reading the implementation

Represent each result with a stable record ID, group, expected label and prediction. Aggregate integer errors and counts before calculating rates. Compare the set of unique IDs with row count to detect exact repetitions. Keep a model-card dictionary with intended use, evaluated units and untested conditions. A model card summarizes evidence; it is not itself a validation method.

## Exercise 1: Count errors by group

The question is: Use groupsA,A,B with predictions1,0,0 and truth1,1,0.

Both numerator and denominator are visible. Reporting only rates would conceal the fact that groupB has a single observation.

```python
rows = [("a", "A", 1, 1), ("b", "A", 1, 0), ("c", "B", 0, 0)]
report = {
    g: (sum(t != p for i, k, t, p in rows if k == g), sum(k == g for i, k, t, p in rows))
    for g in ["A", "B"]
}
assert report == {"A": (1, 2), "B": (0, 1)}
```

**Expected:** A1/2 errors; B0/1.

**Verify:** Compare the computed values or written argument with A1/2 errors; B0/1.

## Exercise 2: Expose duplicate confidence

The question is: Repeat the groupB row five times and compare row count with unique IDs.

Duplicating a correct observation can improve a row-weighted score without testing a new case. Identity-aware evaluation prevents artificial increases in apparent evidence.

```python
repeated = rows + [rows[-1]] * 5
assert len(repeated) == 8 and len({r[0] for r in repeated}) == 3
```

**Expected:** 8 rows but only3 unique IDs.

**Verify:** Compare the computed values or written argument with 8 rows but only3 unique IDs.

## Exercise 3: Evaluate fixed perturbations

The question is: Use f(x)=x>=0 with base1 and perturbations-.1,-.9,-1.1.

The last perturbation crosses the defined decision boundary. Whether it is a robustness failure depends on whether the label is supposed to remain unchanged under that shift.

```python
base = 1.0
shifts = [-0.1, -0.9, -1.1]
pred = [int(base + s >= 0) for s in shifts]
assert pred == [1, 1, 0]
```

**Expected:** first two retain class1; final perturbation changes to0.

**Verify:** Compare the computed values or written argument with first two retain class1; final perturbation changes to0.

## Exercise 4: Keep severities separate

The question is: Record one severe failure and nine minor passes; count severe failures independently of total pass rate.

A high average can hide a rare unacceptable outcome. The decision rule should state whether a severe failure blocks release regardless of the aggregate rate.

```python
severity = ["minor"] * 9 + ["severe"]
passed = [True] * 9 + [False]
assert sum(passed) / len(passed) == 0.9
assert sum(s == "severe" and not p for s, p in zip(severity, passed)) == 1
```

**Expected:** 90percent passes and 1 severe failure.

**Verify:** Compare the computed values or written argument with 90percent passes and 1 severe failure.

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

**Expected:** card includes count3 and an untested future-population condition.

**Verify:** Compare the computed values or written argument with card includes count3 and an untested future-population condition.

## Exercise 6: Reject an empty group rate

The question is: Compute a rate only when its group has observations.

No observations and zero observed failures are different states. Mapping both to zero would make an untested group look perfectly reliable.

```python
def rate(errors, count):
    return None if count == 0 else errors / count


assert rate(0, 0) is None and rate(0, 1) == 0
```

**Expected:** empty group producesNone, not0.

**Verify:** Compare the computed values or written argument with empty group producesNone, not0.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
