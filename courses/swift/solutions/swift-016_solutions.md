# swift-016: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-016_solution.swift](swift-016_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Combine repeated valid names:** Duplicate names are deliberately accumulated after validation. Pear totals 6 and apple totals 3.

**Keep rejection separate from zero:** This result preserves the difference between accepted zero, absence and invalid input. The valid zero remains present while three records are rejected.

## Task answers

### Task 1: Predict and explain

Trace each line through field count, name and quantity checks.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Duplicate names are deliberately accumulated after validation. Pear totals 6 and apple totals 3.

### Task 2: Guided modification

Add a valid duplicate and predict the new aggregate.

No separate reference answer has been written for this task. Start from Example B: This result preserves the difference between accepted zero, absence and invalid input. The valid zero remains present while three records are rejected.

### Task 3: Independent construction

Produce a sorted text report with accepted totals and rejected count.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
let result = importRows(["pear,2", "apple,3", "bad", "pear,1"])
var lines = result.counts.keys.sorted().map { "\($0): \(result.counts[$0]!)" }
lines.append("rejected: \(result.rejected)")
precondition(lines.joined(separator: "\n") == "apple: 3\npear: 3\nrejected: 1")
```

**Observe:** The report lists apple: 3, pear: 3 and rejected: 1.

Sorting the keys makes the report deterministic, and the rejected count is reported beside the totals instead of being dropped.

### Task 4: Diagnose a defect

Diagnose replacing failed Int parsing with zero.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Check field count before indexing. String splitting can omit empty fields unless configured, so this fixture preserves them deliberately. Production totals also need an overflow policy.

### Task 5: Boundary evidence

Test empty names, extra fields, zero and an empty input list.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Combine repeated valid names) and Example B (Keep rejection separate from zero).

### Task 6: Transfer and justify

Design a reusable result that retains safe line-specific reasons without storing raw sensitive input.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Admission**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A first useful Swift project combines optional parsing, value models, loops and deterministic reporting. The critical boundary is admission: malformed or negative quantities must not become accepted zero values. A report should separately account for valid quantities and rejected records.

The fixture uses in-memory lines and produces a value result, so it runs offline and is easy to test. External file loading can be added later as an adapter. Preserve a clear contract for duplicate names and ordering. The same small project will return in later lessons with Codable, async ownership and app presentation.

Split creates field substrings; convert them deliberately when storing long-lived names. Int parsing returns an optional. Dictionary default mutation accumulates admitted duplicates. sorted fixes presentation order.

Check field count before indexing. String splitting can omit empty fields unless configured, so this fixture preserves them deliberately. Production totals also need an overflow policy.

## Review before continuing

Run the reference and confirm that it prints `swift-016: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
