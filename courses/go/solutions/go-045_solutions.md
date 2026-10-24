# go-045: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

Several controller replicas improve availability, but some operations need a single active coordinator. Leader election uses a lease-like coordination record so candidates can observe and renew leadership. It is not a magical exactly-once guarantee. A paused process can continue believing it is leader after another process takes over; external side effects may therefore need fencing tokens or idempotency controls at the destination. Time assumptions, renewal deadlines and shutdown behavior matter. The client-go leader-election package explicitly does not provide fencing by itself. This lesson uses a deterministic logical clock to examine lease policy without sleeping or contacting a cluster.

A lease model records holder and expiry. A current holder can renew, another candidate must wait until expiry, and a candidate must stop leader-only work when renewal is lost. Real lease acquisition requires optimistic concurrency at the API server, not a local map assignment. A monotonically enforced fencing token belongs at the protected external system; Kubernetes resourceVersion should not be repurposed as a numeric application token.

## 1. Acquire an empty lease

Let candidate a acquire at logical time 10 for five units.

```go
l := Lease{}
check(acquire(&l, "a", 10, 5) && l.Holder == "a" && l.Expires == 15, "acquire")
```

**Expected:** Holder becomes a and expiry 15.

This local policy model does not implement distributed atomicity. A real update must be protected by the API concurrency contract.

## 2. Reject a competing candidate

Let b request an unexpired lease held by a.

```go
l := Lease{Holder: "a", Expires: 15}
check(!acquire(&l, "b", 12, 5) && l.Holder == "a", "contender")
```

**Expected:** The request fails and a remains holder.

The contender waits while the current claim remains valid under this model.

## 3. Renew current leadership

Let a renew its lease before expiry.

```go
l := Lease{Holder: "a", Expires: 15}
check(acquire(&l, "a", 13, 5) && l.Expires == 18, "renew")
```

**Expected:** Expiry advances to 18.

Renewal extends a claim; it does not prove a formerly paused process cannot still perform external work.

## 4. Take over after expiry

Let b acquire at the exact expiry boundary.

```go
l := Lease{Holder: "a", Expires: 15}
check(acquire(&l, "b", 15, 5) && l.Holder == "b", "takeover")
```

**Expected:** Holder becomes b.

The boundary policy is explicit. Real clock-skew and API latency assumptions require careful configuration and testing.

## 5. Reject a stale fenced operation

Compare an old authority token 4 with current token 5.

```go
current := 5
accept := func(token int) bool { return token == current }
check(!accept(4) && accept(5), "fencing")
```

**Expected:** Only token 5 is accepted by the destination model.

The protected destination enforces the token. Merely logging that leadership changed does not fence stale work.

## 6. Transfer invalid-duration refusal

Attempt a lease with a nonpositive duration.

```go
l := Lease{}
check(!acquire(&l, "a", 10, 0) && l.Holder == "", "duration")
```

**Expected:** No lease is acquired.

Invalid timing configuration must fail before coordination starts. Silent fallback can create unpredictable failover behavior.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
