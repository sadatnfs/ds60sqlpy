# swift-005: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-005_solution.swift](swift-005_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Preserve zero as a value:** The branch proves presence before the wrapped integer is used. A present zero remains distinct from nil.

**Parse with an absence policy:** The fallback is an explicit display sentinel in this fixture, not a valid quantity. Parsing produces an optional and malformed text is absent.

## Task answers

### Task 1: Predict and explain

Explain the difference between nil and a wrapped zero.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The branch proves presence before the wrapped integer is used. A present zero remains distinct from nil.

### Task 2: Guided modification

Replace the display sentinel with an unknown label.

No separate reference answer has been written for this task. Start from Example B: The fallback is an explicit display sentinel in this fixture, not a valid quantity. Parsing produces an optional and malformed text is absent.

### Task 3: Independent construction

Write a parser accepting only present nonnegative integers.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
func parseCount(_ text: String?) -> Int? {
  guard let text, let value = Int(text), value >= 0 else { return nil }
  return value
}
precondition(parseCount("12") == 12 && parseCount("0") == 0)
precondition(parseCount(nil) == nil && parseCount("-3") == nil)
precondition(parseCount("x") == nil)
```

**Observe:** 12 and 0 are accepted; nil, -3 and x are rejected.

One guard handles absence, non-numeric text and negative values, and a valid 0 is still returned as a value.

### Task 4: Diagnose a defect

Diagnose force-unwrapping malformed external text.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Optional chaining preserves absence; it does not validate the remaining value. A default chosen too early can erase meaningful missingness. Never silence absence merely to satisfy a compiler diagnostic.

### Task 5: Boundary evidence

Test empty, zero, negative and out-of-range input.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Preserve zero as a value) and Example B (Parse with an absence policy).

### Task 6: Transfer and justify

Model an optional measurement whose absence must survive serialization and reporting.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Optional**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

An optional represents either a wrapped value or no value. This makes absence part of the type rather than an undocumented sentinel. Int zero can be a real measurement, so it should not also mean missing. Optional binding introduces a nonoptional value only inside the branch where presence has been established.

A force unwrap asserts that absence is impossible and traps if that assertion is wrong. It is suitable for tightly controlled fixture literals but is usually a poor external-input policy. Prefer if let for branching and guard let for an early-exit precondition. A fallback with ?? is valid only when the domain really assigns that replacement meaning.

`Int?` abbreviates Optional<Int>. `if let value = optional` unwraps on the present branch. `guard let` requires an early exit on failure. `??` selects a fallback only when the optional is nil.

Optional chaining preserves absence; it does not validate the remaining value. A default chosen too early can erase meaningful missingness. Never silence absence merely to satisfy a compiler diagnostic.

## Review before continuing

Run the reference and confirm that it prints `swift-005: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
