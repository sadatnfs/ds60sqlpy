# go-046: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-046_solution.go` implements all six cases.

## Mechanism

Admission evaluates an API request after authentication and authorization and before persistence. Mutating admission can change an object; validating admission can accept or reject it. A webhook introduces a network dependency into control-plane writes, so latency, availability and failurePolicy have real consequences. Fail-open can preserve availability while allowing objects that were not checked; fail-closed can enforce policy while blocking writes during an outage. Choose deliberately and test recovery. AdmissionReview responses must correspond to the request UID and use the supported API version. A validation decision is not permission to perform unrelated side effects, especially for dry-run requests.

Separate the pure policy from the HTTP and AdmissionReview adapter. The fixture validates a replica range and preserves a synthetic request UID in its decision. A real adapter needs bounded body parsing, TLS, a configured timeout, correct response schema and no hidden external side effects. Rejection messages should identify the field and rule without exposing credentials or excessive source content.

## 1. Accept a valid range: change one input

Copy worked example 1, change `d := admit("r1", 3, 5, false)` to `d := admit("r2", 3, 5, false)` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
d := admit("r1", 3, 5, false)
check(d.Allowed && d.UID == "r1", "allow")
```

**Expected:** The edited run panics with `allow` because `d.Allowed && d.UID == "r1"` no longer holds.

**Verify:** Restoring `d := admit("r1", 3, 5, false)` makes the check pass again with the worked observation: the decision allows the request.

The pure rule is independently testable. The HTTP adapter still needs protocol and transport validation.

## 2. Reject a negative value: diagnose an edited check

A careless edit rewrote the check in worked example 2 as `check(!d.Allowed && d.Reason == "", "negative")`. Explain the failure, then restore it.

The unchanged code is worked example 2:

```go
d := admit("r2", -1, 5, false)
check(!d.Allowed && d.Reason != "", "negative")
```

**Expected:** The defective run panics with `negative`; after restoring `check(!d.Allowed && d.Reason != "", "negative")`, the decision denies it with a reason.

**Verify:** The edited check fails with message `negative` for a state that `!d.Allowed && d.Reason != ""` accepts.

Field-specific validation gives an actionable failure instead of an unexplained generic denial.

## 3. Check the exact upper boundary

Validate counts 5 and 6 against maximum 5.

```go
check(admit("r3", 5, 5, false).Allowed && !admit("r4", 6, 5, false).Allowed, "boundary")
```

**Expected:** Five is allowed and six is denied.

**Verify:** Your solution must keep `admit("r3", 5, 5, false).Allowed && !admit("r4", 6, 5, false).Allowed` true. Control: changing `check(admit("r3", 5, 5, false).Allowed && !admit("r4", 6, 5, false).Allowed, "boundary")` to `check(admit("r3", 6, 5, false).Allowed && !admit("r4", 6, 5, false).Allowed, "boundary")` panics with message `boundary`; revert it.

The inclusive bound must be clear. Boundary tests catch a common off-by-one policy defect.

## 4. Preserve request identity

Validate a request and inspect the response UID.

```go
d := admit("request-42", 2, 5, false)
check(d.UID == "request-42", "UID")
```

**Expected:** The exact request UID is copied.

**Verify:** Your solution must keep `d.UID == "request-42"` true. Control: changing `d := admit("request-42", 2, 5, false)` to `d := admit("request-43", 2, 5, false)` panics with message `UID`; revert it.

A response for another request must not be accepted as evidence for this one. Identity binding is part of the webhook protocol.

## 5. Keep dry-run side effects absent

Evaluate the same allowed request once in dry-run mode and once for real.

```go
d := admit("r5", 2, 5, true)
live := admit("r6", 2, 5, false)
check(d.Allowed && d.SideEffects == 0 && live.Allowed && live.SideEffects == 1, "dry run")
```

**Expected:** Both decisions allow the request; only the real evaluation records a side effect.

**Verify:** Your solution must keep `d.Allowed && d.SideEffects == 0 && live.Allowed && live.SideEffects == 1` true. Control: changing `d := admit("r5", 2, 5, true)` to `d := admit("r5", 2, 5, false)` panics with message `dry run`; revert it.

This validator records one audit side effect for an allowed real request and none for dry run. Real webhooks must declare their side-effect class accurately and skip side effects when the request is a dry run.

## 6. Transfer missing identity refusal

Evaluate a request lacking its UID.

```go
d := admit("", 2, 5, false)
check(!d.Allowed, "missing UID")
```

**Expected:** The decision is denied.

**Verify:** Your solution must keep `!d.Allowed` true. Control: changing `check(!d.Allowed, "missing UID")` to `check(d.Allowed, "missing UID")` panics with message `missing UID`; revert it.

A valid numeric object is insufficient if the adapter cannot bind the response to a request. Protocol validation precedes domain success.

## Transfer after comparison

Admission sits between authorization and storage, so policy engines, defaulting webhooks and validating admission policies all follow this contract. When a deploy fails with a denied request, the reason should name the field and rule. When you write one, test boundaries, dry run and the unavailable case, and measure latency, because it sits on every write path it covers.
