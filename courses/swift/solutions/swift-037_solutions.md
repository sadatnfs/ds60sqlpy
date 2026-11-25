# swift-037: explanation and comparison

Reference program: [swift-037_solution.swift](swift-037_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Apply a bounded display policy:** The wrapper enforces a deliberate display range at every assignment. Assignments are clamped into zero through ten.

**Retain valid interior values:** The projected information explains the policy without exposing mutable internal storage. A valid interior value is unchanged and the projection exposes the range.

## Task answers

### Task 1: Predict and explain

Trace initialization and both setter calls.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let direct = Clamped(wrappedValue: 15, 0...10)
precondition(direct.wrappedValue == 10)
var control = Control()
precondition(control.level == 0)
control.level = 12
precondition(control.level == 10)
control.level = -2
precondition(control.level == 0)
```

**Observe:** Initializing with 15 already clamps to 10, Control starts at 0, and the two setters store 10 then 0.

@Clamped(0...10) var level = 0 calls init(wrappedValue: 0, 0...10), which clamps once; each later assignment goes through the wrappedValue setter, which clamps again.

### Task 2: Guided modification

Change the allowed range and update boundary tests.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
struct Volume {
  @Clamped(1...5) var level = 3
}
var volume = Volume()
volume.level = 0
precondition(volume.level == 1)
volume.level = 6
precondition(volume.level == 5)
precondition(volume.$level == 1...5)
```

**Observe:** With range 1...5, 0 becomes 1, 6 becomes 5, and the projection reports 1...5.

The range is a wrapper argument, so changing it moves both boundaries and the tests must move with it; the projection lets the test read the active range.

### Task 3: Independent construction

Create a wrapper with an explicit normalization policy for a local display field.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
var label = DisplayLabel()
label.title = "  Report  "
precondition(label.title == "Report")
precondition(DisplayLabel(title: " x ").title == "x")
```

**Observe:** Both assignment and initialization store the trimmed text Report and x.

The wrapper applies one normalization policy in its setter, and init(wrappedValue:) routes initial values through the same setter.

### Task 4: Diagnose a defect

Explain why silently clamping a payment amount would be misleading.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
struct Payment {
  @Clamped(0...100) var amount = 0
}
var payment = Payment()
payment.amount = 250
precondition(payment.amount == 100)
enum AmountError: Error { case outOfRange }
func checkedAmount(_ value: Int) throws -> Int {
  guard (0...100).contains(value) else { throw AmountError.outOfRange }
  return value
}
precondition((try? checkedAmount(250)) == nil)
```

**Observe:** The clamped payment silently becomes 100, while the checked version refuses 250.

Clamping a payment changes what the user asked to pay without telling them; a failure that can be reported is the honest result for money.

### Task 5: Boundary evidence

Test both endpoints and one value outside each.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
var control = Control()
control.level = 0
precondition(control.level == 0)
control.level = 10
precondition(control.level == 10)
control.level = -1
precondition(control.level == 0)
control.level = 11
precondition(control.level == 10)
```

**Observe:** The endpoints 0 and 10 are kept, -1 becomes 0, and 11 becomes 10.

The range is closed, so both endpoints are valid stored values; one step past either end is pulled back to that endpoint.

### Task 6: Transfer and justify

Choose a wrapper or explicit validation method based on whether assignment can fail meaningfully.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** `Clamped` is a property wrapper that stores an Int and a `ClosedRange`, clamps in both its initializer and its `wrappedValue` setter, and projects the range through `projectedValue`. `Control` declares `@Clamped(0...10) var level = 0`. Example A assigns values above and below the range; Example B assigns 4 and reads `$level`. The task 3 answer is a wrapper that trims text on both initialization and assignment.

**Why it is correct.** Assigning 12 runs `min(max(12, 0), 10)`, which is 10. Assigning -2 runs `min(max(-2, 0), 10)`, which is 0. For 4 both bounds leave it alone. Reading `control.$level` returns the projection, which is the range `0...10` rather than the stored integer. In task 3 both assignment and initialization store the trimmed text Report and x, because the same normalization runs in both places.

**A plausible wrong approach.** Clamping only in the setter and storing `wrappedValue` unchanged in `init` would let `@Clamped(0...10) var level = 15` start at 15, an out-of-range value that no assignment produced. Using the same silent clamping for a payment amount (task 4) would turn an invalid 120 into a charged 100 with no error the caller can see.

**How to verify.** For task 5, assign 0 and 10 and confirm they are kept, then assign -1 and 11 and confirm they become 0 and 10. For task 2, change the range to `1...5` and update all four boundary checks together, including the initial value, which must now lie in the new range.

## Mechanism and diagnostic reasoning

A property wrapper packages behavior around property storage and access. It can validate, normalize or project a reusable policy, but it should not hide surprising I/O or authorization. The wrappedValue is the property-facing interface; projectedValue can expose related information using dollar-prefixed access.

Wrapper behavior is part of the containing type's semantics. Decide whether invalid assignments are rejected, clamped or represented as an error, and make that choice visible to readers. A clamped value can be appropriate for a display control but inappropriate for financial input where silent correction hides an error.

`@propertyWrapper` marks a wrapper type. wrappedValue supplies get/set behavior. `@Clamped var level` applies it. A projectedValue is read through `$level` when declared.

A wrapper is not a substitute for validating external input. Hidden side effects make ordinary-looking assignment hard to reason about. Document projection and mutation semantics.

## Review before continuing

Run the reference and confirm it prints `swift-037: passed`, then rerun the guide's counterexample.
