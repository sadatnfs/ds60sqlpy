# swift-014: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-014_solution.swift](swift-014_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Derive instead of duplicating:** One source of truth prevents stale duplicated state. Area changes with width without a separately updated area field.

**Expose a conversion property:** A computed property can expose a convenient representation while retaining one stored unit. The getter and setter translate between temperature scales.

## Task answers

### Task 1: Predict and explain

Trace which properties are stored and which are derived.

No separate reference answer has been written for this task. Example A is the evidence to compare with: One source of truth prevents stale duplicated state. Area changes with width without a separately updated area field.

### Task 2: Guided modification

Add a computed rectangle perimeter.

No separate reference answer has been written for this task. Start from Example B: A computed property can expose a convenient representation while retaining one stored unit. The getter and setter translate between temperature scales.

### Task 3: Independent construction

Build a value model with one stored unit and a documented converted view.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
/// Stores meters only; feet is a derived view and is never stored.
struct Length {
  var meters: Double
  var feet: Double { meters / 0.3048 }
}
let length = Length(meters: 3.048)
precondition(abs(length.feet - 10) < 1e-9)
```

**Observe:** 3.048 meters reads as 10 feet.

With a single stored unit there is nothing to keep in sync; the converted value is computed from meters every time it is read.

### Task 4: Diagnose a defect

Diagnose a separately stored area that is not updated after width changes.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Expensive computed properties can surprise callers who expect cheap access. Observers can hide cascading side effects. Avoid duplicating state unless there is a measured caching need and invalidation policy.

### Task 5: Boundary evidence

Test zero and a non-integer conversion case.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Derive instead of duplicating) and Example B (Expose a conversion property).

### Task 6: Transfer and justify

Choose an explicit method instead of a setter for a state change with validation and failure.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Stored property**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A stored property retains data; a computed property derives a value from other state. Prefer deriving cheap dependent values instead of storing duplicates that can disagree. A property observer reacts to a stored-value change but should not become an invisible substitute for a clear domain operation.

Computed setters translate an external representation back into stored state. That translation may lose information, so document it. Access control can permit reading without external writing. Property wrappers later package reusable access behavior, but start by understanding the plain getter and setter contract.

`var area: Int { width * height }` computes a value. `get` and `set` define two-way access; newValue names the assigned value. didSet observes assignments after the new value is stored.

Expensive computed properties can surprise callers who expect cheap access. Observers can hide cascading side effects. Avoid duplicating state unless there is a measured caching need and invalidation policy.

## Review before continuing

Run the reference and confirm that it prints `swift-014: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
