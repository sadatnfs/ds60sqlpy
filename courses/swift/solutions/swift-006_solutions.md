# swift-006: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-006_solution.swift](swift-006_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Classify thresholds:** The ranges express the inclusive boundary and keep out-of-domain values separate. 59 retries, 60 passes and 101 is invalid.

**Use a guard for a required value:** The unwrapped binding is available after the guard because every failing path has returned. The early exit excludes missing and empty values before the valid path.

## Task answers

### Task 1: Predict and explain

Predict each threshold case before running.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The ranges express the inclusive boundary and keep out-of-domain values separate. 59 retries, 60 passes and 101 is invalid.

### Task 2: Guided modification

Move the pass boundary to 70 and update adjacent tests.

No separate reference answer has been written for this task. Start from Example B: The unwrapped binding is available after the guard because every failing path has returned. The early exit excludes missing and empty values before the valid path.

### Task 3: Independent construction

Write a three-way classifier for negative, zero and positive quantities.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
func sign(_ quantity: Int) -> String {
  switch quantity {
  case ..<0: return "negative"
  case 0: return "zero"
  default: return "positive"
  }
}
precondition(sign(-2) == "negative" && sign(0) == "zero")
precondition(sign(7) == "positive")
```

**Observe:** -2, 0 and 7 are classified as negative, zero and positive.

After the two explicit cases, only positive integers remain, so the default case is exactly the positive branch.

### Task 4: Diagnose a defect

Diagnose a closed range used where an exclusive upper bound was intended.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A default can hide future cases. Guard must actually exit on failure. Avoid treating every invalid value as the normal else category without a stated policy.

### Task 5: Boundary evidence

Test both ends of the valid domain and one value beyond each.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Classify thresholds) and Example B (Use a guard for a required value).

### Task 6: Transfer and justify

Replace a broad default in an enum switch with explicit cases and explain the maintenance benefit.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Exhaustiveness**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Control flow selects which operations execute. A branch should correspond to a domain distinction that can be explained before reading the code. Swift switch does not implicitly fall through to the next case, and the compiler requires coverage of possible inputs. This helps make state handling deliberate.

Range boundaries remain a source of mistakes. A closed range includes both ends; a half-open range excludes its upper end. Use fixtures exactly at transitions and outside the valid domain. A broad default can satisfy exhaustiveness while still hiding a new state, so prefer explicit enum cases when the domain is finite.

`if` requires a Bool. `switch` matches cases without implicit fallthrough. `0..<10` excludes ten; `0...10` includes it. A where clause narrows a matched case.

A default can hide future cases. Guard must actually exit on failure. Avoid treating every invalid value as the normal else category without a stated policy.

## Review before continuing

Run the reference and confirm that it prints `swift-006: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
