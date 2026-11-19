# swift-037: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-037_solution.swift](swift-037_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Apply a bounded display policy:** The wrapper enforces a deliberate display range at every assignment. Assignments are clamped into zero through ten.

**Retain valid interior values:** The projected information explains the policy without exposing mutable internal storage. A valid interior value is unchanged and the projection exposes the range.

## Task answers

### Task 1: Predict and explain

Trace initialization and both setter calls.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The wrapper enforces a deliberate display range at every assignment. Assignments are clamped into zero through ten.

### Task 2: Guided modification

Change the allowed range and update boundary tests.

No separate reference answer has been written for this task. Start from Example B: The projected information explains the policy without exposing mutable internal storage. A valid interior value is unchanged and the projection exposes the range.

### Task 3: Independent construction

Create a wrapper with an explicit normalization policy for a local display field.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
var label = DisplayLabel()
label.title = "  Report  "
precondition(label.title == "Report")
precondition(DisplayLabel(title: " x ").title == "x")
```

**Observe:** Both assignment and initialization store the trimmed text Report and x.

The wrapper applies one normalization policy in its setter, and init(wrappedValue:) routes initial values through the same setter.

### Task 4: Diagnose a defect

Explain why silently clamping a payment amount would be misleading.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A wrapper is not a substitute for validating external input. Hidden side effects make ordinary-looking assignment hard to reason about. Document projection and mutation semantics.

### Task 5: Boundary evidence

Test both endpoints and one value outside each.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Apply a bounded display policy) and Example B (Retain valid interior values).

### Task 6: Transfer and justify

Choose a wrapper or explicit validation method based on whether assignment can fail meaningfully.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Property wrapper**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A property wrapper packages behavior around property storage and access. It can validate, normalize or project a reusable policy, but it should not hide surprising I/O or authorization. The wrappedValue is the property-facing interface; projectedValue can expose related information using dollar-prefixed access.

Wrapper behavior is part of the containing type's semantics. Decide whether invalid assignments are rejected, clamped or represented as an error, and make that choice visible to readers. A clamped value can be appropriate for a display control but inappropriate for financial input where silent correction hides an error.

`@propertyWrapper` marks a wrapper type. wrappedValue supplies get/set behavior. `@Clamped var level` applies it. A projectedValue is read through `$level` when declared.

A wrapper is not a substitute for validating external input. Hidden side effects make ordinary-looking assignment hard to reason about. Document projection and mutation semantics.

## Review before continuing

Run the reference and confirm that it prints `swift-037: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
