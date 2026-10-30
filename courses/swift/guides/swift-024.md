# swift-024: Files, URLs and owned persistence

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-023`

## Learning objectives

Persist a Codable value in a temporary file and validate after reading. Then design a durable app save with atomic replacement and a recoverable previous version.

## Purpose and mental model

Foundation represents file locations with URLs as well as path strings. A file URL is distinct from an HTTP URL. Relative locations depend on a working directory, and a worker temporary directory is not the classroom progress store. Keep ownership and persistence scope explicit.

A portable example creates a unique temporary directory, writes a small value, reads it back and removes only that owned directory. Defer places cleanup near acquisition and executes when scope exits, including throwing paths. Durable application storage needs additional policies for atomic replacement, schema migration, backups and errors. A temporary round trip does not prove crash recovery.

## Vocabulary and concepts

**File URL:** A structured location identifying a filesystem resource.

**Defer:** A cleanup action executed when the current scope exits.

**Persistence scope:** The lifetime and location in which data is expected to survive.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

FileManager.default.temporaryDirectory supplies a temporary base. appendingPathComponent constructs a child URL. Data.write and Data(contentsOf:) operate on bytes. defer registers cleanup for the current scope.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Round-trip in an owned directory

Random path identity prevents collisions while content and assertions remain deterministic.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let manager = FileManager.default
      let root = manager.temporaryDirectory.appendingPathComponent(
        UUID().uuidString, isDirectory: true)
      try manager.createDirectory(at: root, withIntermediateDirectories: true)
      defer { try? manager.removeItem(at: root) }
      let file = root.appendingPathComponent("note.txt")
      let expected = Data("café".utf8)
      try expected.write(to: file)
      let actual = try Data(contentsOf: file)
      precondition(actual == expected)
    }
    print("swift-024: passed")
  }
}
```

**Observe:** The UTF-8 bytes round-trip in a uniquely owned location.

### Example B: Distinguish file and network locations

A URL is not permission to access its target; the example classifies values without contacting either target.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let file = URL(fileURLWithPath: "/tmp/example.txt")
      let remote = URL(string: "https://example.invalid/data")!
      precondition(file.isFileURL && !remote.isFileURL)
    }
    print("swift-024: passed")
  }
}
```

**Observe:** The two URLs carry different location schemes.

## Exercises

1. **Predict and explain.** Trace acquisition, use and defer cleanup.

2. **Guided modification.** Write and read two separate small files under the owned directory.

3. **Independent construction.** Persist a Codable value in a temporary file and validate after reading.

4. **Diagnose a defect.** Diagnose assuming worker temporary files survive container replacement.

5. **Boundary evidence.** Test empty bytes and a missing file as distinct outcomes.

6. **Transfer and justify.** Design a durable app save with atomic replacement and a recoverable previous version.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Never remove an arbitrary caller-provided directory. A normalized path does not defeat symlink races. Try? in cleanup intentionally suppresses a secondary error here; production code should record cleanup failure appropriately.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain File URL, Defer, Persistence scope without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-024: Files, URLs and owned persistence.
Read courses/swift/guides/swift-024.md and courses/swift/lessons/swift-024.swift. Prerequisites: swift-023.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-024_solution.swift and
courses/swift/solutions/swift-024_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
