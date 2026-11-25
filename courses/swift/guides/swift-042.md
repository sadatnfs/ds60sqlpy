# swift-042: App persistence, migrations and recoverable saves

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-041`

## Learning objectives

Save, load and migrate app data with recoverable errors. The central exercise is task 3: Inspect JourneyApp save and load errors with an owned test file.

## Purpose and mental model

Saving app state is a format and recovery contract. A successful encode does not mean bytes were durably committed. A successful write does not prove the next version can decode them. Include a schema version and define how unknown versions are handled. Never erase a user's existing file merely because decoding fails.

The app fixture stores a small Codable document in its application support directory and uses atomic replacement. On read failure it retains the file, reports the error and avoids an automatic overwrite. The Linux pad exercises the schema boundary with in-memory bytes. Filesystem and crash-recovery behavior need separate project evidence.

## Vocabulary and concepts

**Schema version:** An identity for the meaning and layout of stored data.

**Migration:** A reviewed transformation from an older format.

**Recovery policy:** How the app retains or restores data after failure.

## How to run this lesson

`SavedPlan` and `supported` are declared above `LessonMain`. Example A encodes and decodes in memory without touching the file system. Task 3's save and load errors are inspected in JourneyApp with a test file you own; never point it at real saved data.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).

The actual save/load implementation is in the [JourneyApp project](../fixtures/JourneyApp/README.md). It deliberately retains an unreadable file for recovery.

## Syntax anatomy and execution trace

A versioned envelope contains schemaVersion and items. Decode first, then validate the version and domain invariants. Data.write with .atomic requests an atomic replacement strategy for the file operation.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** The document holds version 1 and the titles Read and Practice. `JSONEncoder().encode` produces UTF-8 JSON bytes with both keys. `JSONDecoder().decode(SavedPlan.self, from:)` reads them back into a new value. The check inspects the decoded version and title count rather than the original, so it proves the round trip preserved both. `supported` is not called here; decoding succeeds for any integer version, which is why validation is a separate step.

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

**Trace.** A document with version 99 is built directly, standing in for a file written by a newer release. `supported` returns false because the version is not 1, and the check confirms the rejection. The second check confirms the titles are still Keep me: rejecting the document did not discard or rewrite it, so the app can keep the source file for recovery instead of overwriting it with an empty plan.

## Exercises

1. **Predict and explain.** Identify the schema and domain validation boundaries.

2. **Guided modification.** Add a version-one optional field while preserving old decoding behavior.

3. **Independent construction.** Inspect JourneyApp save and load errors with an owned test file.

4. **Diagnose a defect.** Diagnose replacing an unreadable saved file with an empty default automatically.

5. **Boundary evidence.** Test empty data, malformed data and an unknown future version.

6. **Transfer and justify.** Design a version-one to version-two migration with backup, rollback and verification steps.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Atomic replacement is not a universal durability or backup guarantee. Do not store secrets in ordinary preferences or unencrypted example files. A migration must preserve meaning, not only produce parseable JSON.

For task 2, a new field must be optional, or an older file without it fails to decode with a missing-key error. The counterexample is decoding the original JSON after adding the field. Task 4's automatic reset turns a recoverable unreadable file into permanent data loss. For task 5, empty data and malformed JSON must throw, while an unknown version decodes but is refused by `supported`.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Read the supported version) before changing anything, and confirm its observation: The supported envelope round-trips with two titles.
2. Compare Example B (Refuse an unknown future schema) with Example A and name the first line whose behavior differs. Its observation is: The unsupported document is rejected without modifying its payload.
3. Before opening the explanation, check your task 3 attempt (Inspect JourneyApp save and load errors with an owned test file) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain why decoding and version validation are separate steps. Say what happens when an older file lacks a newly added non-optional property. List the steps for migrating version 1 files to version 2, including where the backup goes and how you would verify the result before deleting it.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Foundation reference documents `JSONEncoder`, `JSONDecoder` and `Data.write(to:options:)`; Apple's article on encoding and decoding custom types covers Codable keys.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
