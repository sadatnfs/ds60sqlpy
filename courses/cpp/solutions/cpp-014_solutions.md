# cpp-014: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

An auditable CLI is a command-line program whose inputs, accepted values, rejected records and output can be reconciled. Parsing and business validation are separate steps. Integer cents avoid decimal rounding ambiguity. The ledger keeps every input accounted for instead of silently discarding bad text.

## Detailed reasoning

Reconciliation is a conservation rule: input_count equals accepted_count plus rejected_count. The total alone is too weak because losing a valid zero changes count without changing money. Keep one ledger row for every raw input before grouping. The malformed suffix 25x is a useful negative control because a convenient prefix parser produces an apparently reasonable but incorrect amount. The capstone succeeds only when another learner can repeat both the normal result and the rejected shortcut.

## Worked example 1

```cpp
for (auto raw : {"10","0","bad","-2","25"}) { /* classify once */ }
```

Expected: Three accepted, two rejected, total 35.

## Worked example 2

```cpp
assert(parse_reading("0")==0); assert(!parse_reading("10x"));
```

Expected: Zero remains valid, while a numeric prefix with trailing junk is rejected.

## Exercise 1: Define the input contract

Write the grammar and rejection policy for the five rows.

**Expected:** Nonnegative base-10 whole fields; bad and -2 rejected.

**Reasoning:** Syntax and domain checks have separate reasons.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Implement the ledger

Store raw row, accepted value or rejection reason.

**Expected:** 5 ledger entries, 3 accepted, 2 rejected.

**Reasoning:** Every source row needs an accountable outcome.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Produce the report

Calculate accepted count and exact total.

**Expected:** accepted=3 rejected=2 total=35.

**Reasoning:** Counts and total are independent contracts.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Inject trailing junk

Replace 25 with 25x.

**Expected:** accepted=2 rejected=3 total=10.

**Reasoning:** Full consumption changes the row disposition.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Test empty input

Run no rows through the same pipeline.

**Expected:** 0 accepted, 0 rejected, total 0.

**Reasoning:** An empty valid file differs from a failed file open.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Hand off reproducibility

Package source, fixture, commands, test results and limitations.

**Expected:** Reviewer reproduces the 5-row ledger and failed suffix case.

**Reasoning:** The handoff needs observed statuses, not just source inspection.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
