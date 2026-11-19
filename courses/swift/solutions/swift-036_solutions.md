# swift-036: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-036_solution.swift](swift-036_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Count a linear search:** An exact operation count avoids fragile machine-speed assumptions. The last-element search performs four comparisons.

**Build a reusable membership index:** Index construction and storage are costs that should be justified by repeated queries. The index preserves four identities and answers membership.

## Task answers

### Task 1: Predict and explain

Count comparisons for first, last and absent targets.

No separate reference answer has been written for this task. Example A is the evidence to compare with: An exact operation count avoids fragile machine-speed assumptions. The last-element search performs four comparisons.

### Task 2: Guided modification

Double input size and predict worst-case work.

No separate reference answer has been written for this task. Start from Example B: Index construction and storage are costs that should be justified by repeated queries. The index preserves four identities and answers membership.

### Task 3: Independent construction

Compare repeated array scans with one built Set under the same identity policy.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
let names = ["pear", "apple", "fig"]
let queries = ["fig", "kiwi", "pear"]
let scanHits = queries.filter { names.contains($0) }.count
let index = Set(names)
let indexHits = queries.filter { index.contains($0) }.count
precondition(scanHits == 2 && indexHits == scanHits)
```

**Observe:** Both approaches find 2 of the 3 queries.

The Set uses the same String equality as the scans, so it answers identically while replacing a linear search per query with one hash lookup.

### Task 4: Diagnose a defect

Diagnose a benchmark that excludes index construction for a one-shot query.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Big-O is a growth model, not an elapsed-time promise. A single stopwatch observation is weak evidence. Avoid optimizing ownership complexity before measuring the real bottleneck.

### Task 5: Boundary evidence

Test duplicate inputs and empty workloads.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Count a linear search) and Example B (Build a reusable membership index).

### Task 6: Transfer and justify

Write a measurement plan covering workload, correctness, optimization mode and allocation evidence.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Complexity**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Performance reasoning begins with the workload and the resource being measured. Array copy-on-write can make assignment cheap until mutation requires unique storage. Repeated front insertion still shifts elements and can dominate runtime regardless of that optimization. A collection's semantic convenience does not imply every operation has the same cost.

Use deterministic operation counts to explain algorithm growth, and use a prepared benchmark for elapsed-time claims. Warmup, optimization, allocation and system load can distort small measurements. Preserve correctness checks when comparing implementations. A faster result that omits validation or changes ordering is not an equivalent implementation.

Set membership can replace repeated linear searches when an equality index is appropriate. reserveCapacity can reduce reallocations but does not change the algorithmic complexity of shifting elements.

Big-O is a growth model, not an elapsed-time promise. A single stopwatch observation is weak evidence. Avoid optimizing ownership complexity before measuring the real bottleneck.

## Review before continuing

Run the reference and confirm that it prints `swift-036: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
