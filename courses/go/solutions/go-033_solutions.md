# go-033: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A repository boundary separates business operations from database mechanics. The application should describe the transaction it needs, while an adapter manages SQL parameters, context cancellation, row scanning and commit or rollback. In database/sql, a DB is a connection pool rather than one connection. A Tx reserves a transaction context whose operations must all use that Tx. Calling the outer DB halfway through a transaction can escape its atomicity. This lesson uses a small copy-on-write transactional model to test policy offline. It is explicitly not evidence about PostgreSQL isolation, driver behavior or network failure. Those require a prepared database integration test.

A callback receiving a transaction-local value can stage changes before committing them to the outer state. An error aborts the staged changes. In a real database/sql adapter, begin with BeginTx(ctx, options), defer Rollback, execute parameterized statements through tx, and inspect Commit errors. SQL syntax and placeholder conventions depend on the selected driver. Never construct SQL by interpolating untrusted values. A transaction whose commit outcome is unknown cannot safely be replayed without an idempotency contract.

## 1. Commit a valid change

Transfer 3 between balances 5 and 5 in a staged transaction.

```go
s := Balances{A: 5, B: 5}
err := transact(&s, func(t *Balances) error { t.A -= 3; t.B += 3; return nil })
check(err == nil && s.A == 2 && s.B == 8, "commit")
```

**Expected:** The committed balances are 2 and 8.

The outer state changes only after the callback succeeds. This proves the local model policy, not database atomicity.

## 2. Rollback an explicit failure

Change staged state and return an error.

```go
s := Balances{A: 5, B: 5}
err := transact(&s, func(t *Balances) error { t.A = 0; return errors.New("reject") })
check(err != nil && s.A == 5, "rollback")
```

**Expected:** The outer balances remain unchanged.

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

The invariant relates both fields. Real isolation must prevent other transactions from observing or creating forbidden combinations.

## 5. Keep a failed retry distinct

Fail one transaction, then explicitly start a new valid transaction.

```go
s := Balances{A: 5, B: 5}
_ = transact(&s, func(t *Balances) error { t.A = 99; return errors.New("fail") })
check(transact(&s, func(t *Balances) error { t.A--; t.B++; return nil }) == nil && s.A == 4, "retry")
```

**Expected:** Only the second change commits.

This retry is safe because the first local model outcome is known. A lost database commit response requires stronger evidence.

## 6. Transfer no-op semantics

Run a transaction that changes nothing.

```go
s := Balances{A: 5, B: 5}
err := transact(&s, func(t *Balances) error { return nil })
check(err == nil && s.A == 5 && s.B == 5, "no-op")
```

**Expected:** The state is preserved and the operation succeeds.

Idempotent no-op behavior is useful, but it does not automatically make arbitrary external side effects replay-safe.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
