# swift-018: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-018_solution.swift](swift-018_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Reuse an ordering mechanism:** The Comparable requirement makes ordering available without dynamic casts. One implementation preserves Int and String results.

**Preserve container element type:** The relationship is encoded in the type rather than a runtime convention. Swapping retains the same concrete element type.

## Task answers

### Task 1: Predict and explain

Identify inferred generic types at every call.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The Comparable requirement makes ordering available without dynamic casts. One implementation preserves Int and String results.

### Task 2: Guided modification

Use larger with Double values and a tie.

No separate reference answer has been written for this task. Start from Example B: The relationship is encoded in the type rather than a runtime convention. Swapping retains the same concrete element type.

### Task 3: Independent construction

Create a generic immutable triple with a rotation operation.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
struct Triple<T> {
  let first: T
  let second: T
  let third: T
  func rotated() -> Triple<T> { Triple(first: second, second: third, third: first) }
}
let rotated = Triple(first: 1, second: 2, third: 3).rotated()
precondition(rotated.first == 2 && rotated.second == 3 && rotated.third == 1)
```

**Observe:** Rotating (1, 2, 3) gives (2, 3, 1).

The properties are let constants, so rotation returns a new triple instead of changing the original.

### Task 4: Diagnose a defect

Diagnose calling an unavailable method on an unconstrained T.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Any discards useful type information. Excessively broad constraints make reuse harder. A generic algorithm still needs domain-specific failure and ordering policies.

### Task 5: Boundary evidence

State tie behavior and test equal inputs.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Reuse an ordering mechanism) and Example B (Preserve container element type).

### Task 6: Transfer and justify

Choose generic or existential abstraction for an API that must preserve concrete result type.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Generic parameter**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Generics preserve type relationships across an algorithm or container. A generic pair stores two values of the same chosen type. The compiler rejects mixing unrelated types unless the API explicitly models that possibility. This is stronger and clearer than storing Any and casting later.

Constraints expose the capabilities an algorithm needs. Comparable permits ordering, while Equatable permits equality. Use the narrowest useful constraint and state behavior for ties and empty inputs. Generic abstraction is valuable when it removes duplicated mechanisms without erasing domain meaning.

`func larger<T: Comparable>` introduces a constrained type parameter. The return type T preserves the input relationship. Generic structs use the same parameter syntax.

Any discards useful type information. Excessively broad constraints make reuse harder. A generic algorithm still needs domain-specific failure and ordering policies.

## Review before continuing

Run the reference and confirm that it prints `swift-018: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
