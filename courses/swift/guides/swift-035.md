# swift-035: Unsafe memory, buffers and scope-limited access

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-034`

## Learning objectives

Keep unsafe buffer access scoped and hidden behind a safe function contract. The central exercise is task 3: Wrap a scoped read-only buffer operation behind a safe function contract.

## Purpose and mental model

Swift normally protects memory through value semantics, ARC and checked collection access. Unsafe pointer APIs deliberately cross that protection boundary for interoperability and specialized performance work. A pointer is valid only while its owner guarantees storage lifetime and binding. Compiling unsafe code does not prove its memory access is valid.

Prefer scoped buffer APIs that lend a pointer only for a closure. Do not store that pointer or use it after the closure returns. Distinguish initialized elements from allocated capacity, and preserve element alignment and type binding. This lesson uses read-only scoped access to an owned array, keeping the demonstration small enough to inspect fully.

## Vocabulary and concepts

**Pointer:** An address-based view of storage with explicit lifetime obligations.

**Borrowed access:** Temporary access without taking ownership.

**Undefined behavior:** Behavior outside the guarantees of the language or memory contract.

## How to run this lesson

Both examples call `withUnsafeBufferPointer` and return an owned result. Task 4 returns `baseAddress` out of the closure; that compiles, but using the pointer afterward is undefined behavior that may appear to work in one run and fail in another, so write it up instead of relying on output.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

withUnsafeBufferPointer temporarily borrows contiguous elements. The pointer count states initialized accessible elements. Return a copied result from the closure, never the borrowed pointer itself.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Borrow only within the closure

Scoped access limits the lifetime reasoning to one visible closure.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let values = [2, 3, 4]
      let total = values.withUnsafeBufferPointer { buffer in buffer.reduce(0, +) }
      precondition(total == 9)
    }
    print("swift-035: passed")
  }
}
```

**Observe:** The result escapes as an integer while the borrowed pointer does not.

**Trace.** `values` is a three-element array. `withUnsafeBufferPointer` gives the closure an `UnsafeBufferPointer<Int>` over the array's contiguous storage, valid only during the call. `reduce(0, +)` reads 2, 3 and 4 through the buffer and returns 9. The closure returns that plain `Int`, which is copied out, and the pointer stops being valid when the closure ends. What escapes is the computed value, never the pointer.

### Example B: Handle empty storage without dereferencing

No base-address dereference is needed, avoiding assumptions about a pointer for empty storage.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let values: [Int] = []
      let count = values.withUnsafeBufferPointer { buffer in buffer.count }
      precondition(count == 0)
    }
    print("swift-035: passed")
  }
}
```

**Observe:** An empty buffer is valid to inspect by count.

**Trace.** `values` is empty. The method still calls the closure, passing a buffer of count 0 whose `baseAddress` may be nil. Reading `buffer.count` is always safe, so the closure returns 0 without ever touching the base address. Code that assumed a non-nil `baseAddress`, for example by force-unwrapping it to pass to a C function, would crash on exactly this input, which is why the empty case is checked separately.

## Exercises

1. **Predict and explain.** Identify the pointer lifetime and the returned owned result.

2. **Guided modification.** Compute a maximum with an explicit empty-input policy.

3. **Independent construction.** Wrap a scoped read-only buffer operation behind a safe function contract.

4. **Diagnose a defect.** Diagnose returning the buffer baseAddress for later use.

5. **Boundary evidence.** Test empty, singleton and multi-element buffers.

6. **Transfer and justify.** Write an interoperability checklist covering ownership, alignment, initialization and error reporting.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Unsafe does not disable all runtime checks or make an operation faster. Never infer lifetime from a pointer value remaining numerically unchanged. Keep native API ownership documented and avoid unsafe code when safe collections suffice.

For task 2, a maximum over an empty buffer has no answer, so a version that starts from `buffer[0]` traps on empty input. The counterexample set is empty, a singleton and an array whose maximum is last. The safe contract returns nil for empty storage, the only element for a singleton and the true maximum otherwise, all without escaping the buffer.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Borrow only within the closure) before changing anything, and confirm its observation: The result escapes as an integer while the borrowed pointer does not.
2. Compare Example B (Handle empty storage without dereferencing) with Example A and name the first line whose behavior differs. Its observation is: An empty buffer is valid to inspect by count.
3. Before opening the explanation, check your task 3 attempt (Wrap a scoped read-only buffer operation behind a safe function contract) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain why the pointer is valid only inside the closure and what could invalidate the storage afterward. Say why reading the count is safe for an empty buffer while dereferencing the base address is not. For task 6, list four questions about ownership, alignment, initialization and errors to ask before calling a C function.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Swift standard library reference documents `withUnsafeBufferPointer(_:)` and `UnsafeBufferPointer`; the Memory Safety chapter explains Swift's safety rules.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-035: Unsafe memory, buffers and scope-limited access.
Read courses/swift/guides/swift-035.md and courses/swift/lessons/swift-035.swift. Prerequisites: swift-034.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-035_solution.swift and
courses/swift/solutions/swift-035_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
