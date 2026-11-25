# swift-024: Files, URLs and owned persistence

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-023`

## Learning objectives

Persist data in owned temporary files with Foundation URLs and remove them on every path. The central exercise is task 3: Persist a Codable value in a temporary file and validate after reading.

## Purpose and mental model

Foundation represents file locations with URLs as well as path strings. A file URL is distinct from an HTTP URL. Relative locations depend on a working directory, and a worker temporary directory is not the classroom progress store. Keep ownership and persistence scope explicit.

A portable example creates a unique temporary directory, writes a small value, reads it back and removes only that owned directory. Defer places cleanup near acquisition and executes when scope exits, including throwing paths. Durable application storage needs additional policies for atomic replacement, schema migration, backups and errors. A temporary round trip does not prove crash recovery.

## Vocabulary and concepts

**File URL:** A structured location identifying a filesystem resource.

**Defer:** A cleanup action executed when the current scope exits.

**Persistence scope:** The lifetime and location in which data is expected to survive.

## How to run this lesson

This lesson touches the file system. Example A creates and removes its own directory under the system temporary directory, normally `/tmp` on Linux. Task 4 is a written diagnosis about container replacement, not a program. Task 5 must distinguish an empty file from a missing one, so catch the read error instead of letting it end the program.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

FileManager.default.temporaryDirectory supplies a temporary base. appendingPathComponent constructs a child URL. Data.write and Data(contentsOf:) operate on bytes. defer registers cleanup for the current scope.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** `temporaryDirectory` gives the system scratch location, and a random UUID component makes a directory name no other run will use. `createDirectory` creates it, and the `defer` registers cleanup that runs when the enclosing `do` block exits, whether by success or by a thrown error. The string café encodes to five UTF-8 bytes, since the é needs two. `write(to:)` stores them, `Data(contentsOf:)` reads them back, and the check compares bytes. Then the block ends and the directory is removed.

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

**Trace.** `URL(fileURLWithPath:)` builds a file URL from a path; it does not check that the file exists. `URL(string:)` parses text and returns an optional, force-unwrapped here only because the literal is authored. The `.invalid` top-level domain is reserved, so even an accidental request could never reach a real server. `isFileURL` reads only the scheme: true for the file URL and false for the https one. Neither line opens a file or contacts a network.

## Exercises

1. **Predict and explain.** Trace acquisition, use and defer cleanup.

2. **Guided modification.** Write and read two separate small files under the owned directory.

3. **Independent construction.** Persist a Codable value in a temporary file and validate after reading.

4. **Diagnose a defect.** Diagnose assuming worker temporary files survive container replacement.

5. **Boundary evidence.** Test empty bytes and a missing file as distinct outcomes.

6. **Transfer and justify.** Design a durable app save with atomic replacement and a recoverable previous version.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Never remove an arbitrary caller-provided directory. A normalized path does not defeat symlink races. Try? in cleanup intentionally suppresses a secondary error here; production code should record cleanup failure appropriately.

For task 5, an empty file and a missing file are easy to confuse if a read failure is mapped to empty data. Write zero bytes to one path and read it, expecting `Data()`; read a path never created and expect a thrown error. A version using `try? Data(contentsOf:) ?? Data()` passes the first case and wrongly passes the second as well.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Round-trip in an owned directory) before changing anything, and confirm its observation: The UTF-8 bytes round-trip in a uniquely owned location.
2. Compare Example B (Distinguish file and network locations) with Example A and name the first line whose behavior differs. Its observation is: The two URLs carry different location schemes.
3. Before opening the explanation, check your task 3 attempt (Persist a Codable value in a temporary file and validate after reading) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain why the directory name uses a fresh UUID instead of a fixed name. State when a `defer` block runs and why it is registered right after the directory is created. Describe how an atomic write keeps the previous save intact if the app stops halfway through writing.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Foundation reference documents `FileManager`, `URL` and `Data`; the Statements reference in the Swift book explains the defer statement.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
