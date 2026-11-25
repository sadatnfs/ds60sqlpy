# swift-011: explanation and comparison

Reference program: [swift-011_solution.swift](swift-011_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Return two related counts:** The grouping is useful locally without requiring an entire class hierarchy. Named tuple fields expose the accounting relationship.

**Model distinct outcomes:** The switch extracts data after establishing the state case. Each outcome exposes only its own meaningful payload.

## Task answers

### Task 1: Predict and explain

Name the meaning of each tuple field.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let summary = (accepted: 3, rejected: 2)
precondition(summary.0 == summary.accepted && summary.1 == summary.rejected)
precondition(summary.accepted + summary.rejected == 5)
```

**Observe:** accepted is position 0 with 3 rows and rejected is position 1 with 2 rows; together they account for 5 rows.

accepted counts rows that entered the result and rejected counts rows that did not, so their sum is every row read; the names make that meaning visible instead of relying on positions.

### Task 2: Guided modification

Add a third accounting field only if its meaning is independent.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
let summary = (accepted: 3, rejected: 2, skipped: 1)
let seen = summary.accepted + summary.rejected + summary.skipped
precondition(seen == 6)
```

**Observe:** With a skipped field of 1, the three fields account for 6 rows.

skipped (for example blank lines) cannot be derived from the other two, so it earns a field; a total field would be redundant because it is always accepted + rejected + skipped.

### Task 3: Independent construction

Model loading, ready and failed states with an enum.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
enum Load {
  case loading
  case ready(Int)
  case failed(String)
}
func label(_ state: Load) -> String {
  switch state {
  case .loading: return "loading"
  case .ready(let count): return "ready:\(count)"
  case .failed(let reason): return "failed:\(reason)"
  }
}
precondition(label(.loading) == "loading" && label(.ready(3)) == "ready:3")
precondition(label(.failed("offline")) == "failed:offline")
```

**Observe:** The states render as loading, ready:3 and failed:offline.

Each case carries only the data that exists in that state, and the switch must handle all three.

### Task 4: Diagnose a defect

Diagnose several optional fields that permit contradictory state combinations.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
struct LoosePage {
  var isLoading: Bool
  var count: Int?
  var error: String?
}
let contradictory = LoosePage(isLoading: true, count: 3, error: "offline")
precondition(contradictory.isLoading && contradictory.count != nil)
precondition(contradictory.error != nil)
enum PageState: Equatable {
  case loading
  case ready(Int)
  case failed(String)
}
precondition(PageState.ready(3) != .failed("offline"))
```

**Observe:** The struct accepts loading, a count and an error at once, while each PageState value is exactly one of loading, ready or failed.

Three independent fields allow eight combinations, most of them meaningless; the enum's cases admit only the three real states, so the contradiction cannot be built.

### Task 5: Boundary evidence

Add a new enum case and inspect the compiler-reported consumers requiring updates.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
enum Load {
  case loading
  case ready(Int)
  case failed(String)
  case cancelled
}
func label(_ state: Load) -> String {
  switch state {
  case .loading: return "loading"
  case .ready(let count): return "ready:\(count)"
  case .failed(let reason): return "failed:\(reason)"
  case .cancelled: return "cancelled"
  }
}
precondition(label(.cancelled) == "cancelled" && label(.ready(2)) == "ready:2")
```

**Observe:** After adding cancelled and handling it, label returns cancelled for the new case and ready:2 as before.

Before the new case clause was written, swiftc stopped with switch must be exhaustive at this switch; that error list is the set of consumers to update, which a default clause would have hidden.

### Task 6: Transfer and justify

Choose tuple or named enum/struct for a reusable public API and explain the tradeoff.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** Example A returns a named tuple `(accepted: 3, rejected: 2)` and checks that the parts sum to 5. Example B defines `enum Outcome` with `.value(Int)` and `.invalid(String)` payloads and renders each case through an exhaustive `switch`. The task 3 answer models loading, ready and failed states as one enum.

**Why it is correct.** The tuple labels make the accounting relationship readable: 3 plus 2 is 5. Each enum case carries only its own data, so the switch binds `count` for `.value(4)` and `reason` for `.invalid("negative")`, producing `count:4` and `error:negative`. In task 3 the ready case carries a count and the failed case carries a reason, so they render as loading, ready:3 and failed:offline.

**A plausible wrong approach.** A struct with `isLoading: Bool`, `items: Int?` and `error: String?` allows contradictions such as loading with an error. The enum makes those combinations unrepresentable. Adding a `default:` to the render switch would also hide a newly added case instead of letting the compiler list every switch to update.

**How to verify.** Add a case such as `.pending` to `Outcome` and compile: the switch in Example B is reported as non-exhaustive, which is the evidence task 5 asks for. Remove it and confirm the rendered array matches again.

## Mechanism and diagnostic reasoning

A tuple groups a fixed set of values without introducing a new nominal type. It is useful for local multi-value results, but a named type is clearer when the same concept crosses several APIs. An enum represents one case from a finite set. Associated values attach data relevant only to that case.

Explicit cases prevent impossible combinations such as success=true with an error message and no result. A switch must handle the alternatives. This is a strong foundation for application state machines, parsing results and asynchronous loading state. Add a new case only when it represents a real domain distinction, then review every consumer.

`(count: Int, rejected: Int)` names tuple components. `enum Outcome { case value(Int); case invalid(String) }` binds case-specific payloads. `case .value(let count)` extracts only the matching payload.

An enum raw value and an associated value solve different problems. A catch-all default can conceal a newly added state. Avoid using tuples so large that their positional relationship becomes obscure.

## Review before continuing

Run the reference and confirm it prints `swift-011: passed`, then rerun the guide's counterexample.
