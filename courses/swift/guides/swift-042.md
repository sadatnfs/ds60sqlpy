# swift-042: App persistence, migrations and recoverable saves

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-041`

## Learning objectives

Inspect JourneyApp save and load errors with an owned test file. Then design a version-one to version-two migration with backup, rollback and verification steps.

## Purpose and mental model

Saving app state is a format and recovery contract. A successful encode does not mean bytes were durably committed. A successful write does not prove the next version can decode them. Include a schema version and define how unknown versions are handled. Never erase a user's existing file merely because decoding fails.

The app fixture stores a small Codable document in its application support directory and uses atomic replacement. On read failure it retains the file, reports the error and avoids an automatic overwrite. The Linux pad exercises the schema boundary with in-memory bytes. Filesystem and crash-recovery behavior need separate project evidence.

## Vocabulary and concepts

**Schema version:** An identity for the meaning and layout of stored data.

**Migration:** A reviewed transformation from an older format.

**Recovery policy:** How the app retains or restores data after failure.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

The actual save/load implementation is in the [JourneyApp project](../fixtures/JourneyApp/README.md). It deliberately retains an unreadable file for recovery.

## Syntax anatomy and execution trace

A versioned envelope contains schemaVersion and items. Decode first, then validate the version and domain invariants. Data.write with .atomic requests an atomic replacement strategy for the file operation.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Read the supported version

Version and payload are inspected independently after decoding.

```swift
import Foundation

struct SavedPlan: Codable {
  let schemaVersion: Int
  let titles: [String]
}
func supported(_ document: SavedPlan) -> Bool {
  document.schemaVersion == 1 && document.titles.allSatisfy { !$0.isEmpty }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let document = SavedPlan(schemaVersion: 1, titles: ["Read", "Practice"])
      let data = try JSONEncoder().encode(document)
      let decoded = try JSONDecoder().decode(SavedPlan.self, from: data)
      precondition(decoded.schemaVersion == 1 && decoded.titles.count == 2)
    }
    print("swift-042: passed")
  }
}
```

**Observe:** The supported envelope round-trips with two titles.

### Example B: Refuse an unknown future schema

Rejection should preserve recoverable source data rather than silently resetting it.

```swift
import Foundation

struct SavedPlan: Codable {
  let schemaVersion: Int
  let titles: [String]
}
func supported(_ document: SavedPlan) -> Bool {
  document.schemaVersion == 1 && document.titles.allSatisfy { !$0.isEmpty }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let document = SavedPlan(schemaVersion: 99, titles: ["Keep me"])
      precondition(!supported(document))
      precondition(document.titles == ["Keep me"])
    }
    print("swift-042: passed")
  }
}
```

**Observe:** The unsupported document is rejected without modifying its payload.

## Exercises

1. **Predict and explain.** Identify the schema and domain validation boundaries.

2. **Guided modification.** Add a version-one optional field while preserving old decoding behavior.

3. **Independent construction.** Inspect JourneyApp save and load errors with an owned test file.

4. **Diagnose a defect.** Diagnose replacing an unreadable saved file with an empty default automatically.

5. **Boundary evidence.** Test empty data, malformed data and an unknown future version.

6. **Transfer and justify.** Design a version-one to version-two migration with backup, rollback and verification steps.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Atomic replacement is not a universal durability or backup guarantee. Do not store secrets in ordinary preferences or unencrypted example files. A migration must preserve meaning, not only produce parseable JSON.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Schema version, Migration, Recovery policy without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-042: App persistence, migrations and recoverable saves.
Read courses/swift/guides/swift-042.md and courses/swift/lessons/swift-042.swift. Prerequisites: swift-041.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-042_solution.swift and
courses/swift/solutions/swift-042_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
