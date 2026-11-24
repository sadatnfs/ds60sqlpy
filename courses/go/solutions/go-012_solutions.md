# go-012: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

defer schedules a function call to execute when the surrounding function returns. It is a resource-lifetime tool, not a general background execution mechanism. Deferred calls run in last-in-first-out order, and their arguments are evaluated when the defer statement executes. Closures can instead read variables at the later execution time. panic unwinds the current goroutine's stack, running defers; recover can intercept it only in the appropriate deferred call during that unwind. Expected invalid input should normally be returned as an error. Recovering every panic and returning a success-shaped value conceals defects and can leave callers unable to distinguish completed work from aborted work.

defer cleanup() registers a call. defer func(){ ... }() registers a closure. A helper function is useful when each loop iteration needs its own cleanup boundary; deferring inside a long loop otherwise accumulates cleanup until the whole function returns. recover returns the active panic value when called correctly from a deferred function. A named return variable can be changed by deferred code, which is powerful but can make flow harder to read.

## 1. Trace cleanup order: predict an edited check

Copy worked example 1 into a scratch pad and change `check(deferOrder() == "second,first", "defer order")` to `check(deferOrder() == "second,first!", "defer order")` inside its check. Before running, predict whether the check still passes and explain why; then restore it.

The unchanged code is worked example 1:

```go
check(deferOrder() == "second,first", "defer order")
```

**Expected:** The changed run panics with `defer order` because the edited check no longer holds. Restoring the original line brings back the worked observation: the observed order is second then first.

The last registered cleanup runs first. This naturally unwinds nested acquisitions in the opposite order from acquisition.

**Approach.** Trace the three deferred calls in `deferOrder` in reverse registration order: the `second` append runs first, then the `first` append, then the join that writes `result`.

**Why it holds here.** Deferred calls run after the bare `return` and may still assign the named result, so the function returns `second,first`. The edited literal adds `!`, so the comparison is false and the check panics with `defer order`.

**A plausible wrong approach.** Predicting an empty string because the bare `return` already returned. A named result can be changed by deferred functions after the return statement, which is how the join reaches the caller.

**Verify.** Print `deferOrder()` to see `second,first`. Swapping the two append lines in the helper flips it to `first,second`, which confirms the order follows registration in reverse.

## 2. Compare captured arguments: diagnose an edited check

A careless edit changed the check in worked example 2 so that it reads `check(deferArgument() != 1, "argument evaluation")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.

The unchanged code is worked example 2:

```go
check(deferArgument() == 1, "argument evaluation")
```

**Expected:** Before the repair the program panics with `argument evaluation`; after it the line reads `check(deferArgument() == 1, "argument evaluation")` again and the deferred argument retains the earlier value 1.

Call arguments are evaluated at registration. This differs from a closure that refers to x and reads it when the closure later runs.

**Approach.** Evaluate when the deferred argument is captured: `defer func(v int){ result = v }(x)` copies `x` into `v` at the `defer` statement, when `x` is still 1.

**Why it holds here.** Changing `x` to 2 afterward cannot change the already evaluated argument, so `deferArgument()` returns 1. The edited check `!= 1` therefore rejects the same state the original accepts and panics with `argument evaluation`.

**A plausible wrong approach.** Assuming the deferred call reads `x` when it finally runs and returns 2. That is the closure behavior of case 3, not the behavior of an argument passed at registration.

**Verify.** Print `deferArgument()` and `deferClosure()` together: the output is `1 2`, and the restored check passes.

## 3. Compare a closure read

Defer a closure reading x, then change x to 2.

```go
check(deferClosure() == 2, "closure read")
```

**Expected:** The closure observes 2.

The closure refers to the variable. Whether this is useful or misleading depends on the intended observation time.

**Approach.** Defer a closure with no parameters that reads `x`, then assign 2 before returning.

**Why it holds here.** The closure refers to the variable `x` itself, not a snapshot, so when it runs after `x = 2` it stores 2 in `result`.

**A plausible wrong approach.** Expecting 1 by analogy with case 2. Only an explicit call argument is evaluated at the `defer` statement; a captured variable is read at execution time.

**Verify.** Print `deferClosure()` and see 2. Rewriting it to pass `x` as an argument changes the output to 1, which isolates evaluation time as the only difference.

## 4. Contain a deliberate panic

Panic with the known value broken inside a helper that recovers it.

```go
check(recoverKnown() == "broken", "recovered value")
```

**Expected:** The helper reports broken explicitly.

The recovery boundary converts this deliberate fixture into inspectable evidence. It does not justify swallowing arbitrary production panics.

**Approach.** Install a deferred function that calls `recover()` and converts any recovered value to text with `fmt.Sprint`, then call `panic("broken")`.

**Why it holds here.** `recover` returns the panic value only when it is called directly by a deferred function during panicking. Here it receives `broken`, stores it in the named `result`, and the helper returns normally.

**A plausible wrong approach.** Calling `recover()` in the ordinary body before `panic`, or from a helper that the deferred function calls. In both places it returns nil, the panic continues, and the program exits with `panic: broken` instead of returning a value.

**Verify.** Print `recoverKnown()` and see `broken`. Remove the `defer` keyword in a scratch copy and the run terminates with a nonzero status and the `panic: broken` message.

## 5. Preserve cleanup during failure

Register cleanup and then panic inside a recovered helper.

```go
check(cleanedAfterPanic(), "cleanup on panic")
```

**Expected:** The cleanup marker is still set.

Stack unwinding runs deferred cleanup before the outer recovery returns. Resource-release logic must still be safe when work is incomplete.

**Approach.** Register a recovery defer and then a cleanup defer that sets `cleaned` to true, and panic afterward.

**Why it holds here.** During panicking, deferred calls still run in reverse order: the cleanup sets `cleaned = true`, then the recovery stops the panic, so the helper returns true.

**A plausible wrong approach.** Writing `cleaned = true` as an ordinary statement after `panic("fixture")`. It is unreachable, so the function returns the zero value false and the check panics with `cleanup on panic`.

**Verify.** Print `cleanedAfterPanic()` and see `true`. Replace the cleanup defer with a plain `cleaned = true` after the `panic` call and the value becomes false, which shows the cleanup depends on deferral, not on line order.

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

**Approach.** Put the defer inside a helper, `scopedCleanup`, and call it once per loop iteration so each call's deferred increment runs when that call returns.

**Why it holds here.** Each of the three calls returns before the next starts, so the three increments happen inside the loop and `count` is 3 at the check.

**A plausible wrong approach.** Writing `defer func(){ count++ }()` directly inside the loop in `main`. All three increments wait until `main` returns, so at the check `count` is still 0 and the `iteration cleanup` check panics. With real files this pattern keeps every handle open until the outer function ends.

**Verify.** Print `count` after the loop and see 3. In the in-loop defer version the same print shows 0.

## Transfer after comparison

Write `releaseOrder() (log string)` that acquires `db`, `cache` and `file` in that order and defers appending each name to a slice that a first-registered defer joins into `log`. Predict `file,cache,db`, then add a deferred call that passes a counter as an argument and one that captures it, and explain which result each would report after the counter changes.
