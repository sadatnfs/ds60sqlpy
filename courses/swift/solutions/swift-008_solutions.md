# swift-008: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-008_solution.swift](swift-008_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Name the dimensions:** Readable call sites reduce accidental parameter swaps and reveal the function purpose. Labels show which dimension each argument supplies.

**Make mutation explicit:** The ampersand makes the mutation boundary visible instead of hiding it behind a normal-looking value call. The caller explicitly grants mutation and observes 5.

## Task answers

### Task 1: Predict and explain

Explain each argument label and local parameter name.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Readable call sites reduce accidental parameter swaps and reveal the function purpose. Labels show which dimension each argument supplies.

### Task 2: Guided modification

Add a depth label for a volume function.

No separate reference answer has been written for this task. Start from Example B: The ampersand makes the mutation boundary visible instead of hiding it behind a normal-looking value call. The caller explicitly grants mutation and observes 5.

### Task 3: Independent construction

Write a pure function normalizing a quantity without mutating its caller.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
func normalized(_ quantity: Int, limit: Int) -> Int {
  min(max(quantity, 0), limit)
}
let requested = 15
precondition(normalized(requested, limit: 10) == 10)
precondition(normalized(-4, limit: 10) == 0 && requested == 15)
```

**Observe:** 15 is normalized to 10 and -4 to 0, while the caller's value stays 15.

The function takes its argument by value and returns a new result, so it cannot change the caller's variable.

### Task 4: Diagnose a defect

Diagnose an inout call missing the ampersand and explain the compiler rule.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Labels are part of API usability. Inout access cannot overlap conflicting access to the same storage. Do not use mutation merely to avoid returning a small value.

### Task 5: Boundary evidence

Test zero and negative dimensions under a documented validation policy.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Name the dimensions) and Example B (Make mutation explicit).

### Task 6: Transfer and justify

Choose return values or inout for an API and justify who owns state changes.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Argument label**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A function groups a computation behind a contract. Swift distinguishes the argument label read at the call site from the parameter name used inside the body. Labels can make an API read as a clear operation rather than an unexplained list of positional values. Use the underscore label only when the surrounding context already makes the meaning clear.

Ordinary value arguments are passed with value semantics. An inout parameter explicitly grants temporary mutation of the caller value under Swift exclusivity rules. Prefer returned values for pure transformations and use inout when mutation is the actual interface. A function contract should state invalid-input behavior and whether any state changes before failure.

`func area(width: Int, height: Int) -> Int` exposes labels. `_ value` removes the external label. `inout` in a declaration pairs with `&` at the call site. `return` supplies the result and exits.

Labels are part of API usability. Inout access cannot overlap conflicting access to the same storage. Do not use mutation merely to avoid returning a small value.

## Review before continuing

Run the reference and confirm that it prints `swift-008: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
