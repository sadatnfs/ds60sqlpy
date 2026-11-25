# go-047: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-047_solution.go` implements all six cases.

## Mechanism

A controller needs several evidence layers. Pure tests check decision rules quickly. Fake-client tests check requested API interactions and local error handling but may omit server defaulting, validation, resourceVersion conflicts and admission behavior. API-server integration tests add those server contracts. An owned disposable cluster adds controllers, scheduling, networking and real cleanup behavior. Passing a fake test is not interchangeable with a successful rollout. Design fault injection around a specific uncertainty: conflict, cancellation, stale cache, forbidden access or unknown outcome. Keep source hashes, exact object identity and cleanup receipts so the evidence can be traced to the program that actually ran.

Use a narrow interface at the application boundary and inject a fake with explicit outcomes. Assert both the result and which calls were made. A forbidden error should not trigger an endless retry loop; a cancellation should stop new calls. For live tests, create a unique owned namespace, retain UIDs, bound all waits and verify cleanup without deleting resources identified only by a reusable name. Do not use production contexts as convenient fixtures.

## 1. Verify one successful API call: change one input

Copy worked example 1, change `f := &FakeReader{Value: 3}` to `f := &FakeReader{Value: 4}` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
f := &FakeReader{Value: 3}
v, err := readOnce(context.Background(), f)
check(err == nil && v == 3 && f.Calls == 1, "success")
```

**Expected:** The edited run panics with `success` because `err == nil && v == 3 && f.Calls == 1` no longer holds.

**Verify:** Restoring `f := &FakeReader{Value: 3}` makes the check pass again with the worked observation: the result is retained and exactly one call occurs.

Call count is evidence about adapter behavior, while the returned value checks the consuming contract.

## 2. Preserve a forbidden error: diagnose an edited check

A careless edit rewrote the check in worked example 2 as `check(errors.Is(err, ErrForbidden) && f.Calls != 1, "forbidden")`. Explain the failure, then restore it.

The unchanged code is worked example 2:

```go
f := &FakeReader{Err: ErrForbidden}
_, err := readOnce(context.Background(), f)
check(errors.Is(err, ErrForbidden) && f.Calls == 1, "forbidden")
```

**Expected:** The defective run panics with `forbidden`; after restoring `check(errors.Is(err, ErrForbidden) && f.Calls == 1, "forbidden")`, the exact cause is visible and only one call occurs.

**Verify:** The edited check fails with message `forbidden` for a state that `errors.Is(err, ErrForbidden) && f.Calls == 1` accepts.

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

**Verify:** Your solution must keep `errors.Is(err, context.Canceled) && f.Calls == 0` true. Control: changing `check(errors.Is(err, context.Canceled) && f.Calls == 0, "cancel")` to `check(errors.Is(err, context.Canceled) && f.Calls != 0, "cancel")` panics with message `cancel`; revert it.

The test verifies absence of a side effect, not merely the final error text.

## 4. Distinguish returned zero from failure

Return a successful zero from the fake.

```go
f := &FakeReader{Value: 0}
v, err := readOnce(context.Background(), f)
check(err == nil && v == 0, "zero success")
```

**Expected:** The zero is accepted with nil error.

**Verify:** Your solution must keep `err == nil && v == 0` true. Control: changing `f := &FakeReader{Value: 0}` to `f := &FakeReader{Value: 1}` panics with message `zero success`; revert it.

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

**Verify:** Your solution must keep `errors.Is(err, cause)` true. Control: an input that falsifies it fails with message `unknown cause`; revert it.

Preserving the cause supports diagnosis. A read retry policy differs from replaying a mutation whose outcome is uncertain.

## 6. Transfer source-bound evidence

Bind a synthetic receipt to its lesson ID and the SHA-256 digest of the exact source text, then compare it with a source that has one extra byte.

```go
source := "package main\n"
digest := func(text string) string { return fmt.Sprintf("%x", sha256.Sum256([]byte(text))) }
receipt := map[string]string{"lesson": "go-047", "source": digest(source)}
check(receipt["lesson"] == "go-047" && receipt["source"] == digest(source) && receipt["source"] != digest(source+" "), "receipt identity")
```

**Expected:** The receipt matches the exact source and rejects the changed source.

**Verify:** Your solution must keep `receipt["lesson"] == "go-047" && receipt["source"] == digest(source) && receipt["source"] != digest(source+" ")` true. Control: changing `receipt := map[string]string{"lesson": "go-047", "source": digest(source)}` to `receipt := map[string]string{"lesson": "go-48", "source": digest(source)}` panics with message `receipt identity`; revert it.

Binding evidence to a digest of the exact bytes means a later edit cannot reuse an old result. This small check illustrates the binding; the classroom records actual source hashes separately.

## Transfer after comparison

Every controller you build after this should carry three test layers: pure decision tests like plan and finalAction, fake-client tests for error handling and call counts, and an integration run against an owned cluster or envtest. Tie each piece of evidence to the exact source revision it tested, so a passing result is never reused for changed code.
