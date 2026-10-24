# go-004: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A function separates a computation from its callers. Its contract names accepted inputs, returned values, mutation and failure. Go passes arguments by value. For an integer this copies the integer; for a slice it copies a descriptor whose backing storage may still be shared. Multiple return values make a result plus error a normal language pattern. Named return variables are real local variables, not a replacement for clear control flow. A pure function depends only on its inputs and does not mutate shared state, which usually makes boundary tests simpler. Design the contract before deciding whether a pointer or a collection is convenient.

func twice(x int) int declares a parameter and a return type. return ends the invocation. (int, error) declares two returned values, which callers normally bind together and check before using the result. A variadic parameter ...int accepts zero or more values; within the function it is a slice. A return from a helper returns only from that helper, not the caller.

## 1. Implement a pure helper

Implement twice and check inputs 7 and 0.

```go
check(twice(7) == 14 && twice(0) == 0, "twice")
```

**Expected:** The results are 14 and 0.

The zero case confirms the helper calculates from its input rather than returning a memorized positive result.

## 2. Return an explicit failure

Implement positiveArea that rejects a nonpositive dimension.

```go
area, err := positiveArea(3, 4)
check(err == nil && area == 12, "area")
_, err = positiveArea(0, 4)
check(err != nil, "invalid area")
```

**Expected:** 3 by 4 returns 12; zero width returns an error.

The error describes a domain policy. Another geometry API might allow zero area, but its contract must say so.

## 3. Trace copied scalar state

Pass 5 to a helper that reassigns its local parameter.

```go
n := 5
reassign(n)
check(n == 5, "value copy")
```

**Expected:** The caller still holds 5.

Reassigning the copied parameter does not reassign the caller variable. This is a language rule, not a compiler optimization.

## 4. Return both ordered values

Implement bounds for two integers.

```go
low, high := bounds(9, 2)
check(low == 2 && high == 9, "bounds")
```

**Expected:** Inputs 9 and 2 return 2 then 9.

Multiple returns can make a small contract clearer than mutating two caller-owned outputs.

## 5. Test a variadic identity

Sum zero inputs and then 1, 2 and 3.

```go
check(total() == 0 && total(1, 2, 3) == 6, "variadic")
```

**Expected:** The results are 0 and 6.

An empty variadic argument list is a normal case. The accumulator's identity determines its answer.

## 6. Transfer the contract

Call the area helper with a negative height and keep the error visible.

```go
value, err := positiveArea(3, -1)
check(err != nil && value == 0, "negative dimension")
```

**Expected:** The invalid domain is rejected before returning a usable area.

Using only value while discarding err would erase the distinction between a valid zero and a rejected request. This helper deliberately reserves zero for its error path.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
