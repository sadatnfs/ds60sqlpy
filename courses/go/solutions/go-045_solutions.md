# go-045: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-045_solution.go` implements all six cases.

## Mechanism

Several controller replicas improve availability, but some operations need a single active coordinator. Leader election uses a lease-like coordination record so candidates can observe and renew leadership. It is not a magical exactly-once guarantee. A paused process can continue believing it is leader after another process takes over; external side effects may therefore need fencing tokens or idempotency controls at the destination. Time assumptions, renewal deadlines and shutdown behavior matter. The client-go leader-election package explicitly does not provide fencing by itself. This lesson uses a deterministic logical clock to examine lease policy without sleeping or contacting a cluster.

A lease model records holder and expiry. A current holder can renew, another candidate must wait until expiry, and a candidate must stop leader-only work when renewal is lost. Real lease acquisition requires optimistic concurrency at the API server, not a local map assignment. A monotonically enforced fencing token belongs at the protected external system; Kubernetes resourceVersion should not be repurposed as a numeric application token.

## 1. Acquire an empty lease: predict an edited check

Copy worked example 1, change `check(acquire(&l, "a", 10, 5) && l.Holder == "a" && l.Expires == 15, "acquire")` to `check(acquire(&l, "a", 11, 5) && l.Holder == "a" && l.Expires == 15, "acquire")` inside its check and predict whether it still passes; then restore it.

The unchanged code is worked example 1:

```go
l := Lease{}
check(acquire(&l, "a", 10, 5) && l.Holder == "a" && l.Expires == 15, "acquire")
```

**Expected:** The edited check panics with `acquire` even though `acquire(&l, "a", 10, 5) && l.Holder == "a" && l.Expires == 15` still holds.

**Verify:** Restoring `check(acquire(&l, "a", 10, 5) && l.Holder == "a" && l.Expires == 15, "acquire")` makes the check pass again with the worked observation: holder becomes a and expiry 15.

This local policy model does not implement distributed atomicity. A real update must be protected by the API concurrency contract.

**Approach.** Trace the edited call `acquire(&l, "a", 11, 5)` on an empty lease: the candidate and duration are valid and nobody holds the lease, so `a` takes it with `Expires` set to 11 plus 5.

**Why it holds here.** Expiry is computed from the acquisition time, so it becomes 16. `acquire` returns true and the holder is `a`, but `l.Expires == 15` fails and the check panics with `acquire`.

**A plausible wrong approach.** Predicting that expiry stays 15 because the lease window is fixed, or that a later `now` is refused. An empty lease is always granted, and the window always starts at the moment of acquisition.

**Verify.** Print `l` after the edited call and see `{a 16}`; the original call gives `{a 15}`.

## 2. Reject a competing candidate: debug a regression

A one-token regression in worked example 2 makes a line read `l := Lease{Holder: "a!", Expires: 15}`. Repair it without changing the check.

The unchanged code is worked example 2:

```go
l := Lease{Holder: "a", Expires: 15}
check(!acquire(&l, "b", 12, 5) && l.Holder == "a", "contender")
```

**Expected:** The defective run panics with `contender`; after restoring `l := Lease{Holder: "a", Expires: 15}`, the request fails and a remains holder.

**Verify:** The failing run shows message `contender`; after the repair `!acquire(&l, "b", 12, 5) && l.Holder == "a"` holds again.

The contender waits while the current claim remains valid under this model.

**Approach.** Run the regressed fixture: the lease is held by `a!` until 15, and `b` asks at 12. The holder differs from the candidate and 12 is before expiry, so `acquire` refuses.

**Why it holds here.** The refusal is correct, so `!acquire(...)` holds; the failing operand is `l.Holder == "a"`, because the fixture names `a!`. Restoring `a` repairs the data without changing `acquire`.

**A plausible wrong approach.** Assuming the contender won and debugging the time comparison in `acquire`. The result is false and the lease is unchanged, so the defect is in the fixture's holder name, not in the policy.

**Verify.** Print the result and `l` and see `false {a! 15}` for the regression and `false {a 15}` after the repair.

## 3. Renew current leadership

Let a renew its lease before expiry.

```go
l := Lease{Holder: "a", Expires: 15}
check(acquire(&l, "a", 13, 5) && l.Expires == 18, "renew")
```

**Expected:** Expiry advances to 18.

**Verify:** Your solution must keep `acquire(&l, "a", 13, 5) && l.Expires == 18` true. Control: changing `check(acquire(&l, "a", 13, 5) && l.Expires == 18, "renew")` to `check(acquire(&l, "a", 14, 5) && l.Expires == 18, "renew")` panics with message `renew`; revert it.

Renewal extends a claim; it does not prove a formerly paused process cannot still perform external work.

**Approach.** Let the current holder `a` call `acquire` at 13. The holder equals the candidate, so the lease is renewed with `Expires` set to 13 plus 5.

**Why it holds here.** Renewal uses the same rule as acquisition, the window starts now, so expiry moves from 15 to 18 and `acquire` returns true.

**A plausible wrong approach.** Renewing by adding the duration to the old expiry, `l.Expires += duration`. That gives 20 instead of 18, the check panics with `renew`, and repeated early renewals would stretch leadership far beyond the configured window.

**Verify.** Print `l` after renewal and see `{a 18}`.

## 4. Take over after expiry

Let b acquire at the exact expiry boundary.

```go
l := Lease{Holder: "a", Expires: 15}
check(acquire(&l, "b", 15, 5) && l.Holder == "b", "takeover")
```

**Expected:** Holder becomes b.

**Verify:** Your solution must keep `acquire(&l, "b", 15, 5) && l.Holder == "b"` true. Control: changing `l := Lease{Holder: "a", Expires: 15}` to `l := Lease{Holder: "a", Expires: 16}` panics with message `takeover`; revert it.

The boundary policy is explicit. Real clock-skew and API latency assumptions require careful configuration and testing.

**Approach.** Ask for the lease as `b` at exactly 15, the stored expiry. The refusal requires `now < l.Expires`, and 15 is not less than 15.

**Why it holds here.** At the boundary the lease counts as expired, so `b` takes over with `Expires` 20 and `l.Holder` is `b`.

**A plausible wrong approach.** Writing the comparison as `now <= l.Expires`. Then `b` is refused at 15, the holder stays `a` and the check panics with `takeover`: a one-tick off-by-one at the boundary.

**Verify.** Print the result and `l` and see `true {b 20}`; repeating at 14 on a fresh lease gives `false {a 15}`.

## 5. Reject a stale fenced operation

Compare an old authority token 4 with current token 5.

```go
current := 5
accept := func(token int) bool { return token == current }
check(!accept(4) && accept(5), "fencing")
```

**Expected:** Only token 5 is accepted by the destination model.

**Verify:** Your solution must keep `!accept(4) && accept(5)` true. Control: changing `accept := func(token int) bool { return token == current }` to `accept := func(token int) bool { return token != current }` panics with message `fencing`; revert it.

The protected destination enforces the token. Merely logging that leadership changed does not fence stale work.

**Approach.** Let the destination accept a write only when its token equals the current fencing token 5.

**Why it holds here.** Token 4 was issued to an earlier leader, so `accept(4)` is false, while the current holder's token 5 is accepted.

**A plausible wrong approach.** Accepting any token the system has issued, `token <= current`. The stale leader's token 4 passes, the check panics with `fencing`, and a paused former leader could overwrite newer data.

**Verify.** Print `accept(3), accept(4), accept(5)` and see `false false true`.

## 6. Transfer invalid-duration refusal

Attempt a lease with a nonpositive duration.

```go
l := Lease{}
check(!acquire(&l, "a", 10, 0) && l.Holder == "", "duration")
```

**Expected:** No lease is acquired.

**Verify:** Your solution must keep `!acquire(&l, "a", 10, 0) && l.Holder == ""` true. Control: changing `check(!acquire(&l, "a", 10, 0) && l.Holder == "", "duration")` to `check(!acquire(&l, "a", 10, 1) && l.Holder == "", "duration")` panics with message `duration`; revert it.

Invalid timing configuration must fail before coordination starts. Silent fallback can create unpredictable failover behavior.

**Approach.** Reject a nonpositive duration before looking at the lease, so a zero duration returns false and leaves the lease empty.

**Why it holds here.** `duration <= 0` is true for 0, so `acquire` returns false without assigning the holder, and `l.Holder` stays empty.

**A plausible wrong approach.** Validating with `duration < 0`. Zero then passes, `a` becomes holder with `Expires` 10, a lease that is already expired, and the check panics with `duration`; any contender could take it the same instant.

**Verify.** Print the result and `l` and see `false { 0}`.

## Transfer after comparison

Add a `Token int` field that `acquire` increments only when the holder changes. Check that `a` taking an empty lease at 10 gets token 1, renewing at 13 keeps 1, `b` taking over at 15 gets 2, and a destination that rejects tokens below the highest seen refuses a late write from `a` with token 1. Explain which check a token incremented on every renewal would change.
