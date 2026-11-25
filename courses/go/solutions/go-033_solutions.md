# go-033: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-033_solution.go` implements all six cases.

## Mechanism

A repository boundary separates business operations from database mechanics. The application should describe the transaction it needs, while an adapter manages SQL parameters, context cancellation, row scanning and commit or rollback. In database/sql, a DB is a connection pool rather than one connection. A Tx reserves a transaction context whose operations must all use that Tx. Calling the outer DB halfway through a transaction can escape its atomicity. This lesson uses a small copy-on-write transactional model to test policy offline. It is explicitly not evidence about PostgreSQL isolation, driver behavior or network failure. Those require a prepared database integration test.

A callback receiving a transaction-local value can stage changes before committing them to the outer state. An error aborts the staged changes. In a real database/sql adapter, begin with BeginTx(ctx, options), defer Rollback, execute parameterized statements through tx, and inspect Commit errors. SQL syntax and placeholder conventions depend on the selected driver. Never construct SQL by interpolating untrusted values. A transaction whose commit outcome is unknown cannot safely be replayed without an idempotency contract.

## 1. Commit a valid change: change one input

Copy worked example 1, change `s := Balances{A: 5, B: 5}` to `s := Balances{A: 6, B: 5}` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
s := Balances{A: 5, B: 5}
err := transact(&s, func(t *Balances) error { t.A -= 3; t.B += 3; return nil })
check(err == nil && s.A == 2 && s.B == 8, "commit")
```

**Expected:** The edited run panics with `commit` because `err == nil && s.A == 2 && s.B == 8` no longer holds.

**Verify:** Restoring `s := Balances{A: 5, B: 5}` makes the check pass again with the worked observation: the committed balances are 2 and 8.

The outer state changes only after the callback succeeds. This proves the local model policy, not database atomicity.

## 2. Rollback an explicit failure: debug a regression

A one-token regression in worked example 2 makes a line read `s := Balances{A: 6, B: 5}`. Repair it without changing the check.

The unchanged code is worked example 2:

```go
s := Balances{A: 5, B: 5}
err := transact(&s, func(t *Balances) error { t.A = 0; return errors.New("reject") })
check(err != nil && s.A == 5, "rollback")
```

**Expected:** The defective run panics with `rollback`; after restoring `s := Balances{A: 5, B: 5}`, the outer balances remain unchanged.

**Verify:** The failing run shows message `rollback`; after the repair `err != nil && s.A == 5` holds again.

A staged mutation is not a committed mutation. The distinction is visible because the model uses a separate value copy.

## 3. Reject invalid funds

Attempt a transfer larger than available balance.

```go
s := Balances{A: 5, B: 5}
err := transact(&s, func(t *Balances) error {
	if t.A < 8 {
		return errors.New("insufficient")
	}
	t.A -= 8
	t.B += 8
	return nil
})
check(err != nil && s.A == 5 && s.B == 5, "funds")
```

**Expected:** The state remains 5 and 5.

**Verify:** Your solution must keep `err != nil && s.A == 5 && s.B == 5` true. Control: changing `s := Balances{A: 5, B: 5}` to `s := Balances{A: 6, B: 5}` panics with message `funds`; revert it.

Validate the invariant in the same transaction that applies the change. A separate preflight read can become stale.

## 4. Preserve total value

Apply two successful transfers and inspect the combined balance.

```go
s := Balances{A: 5, B: 5}
for i := 0; i < 2; i++ {
	check(transact(&s, func(t *Balances) error { t.A--; t.B++; return nil }) == nil, "transfer")
}
check(s.A+s.B == 10, "total")
```

**Expected:** The total remains 10.

**Verify:** Your solution must keep `s.A+s.B == 10` true. Control: changing `check(s.A+s.B == 10, "total")` to `check(s.A-s.B == 10, "total")` panics with message `total`; revert it.

The invariant relates both fields. Real isolation must prevent other transactions from observing or creating forbidden combinations.

## 5. Keep a failed retry distinct

Fail one transaction, then explicitly start a new valid transaction.

```go
s := Balances{A: 5, B: 5}
_ = transact(&s, func(t *Balances) error { t.A = 99; return errors.New("fail") })
check(transact(&s, func(t *Balances) error { t.A--; t.B++; return nil }) == nil && s.A == 4, "retry")
```

**Expected:** Only the second change commits.

**Verify:** Your solution must keep `transact(&s, func(t *Balances) error { t.A--; t.B++; return nil }) == nil && s.A == 4` true. Control: changing `s := Balances{A: 5, B: 5}` to `s := Balances{A: 6, B: 5}` panics with message `retry`; revert it.

This retry is safe because the first local model outcome is known. A lost database commit response requires stronger evidence.

## 6. Transfer no-op semantics

Run a transaction that changes nothing.

```go
s := Balances{A: 5, B: 5}
err := transact(&s, func(t *Balances) error { return nil })
check(err == nil && s.A == 5 && s.B == 5, "no-op")
```

**Expected:** The state is preserved and the operation succeeds.

**Verify:** Your solution must keep `err == nil && s.A == 5 && s.B == 5` true. Control: changing `s := Balances{A: 5, B: 5}` to `s := Balances{A: 6, B: 5}` panics with message `no-op`; revert it.

Idempotent no-op behavior is useful, but it does not automatically make arbitrary external side effects replay-safe.

## Transfer after comparison

The Kubernetes lessons use the same staging idea: a controller computes a desired object, writes it once and treats a conflict as a reason to re-read rather than to patch blindly. Whenever a write can fail halfway, decide which state the caller may observe, and make retries safe by checking what actually committed before trying again.
