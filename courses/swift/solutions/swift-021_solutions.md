# swift-021: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-021_solution.swift](swift-021_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Validate before returning:** Failure carries a domain category instead of masquerading as zero. Three is accepted and a negative quantity is rejected.

**Store an outcome for later inspection:** Result separates when an operation executes from when its outcome is examined. The stored outcome retains a QuantityError.

## Task answers

### Task 1: Predict and explain

Trace the normal and throwing paths.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Failure carries a domain category instead of masquerading as zero. Three is accepted and a negative quantity is rejected.

### Task 2: Guided modification

Distinguish malformed text from negative quantity with separate error cases.

No separate reference answer has been written for this task. Start from Example B: Result separates when an operation executes from when its outcome is examined. The stored outcome retains a QuantityError.

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

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Try! turns recoverable failure into a trap. Try? deliberately discards error detail, so use it only when absence is the intended contract. Do not catch assertion failures as ordinary input errors.

### Task 5: Boundary evidence

Test empty, zero and out-of-range input.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Validate before returning) and Example B (Store an outcome for later inspection).

### Task 6: Transfer and justify

Choose Optional, throws or Result for three APIs and explain each semantic distinction.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Error**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Swift errors represent recoverable failure that a caller must acknowledge with try. A throwing function can return its normal type or throw an Error value. Catching belongs at a layer that can recover, translate or report meaningfully. A generic fallback can hide a failed operation as an ordinary empty result.

Result stores success or failure as a value, useful when an outcome must be retained or passed through another API. Optional absence and errors are different: a missing lookup may be expected, while malformed input carries a reason. Preserve those distinctions instead of force-trying external operations.

`throws` declares failure capability. `try` acknowledges a throwing call. `do/catch` handles errors. Result<Success, Failure> stores an outcome, with Failure conforming to Error.

Try! turns recoverable failure into a trap. Try? deliberately discards error detail, so use it only when absence is the intended contract. Do not catch assertion failures as ordinary input errors.

## Review before continuing

Run the reference and confirm that it prints `swift-021: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
