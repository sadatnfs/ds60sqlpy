# swift-036: Performance, copy costs and complexity

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-035`

## Learning objectives

Compare algorithm costs and copy behavior with evidence rather than assumptions. The central exercise is task 3: Compare repeated array scans with one built Set under the same identity policy.

## Purpose and mental model

Performance reasoning begins with the workload and the resource being measured. Array copy-on-write can make assignment cheap until mutation requires unique storage. Repeated front insertion still shifts elements and can dominate runtime regardless of that optimization. A collection's semantic convenience does not imply every operation has the same cost.

Use deterministic operation counts to explain algorithm growth, and use a prepared benchmark for elapsed-time claims. Warmup, optimization, allocation and system load can distort small measurements. Preserve correctness checks when comparing implementations. A faster result that omits validation or changes ordering is not an equivalent implementation.

## Vocabulary and concepts

**Complexity:** Growth of resource usage as workload size changes.

**Allocation:** Obtaining storage for values or objects.

**Benchmark equivalence:** Ensuring compared implementations satisfy the same contract.

## How to run this lesson

Both examples count work instead of timing it, so they behave identically on any machine and any optimization level. For task 3, count comparisons for the array scans and count the Set insertions separately. Task 4 is about benchmark design; describe the missing cost and add it to your measurement rather than timing anything in the pad.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

Set membership can replace repeated linear searches when an equality index is appropriate. reserveCapacity can reduce reallocations but does not change the algorithmic complexity of shifting elements.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Count a linear search

An exact operation count avoids fragile machine-speed assumptions.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let values = [2, 4, 6, 8]
      var comparisons = 0
      for value in values {
        comparisons += 1
        if value == 8 { break }
      }
      precondition(comparisons == 4)
    }
    print("swift-036: passed")
  }
}
```

**Observe:** The last-element search performs four comparisons.

**Trace.** `comparisons` starts at 0. The loop visits 2 and increments to 1, finding no match; it visits 4 and increments to 2; 6 makes 3; then 8 makes 4 and matches, so `break` ends the loop. Searching for the last element costs one comparison per element. Searching for 2 would cost 1, and searching for an absent 9 would cost 4 without ever breaking. Counting operations makes these three cases exact.

### Example B: Build a reusable membership index

Index construction and storage are costs that should be justified by repeated queries.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let index = Set([2, 4, 6, 8])
      precondition(index.contains(8) && !index.contains(9))
      precondition(index.count == 4)
    }
    print("swift-036: passed")
  }
}
```

**Observe:** The index preserves four identities and answers membership.

**Trace.** `Set([2, 4, 6, 8])` hashes each element once to build the index, which is the up-front cost. `contains(8)` hashes 8 and checks one bucket, so it does not scan the elements. `contains(9)` likewise returns false without visiting every element. `count` is 4 because the input had no duplicates; with `[2, 2, 4]`, the set would hold two elements. The index pays off only when many lookups share the construction cost.

## Exercises

1. **Predict and explain.** Count comparisons for first, last and absent targets.

2. **Guided modification.** Double input size and predict worst-case work.

3. **Independent construction.** Compare repeated array scans with one built Set under the same identity policy.

4. **Diagnose a defect.** Diagnose a benchmark that excludes index construction for a one-shot query.

5. **Boundary evidence.** Test duplicate inputs and empty workloads.

6. **Transfer and justify.** Write a measurement plan covering workload, correctness, optimization mode and allocation evidence.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Big-O is a growth model, not an elapsed-time promise. A single stopwatch observation is weak evidence. Avoid optimizing ownership complexity before measuring the real bottleneck.

Task 4's benchmark times only `contains` after building the set outside the timed region. For a single query that hides the dominant cost: building the set touches every element once, the same as one linear scan, plus hashing and allocation. The counterexample workload is exactly one lookup, where the plain scan wins. For task 5, an empty workload must cost zero comparisons in both designs.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Count a linear search) before changing anything, and confirm its observation: The last-element search performs four comparisons.
2. Compare Example B (Build a reusable membership index) with Example A and name the first line whose behavior differs. Its observation is: The index preserves four identities and answers membership.
3. Before opening the explanation, check your task 3 attempt (Compare repeated array scans with one built Set under the same identity policy) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

State the comparison counts for first, last and absent targets in a four-element array, then for eight elements. Explain when building a Set is worth its cost. Describe why a release build and a debug build can disagree on timing but must agree on operation counts and results.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): Look up `Set` and `Array.contains` in the standard library reference, where each method states its complexity, and review sets under Collection Types.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-036: Performance, copy costs and complexity.
Read courses/swift/guides/swift-036.md and courses/swift/lessons/swift-036.swift. Prerequisites: swift-035.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-036_solution.swift and
courses/swift/solutions/swift-036_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
