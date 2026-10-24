# go-047: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A controller needs several evidence layers. Pure tests check decision rules quickly. Fake-client tests check requested API interactions and local error handling but may omit server defaulting, validation, resourceVersion conflicts and admission behavior. API-server integration tests add those server contracts. An owned disposable cluster adds controllers, scheduling, networking and real cleanup behavior. Passing a fake test is not interchangeable with a successful rollout. Design fault injection around a specific uncertainty: conflict, cancellation, stale cache, forbidden access or unknown outcome. Keep source hashes, exact object identity and cleanup receipts so the evidence can be traced to the program that actually ran.

Use a narrow interface at the application boundary and inject a fake with explicit outcomes. Assert both the result and which calls were made. A forbidden error should not trigger an endless retry loop; a cancellation should stop new calls. For live tests, create a unique owned namespace, retain UIDs, bound all waits and verify cleanup without deleting resources identified only by a reusable name. Do not use production contexts as convenient fixtures.

## 1. Verify one successful API call

Run a fake client configured to return a value.

```go
f := &FakeReader{Value: 3}
v, err := readOnce(context.Background(), f)
check(err == nil && v == 3 && f.Calls == 1, "success")
```

**Expected:** The result is retained and exactly one call occurs.

Call count is evidence about adapter behavior, while the returned value checks the consuming contract.

## 2. Preserve a forbidden error

Make the fake return ErrForbidden.

```go
f := &FakeReader{Err: ErrForbidden}
_, err := readOnce(context.Background(), f)
check(errors.Is(err, ErrForbidden) && f.Calls == 1, "forbidden")
```

**Expected:** The exact cause is visible and only one call occurs.

Authorization failure is not repaired by repeating the same request. Surface the required permission or configuration diagnosis.

## 3. Stop before a canceled call

Cancel context before invoking the adapter.

```go
ctx, cancel := context.WithCancel(context.Background())
cancel()
f := &FakeReader{}
_, err := readOnce(ctx, f)
check(errors.Is(err, context.Canceled) && f.Calls == 0, "cancel")
```

**Expected:** No API call is made.

The test verifies absence of a side effect, not merely the final error text.

## 4. Distinguish returned zero from failure

Return a successful zero from the fake.

```go
f := &FakeReader{Value: 0}
v, err := readOnce(context.Background(), f)
check(err == nil && v == 0, "zero success")
```

**Expected:** The zero is accepted with nil error.

Result value and operation status are separate channels. A zero cannot stand in for every failure.

## 5. Retain an unknown failure

Return an unexpected error cause.

```go
cause := errors.New("transport outcome unknown")
f := &FakeReader{Err: cause}
_, err := readOnce(context.Background(), f)
check(errors.Is(err, cause), "unknown cause")
```

**Expected:** The cause remains inspectable.

Preserving the cause supports diagnosis. A read retry policy differs from replaying a mutation whose outcome is uncertain.

## 6. Transfer source-bound evidence

Bind a synthetic receipt to its lesson ID and source digest label.

```go
receipt := map[string]string{"lesson": "go-047", "source": "reviewed-fixture"}
check(receipt["lesson"] == "go-047" && receipt["source"] == "reviewed-fixture", "receipt identity")
```

**Expected:** Both identifiers survive comparison.

This small metadata check illustrates binding, not a cryptographic receipt implementation. The classroom records actual source hashes separately.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
