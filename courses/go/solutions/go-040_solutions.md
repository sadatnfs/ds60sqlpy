# go-040: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-040_solution.go` implements all six cases.

## Mechanism

A controller queue decouples event ingestion from reconciliation. Repeated events for one key can be coalesced because reconciliation reads the latest state. A failing key should not spin in a tight loop or prevent unrelated keys from progressing. Rate-limited retry combines an increasing delay with a cap and often jitter; cancellation and a maximum work policy prevent unlimited resource use. Permanent invalid input differs from a transient API failure. Success should clear retry history so an old failure does not penalize a repaired object forever. This lesson models scheduling decisions without sleeping or claiming a full implementation of client-go workqueue semantics.

A queue key usually names a namespace and object name, not a pointer to a stale object. The worker gets a key, defers Done, reconciles and either Forget on success or schedules a rate-limited retry. The fixture uses integer delay units to test a capped exponential policy deterministically. Production jitter should be tested with an injected source rather than a fixed assumption about wall-clock timing.

## 1. Calculate increasing delay: predict an edited check

Copy worked example 1, change `check(delay(0) == 1 && delay(1) == 2 && delay(2) == 4, "growth")` to `check(delay(1) == 1 && delay(1) == 2 && delay(2) == 4, "growth")` inside its check and predict whether it still passes; then restore it.

The unchanged code is worked example 1:

```go
check(delay(0) == 1 && delay(1) == 2 && delay(2) == 4, "growth")
```

**Expected:** The edited check panics with `growth` even though `delay(0) == 1 && delay(1) == 2 && delay(2) == 4` still holds.

**Verify:** Restoring `check(delay(0) == 1 && delay(1) == 2 && delay(2) == 4, "growth")` makes the check pass again with the worked observation: the delays are 1, 2 and 4 units.

The first attempt and retry numbering must be documented. Ambiguous numbering creates off-by-one operational behavior.

## 2. Cap the delay: diagnose an edited check

A careless edit rewrote the check in worked example 2 as `check(delay(3) != 8 && delay(10) == 8, "cap")`. Explain the failure, then restore it.

The unchanged code is worked example 2:

```go
check(delay(3) == 8 && delay(10) == 8, "cap")
```

**Expected:** The defective run panics with `cap`; after restoring `check(delay(3) == 8 && delay(10) == 8, "cap")`, the delay never exceeds 8 units.

**Verify:** The edited check fails with message `cap` for a state that `delay(3) == 8 && delay(10) == 8` accepts.

A cap prevents exponential growth from becoming impractical or overflowing. It does not replace a total retry budget.

## 3. Coalesce duplicate keys

Enqueue alpha twice and beta once in a set model.

```go
pending := map[string]bool{}
for _, key := range []string{"alpha", "alpha", "beta"} {
	pending[key] = true
}
check(len(pending) == 2, "coalesce")
```

**Expected:** There are two pending identities.

**Verify:** Your solution must keep `len(pending) == 2` true. Control: changing `for _, key := range []string{"alpha", "alpha", "beta"} {` to `for _, key := range []string{"alpha!", "alpha", "beta"} {` panics with message `coalesce`; revert it.

This model demonstrates identity coalescing only. A real workqueue also handles dirty keys that change while already processing.

## 4. Separate invalid from transient

Classify a validation failure and a timeout-like failure.

```go
check(!retryable("invalid") && retryable("transient"), "classification")
```

**Expected:** Only the transient class is retried.

**Verify:** Your solution must keep `!retryable("invalid") && retryable("transient")` true. Control: changing `check(!retryable("invalid") && retryable("transient"), "classification")` to `check(!retryable("invalid") && retryable("transient!"), "classification")` panics with message `classification`; revert it.

Blindly retrying invalid desired state wastes resources and delays useful feedback to the user.

## 5. Reset successful history

Clear a key after successful reconciliation.

```go
attempts := map[string]int{"demo": 3}
delete(attempts, "demo")
check(delay(attempts["demo"]) == 1, "reset")
```

**Expected:** Its next failure starts at the first delay.

**Verify:** Your solution must keep `delay(attempts["demo"]) == 1` true. Control: changing `check(delay(attempts["demo"]) == 1, "reset")` to `check(delay(attempts["demo"]) != 1, "reset")` panics with message `reset`; revert it.

Success ends the current failure sequence. Retaining stale backoff can make a later unrelated event appear inexplicably slow.

## 6. Transfer a total budget

Spend a total waiting budget of 10 units on retries whose delays come from delay(attempt).

```go
spent, attempts := 0, 0
for attempt := 0; ; attempt++ {
	d := delay(attempt)
	if spent+d > 10 {
		break
	}
	spent += d
	attempts++
}
check(attempts == 3 && spent == 7, "budget")
```

**Expected:** Three retries fit (1+2+4=7 units); the fourth delay of 8 would exceed the budget.

**Verify:** Your solution must keep `attempts == 3 && spent == 7` true. Control: changing `if spent+d > 10 {` to `if spent-d > 10 {` panics with message `budget`; revert it.

A delay cap bounds waiting per retry, while an attempt or elapsed-time budget bounds total work. Both are separate policies, and the total budget is checked before a delay is spent.

## Transfer after comparison

client-go's workqueue implements this policy: Add coalesces keys, AddRateLimited applies per-key backoff and Forget resets it after success. The same decisions apply to any background worker calling a remote service: classify errors, cap delays, add jitter in production and bound total effort with a deadline so one stuck key cannot consume the whole budget.
