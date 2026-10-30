# swift-016: Foundation project: an honest inventory importer

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-015`

## Learning objectives

Produce a sorted text report with accepted totals and rejected count. Then design a reusable result that retains safe line-specific reasons without storing raw sensitive input.

## Purpose and mental model

A first useful Swift project combines optional parsing, value models, loops and deterministic reporting. The critical boundary is admission: malformed or negative quantities must not become accepted zero values. A report should separately account for valid quantities and rejected records.

The fixture uses in-memory lines and produces a value result, so it runs offline and is easy to test. External file loading can be added later as an adapter. Preserve a clear contract for duplicate names and ordering. The same small project will return in later lessons with Codable, async ownership and app presentation.

## Vocabulary and concepts

**Admission:** The decision to accept a record into domain processing.

**Aggregation:** Combining accepted values under shared keys.

**Rejection evidence:** A retained description or count of excluded inputs.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

Split creates field substrings; convert them deliberately when storing long-lived names. Int parsing returns an optional. Dictionary default mutation accumulates admitted duplicates. sorted fixes presentation order.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Combine repeated valid names

Duplicate names are deliberately accumulated after validation.

```swift
import Foundation

func importRows(_ lines: [String]) -> (counts: [String: Int], rejected: Int) {
  var counts: [String: Int] = [:]
  var rejected = 0
  for line in lines {
    let fields = line.split(separator: ",", omittingEmptySubsequences: false)
    guard fields.count == 2, !fields[0].isEmpty, let quantity = Int(fields[1]), quantity >= 0 else {
      rejected += 1
      continue
    }
    counts[String(fields[0]), default: 0] += quantity
  }
  return (counts, rejected)
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let result = importRows(["pear,2", "apple,3", "pear,4"])
      precondition(result.counts == ["pear": 6, "apple": 3])
      precondition(result.rejected == 0)
    }
    print("swift-016: passed")
  }
}
```

**Observe:** Pear totals 6 and apple totals 3.

### Example B: Keep rejection separate from zero

This result preserves the difference between accepted zero, absence and invalid input.

```swift
import Foundation

func importRows(_ lines: [String]) -> (counts: [String: Int], rejected: Int) {
  var counts: [String: Int] = [:]
  var rejected = 0
  for line in lines {
    let fields = line.split(separator: ",", omittingEmptySubsequences: false)
    guard fields.count == 2, !fields[0].isEmpty, let quantity = Int(fields[1]), quantity >= 0 else {
      rejected += 1
      continue
    }
    counts[String(fields[0]), default: 0] += quantity
  }
  return (counts, rejected)
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let result = importRows(["pear,0", "bad", "apple,-1", "pear,no"])
      precondition(result.counts == ["pear": 0])
      precondition(result.rejected == 3)
      precondition(importRows([]).counts.isEmpty)
    }
    print("swift-016: passed")
  }
}
```

**Observe:** The valid zero remains present while three records are rejected.

## Exercises

1. **Predict and explain.** Trace each line through field count, name and quantity checks.

2. **Guided modification.** Add a valid duplicate and predict the new aggregate.

3. **Independent construction.** Produce a sorted text report with accepted totals and rejected count.

4. **Diagnose a defect.** Diagnose replacing failed Int parsing with zero.

5. **Boundary evidence.** Test empty names, extra fields, zero and an empty input list.

6. **Transfer and justify.** Design a reusable result that retains safe line-specific reasons without storing raw sensitive input.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Check field count before indexing. String splitting can omit empty fields unless configured, so this fixture preserves them deliberately. Production totals also need an overflow policy.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Admission, Aggregation, Rejection evidence without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-016: Foundation project: an honest inventory importer.
Read courses/swift/guides/swift-016.md and courses/swift/lessons/swift-016.swift. Prerequisites: swift-015.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-016_solution.swift and
courses/swift/solutions/swift-016_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
