# swift-024: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-024_solution.swift](swift-024_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Round-trip in an owned directory:** Random path identity prevents collisions while content and assertions remain deterministic. The UTF-8 bytes round-trip in a uniquely owned location.

**Distinguish file and network locations:** A URL is not permission to access its target; the example classifies values without contacting either target. The two URLs carry different location schemes.

## Task answers

### Task 1: Predict and explain

Trace acquisition, use and defer cleanup.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Random path identity prevents collisions while content and assertions remain deterministic. The UTF-8 bytes round-trip in a uniquely owned location.

### Task 2: Guided modification

Write and read two separate small files under the owned directory.

No separate reference answer has been written for this task. Start from Example B: A URL is not permission to access its target; the example classifies values without contacting either target. The two URLs carry different location schemes.

### Task 3: Independent construction

Persist a Codable value in a temporary file and validate after reading.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
struct Stock: Codable, Equatable {
  let name: String
  let quantity: Int
}
let manager = FileManager.default
let folder = manager.temporaryDirectory.appendingPathComponent(
  UUID().uuidString, isDirectory: true)
try manager.createDirectory(at: folder, withIntermediateDirectories: true)
defer { try? manager.removeItem(at: folder) }
let file = folder.appendingPathComponent("stock.json")
let saved = Stock(name: "pear", quantity: 3)
try JSONEncoder().encode(saved).write(to: file)
let restored = try JSONDecoder().decode(Stock.self, from: Data(contentsOf: file))
precondition(restored == saved && restored.quantity >= 0)
```

**Observe:** The value read back equals the saved one and passes the quantity check; the folder is removed at the end of the block.

The folder is unique to this run, defer removes it on every exit path, and the decoded value is checked before use.

### Task 4: Diagnose a defect

Diagnose assuming worker temporary files survive container replacement.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Never remove an arbitrary caller-provided directory. A normalized path does not defeat symlink races. Try? in cleanup intentionally suppresses a secondary error here; production code should record cleanup failure appropriately.

### Task 5: Boundary evidence

Test empty bytes and a missing file as distinct outcomes.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Round-trip in an owned directory) and Example B (Distinguish file and network locations).

### Task 6: Transfer and justify

Design a durable app save with atomic replacement and a recoverable previous version.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **File URL**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Foundation represents file locations with URLs as well as path strings. A file URL is distinct from an HTTP URL. Relative locations depend on a working directory, and a worker temporary directory is not the classroom progress store. Keep ownership and persistence scope explicit.

A portable example creates a unique temporary directory, writes a small value, reads it back and removes only that owned directory. Defer places cleanup near acquisition and executes when scope exits, including throwing paths. Durable application storage needs additional policies for atomic replacement, schema migration, backups and errors. A temporary round trip does not prove crash recovery.

FileManager.default.temporaryDirectory supplies a temporary base. appendingPathComponent constructs a child URL. Data.write and Data(contentsOf:) operate on bytes. defer registers cleanup for the current scope.

Never remove an arbitrary caller-provided directory. A normalized path does not defeat symlink races. Try? in cleanup intentionally suppresses a secondary error here; production code should record cleanup failure appropriately.

## Review before continuing

Run the reference and confirm that it prints `swift-024: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
