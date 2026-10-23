# cpp-014: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

An auditable CLI is a command-line program whose inputs, accepted values, rejected records and output can be reconciled. Parsing and business validation are separate steps. Integer cents avoid decimal rounding ambiguity. The ledger keeps every input accounted for instead of silently discarding bad text.

## Detailed reasoning

Reconciliation is a conservation rule: input_count equals accepted_count plus rejected_count. The total alone is too weak because losing a valid zero changes count without changing money. Keep one ledger row for every raw input before grouping. The malformed suffix 25x is a useful negative control because a convenient prefix parser produces an apparently reasonable but incorrect amount. The capstone succeeds only when another learner can repeat both the normal result and the rejected shortcut.

<!-- depth:start -->
## A small CLI with an explicit data contract

The capstone is a pipeline with boundaries: obtain raw lines, validate each field, classify each record, aggregate accepted values, then publish a report. Each stage has a different failure policy. A malformed row contributes to rejected count; a missing input file or exceeded input budget is a fatal operation failure. Treating both as an empty successful dataset would make operational errors indistinguishable from legitimate data.

The five-row fixture contains10, 0, bad, -2 and 25. Under the declared nonnegative integer grammar, three rows are accepted and two rejected. The accepted values sum to 35. The conservation equation accepted+rejected=input rows is an independent check: a correct total can still hide a dropped zero or an uncounted malformed row. Preserve all three report values rather than testing only the sum.

Parsing and aggregation should not be interleaved in a way that publishes partially trusted values. For10x, a prefix conversion may yield10, but full consumption fails and the row must not contribute. For0, optional presence is true even though the number is zero. For -2, integer parsing succeeds but the domain policy rejects negative readings. These are three different branches that the reference exercises.

The browser example uses an embedded deterministic vector. The separate executable reference also supports --input FILE for a host file-driven run. It caps row count and line length, checks open/read failures and returns status 2 for fatal errors. The ordinary successful report returns 0. A malformed row is counted under the declared report policy rather than necessarily aborting the whole file. That policy must be stated, because strict-all-or-nothing ingestion would be a different product.

File format is part of the interface. These fixtures are one decimal reading per line, not CSV with headers, quoted fields or comma-separated records. A filename ending in csv does not turn the parser into a CSV implementation. The working directory controls relative path resolution, while the command-line argument chooses the file. Keep the source path, executable path and input path distinct in the handoff.

A bounded program also needs a publication rule. The report should be emitted only after the reader has finished within its budget and any fatal I/O condition has been checked. Otherwise a caller may mistake a partial total printed before a later failure for the final answer. The capstone's fixed output schema gives another program an inspectable contract without requiring it to infer meaning from a mixture of progress text and data.

## Debugging the contract

When total35 passes but counts do not, inspect zero handling and rejected-row accounting. When a missing file reports success, check the file-open guard and process exit code. When a suffix is accepted, inspect both from_chars outputs. When a large input consumes too much memory before rejection, enforce line/row budgets during reading rather than after loading the entire file. A learner should be able to explain which errors are per-record rejections and which prevent publication of any final report.
<!-- depth:end -->

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
