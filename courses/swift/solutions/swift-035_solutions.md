# swift-035: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-035_solution.swift](swift-035_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Borrow only within the closure:** Scoped access limits the lifetime reasoning to one visible closure. The result escapes as an integer while the borrowed pointer does not.

**Handle empty storage without dereferencing:** No base-address dereference is needed, avoiding assumptions about a pointer for empty storage. An empty buffer is valid to inspect by count.

## Task answers

### Task 1: Predict and explain

Identify the pointer lifetime and the returned owned result.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Scoped access limits the lifetime reasoning to one visible closure. The result escapes as an integer while the borrowed pointer does not.

### Task 2: Guided modification

Compute a maximum with an explicit empty-input policy.

No separate reference answer has been written for this task. Start from Example B: No base-address dereference is needed, avoiding assumptions about a pointer for empty storage. An empty buffer is valid to inspect by count.

### Task 3: Independent construction

Wrap a scoped read-only buffer operation behind a safe function contract.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
/// Returns the sum of the values; the buffer pointer never escapes this call.
func total(of values: [Int]) -> Int {
  values.withUnsafeBufferPointer { buffer in
    var sum = 0
    for value in buffer { sum += value }
    return sum
  }
}
precondition(total(of: [2, 3, 4]) == 9 && total(of: []) == 0)
```

**Observe:** The safe wrapper returns 9 for [2, 3, 4] and 0 for an empty array.

Callers see an ordinary function; the unsafe pointer exists only inside the closure and is read-only, so it cannot outlive the array.

### Task 4: Diagnose a defect

Diagnose returning the buffer baseAddress for later use.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Unsafe does not disable all runtime checks or make an operation faster. Never infer lifetime from a pointer value remaining numerically unchanged. Keep native API ownership documented and avoid unsafe code when safe collections suffice.

### Task 5: Boundary evidence

Test empty, singleton and multi-element buffers.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Borrow only within the closure) and Example B (Handle empty storage without dereferencing).

### Task 6: Transfer and justify

Write an interoperability checklist covering ownership, alignment, initialization and error reporting.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Pointer**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Swift normally protects memory through value semantics, ARC and checked collection access. Unsafe pointer APIs deliberately cross that protection boundary for interoperability and specialized performance work. A pointer is valid only while its owner guarantees storage lifetime and binding. Compiling unsafe code does not prove its memory access is valid.

Prefer scoped buffer APIs that lend a pointer only for a closure. Do not store that pointer or use it after the closure returns. Distinguish initialized elements from allocated capacity, and preserve element alignment and type binding. This lesson uses read-only scoped access to an owned array, keeping the demonstration small enough to inspect fully.

withUnsafeBufferPointer temporarily borrows contiguous elements. The pointer count states initialized accessible elements. Return a copied result from the closure, never the borrowed pointer itself.

Unsafe does not disable all runtime checks or make an operation faster. Never infer lifetime from a pointer value remaining numerically unchanged. Keep native API ownership documented and avoid unsafe code when safe collections suffice.

## Review before continuing

Run the reference and confirm that it prints `swift-035: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
