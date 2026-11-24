# swift-003: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-003_solution.swift](swift-003_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Observe overflow without crashing:** The flag is essential: the partial result alone cannot identify the intended mathematical sum. 255 plus one reports overflow and a wrapped partial result of zero.

**Use a numerical comparison policy:** The force unwrap is limited to authored literal fixtures known to parse; external text needs conditional handling. The floating result meets the stated tolerance and the decimal fixture retains decimal intent.

## Task answers

### Task 1: Predict and explain

Predict the overflow flag and partial result.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
precondition(UInt8.max == 255)
let result = UInt8.max.addingReportingOverflow(1)
precondition(result.overflow == true)
precondition(result.partialValue == 0)
```

**Observe:** UInt8.max is 255; adding 1 reports overflow true and partial value 0.

256 needs a ninth bit, so the low eight bits are all zero; the reporting operation returns that wrapped value together with the flag instead of trapping.

### Task 2: Guided modification

Repeat the boundary with UInt8 zero minus one using the reporting operation.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
let result = UInt8(0).subtractingReportingOverflow(1)
precondition(result.overflow)
precondition(result.partialValue == 255)
precondition(UInt8(1).subtractingReportingOverflow(1).partialValue == 0)
```

**Observe:** 0 minus 1 reports overflow with partial value 255, while 1 minus 1 is 0 without overflow.

An unsigned type has no -1, so the lower boundary wraps to the top of the range; the flag is the only signal that 255 is not a real difference.

### Task 3: Independent construction

Write checked quantity addition that returns an explicit rejected outcome.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
enum Addition: Equatable {
  case accepted(UInt8)
  case rejected
}
func add(_ left: UInt8, _ right: UInt8) -> Addition {
  let result = left.addingReportingOverflow(right)
  return result.overflow ? .rejected : .accepted(result.partialValue)
}
precondition(add(200, 50) == .accepted(250))
precondition(add(200, 56) == .rejected)
```

**Observe:** 200 + 50 is accepted as 250; 200 + 56 is rejected instead of wrapping to 0.

addingReportingOverflow exposes the overflow flag, and the enum gives the rejected outcome its own case rather than a sentinel number.

### Task 4: Diagnose a defect

Diagnose ignoring the overflow flag.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
let ignored = UInt8(250).addingReportingOverflow(10).partialValue
precondition(ignored == 4)
let checked = UInt8(250).addingReportingOverflow(10)
precondition(checked.overflow && checked.partialValue == ignored)
```

**Observe:** Reading only partialValue turns 250 + 10 into 4; the same result's overflow flag is true.

260 minus 256 leaves 4, a plausible-looking quantity. Code that drops the flag reports it as a real total, so the flag must be checked before the partial value is used.

### Task 5: Boundary evidence

Compare zero, normal and maximum-range inputs.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
func checkedAdd(_ left: UInt8, _ right: UInt8) -> UInt8? {
  let result = left.addingReportingOverflow(right)
  return result.overflow ? nil : result.partialValue
}
precondition(checkedAdd(0, 0) == 0)
precondition(checkedAdd(100, 55) == 155)
precondition(checkedAdd(255, 0) == 255)
precondition(checkedAdd(255, 1) == nil)
```

**Observe:** 0 + 0 is 0, 100 + 55 is 155, 255 + 0 is 255, and 255 + 1 is rejected as nil.

The maximum itself is still a valid sum; only the step past 255 overflows, so testing 255 + 0 and 255 + 1 pins the boundary from both sides.

### Task 6: Transfer and justify

Choose a numeric representation and rounding policy for a price calculation.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Write checked quantity addition that returns an explicit rejected outcome) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** Example A calls `addingReportingOverflow` on `UInt8.max` and reads both the `partialValue` and the `overflow` flag. Example B compares `0.1 + 0.2` with 0.3 under an explicit tolerance of `1e-12` and repeats the sum with `Decimal` parsed from literal strings. The task 3 answer rejects a quantity sum that overflows instead of wrapping it.

**Why it is correct.** `UInt8` holds 0 through 255, so 255 + 1 has no representation; the reporting call returns 0 as the wrapped bits and sets `overflow` to true. The ordinary sum 2 + 3 stays in range with partial value 5. Binary `Double` cannot store 0.1 exactly, so a tolerance is the honest comparison, while `Decimal` keeps base-ten digits.

**A plausible wrong approach.** Reading only `partialValue` and treating 0 as the answer is the classic error: 255 + 1 would silently become an empty total. The `precondition(result.overflow)` line catches it. Comparing `0.1 + 0.2 == 0.3` directly also fails, because the double sum is 0.30000000000000004.

**How to verify.** For task 3, the observable values are 200 + 50 accepted as 250 and 200 + 56 rejected rather than wrapped to 0. Change the tolerance to `1e-20` and confirm the floating comparison fails, showing that the threshold is a policy you chose.

## Mechanism and diagnostic reasoning

Integer values have bounded ranges. Ordinary overflowing integer arithmetic traps in Swift, while reporting-overflow operations return both a result and an overflow flag. Wrapping operators are explicit and useful for domains such as fixed-width bit arithmetic, but usually wrong for quantities or balances.

Floating-point values approximate many decimal fractions. Compare a result according to a numerical error contract rather than expecting every decimal identity to hold exactly. Decimal can represent base-ten financial quantities more naturally, but rounding and units still require a policy. A type choice does not replace domain reasoning.

`addingReportingOverflow` returns a tuple with partialValue and overflow. `&+` explicitly wraps. `abs(actual - expected) < tolerance` expresses a simple absolute error bound appropriate only to the stated scale.

A tolerance that hides a unit error is not a numerical policy. Avoid wrapping operators for business totals unless modulo behavior is intended. Never force-unwrap untrusted numeric text.

## Review before continuing

Run the reference and confirm that it prints `swift-003: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
