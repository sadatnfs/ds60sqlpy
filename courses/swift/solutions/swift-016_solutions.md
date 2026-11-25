# swift-016: explanation and comparison

Reference program: [swift-016_solution.swift](swift-016_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Combine repeated valid names:** Duplicate names are deliberately accumulated after validation. Pear totals 6 and apple totals 3.

**Keep rejection separate from zero:** This result preserves the difference between accepted zero, absence and invalid input. The valid zero remains present while three records are rejected.

## Task answers

### Task 1: Predict and explain

Trace each line through field count, name and quantity checks.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let lines = ["pear,2", "bad", ",3", "pear,x", "pear,-1", "apple,3"]
let verdicts = lines.map { importRows([$0]).rejected == 0 ? "ok" : "rejected" }
precondition(verdicts == ["ok", "rejected", "rejected", "rejected", "rejected", "ok"])
```

**Observe:** pear,2 and apple,3 pass; bad, ,3, pear,x and pear,-1 are rejected.

bad fails the two-field check, ,3 has an empty name, x fails Int parsing, and -1 fails the nonnegative check; each line stops at its first failed guard condition.

### Task 2: Guided modification

Add a valid duplicate and predict the new aggregate.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
let result = importRows(["pear,2", "apple,3", "pear,4", "apple,1"])
precondition(result.counts == ["pear": 6, "apple": 4])
precondition(result.rejected == 0)
```

**Observe:** Adding apple,1 raises apple to 4 while pear stays 6, with nothing rejected.

counts[name, default: 0] += quantity adds to an existing key instead of replacing it, so a duplicate name accumulates.

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

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
func lenientQuantity(_ text: Substring) -> Int { Int(text) ?? 0 }
precondition(lenientQuantity("no") == lenientQuantity("0"))
let result = importRows(["pear,0", "pear,no"])
precondition(result.counts == ["pear": 0] && result.rejected == 1)
```

**Observe:** The lenient parser makes no and 0 indistinguishable; the importer keeps pear at 0 and counts one rejection.

Int(text) ?? 0 turns malformed input into a valid-looking zero, hiding the defect; the importer's guard rejects the line so it is reported instead.

### Task 5: Boundary evidence

Test empty names, extra fields, zero and an empty input list.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
precondition(importRows([",2"]).rejected == 1)
precondition(importRows(["pear,2,extra"]).rejected == 1)
precondition(importRows(["pear,0"]).counts == ["pear": 0])
let empty = importRows([])
precondition(empty.counts.isEmpty && empty.rejected == 0)
```

**Observe:** An empty name and an extra field are each rejected, pear,0 is accepted as 0, and no input gives no counts and no rejections.

omittingEmptySubsequences: false keeps the empty name and the extra field visible to the field-count and name checks, and an empty list simply never enters the loop.

### Task 6: Transfer and justify

Design a reusable result that retains safe line-specific reasons without storing raw sensitive input.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** The helper `importRows` splits each line on commas without dropping empty fields, then admits a row only if it has exactly two fields, a non-empty name and a nonnegative integer quantity. Admitted rows are added into a dictionary with a default of 0; everything else increments `rejected`. The task 3 answer turns the result into a sorted text report.

**Why it is correct.** In Example A, pear appears twice with 2 and 4, so the dictionary accumulates 6, and apple holds 3 with nothing rejected. In Example B, `pear,0` is admitted as a real zero, while `bad` has one field, `apple,-1` is negative and `pear,no` does not parse, giving 3 rejections. An empty input yields an empty dictionary.

**A plausible wrong approach.** Replacing a failed parse with `Int(fields[1]) ?? 0` makes `pear,no` look like a valid zero, so the rejected count drops to 2 and the check on 3 fails. Indexing `fields[1]` before checking the field count would trap on `bad`, which has no second field.

**How to verify.** The task 3 report lists apple: 3, pear: 3 and rejected: 1. For task 5, add `,5` (empty name) and `pear,1,2` (extra field) to the Example B input and predict 5 rejections before running.

## Mechanism and diagnostic reasoning

A first useful Swift project combines optional parsing, value models, loops and deterministic reporting. The critical boundary is admission: malformed or negative quantities must not become accepted zero values. A report should separately account for valid quantities and rejected records.

The fixture uses in-memory lines and produces a value result, so it runs offline and is easy to test. External file loading can be added later as an adapter. Preserve a clear contract for duplicate names and ordering. The same small project will return in later lessons with Codable, async ownership and app presentation.

Split creates field substrings; convert them deliberately when storing long-lived names. Int parsing returns an optional. Dictionary default mutation accumulates admitted duplicates. sorted fixes presentation order.

Check field count before indexing. String splitting can omit empty fields unless configured, so this fixture preserves them deliberately. Production totals also need an overflow policy.

## Review before continuing

Run the reference and confirm it prints `swift-016: passed`, then rerun the guide's counterexample.
