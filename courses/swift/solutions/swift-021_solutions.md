# swift-021: explanation and comparison

Reference program: [swift-021_solution.swift](swift-021_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Validate before returning:** Failure carries a domain category instead of masquerading as zero. Three is accepted and a negative quantity is rejected.

**Store an outcome for later inspection:** Result separates when an operation executes from when its outcome is examined. The stored outcome retains a QuantityError.

## Task answers

### Task 1: Predict and explain

Trace the normal and throwing paths.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
func trace(_ text: String) -> String {
  do {
    let value = try parseQuantity(text)
    return "returned \(value)"
  } catch {
    return "threw"
  }
}
precondition(trace("3") == "returned 3")
precondition(trace("-1") == "threw" && trace("x") == "threw")
```

**Observe:** 3 follows the normal path and returns 3, while -1 and x leave through the throw.

parseQuantity either reaches return value or exits at throw; the guard decides which, and control resumes in the caller's catch only on the throwing path.

### Task 2: Guided modification

Distinguish malformed text from negative quantity with separate error cases.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
enum QuantityProblem: Error, Equatable {
  case malformed
  case negative
}
func strictQuantity(_ text: String) throws(QuantityProblem) -> Int {
  guard let value = Int(text) else { throw .malformed }
  guard value >= 0 else { throw .negative }
  return value
}
func problem(_ text: String) -> QuantityProblem? {
  do { _ = try strictQuantity(text) } catch { return error }
  return nil
}
precondition(problem("x") == .malformed && problem("-1") == .negative)
precondition(problem("4") == nil)
```

**Observe:** x reports malformed, -1 reports negative, and 4 reports no problem.

Splitting the guard into two conditions with distinct cases lets the caller tell a typing mistake from a domain violation; the typed throws makes the caught error a QuantityProblem.

### Task 3: Independent construction

Write a throwing validator for an inventory record.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
struct Record {
  let name: String
  let quantity: Int
}
enum RecordError: Error, Equatable {
  case emptyName
  case negativeQuantity
}
func validate(_ record: Record) throws -> Record {
  guard !record.name.isEmpty else { throw RecordError.emptyName }
  guard record.quantity >= 0 else { throw RecordError.negativeQuantity }
  return record
}
let valid = try validate(Record(name: "pear", quantity: 2))
precondition(valid.quantity == 2)
var caught: RecordError? = nil
do {
  _ = try validate(Record(name: "", quantity: 1))
} catch let error as RecordError {
  caught = error
}
precondition(caught == .emptyName)
```

**Observe:** A valid record passes; an empty name throws RecordError.emptyName.

Each rule throws its own error case, so the caller learns which rule failed instead of receiving a generic false.

### Task 4: Diagnose a defect

Diagnose try? used where discarding the error reason loses required evidence.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
precondition((try? parseQuantity("x")) == nil)
precondition((try? parseQuantity("-1")) == nil)
let kept = Result { try parseQuantity("-1") }
if case .failure(let error) = kept { precondition(error is QuantityError) }
```

**Observe:** try? turns both malformed and negative input into the same nil, while Result keeps the QuantityError.

When the reason must be reported, try? discards the evidence; do/catch or Result preserves the error for the caller to inspect.

### Task 5: Boundary evidence

Test empty, zero and out-of-range input.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
func accepts(_ text: String) -> Bool { (try? parseQuantity(text)) != nil }
precondition(!accepts(""))
let zero = try parseQuantity("0")
precondition(zero == 0)
precondition(!accepts("99999999999999999999"))
```

**Observe:** Empty text is rejected, 0 is accepted as 0, and a value beyond Int.max is rejected.

Int("") and Int on an overflowing literal both return nil, so the guard throws; 0 passes the value >= 0 check exactly.

### Task 6: Transfer and justify

Choose Optional, throws or Result for three APIs and explain each semantic distinction.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** `parseQuantity` throws `QuantityError.invalid` when the text is not an integer or is negative. Example A uses `try` on valid input and a `do`/`catch` that records the rejection of -1. Example B wraps a throwing call in `Result` and inspects it later with a switch. The task 3 answer writes a throwing validator for an inventory record.

**Why it is correct.** "3" parses to 3 and passes the nonnegative guard, so it returns normally. "-1" parses but fails `value >= 0`, so the catch clause runs and sets `rejected`. "bad" fails `Int(text)`, so the Result holds `.failure`, and `error is QuantityError` confirms the category. In task 3, a valid record passes and an empty name throws `RecordError.emptyName`.

**A plausible wrong approach.** Writing `let quantity = (try? parseQuantity(text)) ?? 0` hides the reason and turns bad text into zero stock, which task 4 asks you to diagnose. Using `try!` on the "-1" input crashes instead of reporting. Both shortcuts pass a happy-path test and fail on the inputs this lesson checks.

**How to verify.** For task 2, add separate `malformed` and `negative` cases, then confirm "bad" produces the first and "-1" the second. For task 5, test empty text (malformed), "0" (accepted) and "99999999999999999999" (malformed, because it overflows Int).

## Mechanism and diagnostic reasoning

Swift errors represent recoverable failure that a caller must acknowledge with try. A throwing function can return its normal type or throw an Error value. Catching belongs at a layer that can recover, translate or report meaningfully. A generic fallback can hide a failed operation as an ordinary empty result.

Result stores success or failure as a value, useful when an outcome must be retained or passed through another API. Optional absence and errors are different: a missing lookup may be expected, while malformed input carries a reason. Preserve those distinctions instead of force-trying external operations.

`throws` declares failure capability. `try` acknowledges a throwing call. `do/catch` handles errors. Result<Success, Failure> stores an outcome, with Failure conforming to Error.

Try! turns recoverable failure into a trap. Try? deliberately discards error detail, so use it only when absence is the intended contract. Do not catch assertion failures as ordinary input errors.

## Review before continuing

Run the reference and confirm it prints `swift-021: passed`, then rerun the guide's counterexample.
