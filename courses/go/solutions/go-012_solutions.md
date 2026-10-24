# go-012: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

defer schedules a function call to execute when the surrounding function returns. It is a resource-lifetime tool, not a general background execution mechanism. Deferred calls run in last-in-first-out order, and their arguments are evaluated when the defer statement executes. Closures can instead read variables at the later execution time. panic unwinds the current goroutine's stack, running defers; recover can intercept it only in the appropriate deferred call during that unwind. Expected invalid input should normally be returned as an error. Recovering every panic and returning a success-shaped value conceals defects and can leave callers unable to distinguish completed work from aborted work.

defer cleanup() registers a call. defer func(){ ... }() registers a closure. A helper function is useful when each loop iteration needs its own cleanup boundary; deferring inside a long loop otherwise accumulates cleanup until the whole function returns. recover returns the active panic value when called correctly from a deferred function. A named return variable can be changed by deferred code, which is powerful but can make flow harder to read.

## 1. Trace cleanup order

Register first and second cleanup markers and return.

```go
check(deferOrder() == "second,first", "defer order")
```

**Expected:** The observed order is second then first.

The last registered cleanup runs first. This naturally unwinds nested acquisitions in the opposite order from acquisition.

## 2. Compare captured arguments

Defer a call with x as an argument, then change x.

```go
check(deferArgument() == 1, "argument evaluation")
```

**Expected:** The deferred argument retains the earlier value 1.

Call arguments are evaluated at registration. This differs from a closure that refers to x and reads it when the closure later runs.

## 3. Compare a closure read

Defer a closure reading x, then change x to 2.

```go
check(deferClosure() == 2, "closure read")
```

**Expected:** The closure observes 2.

The closure refers to the variable. Whether this is useful or misleading depends on the intended observation time.

## 4. Contain a deliberate panic

Panic with the known value broken inside a helper that recovers it.

```go
check(recoverKnown() == "broken", "recovered value")
```

**Expected:** The helper reports broken explicitly.

The recovery boundary converts this deliberate fixture into inspectable evidence. It does not justify swallowing arbitrary production panics.

## 5. Preserve cleanup during failure

Register cleanup and then panic inside a recovered helper.

```go
check(cleanedAfterPanic(), "cleanup on panic")
```

**Expected:** The cleanup marker is still set.

Stack unwinding runs deferred cleanup before the outer recovery returns. Resource-release logic must still be safe when work is incomplete.

## 6. Transfer function-scoped cleanup

Run three helpers, each with its own deferred marker.

```go
count := 0
for i := 0; i < 3; i++ {
	scopedCleanup(&count)
}
check(count == 3, "iteration cleanup")
```

**Expected:** All three markers are present after the loop.

A helper creates a cleanup boundary per iteration. A defer in the outer loop's function would postpone all three releases until that outer function returned.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
