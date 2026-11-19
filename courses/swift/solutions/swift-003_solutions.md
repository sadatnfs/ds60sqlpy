# swift-003: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-003_solution.swift](swift-003_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Observe overflow without crashing:** The flag is essential: the partial result alone cannot identify the intended mathematical sum. 255 plus one reports overflow and a wrapped partial result of zero.

**Use a numerical comparison policy:** The force unwrap is limited to authored literal fixtures known to parse; external text needs conditional handling. The floating result meets the stated tolerance and the decimal fixture retains decimal intent.

## Task answers

### Task 1: Predict and explain

Predict the overflow flag and partial result.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The flag is essential: the partial result alone cannot identify the intended mathematical sum. 255 plus one reports overflow and a wrapped partial result of zero.

### Task 2: Guided modification

Repeat the boundary with UInt8 zero minus one using the reporting operation.

No separate reference answer has been written for this task. Start from Example B: The force unwrap is limited to authored literal fixtures known to parse; external text needs conditional handling. The floating result meets the stated tolerance and the decimal fixture retains decimal intent.

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

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A tolerance that hides a unit error is not a numerical policy. Avoid wrapping operators for business totals unless modulo behavior is intended. Never force-unwrap untrusted numeric text.

### Task 5: Boundary evidence

Compare zero, normal and maximum-range inputs.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Observe overflow without crashing) and Example B (Use a numerical comparison policy).

### Task 6: Transfer and justify

Choose a numeric representation and rounding policy for a price calculation.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Overflow**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Integer values have bounded ranges. Ordinary overflowing integer arithmetic traps in Swift, while reporting-overflow operations return both a result and an overflow flag. Wrapping operators are explicit and useful for domains such as fixed-width bit arithmetic, but usually wrong for quantities or balances.

Floating-point values approximate many decimal fractions. Compare a result according to a numerical error contract rather than expecting every decimal identity to hold exactly. Decimal can represent base-ten financial quantities more naturally, but rounding and units still require a policy. A type choice does not replace domain reasoning.

`addingReportingOverflow` returns a tuple with partialValue and overflow. `&+` explicitly wraps. `abs(actual - expected) < tolerance` expresses a simple absolute error bound appropriate only to the stated scale.

A tolerance that hides a unit error is not a numerical policy. Avoid wrapping operators for business totals unless modulo behavior is intended. Never force-unwrap untrusted numeric text.

## Review before continuing

Run the reference and confirm that it prints `swift-003: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
