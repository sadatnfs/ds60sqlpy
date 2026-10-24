# go-037: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A controller repeatedly compares desired and observed state and takes a bounded step toward convergence. Reconciliation is level-based: it should ask what is true now rather than assume it received every historical event. Events are hints that work may be needed, not an exactly-once command log. A successful reconcile can be a no-op when the object already satisfies intent. Repeating it should not create duplicate side effects. Separate a pure decision function from the API adapter so planning can be tested deterministically. External operations need ownership, idempotency keys and explicit handling of uncertain outcomes.

Represent desired and observed state as small values, then return a typed action such as create, update or none. Avoid embedding API calls inside every conditional. The adapter performs an action, records evidence and schedules another observation. A real controller often converges over several reconciliations rather than blocking until every resource becomes ready. Status should describe observed facts, including the generation to which they apply.

## 1. Plan a missing child

Observe no child for a desired replica count of 3.

```go
check(plan(3, false, 0) == "create", "missing child")
```

**Expected:** The action is create.

The planner reports intent without performing a cluster mutation. The adapter still needs an exact owner identity.

## 2. Plan a changed child

Observe an existing child with count 2 while desired is 3.

```go
check(plan(3, true, 2) == "update", "changed child")
```

**Expected:** The action is update.

The update is justified by a current difference, not by assuming a prior event was delivered once.

## 3. Make convergence a no-op

Observe an existing child already at count 3.

```go
check(plan(3, true, 3) == "none", "converged")
```

**Expected:** The action is none.

A repeated event should not produce duplicate writes after convergence. No-op behavior also reduces control-plane load.

## 4. Reject invalid desired state

Supply a negative desired count.

```go
check(plan(-1, true, 2) == "invalid", "invalid intent")
```

**Expected:** The planner returns invalid.

A persistent validation error should be surfaced to the user rather than retried forever as if it were a transient API outage.

## 5. Simulate a converging step

Start at count 1, apply the planned update to 3 and plan again.

```go
current := 1
check(plan(3, true, current) == "update", "first plan")
current = 3
check(plan(3, true, current) == "none", "second plan")
```

**Expected:** The next plan is none.

The state transition shows convergence for this simple model. Distributed delays and conflicts belong to adapter-level integration tests.

## 6. Transfer scale-to-zero

Request zero for an existing child with count 2.

```go
check(plan(0, true, 2) == "update" && plan(0, true, 0) == "none", "zero scale")
```

**Expected:** The planner requests update, then converges at zero.

Zero can be a valid desired value. Confusing it with absence would prevent a legitimate scale-to-zero operation.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
