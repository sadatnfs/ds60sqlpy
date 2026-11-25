# swift-015: explanation and comparison

Reference program: [swift-015_solution.swift](swift-015_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Transform a sequence:** The transformation is pure and its element-to-element relationship is visible. Map creates transformed values while retaining the original array.

**Freeze a captured value deliberately:** This differs from a closure observing a mutable captured variable later. The explicit capture list retains factor 2 for the closure.

## Task answers

### Task 1: Predict and explain

Predict the mapped result and unchanged source.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let values = [1, 2, 3]
let doubled = values.map { $0 * 2 }
precondition(doubled == [2, 4, 6])
precondition(values == [1, 2, 3] && doubled.count == values.count)
```

**Observe:** map gives [2, 4, 6], and values remains [1, 2, 3] with the same count.

map calls the closure once per element and builds a new array of the same length; it never writes to its source.

### Task 2: Guided modification

Filter even numbers before mapping.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
let values = [1, 2, 3, 4]
let evensDoubled = values.filter { $0 % 2 == 0 }.map { $0 * 2 }
precondition(evensDoubled == [4, 8])
```

**Observe:** Filtering keeps 2 and 4, and mapping doubles them to [4, 8].

Filtering first means the map closure only sees even values; mapping first and filtering afterward would test the doubled values, which are all even.

### Task 3: Independent construction

Write a function accepting a transformation closure.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
func transformAll(_ values: [Int], _ change: (Int) -> Int) -> [Int] {
  var result: [Int] = []
  for value in values { result.append(change(value)) }
  return result
}
let scaled = transformAll([1, 2, 3]) { $0 * 10 }
precondition(scaled == [10, 20, 30])
```

**Observe:** Applying the closure gives 10, 20 and 30.

The caller supplies the behavior; the closure is non-escaping, so it runs only during the call.

### Task 4: Diagnose a defect

Diagnose a closure whose captured mutable state changes before later execution.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
var factor = 2
let live = { (value: Int) in value * factor }
let frozen = { [factor] (value: Int) in value * factor }
factor = 5
precondition(live(3) == 15)
precondition(frozen(3) == 6)
```

**Observe:** After factor becomes 5, the live closure returns 15 while the capture-list closure still returns 6.

A closure captures the variable itself, so it reads the value current at call time; [factor] copies the value when the closure is created.

### Task 5: Boundary evidence

Test empty arrays and a closure that returns an optional.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
precondition([Int]().map { $0 * 2 }.isEmpty)
let parsed = ["1", "x", "3"].map { Int($0) }
precondition(parsed == [1, nil, 3])
let valid = ["1", "x", "3"].compactMap { Int($0) }
precondition(valid == [1, 3])
```

**Observe:** Mapping an empty array gives an empty array; map keeps nil for x, while compactMap drops it and returns [1, 3].

When the closure returns Int?, map produces [Int?] and preserves the failure in position; compactMap discards failures, which is a policy choice, not a neutral default.

### Task 6: Transfer and justify

Choose a named function or closure for a reusable domain transformation and explain readability and capture policy.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** Example A maps `[1, 2, 3]` through a doubling closure and confirms the source is untouched. Example B creates a closure with an explicit capture list `[factor]`, then changes `factor` to 5 before calling it. The task 3 answer writes a function that accepts a transformation closure and applies it.

**Why it is correct.** `map` builds a new array from each element, so `[2, 4, 6]` appears while `values` stays `[1, 2, 3]`. The capture list copies `factor` when the closure is created, so the closure multiplies by 2 even after the outer variable becomes 5: `scale(3)` is 6. In task 3, applying a times-ten closure gives 10, 20 and 30.

**A plausible wrong approach.** Dropping the capture list, `{ (value: Int) in value * factor }`, captures the variable itself, so after `factor = 5` the call returns 15 and the `scale(3) == 6` check fails. That is the delayed-execution surprise task 4 asks you to diagnose.

**How to verify.** Remove `[factor]` in a scratch pad and confirm the result changes to 15. For task 5, map an empty array (result is empty) and use `compactMap { Int($0) }` on `["1", "x"]` to see an optional-returning closure keep only 1.

## Mechanism and diagnostic reasoning

A closure is executable behavior that can be passed as a value. It can capture surrounding variables, which lets it remember context but can also create surprising mutation or lifetime relationships. Swift capture lists can copy a value at closure creation or weaken a reference, depending on the declared policy.

Map transforms each element while filter selects elements. These operations express intent when the closure remains small and clear. Avoid compressing a complex domain algorithm into a chain whose intermediate states nobody can inspect. Name important transformations and preserve a traceable failure boundary.

`{ value in value * 2 }` is a closure. `$0` abbreviates its first argument. A capture list such as `[factor]` captures the current value. Function types use `(Input) -> Output`.

An escaping closure can outlive its creating scope. Capturing self strongly can create a retain cycle, covered in ARC. A short expression is not automatically clearer than a named intermediate.

## Review before continuing

Run the reference and confirm it prints `swift-015: passed`, then rerun the guide's counterexample.
