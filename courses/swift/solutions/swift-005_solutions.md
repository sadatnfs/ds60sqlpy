# swift-005: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-005_solution.swift](swift-005_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Preserve zero as a value:** The branch proves presence before the wrapped integer is used. A present zero remains distinct from nil.

**Parse with an absence policy:** The fallback is an explicit display sentinel in this fixture, not a valid quantity. Parsing produces an optional and malformed text is absent.

## Task answers

### Task 1: Predict and explain

Explain the difference between nil and a wrapped zero.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let wrappedZero: Int? = 0
let absent: Int? = nil
precondition(wrappedZero != absent)
precondition(wrappedZero.map { $0 + 1 } == 1 && absent.map { $0 + 1 } == nil)
precondition((wrappedZero ?? 99) == 0 && (absent ?? 99) == 99)
```

**Observe:** Wrapped 0 maps to 1 and keeps 0 under ??, while nil stays nil under map and takes the default 99.

Optional 0 is a present measurement that happens to be zero; nil is the absence of any measurement, so operations on the value run only for the wrapped case.

### Task 2: Guided modification

Replace the display sentinel with an unknown label.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
func display(_ reading: Int?) -> String { reading.map { "\($0)" } ?? "unknown" }
precondition(display(Int("42")) == "42")
precondition(display(Int("forty-two")) == "unknown")
precondition(display(0) == "0")
```

**Observe:** 42 displays as 42, malformed text as unknown, and a real 0 still as 0.

The label is chosen only at display time, so the stored value stays nil; Example B's -1 sentinel would have looked like a real reading.

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

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
let external = "forty-two"
let parsed = Int(external)
precondition(parsed == nil)
let outcome: String
if let value = parsed { outcome = "value:\(value)" } else { outcome = "rejected:\(external)" }
precondition(outcome == "rejected:forty-two")
```

**Observe:** Int("forty-two") is nil, and the optional binding routes it to rejected:forty-two.

Writing Int(external)! would trap with Unexpectedly found nil while unwrapping, ending the program on ordinary bad input; binding the optional turns the failure into a reported outcome.

### Task 5: Boundary evidence

Test empty, zero, negative and out-of-range input.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
func parseCount(_ text: String?) -> Int? {
  guard let text, let value = Int(text), value >= 0 else { return nil }
  return value
}
precondition(parseCount("") == nil)
precondition(parseCount("0") == 0)
precondition(parseCount("-1") == nil)
precondition(parseCount("9223372036854775807") == Int.max)
precondition(parseCount("9223372036854775808") == nil)
```

**Observe:** Empty text and -1 are rejected, 0 and Int.max are accepted, and one past Int.max is rejected.

Int(_:) itself returns nil for empty and out-of-range text, and the guard adds the nonnegative rule, so every boundary maps to nil or a value without a trap.

### Task 6: Transfer and justify

Model an optional measurement whose absence must survive serialization and reporting.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Write a parser accepting only present nonnegative integers) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** Example A stores a present zero and a nil in two `Int?` bindings and uses `if let` to prove the zero is present before reading it. Example B parses "42" and "forty-two" with `Int(_:)`, then shows `?? -1` as a display sentinel. The task 3 answer accepts only present, nonnegative integers.

**Why it is correct.** `Int("42")` succeeds and `Int("forty-two")` returns nil because the initializer is failable. The zero in Example A is wrapped as `.some(0)`, which is different from `.none`, so the `if let` branch runs and finds 0. In task 3, 12 and 0 pass; nil, -3 and the text x are rejected.

**A plausible wrong approach.** Using `Int(text)!` on external input looks shorter, but `Int("forty-two")!` crashes the process. Another tempting mistake is defaulting with `?? 0` early; then a missing reading and a real zero become indistinguishable, which is the exact difference Example A protects.

**How to verify.** Check the task 3 table: 12 and 0 accepted; nil, -3 and x rejected. Replace `measured` with nil and confirm `preconditionFailure("present zero")` stops the run, proving the absent path is reachable and reported.

## Mechanism and diagnostic reasoning

An optional represents either a wrapped value or no value. This makes absence part of the type rather than an undocumented sentinel. Int zero can be a real measurement, so it should not also mean missing. Optional binding introduces a nonoptional value only inside the branch where presence has been established.

A force unwrap asserts that absence is impossible and traps if that assertion is wrong. It is suitable for tightly controlled fixture literals but is usually a poor external-input policy. Prefer if let for branching and guard let for an early-exit precondition. A fallback with ?? is valid only when the domain really assigns that replacement meaning.

`Int?` abbreviates Optional<Int>. `if let value = optional` unwraps on the present branch. `guard let` requires an early exit on failure. `??` selects a fallback only when the optional is nil.

Optional chaining preserves absence; it does not validate the remaining value. A default chosen too early can erase meaningful missingness. Never silence absence merely to satisfy a compiler diagnostic.

## Review before continuing

Run the reference and confirm that it prints `swift-005: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
