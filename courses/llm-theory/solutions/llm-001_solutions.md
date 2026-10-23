# llm-001: worked solutions

Open this reference after an attempt or an explicit reveal request. Preserve
your own version beside it. The [learner guide](../guides/llm-001.md) contains
the public fixture and its independent Expected/Verify contracts. These six
sections correspond to the same six learner actions, rather than six answer
steps for one task. A different implementation is acceptable when it preserves
the stated input policy, observations and evidence boundary.

The [executable reference](llm-001_solution.py) exposes a `verify()` helper for
authors and later comparison. It uses only local literals and the declared
Python/NumPy environment. An assertion failure should retain its actual input
and smallest failing observation. A passing reference is evidence about these
fixed cases; use a changed fixture and a closed-reference explanation before
recommending progression. The reading worksheet remains a reading exercise,
regardless of the optional arithmetic checker.

## Exercise 1: Classify six claims

A fixed mask blocking later keys and a score matrix having one row per query are mechanism claims about a specified computation. They require inspection and tests under the stated assumptions. A 2/3 correctness table and a fixture with no observed failures are empirical descriptions of finite observations. All future outputs are true and zero observed failures means zero possible risk overreach the evidence. Classification does not make an empirical claim strong by itself; the set, metric and unit still need inspection.

**Expected:** Mechanism, empirical, unsupported, empirical, unsupported, mechanism, in that order.

**Verify:** Write the evidence type and a test or counterexample next to all six statements; do not substitute a single reliability label.

## Exercise 2: Compute two accuracies

The record-weighted calculation averages [1,1,0], giving 2/3. Family A has mean 1 and family B has mean 0; equal-family weighting gives 1/2. These are different weighting rules over the same records. A reviewer needs both the table and the chosen policy to understand the report. Selecting whichever average makes a system look better after seeing results would be a form of evaluation selection, not a neutral change of formatting.

**Expected:** Record-weighted 2/3 and equal-family 1/2.

**Verify:** Inspect the three correctness values and the two separate family means before calculating the final averages.

## Exercise 3: Challenge fluent correctness

The arithmetic reference is 15, while the observed sentence asserts 13. It is linguistically fluent and factually incorrect under this explicit reference. That one counterexample is sufficient to refute a universal implication from fluency to truth. It does not establish that every generated answer is false or that fluency is never useful. Keep the inference proportional to the evidence: this case demonstrates a possible failure, and broader frequency claims require a defined sample.

**Expected:** It contradicts fluent answers are always correct; it does not show that every answer is false.

**Verify:** Record reference 15, observed 13 and the single failed equality as the counterexample.

## Exercise 4: Detect repeated evidence

A second copy of q1 has no new question identity. Rejecting a duplicate ID prevents accidental double counting from a repeated export or merge. Two different question IDs in the same source family can be legitimate records, but they are not automatically independent families. Keep both IDs and group them when the evaluation unit requires it. Silently deduplicating without reporting the policy could also discard meaningful repeated measurements, so the reference chooses an explicit failure for identical IDs.

**Expected:** A repeated question ID is rejected; related but distinct IDs must remain in their family for grouped evaluation.

**Verify:** Capture the duplicate-ID ValueError in the optional reference checker or identify the repeated row explicitly in writing.

## Exercise 5: Refuse an empty accuracy

An empty set has no mean correctness because its denominator is zero. Returning one would assert perfect performance without observations, and returning zero would confuse absence with measured failure. The reference raises ValueError. A written worksheet can state the same undefined status without running code. Follow the rejected case with the original valid table to confirm the checker does not change records or retain an erroneous global state after an invalid request.

**Expected:** The mean is undefined; the reference raises ValueError for an empty evaluation.

**Verify:** Retain the empty-set diagnosis and then recompute the original 2/3 table to show the valid result remains available.

## Exercise 6: Transfer to a new family balance

Three correct records from family A and one incorrect record from B give 3/4 by records. The two family means remain 1 and 0, so the equal-family average is 1/2. Report four observed questions from two authored families and the exact scoring rule. This table does not establish unseen-family accuracy, language-model factuality or complete-system safety. A fresh assessment should introduce held-out source families under a protocol chosen before inspecting which policy produces the preferred number.

**Expected:** Record-weighted accuracy 3/4; equal-family accuracy 1/2. The report names four records and two families.

**Verify:** Inspect a four-row table, both denominators and a statement that unseen families remain untested.

## Inspectable reference functions

The core functions below make the input and reduction policies explicit. The
separate executable file adds all six exercise checks. Do not replace a failed
assertion with a flattering default value or remove the invalid-input case.

```python
from __future__ import annotations


def evaluate(rows):
    rows = list(rows)
    if not rows:
        raise ValueError("nonempty question evaluation required")
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("duplicate question ID")
    if any(type(row["correct"]) is not bool for row in rows):
        raise TypeError("correct must be boolean")
    groups = {}
    for row in rows:
        groups.setdefault(row["family"], []).append(row["correct"])
    record = sum(row["correct"] for row in rows) / len(rows)
    family = sum(sum(values) / len(values) for values in groups.values()) / len(groups)
    return {
        "records": len(rows),
        "families": len(groups),
        "record_accuracy": record,
        "family_accuracy": family,
    }
```

## Retrieval and alternatives

Without the examples, distinguish a mechanism claim from an empirical claim using one new sentence each. Then explain how a family-weighted metric can differ from a record-weighted one without either calculation being arithmetically wrong.

After revealing this file, choose another fixture before treating the answer
as independent retrieval evidence. Explain why the rejected case is invalid,
not merely which exception class appeared. Alternative notation, array layout
or a direct calculation is welcome when its domain meaning and denominator
remain explicit. Keep implementation correctness separate from broad claims
about unseen model quality, reliability or safety.
