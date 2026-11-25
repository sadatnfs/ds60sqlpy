# go-026: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-026_solution.go` implements all six cases.

## Mechanism

Cancellation is cooperative: a context signals that work should stop, but does not forcibly interrupt every function. Pass context as the first parameter to work whose lifetime belongs to its caller. Derived contexts form a tree, so canceling a parent cancels descendants. Always call the returned cancel function when the owned operation ends, including early success, to release associated resources. A select can wait for work or cancellation, but if both cases are ready its choice is not a priority rule. Check required preconditions explicitly when already-canceled work must never begin.

context.WithCancel returns a child and cancel function. Done closes on cancellation; Err explains cancellation or deadline expiry. WithDeadline accepts a past time for deterministic testing. A select arm receiving from ctx.Done cooperates with cancellation. Context values carry request-scoped metadata, not optional function arguments, authentication guarantees or mutable application state.

## 1. Cancel a child: predict an edited check

Copy worked example 1, change `check(ctx.Err() == context.Canceled, "cancel")` to `check(ctx.Err() != context.Canceled, "cancel")` inside its check and predict whether it still passes; then restore it.

The unchanged code is worked example 1:

```go
ctx, cancel := context.WithCancel(context.Background())
cancel()
check(ctx.Err() == context.Canceled, "cancel")
```

**Expected:** The edited check panics with `cancel` even though `ctx.Err() == context.Canceled` still holds.

**Verify:** Restoring `check(ctx.Err() == context.Canceled, "cancel")` makes the check pass again with the worked observation: err returns context.Canceled.

Cancellation is visible through Err and the closed Done channel. Repeated cancel calls are safe.

**Approach.** Cancel a fresh `WithCancel` context and read `ctx.Err()` immediately; it is `context.Canceled`, which makes the edited `!=` comparison false.

**Why it holds here.** `cancel` closes `Done` and records the error before it returns, so no receive or delay is needed. The edited check rejects that state and panics with `cancel`.

**A plausible wrong approach.** Predicting that `Err` stays nil until something receives from `ctx.Done()`, so the edited check would pass. Cancellation is recorded synchronously by `cancel`, not by observers.

**Verify.** Print `ctx.Err()` and see `context canceled`, and call `cancel()` a second time to confirm nothing changes and nothing panics.

## 2. Propagate parent cancellation: diagnose an edited check

A careless edit rewrote the check in worked example 2 as `check(parent.Err() != context.Canceled && child.Err() == context.Canceled, "tree")`. Explain the failure, then restore it.

The unchanged code is worked example 2:

```go
parent, cancel := context.WithCancel(context.Background())
child, stop := context.WithCancel(parent)
defer stop()
cancel()
check(parent.Err() == context.Canceled && child.Err() == context.Canceled, "tree")
```

**Expected:** The defective run panics with `tree`; after restoring `check(parent.Err() == context.Canceled && child.Err() == context.Canceled, "tree")`, both contexts become canceled.

**Verify:** The edited check fails with message `tree` for a state that `parent.Err() == context.Canceled && child.Err() == context.Canceled` accepts.

A child cannot extend work beyond the lifetime requested by its parent.

**Approach.** Cancel the parent of a derived child and read both errors; both are `context.Canceled` because cancellation flows from parent to children.

**Why it holds here.** The edited check requires `parent.Err()` to differ from `context.Canceled`, which is false right after `cancel()`, so it panics with `tree` while the child condition still holds.

**A plausible wrong approach.** Deriving the child from `context.Background()` instead of `parent`. The child is then unrelated, its `Err` stays nil after the parent is canceled, and the original check panics with `tree`.

**Verify.** Print `parent.Err(), child.Err()` and see `context canceled context canceled`. Keep `defer stop()`: `go vet` reports a lost cancel function when a derived context's cancel is discarded.

## 3. Keep child cancellation local

Cancel a child of a live parent.

```go
parent := context.Background()
child, cancel := context.WithCancel(parent)
cancel()
check(child.Err() != nil && parent.Err() == nil, "child")
```

**Expected:** The child is canceled; the parent is unchanged.

**Verify:** Your solution must keep `child.Err() != nil && parent.Err() == nil` true. Control: changing `check(child.Err() != nil && parent.Err() == nil, "child")` to `check(child.Err() == nil && parent.Err() == nil, "child")` panics with message `child`; revert it.

Cancellation propagates downward. One sub-operation can end without canceling unrelated siblings.

**Approach.** Cancel a child derived from `context.Background()` and compare the two errors.

**Why it holds here.** Cancellation propagates only downward, so the child records `context.Canceled` while the parent is unaffected; `Background` can never be canceled and its `Err` is always nil.

**A plausible wrong approach.** Assuming cancellation travels upward and checking `parent.Err() != nil`. That is never true for `Background`, so the check would panic every run.

**Verify.** Print `child.Err(), parent.Err()` and see `context canceled <nil>`.

## 4. Test an expired deadline

Construct a context with a deadline at Unix time zero.

```go
ctx, cancel := context.WithDeadline(context.Background(), time.Unix(0, 0))
defer cancel()
check(ctx.Err() == context.DeadlineExceeded, "deadline")
```

**Expected:** Err is context.DeadlineExceeded.

**Verify:** Your solution must keep `ctx.Err() == context.DeadlineExceeded` true. Control: changing `check(ctx.Err() == context.DeadlineExceeded, "deadline")` to `check(ctx.Err() != context.DeadlineExceeded, "deadline")` panics with message `deadline`; revert it.

The past deadline avoids flaky sleeps. Real work also needs a separate cleanup allowance after its budget expires.

**Approach.** Create the context with a deadline at `time.Unix(0, 0)`, which is already in the past, so it is done when `WithDeadline` returns.

**Why it holds here.** A context whose deadline has passed is created already expired with `context.DeadlineExceeded`, which is a different error from `context.Canceled`, so the check passes without sleeping.

**A plausible wrong approach.** Using `context.WithTimeout(ctx, time.Millisecond)` and checking at once. `Err` is still nil at that moment and the check panics with `deadline`; adding a sleep makes it pass only when the scheduler cooperates.

**Verify.** Print `ctx.Err()` and see `context deadline exceeded`, and print `ctx.Deadline()` to see the 1970 time with `true`.

## 5. Refuse already canceled work

Call a helper that checks its context before calculation.

```go
ctx, cancel := context.WithCancel(context.Background())
cancel()
v, err := contextValue(ctx, 4)
check(v == 0 && err == context.Canceled, "refusal")
```

**Expected:** It returns cancellation without a result.

**Verify:** Your solution must keep `v == 0 && err == context.Canceled` true. Control: changing `check(v == 0 && err == context.Canceled, "refusal")` to `check(v != 0 && err == context.Canceled, "refusal")` panics with message `refusal`; revert it.

A preflight check expresses the already-canceled policy. A later select alone cannot guarantee cancellation wins over another ready arm.

**Approach.** Have `contextValue` check `ctx.Err()` before doing any work and return 0 with that error when the context is already done.

**Why it holds here.** The context was canceled before the call, so the preflight returns `0, context.Canceled` and the calculation never runs.

**A plausible wrong approach.** Computing first and reporting afterward, as in `return 2 * x, ctx.Err()`. The error is correct, but `v` is 8, so the check panics with `refusal` and a caller may use a result from canceled work.

**Verify.** Print `v, err` and see `0 context canceled`.

## 6. Transfer successful work

Use the same helper with a live context.

```go
v, err := contextValue(context.Background(), 4)
check(err == nil && v == 8, "live")
```

**Expected:** It returns 8 without error.

**Verify:** Your solution must keep `err == nil && v == 8` true. Control: changing `v, err := contextValue(context.Background(), 4)` to `v, err := contextValue(context.Background(), 5)` panics with message `live`; revert it.

Long loops or I/O must cooperate during work as well. One entry check is sufficient only for this tiny immediate calculation.

**Approach.** Call the same helper with `context.Background()`, which is never canceled, so the preflight passes and the helper returns `2 * 4`.

**Why it holds here.** `ctx.Err()` is nil for a live context, so the helper reaches `return 2*x, nil` and the check sees 8 with no error.

**A plausible wrong approach.** Passing `nil` because no cancellation is wanted. The helper calls `ctx.Err()` on a nil interface and panics with a nil pointer dereference; use `context.Background()` or `context.TODO()`.

**Verify.** Print `v, err` and see `8 <nil>`.

## Transfer after comparison

Write `sumUntil(ctx context.Context, xs []int) (int, error)` that checks `ctx.Err()` before each element. Check it returns 6 and nil for 1, 2, 3 under `Background`, 0 and `context.Canceled` for a canceled context, and 0 and `context.DeadlineExceeded` for a deadline at `time.Unix(0, 0)`. Explain why checking only after the loop would return the full sum together with an error.
