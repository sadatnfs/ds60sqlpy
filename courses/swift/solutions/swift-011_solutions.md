# swift-011: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-011_solution.swift](swift-011_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Return two related counts:** The grouping is useful locally without requiring an entire class hierarchy. Named tuple fields expose the accounting relationship.

**Model distinct outcomes:** The switch extracts data after establishing the state case. Each outcome exposes only its own meaningful payload.

## Task answers

### Task 1: Predict and explain

Name the meaning of each tuple field.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The grouping is useful locally without requiring an entire class hierarchy. Named tuple fields expose the accounting relationship.

### Task 2: Guided modification

Add a third accounting field only if its meaning is independent.

No separate reference answer has been written for this task. Start from Example B: The switch extracts data after establishing the state case. Each outcome exposes only its own meaningful payload.

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

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: An enum raw value and an associated value solve different problems. A catch-all default can conceal a newly added state. Avoid using tuples so large that their positional relationship becomes obscure.

### Task 5: Boundary evidence

Add a new enum case and inspect the compiler-reported consumers requiring updates.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Return two related counts) and Example B (Model distinct outcomes).

### Task 6: Transfer and justify

Choose tuple or named enum/struct for a reusable public API and explain the tradeoff.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Tuple**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A tuple groups a fixed set of values without introducing a new nominal type. It is useful for local multi-value results, but a named type is clearer when the same concept crosses several APIs. An enum represents one case from a finite set. Associated values attach data relevant only to that case.

Explicit cases prevent impossible combinations such as success=true with an error message and no result. A switch must handle the alternatives. This is a strong foundation for application state machines, parsing results and asynchronous loading state. Add a new case only when it represents a real domain distinction, then review every consumer.

`(count: Int, rejected: Int)` names tuple components. `enum Outcome { case value(Int); case invalid(String) }` binds case-specific payloads. `case .value(let count)` extracts only the matching payload.

An enum raw value and an associated value solve different problems. A catch-all default can conceal a newly added state. Avoid using tuples so large that their positional relationship becomes obscure.

## Review before continuing

Run the reference and confirm that it prints `swift-011: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
