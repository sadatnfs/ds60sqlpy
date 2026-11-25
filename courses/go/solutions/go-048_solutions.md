# go-048: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-048_solution.go` implements all six cases.

## Mechanism

The capstone combines desired-state validation, exact identity, idempotent planning, cancellation and durable observations. A controller is successful when repeated observations converge without duplicating effects or damaging resources it does not own. Begin with an explicit state diagram and classify each operation as pure, read-only, idempotent mutation or potentially uncertain external side effect. Record what an operation observed and what it requested, not an invented certainty that the whole system is ready. Production readiness also includes minimal RBAC, bounded queues, useful status, metrics, graceful shutdown and a recovery runbook. This offline capstone proves a small orchestration model; the prepared client-go project and owned Kubernetes module supply the separate real-system learning routes.

The model stores UID, desired count, current count and a write counter. reconcileCap first checks cancellation, then ownership, then input validity, and finally changes state only when needed. The ordering prevents invalid or unauthorized work from reaching mutation. A real adapter adds optimistic concurrency, API errors, status subresources and cleanup. Preserve these boundaries when replacing the in-memory store rather than moving all logic into one untestable function.

## 1. Converge from a different state: change one input

Copy worked example 1, change `err := reconcileCap(context.Background(), &s, "u1", 3)` to `err := reconcileCap(context.Background(), &s, "u1", 4)` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
s := CapState{UID: "u1", Current: 1}
err := reconcileCap(context.Background(), &s, "u1", 3)
check(err == nil && s.Current == 3 && s.Writes == 1, "converge")
```

**Expected:** The edited run panics with `converge` because `err == nil && s.Current == 3 && s.Writes == 1` no longer holds.

**Verify:** Restoring `err := reconcileCap(context.Background(), &s, "u1", 3)` makes the check pass again with the worked observation: the count becomes 3 with one write.

The mutation is justified by a current difference under a verified identity.

## 2. Repeat without duplicate writes: diagnose an edited check

A careless edit rewrote the check in worked example 2 as `check(reconcileCap(context.Background(), &s, "u1", 4) == nil, "first")`. Explain the failure, then restore it.

The unchanged code is worked example 2:

```go
s := CapState{UID: "u1", Current: 1}
check(reconcileCap(context.Background(), &s, "u1", 3) == nil, "first")
check(reconcileCap(context.Background(), &s, "u1", 3) == nil && s.Writes == 1, "idempotent")
```

**Expected:** The defective run panics with `idempotent`; after restoring `check(reconcileCap(context.Background(), &s, "u1", 3) == nil, "first")`, only the first call writes.

**Verify:** The edited check fails with message `idempotent` for a state that `reconcileCap(context.Background(), &s, "u1", 3) == nil && s.Writes == 1` accepts.

Repeated notification is normal. Converged state should remain a no-op.

## 3. Refuse a replacement object

Supply expected UID old while observed UID is new.

```go
s := CapState{UID: "new", Current: 1}
err := reconcileCap(context.Background(), &s, "old", 3)
check(err != nil && s.Current == 1 && s.Writes == 0, "ownership")
```

**Expected:** No write occurs and an ownership error is returned.

**Verify:** Your solution must keep `err != nil && s.Current == 1 && s.Writes == 0` true. Control: changing `s := CapState{UID: "new", Current: 1}` to `s := CapState{UID: "new", Current: 2}` panics with message `ownership`; revert it.

A reusable name cannot authorize modification of a replacement incarnation.

## 4. Preserve state on invalid intent

Request a negative count.

```go
s := CapState{UID: "u1", Current: 1}
err := reconcileCap(context.Background(), &s, "u1", -1)
check(err != nil && s.Current == 1 && s.Writes == 0, "invalid")
```

**Expected:** The operation fails without mutation.

**Verify:** Your solution must keep `err != nil && s.Current == 1 && s.Writes == 0` true. Control: changing `s := CapState{UID: "u1", Current: 1}` to `s := CapState{UID: "u1", Current: 2}` panics with message `invalid`; revert it.

Validation occurs before state changes. A failure-shaped return after mutation would violate the transaction boundary.

## 5. Cancel before new work

Pass an already-canceled context.

```go
ctx, cancel := context.WithCancel(context.Background())
cancel()
s := CapState{UID: "u1", Current: 1}
err := reconcileCap(ctx, &s, "u1", 3)
check(errors.Is(err, context.Canceled) && s.Writes == 0, "cancel")
```

**Expected:** No write occurs and cancellation is retained.

**Verify:** Your solution must keep `errors.Is(err, context.Canceled) && s.Writes == 0` true. Control: changing `check(errors.Is(err, context.Canceled) && s.Writes == 0, "cancel")` to `check(errors.Is(err, context.Canceled) && s.Writes != 0, "cancel")` panics with message `cancel`; revert it.

The caller retains control of the work lifetime. Later external steps would need their own context-aware boundaries.

## 6. Transfer restart reasoning

Copy the converged durable state into a new controller invocation.

```go
s := CapState{UID: "u1", Current: 3, Writes: 1}
restored := s
check(reconcileCap(context.Background(), &restored, "u1", 3) == nil && restored.Writes == 1, "restart")
```

**Expected:** The restarted invocation makes no additional write.

**Verify:** Your solution must keep `reconcileCap(context.Background(), &restored, "u1", 3) == nil && restored.Writes == 1` true. Control: changing `s := CapState{UID: "u1", Current: 3, Writes: 1}` to `s := CapState{UID: "u1", Current: 4, Writes: 1}` panics with message `restart`; revert it.

Recovery reads current durable state rather than replaying an assumed unfinished command. Real persistence and unknown API outcomes require integration evidence beyond this value-copy model.

## Transfer after comparison

This checklist carries into any reliable background system, not only Kubernetes: validate intent, confirm identity, honor cancellation, write only when state differs and prove each property with a test that counts effects. Apply it to a job runner, a sync service or a migration tool, and document the operational contract alongside the code.
