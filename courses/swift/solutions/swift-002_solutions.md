# swift-002: explanation and comparison

Reference program: [swift-002_solution.swift](swift-002_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Reassign only mutable state:** The code exposes which part is state and which part is a stable input. The accumulator becomes 8 while the fixed amount remains 4.

**Convert before division:** Converting after integer division would preserve the already truncated result. Integer division yields 3; floating division yields 3.5.

## Task answers

### Task 1: Predict and explain

Identify the inferred type of every binding.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let perBox = 4
var total = 0
total += perBox
let whole = 7 / 2
let fractional = Double(7) / Double(2)
precondition(type(of: perBox) == Int.self && type(of: total) == Int.self)
precondition(type(of: whole) == Int.self && type(of: fractional) == Double.self)
```

**Observe:** perBox, total and whole are inferred as Int and fractional as Double.

Integer literals default to Int, so 7 / 2 stays Int; the explicit Double conversions make the division and its result Double. type(of:) confirms the static choice at run time.

### Task 2: Guided modification

Replace an unnecessary var with let and explain why it still compiles.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
let perBox = 4
let boxes = 2
let total = perBox * boxes
precondition(total == 8 && perBox == 4)
```

**Observe:** Computing the total once as perBox * boxes gives 8 with every binding declared let.

Example A needs var because += reassigns total twice. When the total is produced by one expression it is assigned exactly once, so let compiles, and swiftc's never-mutated warning disappears.

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

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
let total = 7
let count = 2
let late = Double(total / count)
let early = Double(total) / Double(count)
precondition(late == 3.0)
precondition(early == 3.5)
```

**Observe:** Converting after the division gives 3.0; converting the operands first gives 3.5.

total / count is Int division and has already discarded the half before Double(...) sees it; the conversion must happen to the operands, not to the truncated quotient.

### Task 5: Boundary evidence

Test an exactly divisible and a non-divisible pair.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
func mean(_ total: Int, _ count: Int) -> Double { Double(total) / Double(count) }
precondition(mean(8, 2) == 4.0 && 8 / 2 == 4)
precondition(mean(7, 2) == 3.5 && 7 / 2 == 3)
```

**Observe:** 8 and 2 give 4.0 by both routes, while 7 and 2 give 3.5 only with the conversion (Int division gives 3).

An exactly divisible pair cannot reveal truncation, so the non-divisible pair is the case that distinguishes the deliberate conversion from integer division.

### Task 6: Transfer and justify

Choose units and types for a small measurement model.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** Example A separates a fixed input, `let perBox = 4`, from an accumulator, `var total`, and adds the box size twice. Example B divides 7 by 2 twice: once with `Int` operands and once after converting both operands to `Double`. The task 3 answer converts a total and count before dividing to get a mean.

**Why it is correct.** `total` ends at 8 because two additions of 4 occur, while `perBox` cannot change since it is a `let` binding. `7 / 2` on integers truncates toward zero and yields 3; `Double(7) / Double(2)` keeps the fraction and yields 3.5. The conversion happens before the operator, so no information is lost.

**A plausible wrong approach.** Writing `Double(7 / 2)` looks like a conversion to floating point, but the integer division has already produced 3, so the result is 3.0, not 3.5. The `fractional == 3.5` check rejects it. Declaring `perBox` with `var` would compile but would hide which value is supposed to stay fixed.

**How to verify.** Run the reference and expect only the marker, since successful checks are silent. Then edit Example B to `Double(7 / 2)` and confirm the precondition on 3.5 fails. For the inferred types, add `let _: Int = whole` and `let _: Double = fractional`; both lines compile.

## Mechanism and diagnostic reasoning

Swift distinguishes a binding that may change from one that may not. `let` prevents reassignment; `var` permits it. Prefer let until a state transition is part of the design. The compiler infers types from context, but inference does not make values dynamically typed. A variable initialized with an Int cannot later become a String.

Conversions are explicit between many numeric types. This makes information-changing boundaries visible. A value being representable in one type does not prove it is valid for a domain. Keep units in names and validation at input boundaries. Later chapters introduce reference types, where a constant reference can still point to a mutable object.

`let count: Int = 3` gives an explicit type. `var total = 0` infers Int. `Double(count)` converts a numeric value. Swift source normally does not need semicolons at line ends.

Let protects the binding, not necessarily every object reachable from it. Avoid forced conversions at a boundary without validating range. A floating type is not automatically more appropriate for a count.

## Review before continuing

Run the reference and confirm it prints `swift-002: passed`, then rerun the guide's counterexample.
