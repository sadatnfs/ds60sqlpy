# swift-002: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-002_solution.swift](swift-002_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Reassign only mutable state:** The code exposes which part is state and which part is a stable input. The accumulator becomes 8 while the fixed amount remains 4.

**Convert before division:** Converting after integer division would preserve the already truncated result. Integer division yields 3; floating division yields 3.5.

## Task answers

### Task 1: Predict and explain

Identify the inferred type of every binding.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The code exposes which part is state and which part is a stable input. The accumulator becomes 8 while the fixed amount remains 4.

### Task 2: Guided modification

Replace an unnecessary var with let and explain why it still compiles.

No separate reference answer has been written for this task. Start from Example B: Converting after integer division would preserve the already truncated result. Integer division yields 3; floating division yields 3.5.

### Task 3: Independent construction

Compute a mean from an integer total and count using a deliberate conversion.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
let total = 7
let count = 2
let mean = Double(total) / Double(count)
precondition(mean == 3.5)
precondition(total / count == 3)
```

**Observe:** The mean is 3.5, while integer division of the same values would give 3.

Converting both operands to Double before dividing is the deliberate step; dividing the Ints first would truncate the result.

### Task 4: Diagnose a defect

Diagnose conversion performed after integer division.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Let protects the binding, not necessarily every object reachable from it. Avoid forced conversions at a boundary without validating range. A floating type is not automatically more appropriate for a count.

### Task 5: Boundary evidence

Test an exactly divisible and a non-divisible pair.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Reassign only mutable state) and Example B (Convert before division).

### Task 6: Transfer and justify

Choose units and types for a small measurement model.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Binding**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Swift distinguishes a binding that may change from one that may not. `let` prevents reassignment; `var` permits it. Prefer let until a state transition is part of the design. The compiler infers types from context, but inference does not make values dynamically typed. A variable initialized with an Int cannot later become a String.

Conversions are explicit between many numeric types. This makes information-changing boundaries visible. A value being representable in one type does not prove it is valid for a domain. Keep units in names and validation at input boundaries. Later chapters introduce reference types, where a constant reference can still point to a mutable object.

`let count: Int = 3` gives an explicit type. `var total = 0` infers Int. `Double(count)` converts a numeric value. Swift source normally does not need semicolons at line ends.

Let protects the binding, not necessarily every object reachable from it. Avoid forced conversions at a boundary without validating range. A floating type is not automatically more appropriate for a count.

## Review before continuing

Run the reference and confirm that it prints `swift-002: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
