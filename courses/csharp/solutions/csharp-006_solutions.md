# csharp-006: explanation and comparison

Reference program: [csharp-006_solution.cs](csharp-006_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Sum with a maintained invariant:** Before each iteration, sum equals the sum of values already visited. Zero is the identity that makes the invariant true initially. The sum is 12 and the empty sum is zero.

**Locate the first match:** Stopping at the first match is part of the contract. Without break, the same loop could return the last match. The first 8 is at index 1; 9 is absent.

## Task answers

### Task 1: Predict and explain

Write the accumulator value before and after every iteration in Example A.

**Written answer.** Before the loop `sum` is 0. After visiting 2 it is 2, after 4 it is 6, and after 6 it is 12. At every point `sum` equals the total of the elements visited so far: 0 for none, then 2, 2 + 4 and 2 + 4 + 6.

**Why it is correct.** The loop body adds exactly the current element and nothing else, so if the invariant holds before an iteration it holds after it. It holds at the start because the total of no elements is 0, and when the loop ends every element has been visited, so `sum` is the full total.

**Plausible wrong approach.** Starting the trace at 2 skips the state before the first iteration, which is the state that explains why an empty array correctly sums to 0. Writing 12 after the first step confuses the final result with an intermediate value.

**How to verify.** Insert `Console.WriteLine($"{value} -> {sum}");` after `sum += value;` and confirm the lines `2 -> 2`, `4 -> 6` and `6 -> 12`. Remove the line afterwards so the lesson output is unchanged.

### Task 2: Guided modification

Skip negative values while preserving the sum invariant.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
int[] values = { 2, -3, 4, -1, 6 };
int sum = 0;
foreach (int value in values) {
  if (value < 0)
    continue;
  sum += value;
}
Check(sum == 12, "negatives skipped");
Check(sum == values.Where(v => v >= 0).Sum(), "same as filtered sum");
```

**Observe:** The sum is 12: the -3 and -1 are skipped and 2, 4 and 6 are added.

The invariant becomes: `sum` equals the total of the nonnegative elements visited so far. `continue` leaves `sum` untouched for a negative value, so the invariant still holds after that iteration, and the final sum matches a separately computed filtered sum.

**Plausible wrong approach.** Writing `sum += Math.Max(value, 0)` gives the same total here but hides the policy inside arithmetic. Writing `if (value < 0) break;` stops at -3 and returns 2, silently dropping every later value.

**How to verify.** Make every value negative and check that `sum` is 0, the same identity as the empty array. Then put a 0 in the array and confirm it is kept, because the rule skips only values below zero.

### Task 3: Independent construction

Implement a first-match search returning a separate not-found representation.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
bool TryFirstIndex(int[] items, int target, out int index) {
  for (int i = 0; i < items.Length; i++) {
    if (items[i] == target) {
      index = i;
      return true;
    }
  }
  index = -1;
  return false;
}
var values = new[] { 5, 7, 7 };
Check(TryFirstIndex(values, 7, out int at) && at == 1, "first match");
Check(!TryFirstIndex(values, 9, out _), "not found");
Check(!TryFirstIndex(Array.Empty<int>(), 1, out _), "empty input");
```

**Observe:** The first 7 is at index 1; a missing target and an empty array both return false.

The loop stops at the first match, and the Try pattern reports not-found through its bool result, so a caller checks that result before using the index instead of mistaking a sentinel such as -1 for a position.

### Task 4: Diagnose a defect

Diagnose the condition i <= values.Length using a one-element array.

**Written answer.** With `values = { 5 }` the loop `for (int i = 0; i <= values.Length; i++)` runs for `i = 0` and reads 5, then tests `1 <= 1`, which is true, and reads `values[1]`. That index does not exist, so the program throws `IndexOutOfRangeException`. The bound must be `i < values.Length`.

**Why it is correct.** A one-element array has length 1 and only index 0. Valid indices run from 0 to `Length - 1`, so the loop must stop when `i` reaches `Length`. With `<=` the loop always makes one extra iteration.

**Plausible wrong approach.** Catching `IndexOutOfRangeException` around the loop hides the off-by-one error while still doing the extra iteration. Changing the start to `i = 1` avoids the crash for this input but skips the first element.

**How to verify.** Run the `<=` version with `{ 5 }` and observe the exception. With `<`, check that a search for 5 returns index 0 and that the loop body runs exactly once.

### Task 5: Boundary evidence

Check empty, singleton, no-match and repeated-match inputs.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
int FirstIndex(int[] items, int target) {
  for (int i = 0; i < items.Length; i++) {
    if (items[i] == target)
      return i;
  }
  return -1;
}
int[] empty = Array.Empty<int>();
int[] single = { 4 };
int[] other = { 1, 2 };
int[] repeated = { 4, 9, 4 };
Check(FirstIndex(empty, 4) == -1, "empty input");
Check(FirstIndex(single, 4) == 0, "singleton match");
Check(FirstIndex(other, 4) == -1, "no match");
Check(FirstIndex(repeated, 4) == 0, "repeated match returns the first");
```

**Observe:** The empty and no-match inputs give -1; the singleton and the repeated input give index 0.

Each input guards a different mistake. The empty array checks that the loop body may run zero times. The singleton checks the first and last index at once. The no-match array checks that the loop ends without inventing a result. The repeated array checks that the search stops at the first 4 instead of reporting index 2.

**Plausible wrong approach.** Testing only `{ 3, 8, 8 }` as in Example B never runs the loop zero times and never reaches the final `return -1`, so a version that returns 0 when nothing matches would pass it while pointing callers at a real element.

**How to verify.** Change `return i;` to remember `i` and continue the loop; the repeated check must then fail with index 2. Restore the early return and all four checks pass.

### Task 6: Transfer and justify

Design a bounded retry loop and explain both its invariant and its stopping argument.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Mechanism and diagnostic reasoning

A loop repeats a state transition. To understand it, state what is true before the first iteration and what remains true after each iteration. This repeated truth is an invariant. A second argument explains termination: some bounded quantity moves toward a stopping condition. A correct-looking body can still fail because its boundary executes once too often or never stops.

`foreach` expresses traversal of an existing sequence and usually avoids manual index bookkeeping. Use an index when the position itself matters, but relate the valid index range to the collection length. Empty inputs are especially revealing because the initial state becomes the final result without any iteration.

`for (initial; condition; update)` initializes once, checks before each body, and updates after each body. For an array of Length n, valid indices are zero through n minus one. `break` exits the loop; `continue` skips the remainder of one iteration.

Loop indices count from zero while lengths count elements. A sentinel such as -1 must be checked before indexing. Mutating a collection during enumeration can invalidate the traversal contract.

## Review before continuing

Run the reference and confirm it prints `csharp-006: passed`, then rerun the guide's counterexample.
