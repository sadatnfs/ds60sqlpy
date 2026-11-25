# swift-008: explanation and comparison

Reference program: [swift-008_solution.swift](swift-008_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Name the dimensions:** Readable call sites reduce accidental parameter swaps and reveal the function purpose. Labels show which dimension each argument supplies.

**Make mutation explicit:** The ampersand makes the mutation boundary visible instead of hiding it behind a normal-looking value call. The caller explicitly grants mutation and observes 5.

## Task answers

### Task 1: Predict and explain

Explain each argument label and local parameter name.

**Written answer.** In `area(width: Int, height: Int)` each parameter has one name, so `width` and `height` serve both as the argument labels at the call site and as the local names inside the body. In `increment(_ value: inout Int)` the underscore removes the label, so callers write `increment(&count)`, while the body still refers to the parameter as `value`. Labels describe the role of an argument to the caller; parameter names are what the implementation reads.

### Task 2: Guided modification

Add a depth label for a volume function.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
func volume(width: Int, height: Int, depth: Int) -> Int { width * height * depth }
precondition(volume(width: 2, height: 3, depth: 4) == 24)
precondition(volume(width: 2, height: 3, depth: 0) == 0)
```

**Observe:** A 2 by 3 by 4 box has volume 24, and depth 0 gives 0.

The depth label makes the third dimension readable at the call site, so a caller cannot silently confuse it with width or height.

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

**Written answer.** Calling `increment(count)` instead of `increment(&count)` is a compile error: swiftc reports that passing a value of type Int to an inout parameter requires an explicit &. The rule exists so that every call that may change the caller's storage is visible where it is written. Because compilation fails, no line of the program runs; adding the ampersand restores the call and Example B again observes 5.

### Task 5: Boundary evidence

Test zero and negative dimensions under a documented validation policy.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
func checkedArea(width: Int, height: Int) -> Int? {
  guard width >= 0, height >= 0 else { return nil }
  return width * height
}
precondition(checkedArea(width: 0, height: 4) == 0)
precondition(checkedArea(width: -3, height: 4) == nil)
precondition(checkedArea(width: -3, height: -4) == nil)
```

**Observe:** A zero width gives area 0, while one or two negative dimensions are rejected as nil.

The policy accepts zero as a degenerate but valid shape and rejects negatives; checking each dimension matters because -3 times -4 would otherwise produce a plausible 12.

### Task 6: Transfer and justify

Choose return values or inout for an API and justify who owns state changes.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** Example A labels both arguments of `area(width:height:)` so every call names its dimensions. Example B declares `increment(_ value: inout Int)` and calls it with `&count`, making mutation visible at the call site. The task 3 answer clamps a quantity with a pure function that returns a new value and leaves the caller's variable alone.

**Why it is correct.** 3 times 4 is 12 and a zero width gives 0, so both area checks hold regardless of label order in the declaration. The `inout` parameter is copied in, incremented and written back when the call ends, so `count` changes from 4 to 5. In task 3, 15 normalizes to 10 and -4 to 0 while the original 15 stays 15.

**A plausible wrong approach.** Calling `increment(count)` without the ampersand is rejected by the compiler, because passing to an `inout` parameter requires explicit `&`. A subtler mistake is making the task 3 normalizer take `inout` and overwrite the caller; the check that the caller still holds 15 then fails.

**How to verify.** Remove the `&` from `increment(&count)` and read the compiler diagnostic, which names the missing ampersand; that is a compile-time rejection, not a runtime failure. Restore it and confirm the task 3 values 10, 0 and the unchanged 15.

## Mechanism and diagnostic reasoning

A function groups a computation behind a contract. Swift distinguishes the argument label read at the call site from the parameter name used inside the body. Labels can make an API read as a clear operation rather than an unexplained list of positional values. Use the underscore label only when the surrounding context already makes the meaning clear.

Ordinary value arguments are passed with value semantics. An inout parameter explicitly grants temporary mutation of the caller value under Swift exclusivity rules. Prefer returned values for pure transformations and use inout when mutation is the actual interface. A function contract should state invalid-input behavior and whether any state changes before failure.

`func area(width: Int, height: Int) -> Int` exposes labels. `_ value` removes the external label. `inout` in a declaration pairs with `&` at the call site. `return` supplies the result and exits.

Labels are part of API usability. Inout access cannot overlap conflicting access to the same storage. Do not use mutation merely to avoid returning a small value.

## Review before continuing

Run the reference and confirm it prints `swift-008: passed`, then rerun the guide's counterexample.
