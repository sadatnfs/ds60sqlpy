# go-048: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

The capstone combines desired-state validation, exact identity, idempotent planning, cancellation and durable observations. A controller is successful when repeated observations converge without duplicating effects or damaging resources it does not own. Begin with an explicit state diagram and classify each operation as pure, read-only, idempotent mutation or potentially uncertain external side effect. Record what an operation observed and what it requested, not an invented certainty that the whole system is ready. Production readiness also includes minimal RBAC, bounded queues, useful status, metrics, graceful shutdown and a recovery runbook. This offline capstone proves a small orchestration model; the prepared client-go project and owned Kubernetes module supply the separate real-system learning routes.

The model stores UID, desired count, current count and a write counter. reconcileCap first checks cancellation, then ownership, then input validity, and finally changes state only when needed. The ordering prevents invalid or unauthorized work from reaching mutation. A real adapter adds optimistic concurrency, API errors, status subresources and cleanup. Preserve these boundaries when replacing the in-memory store rather than moving all logic into one untestable function.

## 1. Converge from a different state

Reconcile owned UID u1 from count 1 to desired 3.

```go
s := CapState{UID: "u1", Current: 1}
err := reconcileCap(context.Background(), &s, "u1", 3)
check(err == nil && s.Current == 3 && s.Writes == 1, "converge")
```

**Expected:** The count becomes 3 with one write.

The mutation is justified by a current difference under a verified identity.

## 2. Repeat without duplicate writes

Run the same desired state twice.

```go
s := CapState{UID: "u1", Current: 1}
check(reconcileCap(context.Background(), &s, "u1", 3) == nil, "first")
check(reconcileCap(context.Background(), &s, "u1", 3) == nil && s.Writes == 1, "idempotent")
```

**Expected:** Only the first call writes.

Repeated notification is normal. Converged state should remain a no-op.

## 3. Refuse a replacement object

Supply expected UID old while observed UID is new.

```go
s := CapState{UID: "new", Current: 1}
err := reconcileCap(context.Background(), &s, "old", 3)
check(err != nil && s.Current == 1 && s.Writes == 0, "ownership")
```

**Expected:** No write occurs and an ownership error is returned.

A reusable name cannot authorize modification of a replacement incarnation.

## 4. Preserve state on invalid intent

Request a negative count.

```go
s := CapState{UID: "u1", Current: 1}
err := reconcileCap(context.Background(), &s, "u1", -1)
check(err != nil && s.Current == 1 && s.Writes == 0, "invalid")
```

**Expected:** The operation fails without mutation.

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

The caller retains control of the work lifetime. Later external steps would need their own context-aware boundaries.

## 6. Transfer restart reasoning

Copy the converged durable state into a new controller invocation.

```go
s := CapState{UID: "u1", Current: 3, Writes: 1}
restored := s
check(reconcileCap(context.Background(), &restored, "u1", 3) == nil && restored.Writes == 1, "restart")
```

**Expected:** The restarted invocation makes no additional write.

Recovery reads current durable state rather than replaying an assumed unfinished command. Real persistence and unknown API outcomes require integration evidence beyond this value-copy model.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
