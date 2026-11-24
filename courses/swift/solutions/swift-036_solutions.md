# swift-036: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-036_solution.swift](swift-036_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Count a linear search:** An exact operation count avoids fragile machine-speed assumptions. The last-element search performs four comparisons.

**Build a reusable membership index:** Index construction and storage are costs that should be justified by repeated queries. The index preserves four identities and answers membership.

## Task answers

### Task 1: Predict and explain

Count comparisons for first, last and absent targets.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
func comparisons(_ values: [Int], _ target: Int) -> Int {
  var count = 0
  for value in values {
    count += 1
    if value == target { break }
  }
  return count
}
let values = [2, 4, 6, 8]
precondition(comparisons(values, 2) == 1)
precondition(comparisons(values, 8) == 4)
precondition(comparisons(values, 9) == 4)
```

**Observe:** Finding the first element takes 1 comparison, the last takes 4, and an absent target also takes 4.

A linear scan stops at a match, so its cost depends on position; an absent target is the worst case because every element must be checked.

### Task 2: Guided modification

Double input size and predict worst-case work.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
func worstCase(_ values: [Int]) -> Int {
  var count = 0
  for value in values {
    count += 1
    if value == -1 { break }
  }
  return count
}
let small = [2, 4, 6, 8]
let large = small + [10, 12, 14, 16]
precondition(worstCase(small) == 4 && worstCase(large) == 8)
```

**Observe:** Doubling the input from 4 to 8 elements doubles the absent-target comparisons from 4 to 8.

Worst-case linear search does one comparison per element, so its work grows in proportion to n.

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

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
let values = Array(1...1000)
var scanWork = 0
for value in values {
  scanWork += 1
  if value == 3 { break }
}
let index = Set(values)
let buildWork = values.count
precondition(index.contains(3) && scanWork == 3 && buildWork == 1000)
```

**Observe:** A single query for 3 scans 3 elements, while building the Set alone touches all 1,000.

For one query, the index costs more to build than the scan it replaces; a benchmark that times only contains hides that cost, and building only pays off over many lookups.

### Task 5: Boundary evidence

Test duplicate inputs and empty workloads.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
let duplicates = [2, 2, 4]
precondition(Set(duplicates).count == 2 && duplicates.count == 3)
precondition(Set(duplicates).contains(2))
let empty: [Int] = []
precondition(!empty.contains(1) && Set(empty).isEmpty)
```

**Observe:** Three inputs with a repeated 2 give a Set of 2 members that still answers contains(2); the empty workload finds nothing.

Set membership collapses duplicates, which preserves yes or no answers but not counts, and an empty input does no comparisons in either strategy.

### Task 6: Transfer and justify

Write a measurement plan covering workload, correctness, optimization mode and allocation evidence.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Compare repeated array scans with one built Set under the same identity policy) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** Example A counts comparisons in a linear search for 8 in `[2, 4, 6, 8]`, breaking on the match. Example B builds a `Set` from the same values once and then answers membership queries. The task 3 answer compares repeated array scans with a single built Set over the same three queries.

**Why it is correct.** 8 is the last element, so the loop compares 2, 4, 6 and 8 and counts 4. Building the Set touches each of the four values once, after which `contains` checks are average constant time; `count` is 4 because all values are distinct. Both approaches in task 3 find 2 of the 3 queries, which shows they agree before any cost is compared.

**A plausible wrong approach.** Timing only the `contains` calls and leaving out the cost of `Set([2, 4, 6, 8])` is the task 4 defect: for a single query the build step is the main cost, so the benchmark favors the Set unfairly. Comparing one stopwatch reading from a debug build is also weak evidence.

**How to verify.** For task 1, a first-element target gives 1 comparison and an absent target gives 4. For task 2, double the input to eight values and predict 8 comparisons in the worst case. For task 5, `Set([2, 2, 4]).count` is 2.

## Mechanism and diagnostic reasoning

Performance reasoning begins with the workload and the resource being measured. Array copy-on-write can make assignment cheap until mutation requires unique storage. Repeated front insertion still shifts elements and can dominate runtime regardless of that optimization. A collection's semantic convenience does not imply every operation has the same cost.

Use deterministic operation counts to explain algorithm growth, and use a prepared benchmark for elapsed-time claims. Warmup, optimization, allocation and system load can distort small measurements. Preserve correctness checks when comparing implementations. A faster result that omits validation or changes ordering is not an equivalent implementation.

Set membership can replace repeated linear searches when an equality index is appropriate. reserveCapacity can reduce reallocations but does not change the algorithmic complexity of shifting elements.

Big-O is a growth model, not an elapsed-time promise. A single stopwatch observation is weak evidence. Avoid optimizing ownership complexity before measuring the real bottleneck.

## Review before continuing

Run the reference and confirm that it prints `swift-036: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
