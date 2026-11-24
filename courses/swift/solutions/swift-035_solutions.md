# swift-035: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-035_solution.swift](swift-035_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Borrow only within the closure:** Scoped access limits the lifetime reasoning to one visible closure. The result escapes as an integer while the borrowed pointer does not.

**Handle empty storage without dereferencing:** No base-address dereference is needed, avoiding assumptions about a pointer for empty storage. An empty buffer is valid to inspect by count.

## Task answers

### Task 1: Predict and explain

Identify the pointer lifetime and the returned owned result.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let values = [2, 3, 4]
let byteCount = values.withUnsafeBytes { bytes in bytes.count }
precondition(byteCount == values.count * MemoryLayout<Int>.stride)
let total = values.withUnsafeBufferPointer { buffer in buffer.reduce(0, +) }
precondition(total == 9)
```

**Observe:** The raw view spans 3 times the Int stride in bytes, and the buffer sums to 9.

Each pointer is valid only inside its closure; what leaves the call is an owned Int (the byte count or the total), never the pointer itself.

### Task 2: Guided modification

Compute a maximum with an explicit empty-input policy.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
func largest(_ values: [Int]) -> Int? {
  values.withUnsafeBufferPointer { buffer in
    guard let first = buffer.first else { return nil }
    return buffer.reduce(first, max)
  }
}
precondition(largest([]) == nil)
precondition(largest([3, 9, 2]) == 9)
```

**Observe:** The empty array gives nil, and [3, 9, 2] gives 9.

An empty buffer has no maximum, so the contract returns nil instead of reading a nonexistent first element or inventing a sentinel.

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

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
let values = [5, 6]
let copied = values.withUnsafeBufferPointer { buffer in Array(buffer) }
precondition(copied == [5, 6])
```

**Observe:** Copying out of the buffer inside the closure returns an owned array [5, 6].

Returning buffer.baseAddress hands out a pointer whose validity ends with the closure; using it later is undefined even if the address looks unchanged. Copy the needed data out while access is still granted.

### Task 5: Boundary evidence

Test empty, singleton and multi-element buffers.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
func bufferSum(_ values: [Int]) -> Int {
  values.withUnsafeBufferPointer { buffer in buffer.reduce(0, +) }
}
precondition(bufferSum([]) == 0)
precondition(bufferSum([7]) == 7)
precondition(bufferSum([1, 2, 3, 4]) == 10)
```

**Observe:** The sums are 0 for empty, 7 for a single element, and 10 for four elements.

reduce never dereferences an empty buffer, and the singleton case shows the loop runs exactly once; all three sizes use the same scoped access.

### Task 6: Transfer and justify

Write an interoperability checklist covering ownership, alignment, initialization and error reporting.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Wrap a scoped read-only buffer operation behind a safe function contract) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** Example A calls `withUnsafeBufferPointer` on `[2, 3, 4]` and reduces the buffer inside the closure, returning only an Int. Example B calls the same method on an empty array and reads only `buffer.count`. The task 3 answer wraps the scoped read behind a safe function that takes and returns ordinary Swift values.

**Why it is correct.** The buffer is valid only for the duration of the closure, and the closure returns an owned Int, so no pointer outlives the borrow. 2 plus 3 plus 4 is 9. For empty storage the buffer's `baseAddress` may be nil, but `count` is defined and is 0, so nothing is dereferenced. The task 3 wrapper returns 9 for `[2, 3, 4]` and 0 for an empty array.

**A plausible wrong approach.** Returning `buffer.baseAddress` from the closure and reading through it later is the task 4 defect: after the closure ends the array may move or be freed, so the read is undefined behavior even if it appears to work once. Force-unwrapping `baseAddress` on the empty array would crash.

**How to verify.** For task 2, write `maxValue` that returns nil for an empty buffer and 4 for `[2, 3, 4]`. For task 5, add a singleton `[7]` and confirm the wrapper returns 7. There is no reliable runtime check for an escaped pointer, so review the closure's return type.

## Mechanism and diagnostic reasoning

Swift normally protects memory through value semantics, ARC and checked collection access. Unsafe pointer APIs deliberately cross that protection boundary for interoperability and specialized performance work. A pointer is valid only while its owner guarantees storage lifetime and binding. Compiling unsafe code does not prove its memory access is valid.

Prefer scoped buffer APIs that lend a pointer only for a closure. Do not store that pointer or use it after the closure returns. Distinguish initialized elements from allocated capacity, and preserve element alignment and type binding. This lesson uses read-only scoped access to an owned array, keeping the demonstration small enough to inspect fully.

withUnsafeBufferPointer temporarily borrows contiguous elements. The pointer count states initialized accessible elements. Return a copied result from the closure, never the borrowed pointer itself.

Unsafe does not disable all runtime checks or make an operation faster. Never infer lifetime from a pointer value remaining numerically unchanged. Keep native API ownership documented and avoid unsafe code when safe collections suffice.

## Review before continuing

Run the reference and confirm that it prints `swift-035: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
