# go-026: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

Cancellation is cooperative: a context signals that work should stop, but does not forcibly interrupt every function. Pass context as the first parameter to work whose lifetime belongs to its caller. Derived contexts form a tree, so canceling a parent cancels descendants. Always call the returned cancel function when the owned operation ends, including early success, to release associated resources. A select can wait for work or cancellation, but if both cases are ready its choice is not a priority rule. Check required preconditions explicitly when already-canceled work must never begin.

context.WithCancel returns a child and cancel function. Done closes on cancellation; Err explains cancellation or deadline expiry. WithDeadline accepts a past time for deterministic testing. A select arm receiving from ctx.Done cooperates with cancellation. Context values carry request-scoped metadata, not optional function arguments, authentication guarantees or mutable application state.

## 1. Cancel a child: predict an edited check

Copy worked example 1 into a scratch pad and change `check(ctx.Err() == context.Canceled, "cancel")` to `check(ctx.Err() != context.Canceled, "cancel")` inside its check. Before running, predict whether the check still passes and explain why; then restore it.

The unchanged code is worked example 1:

```go
ctx, cancel := context.WithCancel(context.Background())
cancel()
check(ctx.Err() == context.Canceled, "cancel")
```

**Expected:** The changed run panics with `cancel` because the edited check no longer holds. Restoring the original line brings back the worked observation: err returns context.Canceled.

Cancellation is visible through Err and the closed Done channel. Repeated cancel calls are safe.

## 2. Propagate parent cancellation: diagnose an edited check

A careless edit changed the check in worked example 2 so that it reads `check(parent.Err() != context.Canceled && child.Err() == context.Canceled, "tree")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.

The unchanged code is worked example 2:

```go
parent, cancel := context.WithCancel(context.Background())
child, stop := context.WithCancel(parent)
defer stop()
cancel()
check(parent.Err() == context.Canceled && child.Err() == context.Canceled, "tree")
```

**Expected:** Before the repair the program panics with `tree`; after it the line reads `check(parent.Err() == context.Canceled && child.Err() == context.Canceled, "tree")` again and both contexts become canceled.

A child cannot extend work beyond the lifetime requested by its parent.

## 3. Keep child cancellation local

Cancel a child of a live parent.

```go
parent := context.Background()
child, cancel := context.WithCancel(parent)
cancel()
check(child.Err() != nil && parent.Err() == nil, "child")
```

**Expected:** The child is canceled; the parent is unchanged.

Cancellation propagates downward. One sub-operation can end without canceling unrelated siblings.

## 4. Test an expired deadline

Construct a context with a deadline at Unix time zero.

```go
ctx, cancel := context.WithDeadline(context.Background(), time.Unix(0, 0))
defer cancel()
check(ctx.Err() == context.DeadlineExceeded, "deadline")
```

**Expected:** Err is context.DeadlineExceeded.

The past deadline avoids flaky sleeps. Real work also needs a separate cleanup allowance after its budget expires.

## 5. Refuse already canceled work

Call a helper that checks its context before calculation.

```go
ctx, cancel := context.WithCancel(context.Background())
cancel()
v, err := contextValue(ctx, 4)
check(v == 0 && err == context.Canceled, "refusal")
```

**Expected:** It returns cancellation without a result.

A preflight check expresses the already-canceled policy. A later select alone cannot guarantee cancellation wins over another ready arm.

## 6. Transfer successful work

Use the same helper with a live context.

```go
v, err := contextValue(context.Background(), 4)
check(err == nil && v == 8, "live")
```

**Expected:** It returns 8 without error.

Long loops or I/O must cooperate during work as well. One entry check is sufficient only for this tiny immediate calculation.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
