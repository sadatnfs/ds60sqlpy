# swift-015: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-015_solution.swift](swift-015_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Transform a sequence:** The transformation is pure and its element-to-element relationship is visible. Map creates transformed values while retaining the original array.

**Freeze a captured value deliberately:** This differs from a closure observing a mutable captured variable later. The explicit capture list retains factor 2 for the closure.

## Task answers

### Task 1: Predict and explain

Predict the mapped result and unchanged source.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The transformation is pure and its element-to-element relationship is visible. Map creates transformed values while retaining the original array.

### Task 2: Guided modification

Filter even numbers before mapping.

No separate reference answer has been written for this task. Start from Example B: This differs from a closure observing a mutable captured variable later. The explicit capture list retains factor 2 for the closure.

### Task 3: Independent construction

Write a function accepting a transformation closure.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
func transformAll(_ values: [Int], _ change: (Int) -> Int) -> [Int] {
  var result: [Int] = []
  for value in values { result.append(change(value)) }
  return result
}
let scaled = transformAll([1, 2, 3]) { $0 * 10 }
precondition(scaled == [10, 20, 30])
```

**Observe:** Applying the closure gives 10, 20 and 30.

The caller supplies the behavior; the closure is non-escaping, so it runs only during the call.

### Task 4: Diagnose a defect

Diagnose a closure whose captured mutable state changes before later execution.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: An escaping closure can outlive its creating scope. Capturing self strongly can create a retain cycle, covered in ARC. A short expression is not automatically clearer than a named intermediate.

### Task 5: Boundary evidence

Test empty arrays and a closure that returns an optional.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Transform a sequence) and Example B (Freeze a captured value deliberately).

### Task 6: Transfer and justify

Choose a named function or closure for a reusable domain transformation and explain readability and capture policy.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Closure**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A closure is executable behavior that can be passed as a value. It can capture surrounding variables, which lets it remember context but can also create surprising mutation or lifetime relationships. Swift capture lists can copy a value at closure creation or weaken a reference, depending on the declared policy.

Map transforms each element while filter selects elements. These operations express intent when the closure remains small and clear. Avoid compressing a complex domain algorithm into a chain whose intermediate states nobody can inspect. Name important transformations and preserve a traceable failure boundary.

`{ value in value * 2 }` is a closure. `$0` abbreviates its first argument. A capture list such as `[factor]` captures the current value. Function types use `(Input) -> Output`.

An escaping closure can outlive its creating scope. Capturing self strongly can create a retain cycle, covered in ARC. A short expression is not automatically clearer than a named intermediate.

## Review before continuing

Run the reference and confirm that it prints `swift-015: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
