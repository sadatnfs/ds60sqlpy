# swift-024: explanation and comparison

Reference program: [swift-024_solution.swift](swift-024_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Round-trip in an owned directory:** Random path identity prevents collisions while content and assertions remain deterministic. The UTF-8 bytes round-trip in a uniquely owned location.

**Distinguish file and network locations:** A URL is not permission to access its target; the example classifies values without contacting either target. The two URLs carry different location schemes.

## Task answers

### Task 1: Predict and explain

Trace acquisition, use and defer cleanup.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let manager = FileManager.default
func useOwnedDirectory() throws -> URL {
  let root = manager.temporaryDirectory.appendingPathComponent(
    UUID().uuidString, isDirectory: true)
  try manager.createDirectory(at: root, withIntermediateDirectories: true)
  defer { try? manager.removeItem(at: root) }
  let file = root.appendingPathComponent("trace.txt")
  try Data("used".utf8).write(to: file)
  precondition(manager.fileExists(atPath: file.path))
  return root
}
let root = try useOwnedDirectory()
precondition(!manager.fileExists(atPath: root.path))
```

**Observe:** The file exists while the function runs, and the directory is gone once the function returns.

Acquisition creates a fresh directory, use writes inside it, and defer runs the cleanup on the way out of the scope, whether by return or by throw.

### Task 2: Guided modification

Write and read two separate small files under the owned directory.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
let manager = FileManager.default
let root = manager.temporaryDirectory.appendingPathComponent(
  UUID().uuidString, isDirectory: true)
try manager.createDirectory(at: root, withIntermediateDirectories: true)
defer { try? manager.removeItem(at: root) }
let first = root.appendingPathComponent("a.txt")
let second = root.appendingPathComponent("b.txt")
try Data("alpha".utf8).write(to: first)
try Data("beta".utf8).write(to: second)
let firstText = try String(contentsOf: first, encoding: .utf8)
let secondText = try String(contentsOf: second, encoding: .utf8)
precondition(firstText == "alpha" && secondText == "beta")
```

**Observe:** a.txt reads back alpha and b.txt reads back beta under the same owned directory.

Each file gets its own name inside the directory this code created, and the single defer removes both when the scope ends.

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

**Written answer.** The worker writes into its container's temporary directory, and that filesystem is discarded when the container is replaced, so a file written in one run is not there for the next. Temporary storage is for scratch data within one run; anything that must persist needs a mounted volume or an external store, and the reader must handle the file being absent.

### Task 5: Boundary evidence

Test empty bytes and a missing file as distinct outcomes.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
let manager = FileManager.default
let root = manager.temporaryDirectory.appendingPathComponent(
  UUID().uuidString, isDirectory: true)
try manager.createDirectory(at: root, withIntermediateDirectories: true)
defer { try? manager.removeItem(at: root) }
let blank = root.appendingPathComponent("blank.bin")
try Data().write(to: blank)
let blankBytes = try Data(contentsOf: blank)
precondition(blankBytes.isEmpty)
var missingFailed = false
do { _ = try Data(contentsOf: root.appendingPathComponent("absent.bin")) } catch {
  missingFailed = true
}
precondition(missingFailed)
```

**Observe:** The empty file reads back as zero bytes, while reading a missing file throws.

An empty file exists and has no content; a missing file is a different outcome that raises an error, so the reader can tell no data from no file.

### Task 6: Transfer and justify

Design a durable app save with atomic replacement and a recoverable previous version.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** Example A creates a uniquely named directory under the temporary directory, registers `defer` cleanup immediately, writes the UTF-8 bytes of "café", and reads them back. Example B builds a file URL and an https URL and checks `isFileURL` on each without opening either. The task 3 answer persists a Codable value in the owned directory.

**Why it is correct.** `UUID().uuidString` makes the directory name collision-free, so the lesson only removes what it created. The bytes written are 5 (c, a, f and two for é), and `Data(contentsOf:)` returns the same 5 bytes, so equality holds. `defer` runs when the block exits, including after a thrown error. The task 3 value reads back equal and passes its quantity check.

**A plausible wrong approach.** Writing to a fixed path such as `/tmp/note.txt` and removing it afterwards could collide with another run or delete a file the lesson does not own. Treating `remote.path` as if it were a local file and calling `Data(contentsOf:)` on it would attempt network access, which the classroom does not allow and the lesson does not need.

**How to verify.** Print `root.path` in a scratch pad before cleanup and confirm it is under the temporary directory and gone after the block. For task 5, write empty `Data()` and read 0 bytes, then read a missing file name and confirm it throws instead of returning empty data.

## Mechanism and diagnostic reasoning

Foundation represents file locations with URLs as well as path strings. A file URL is distinct from an HTTP URL. Relative locations depend on a working directory, and a worker temporary directory is not the classroom progress store. Keep ownership and persistence scope explicit.

A portable example creates a unique temporary directory, writes a small value, reads it back and removes only that owned directory. Defer places cleanup near acquisition and executes when scope exits, including throwing paths. Durable application storage needs additional policies for atomic replacement, schema migration, backups and errors. A temporary round trip does not prove crash recovery.

FileManager.default.temporaryDirectory supplies a temporary base. appendingPathComponent constructs a child URL. Data.write and Data(contentsOf:) operate on bytes. defer registers cleanup for the current scope.

Never remove an arbitrary caller-provided directory. A normalized path does not defeat symlink races. Try? in cleanup intentionally suppresses a secondary error here; production code should record cleanup failure appropriately.

## Review before continuing

Run the reference and confirm it prints `swift-024: passed`, then rerun the guide's counterexample.
