# swift-006: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-006_solution.swift](swift-006_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Classify thresholds:** The ranges express the inclusive boundary and keep out-of-domain values separate. 59 retries, 60 passes and 101 is invalid.

**Use a guard for a required value:** The unwrapped binding is available after the guard because every failing path has returned. The early exit excludes missing and empty values before the valid path.

## Task answers

### Task 1: Predict and explain

Predict each threshold case before running.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
func classify(_ score: Int) -> String {
  switch score {
  case 0..<60: return "retry"
  case 60...100: return "pass"
  default: return "invalid"
  }
}
let predicted = ["retry", "pass", "invalid"]
precondition([59, 60, 101].map(classify) == predicted)
```

**Observe:** 59 is retry, 60 is pass and 101 is invalid, matching the predictions written beforehand.

0..<60 excludes 60, so 60 falls to the closed range 60...100; 101 lies outside both ranges and reaches default.

### Task 2: Guided modification

Move the pass boundary to 70 and update adjacent tests.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
func classify(_ score: Int) -> String {
  switch score {
  case 0..<70: return "retry"
  case 70...100: return "pass"
  default: return "invalid"
  }
}
precondition(classify(69) == "retry" && classify(70) == "pass")
precondition(classify(60) == "retry" && classify(100) == "pass")
```

**Observe:** With the boundary at 70, 69 retries, 70 passes, and the old pass score 60 now retries.

Both range bounds move together, and the adjacent tests move to 69 and 70 so they still sit on either side of the new boundary.

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

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
func overlapping(_ score: Int) -> String {
  switch score {
  case 0...60: return "retry"
  case 60...100: return "pass"
  default: return "invalid"
  }
}
func fixed(_ score: Int) -> String {
  switch score {
  case 0..<60: return "retry"
  case 60...100: return "pass"
  default: return "invalid"
  }
}
precondition(overlapping(60) == "retry" && fixed(60) == "pass")
precondition(overlapping(59) == fixed(59))
```

**Observe:** With 0...60 the score 60 is classified as retry; the exclusive 0..<60 gives pass, and 59 agrees in both.

Swift takes the first matching case, so a closed range that includes 60 captures the boundary before the pass case is reached; only the boundary value exposes the defect.

### Task 5: Boundary evidence

Test both ends of the valid domain and one value beyond each.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
func classify(_ score: Int) -> String {
  switch score {
  case 0..<60: return "retry"
  case 60...100: return "pass"
  default: return "invalid"
  }
}
precondition(classify(0) == "retry" && classify(100) == "pass")
precondition(classify(-1) == "invalid" && classify(101) == "invalid")
```

**Observe:** 0 retries and 100 passes, while -1 and 101 are invalid.

0 and 100 are the two ends of the valid domain and -1 and 101 the first values past them, so each range bound is tested from inside and outside.

### Task 6: Transfer and justify

Replace a broad default in an enum switch with explicit cases and explain the maintenance benefit.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Write a three-way classifier for negative, zero and positive quantities) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** Example A uses a `switch` over ranges: `0..<60` returns retry, `60...100` returns pass, and `default` returns invalid. Example B uses `guard let text, !text.isEmpty` to exit early for nil and empty input. The task 3 answer classifies a quantity as negative, zero or positive with explicit cases.

**Why it is correct.** The half-open range `0..<60` excludes 60, so 59 retries and 60 falls into the closed range `60...100` and passes. 101 matches neither range and reaches `default`. The guard returns on both failure conditions, so after it the compiler knows `text` is a non-empty String and the valid path can interpolate it.

**A plausible wrong approach.** Writing `0...60` for the retry band looks harmless but makes 60 retry because the first matching case wins; the `classify(60) == "pass"` check fails. A guard whose else branch prints a message without returning will not compile, because guard must leave the scope.

**How to verify.** For task 3, expect -2, 0 and 7 to classify as negative, zero and positive. Move the pass boundary to 70 as task 2 asks and confirm that 69 and 70 now need new checks while 59 still retries.

## Mechanism and diagnostic reasoning

Control flow selects which operations execute. A branch should correspond to a domain distinction that can be explained before reading the code. Swift switch does not implicitly fall through to the next case, and the compiler requires coverage of possible inputs. This helps make state handling deliberate.

Range boundaries remain a source of mistakes. A closed range includes both ends; a half-open range excludes its upper end. Use fixtures exactly at transitions and outside the valid domain. A broad default can satisfy exhaustiveness while still hiding a new state, so prefer explicit enum cases when the domain is finite.

`if` requires a Bool. `switch` matches cases without implicit fallthrough. `0..<10` excludes ten; `0...10` includes it. A where clause narrows a matched case.

A default can hide future cases. Guard must actually exit on failure. Avoid treating every invalid value as the normal else category without a stated policy.

## Review before continuing

Run the reference and confirm that it prints `swift-006: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
