# swift-042: explanation and comparison

Reference program: [swift-042_solution.swift](swift-042_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Read the supported version:** Version and payload are inspected independently after decoding. The supported envelope round-trips with two titles.

**Refuse an unknown future schema:** Rejection should preserve recoverable source data rather than silently resetting it. The unsupported document is rejected without modifying its payload.

## Task answers

### Task 1: Predict and explain

Identify the schema and domain validation boundaries.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let future = Data(#"{"schemaVersion":99,"titles":["Keep"]}"#.utf8)
let decoded = try JSONDecoder().decode(SavedPlan.self, from: future)
precondition(decoded.schemaVersion == 99 && !supported(decoded))
let blank = SavedPlan(schemaVersion: 1, titles: [""])
precondition(!supported(blank))
```

**Observe:** A version 99 document decodes as JSON but is unsupported, and a version 1 document with a blank title is also refused.

Decoding only checks shape; the version gate and the nonempty-title rule are separate checks applied afterward, which is why both documents parse yet neither is accepted.

### Task 2: Guided modification

Add a version-one optional field while preserving old decoding behavior.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
struct SavedPlanWithNote: Codable {
  let schemaVersion: Int
  let titles: [String]
  let note: String?
}
let old = Data(#"{"schemaVersion":1,"titles":["Read"]}"#.utf8)
let decoded = try JSONDecoder().decode(SavedPlanWithNote.self, from: old)
precondition(decoded.note == nil && decoded.titles == ["Read"])
```

**Observe:** An old version 1 document without note still decodes, with note set to nil.

Synthesized decoding treats an optional property as absent-means-nil, so adding an optional field stays compatible with files written before it existed.

### Task 3: Independent construction

Inspect JourneyApp save and load errors with an owned test file.

**Written answer.** The full app check needs a prepared Mac and was not run here. PlanStore decodes plan.json through StudyPlan.decode; on failure it sets persistenceBlocked, keeps the file, and shows The saved plan could not be loaded. A reference JourneyCore test on swift:6.3.3-amazonlinux2023 confirmed the inputs: empty and truncated data threw DecodingError, and schemaVersion 2 threw unsupportedVersion. Test with a copy in your own directory, never with your only saved plan.

### Task 4: Diagnose a defect

Diagnose replacing an unreadable saved file with an empty default automatically.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
enum LoadResult: Equatable {
  case loaded([String])
  case blocked(original: Data)
}
func load(_ data: Data) -> LoadResult {
  guard let plan = try? JSONDecoder().decode(SavedPlan.self, from: data), supported(plan)
  else { return .blocked(original: data) }
  return .loaded(plan.titles)
}
let unreadable = Data("{".utf8)
precondition(load(unreadable) == .blocked(original: unreadable))
```

**Observe:** An unreadable file produces blocked with the original bytes kept, instead of an empty plan.

Replacing an unreadable file with an empty default looks like a fresh start, but the next save overwrites the user's only copy. Blocking writes and keeping the original leaves recovery possible.

### Task 5: Boundary evidence

Test empty data, malformed data and an unknown future version.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
let decoder = JSONDecoder()
precondition((try? decoder.decode(SavedPlan.self, from: Data())) == nil)
precondition((try? decoder.decode(SavedPlan.self, from: Data("[1,".utf8))) == nil)
let future = try decoder.decode(
  SavedPlan.self, from: Data(#"{"schemaVersion":2,"titles":[]}"#.utf8))
precondition(!supported(future))
```

**Observe:** Empty data and malformed JSON both fail to decode, while a version 2 document decodes but is unsupported.

The three cases fail at different layers, so each gets its own check: empty and malformed data fail in decoding, and the future version fails in the version policy.

### Task 6: Transfer and justify

Design a version-one to version-two migration with backup, rollback and verification steps.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** `SavedPlan` is a `Codable` envelope carrying `schemaVersion` and `titles`. Example A encodes a version 1 plan with `JSONEncoder` and decodes it back. Example B builds a version 99 plan and asks `supported`, which accepts only version 1 with no empty titles.

**Why it is correct.** Encoding and decoding a struct whose properties are an Int and an array of Strings preserves both, so the decoded plan has version 1 and two titles. Decoding succeeding only proves the JSON had the right shape; `supported` then applies the separate rule that only version 1 is understood. Version 99 fails that check, and since `supported` reads but never writes, the titles stay `["Keep me"]`.

**A plausible wrong approach.** Catching any load failure and writing a fresh empty plan over the file is the task 4 defect: a document from a newer app version, or one with a single corrupted byte, is destroyed, and the user loses data that a later version could have read. Checking only that decoding succeeded would accept version 99 and treat unknown fields as missing.

**How to verify.** For task 5, decode empty `Data()` and a truncated JSON string and confirm each throws instead of returning a default. For task 2, add an optional `note: String?`, decode an old version 1 document without it, and confirm `note` is nil and the titles are intact.

## Mechanism and diagnostic reasoning

Saving app state is a format and recovery contract. A successful encode does not mean bytes were durably committed. A successful write does not prove the next version can decode them. Include a schema version and define how unknown versions are handled. Never erase a user's existing file merely because decoding fails.

The app fixture stores a small Codable document in its application support directory and uses atomic replacement. On read failure it retains the file, reports the error and avoids an automatic overwrite. The Linux pad exercises the schema boundary with in-memory bytes. Filesystem and crash-recovery behavior need separate project evidence.

A versioned envelope contains schemaVersion and items. Decode first, then validate the version and domain invariants. Data.write with .atomic requests an atomic replacement strategy for the file operation.

Atomic replacement is not a universal durability or backup guarantee. Do not store secrets in ordinary preferences or unencrypted example files. A migration must preserve meaning, not only produce parseable JSON.

## Review before continuing

Run the reference and confirm it prints `swift-042: passed`, then rerun the guide's counterexample.
