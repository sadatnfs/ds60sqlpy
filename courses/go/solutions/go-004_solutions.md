# go-004: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A function separates a computation from its callers. Its contract names accepted inputs, returned values, mutation and failure. Go passes arguments by value. For an integer this copies the integer; for a slice it copies a descriptor whose backing storage may still be shared. Multiple return values make a result plus error a normal language pattern. Named return variables are real local variables, not a replacement for clear control flow. A pure function depends only on its inputs and does not mutate shared state, which usually makes boundary tests simpler. Design the contract before deciding whether a pointer or a collection is convenient.

func twice(x int) int declares a parameter and a return type. return ends the invocation. (int, error) declares two returned values, which callers normally bind together and check before using the result. A variadic parameter ...int accepts zero or more values; within the function it is a slice. A return from a helper returns only from that helper, not the caller.

## 1. Implement a pure helper: predict an edited check

Copy worked example 1 into a scratch pad and change `check(twice(7) == 14 && twice(0) == 0, "twice")` to `check(twice(8) == 14 && twice(0) == 0, "twice")` inside its check. Before running, predict whether the check still passes and explain why; then restore it.

The unchanged code is worked example 1:

```go
check(twice(7) == 14 && twice(0) == 0, "twice")
```

**Expected:** The changed run panics with `twice` because the edited check no longer holds. Restoring the original line brings back the worked observation: the results are 14 and 0.

The zero case confirms the helper calculates from its input rather than returning a memorized positive result.

**Approach.** Evaluate the edited check with the helper's definition: `twice(8)` returns 16, so the first operand `twice(8) == 14` is false before `twice(0) == 0` is even considered.

**Why it holds here.** `twice` is a pure function of its argument, so nothing else can change its answer. The edited claim pairs input 8 with the output for 7, which is simply false, and `check` panics with `twice`.

**A plausible wrong approach.** Predicting that the check still passes because `twice` is correct. A correct helper cannot rescue a wrong claim; the check states a specific input and output pair, and that pair is what changed.

**Verify.** Run the edited check and read the `twice` panic, then print `twice(8)` to see 16. Restore 7 and the program prints `Worked example checks passed.`

## 2. Return an explicit failure: debug a regression

A regression changed one token in worked example 2, so one line now reads `_, err = positiveArea(1, 4)`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.

The unchanged code is worked example 2:

```go
area, err := positiveArea(3, 4)
check(err == nil && area == 12, "area")
_, err = positiveArea(0, 4)
check(err != nil, "invalid area")
```

**Expected:** Before the repair the program panics with `invalid area`; after it the line reads `_, err = positiveArea(0, 4)` again and 3 by 4 returns 12; zero width returns an error.

The error describes a domain policy. Another geometry API might allow zero area, but its contract must say so.

**Approach.** Read the guard in `positiveArea`: it returns an error only when `w <= 0 || h <= 0`. With the regressed call `positiveArea(1, 4)` both dimensions are positive, so it returns 4 and a nil error.

**Why it holds here.** The second check asserts `err != nil`, so a valid rectangle makes it panic with `invalid area`. Restoring width 0 brings back the rejected input the check was written for.

**A plausible wrong approach.** Repairing the panic by tightening the guard to `w <= 1`. That makes this line pass but also rejects a genuine 1 by 4 rectangle, so it changes the domain policy instead of fixing the test input.

**Verify.** Print `err` for both calls: width 1 shows `<nil>` and width 0 shows `positive dimensions required`. After the repair both checks pass and the success line appears.

## 3. Trace copied scalar state

Pass 5 to a helper that reassigns its local parameter.

```go
n := 5
reassign(n)
check(n == 5, "value copy")
```

**Expected:** The caller still holds 5.

Reassigning the copied parameter does not reassign the caller variable. This is a language rule, not a compiler optimization.

**Approach.** Call `reassign(n)` with `n` holding 5 and inspect `n` afterward. The parameter `x` inside `reassign` is a separate copy of the argument.

**Why it holds here.** Go passes an `int` by value, so `x = 99` writes only to the helper's local copy, which disappears when the function returns. The caller's `n` is still 5 and `check(n == 5, ...)` passes.

**A plausible wrong approach.** Expecting 99 because the helper assigns to its parameter, as a pass-by-reference language would. To really change the caller you would need `func reassign(x *int) { *x = 99 }` and the call `reassign(&n)`.

**Verify.** Print `n` after the call and see 5. Then write the pointer version in a scratch pad: `n` becomes 99, which confirms that only an explicit pointer shares the caller's variable.

## 4. Return both ordered values

Implement bounds for two integers.

```go
low, high := bounds(9, 2)
check(low == 2 && high == 9, "bounds")
```

**Expected:** Inputs 9 and 2 return 2 then 9.

Multiple returns can make a small contract clearer than mutating two caller-owned outputs.

**Approach.** Implement `bounds` with one comparison: when `a < b` return `a, b`, otherwise return `b, a`. Both values come back as separate results.

**Why it holds here.** For 9 and 2 the test `9 < 2` is false, so the function returns 2 then 9, which is exactly the order the check expects.

**A plausible wrong approach.** Writing the condition backward as `if a > b { return a, b }`. For 9 and 2 it returns 9 then 2, so `low == 2` fails and the `bounds` panic points straight at the comparison.

**Verify.** Check three inputs: `bounds(9, 2)` and `bounds(2, 9)` both give `2 9`, and `bounds(4, 4)` gives `4 4`. The equal case shows the else branch is harmless when the values match.

## 5. Test a variadic identity

Sum zero inputs and then 1, 2 and 3.

```go
check(total() == 0 && total(1, 2, 3) == 6, "variadic")
```

**Expected:** The results are 0 and 6.

An empty variadic argument list is a normal case. The accumulator's identity determines its answer.

**Approach.** Start the accumulator at 0 and range over the variadic slice `values`, adding each element.

**Why it holds here.** When `total()` receives no arguments, `values` is a nil slice and the loop runs zero times, so the result is the additive identity 0. For 1, 2 and 3 the loop adds to 6.

**A plausible wrong approach.** Seeding the accumulator with `values[0]` and looping from index 1. That works for `total(1, 2, 3)` but `total()` panics with an index out of range, because a call with no arguments is a normal input here.

**Verify.** Print `total()` and `total(1, 2, 3)` to see 0 and 6. Also try `total([]int{4, 5}...)`, which passes an existing slice and returns 9.

## 6. Transfer the contract

Call the area helper with a negative height and keep the error visible.

```go
value, err := positiveArea(3, -1)
check(err != nil && value == 0, "negative dimension")
```

**Expected:** The invalid domain is rejected before returning a usable area.

Using only value while discarding err would erase the distinction between a valid zero and a rejected request. This helper deliberately reserves zero for its error path.

**Approach.** Call `positiveArea(3, -1)` and keep both results, checking that `err` is non-nil and that `value` is the reserved 0.

**Why it holds here.** The guard uses `||`, so a negative height alone is enough to take the error path, which returns 0 together with the error.

**A plausible wrong approach.** Writing the guard as `w <= 0 && h <= 0`. It rejects only rectangles where both sides are invalid, so `positiveArea(3, -1)` returns -3 with a nil error and the `negative dimension` check panics.

**Verify.** Print `value, err` and see `0 positive dimensions required`. Swapping to `positiveArea(-3, 1)` must give the same result, which confirms either dimension alone triggers the policy.

## Transfer after comparison

Write a `perimeter(w, h int) (int, error)` helper with the same policy as `positiveArea`. Check that 3 by 4 returns 14, that 0 by 4 and 3 by -1 return errors, and pass a `Rect{W: 3, H: 4}` struct to a helper that changes `W` to show the caller's struct keeps 3. Explain which check an `&&` guard or a pointer-free mutation would fail.
