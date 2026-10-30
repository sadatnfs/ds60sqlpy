# swift-036: Performance, copy costs and complexity

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-035`

## Learning objectives

Compare repeated array scans with one built Set under the same identity policy. Then write a measurement plan covering workload, correctness, optimization mode and allocation evidence.

## Purpose and mental model

Performance reasoning begins with the workload and the resource being measured. Array copy-on-write can make assignment cheap until mutation requires unique storage. Repeated front insertion still shifts elements and can dominate runtime regardless of that optimization. A collection's semantic convenience does not imply every operation has the same cost.

Use deterministic operation counts to explain algorithm growth, and use a prepared benchmark for elapsed-time claims. Warmup, optimization, allocation and system load can distort small measurements. Preserve correctness checks when comparing implementations. A faster result that omits validation or changes ordering is not an equivalent implementation.

## Vocabulary and concepts

**Complexity:** Growth of resource usage as workload size changes.

**Allocation:** Obtaining storage for values or objects.

**Benchmark equivalence:** Ensuring compared implementations satisfy the same contract.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

Set membership can replace repeated linear searches when an equality index is appropriate. reserveCapacity can reduce reallocations but does not change the algorithmic complexity of shifting elements.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

## Exercises

1. **Predict and explain.** Count comparisons for first, last and absent targets.

2. **Guided modification.** Double input size and predict worst-case work.

3. **Independent construction.** Compare repeated array scans with one built Set under the same identity policy.

4. **Diagnose a defect.** Diagnose a benchmark that excludes index construction for a one-shot query.

5. **Boundary evidence.** Test duplicate inputs and empty workloads.

6. **Transfer and justify.** Write a measurement plan covering workload, correctness, optimization mode and allocation evidence.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Big-O is a growth model, not an elapsed-time promise. A single stopwatch observation is weak evidence. Avoid optimizing ownership complexity before measuring the real bottleneck.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Complexity, Allocation, Benchmark equivalence without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
