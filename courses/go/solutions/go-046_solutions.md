# go-046: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

Admission evaluates an API request after authentication and authorization and before persistence. Mutating admission can change an object; validating admission can accept or reject it. A webhook introduces a network dependency into control-plane writes, so latency, availability and failurePolicy have real consequences. Fail-open can preserve availability while allowing objects that were not checked; fail-closed can enforce policy while blocking writes during an outage. Choose deliberately and test recovery. AdmissionReview responses must correspond to the request UID and use the supported API version. A validation decision is not permission to perform unrelated side effects, especially for dry-run requests.

Separate the pure policy from the HTTP and AdmissionReview adapter. The fixture validates a replica range and preserves a synthetic request UID in its decision. A real adapter needs bounded body parsing, TLS, a configured timeout, correct response schema and no hidden external side effects. Rejection messages should identify the field and rule without exposing credentials or excessive source content.

## 1. Accept a valid range: change one input

Copy worked example 1 into a scratch pad and change `d := admit("r1", 3, 5, false)` to `d := admit("r2", 3, 5, false)`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.

The unchanged code is worked example 1:

```go
d := admit("r1", 3, 5, false)
check(d.Allowed && d.UID == "r1", "allow")
```

**Expected:** The changed run panics with `allow` because `d.Allowed && d.UID == "r1"` no longer holds. Restoring the original line brings back the worked observation: the decision allows the request.

The pure rule is independently testable. The HTTP adapter still needs protocol and transport validation.

## 2. Reject a negative value: diagnose an edited check

A careless edit changed the check in worked example 2 so that it reads `check(!d.Allowed && d.Reason == "", "negative")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.

The unchanged code is worked example 2:

```go
d := admit("r2", -1, 5, false)
check(!d.Allowed && d.Reason != "", "negative")
```

**Expected:** Before the repair the program panics with `negative`; after it the line reads `check(!d.Allowed && d.Reason != "", "negative")` again and the decision denies it with a reason.

Field-specific validation gives an actionable failure instead of an unexplained generic denial.

## 3. Check the exact upper boundary

Validate counts 5 and 6 against maximum 5.

```go
check(admit("r3", 5, 5, false).Allowed && !admit("r4", 6, 5, false).Allowed, "boundary")
```

**Expected:** Five is allowed and six is denied.

The inclusive bound must be clear. Boundary tests catch a common off-by-one policy defect.

## 4. Preserve request identity

Validate a request and inspect the response UID.

```go
d := admit("request-42", 2, 5, false)
check(d.UID == "request-42", "UID")
```

**Expected:** The exact request UID is copied.

A response for another request must not be accepted as evidence for this one. Identity binding is part of the webhook protocol.

## 5. Keep dry-run side effects absent

Evaluate the same allowed request once in dry-run mode and once for real.

```go
d := admit("r5", 2, 5, true)
live := admit("r6", 2, 5, false)
check(d.Allowed && d.SideEffects == 0 && live.Allowed && live.SideEffects == 1, "dry run")
```

**Expected:** Both decisions allow the request; only the real evaluation records a side effect.

This validator records one audit side effect for an allowed real request and none for dry run. Real webhooks must declare their side-effect class accurately and skip side effects when the request is a dry run.

## 6. Transfer missing identity refusal

Evaluate a request lacking its UID.

```go
d := admit("", 2, 5, false)
check(!d.Allowed, "missing UID")
```

**Expected:** The decision is denied.

A valid numeric object is insufficient if the adapter cannot bind the response to a request. Protocol validation precedes domain success.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
