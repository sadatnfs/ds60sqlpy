# go-023: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-023_solution.go` implements all six cases.

## Mechanism

An HTTP client owns a request lifecycle that can fail before any response exists or return a valid HTTP response describing an application failure. A 404 is usually not a transport error. Callers must inspect status, bound response bodies and close every acquired response body. Context cancellation propagates an explicit stop signal, while a client timeout bounds the overall operation. Reuse clients and transports in real services rather than constructing an unbounded pool of connections. This lesson injects a RoundTripper fake so the real client logic can be exercised without DNS, ports or external services.

RoundTrip(*http.Request) returns a response or a transport error. A function adapter can implement that interface for tests. NewRequestWithContext binds a request to cancellation. Client.Do follows client policy, including status-independent transport success. Read at most limit+1 bytes to detect oversized bodies. A response body must be closed even when its status is not accepted.

## 1. Read a successful response: change one input

Copy worked example 1, change `v, err := fetch(context.Background(), 200, "ready", 8)` to `v, err := fetch(context.Background(), 201, "ready", 8)` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
v, err := fetch(context.Background(), 200, "ready", 8)
check(err == nil && v == "ready", "client success")
```

**Expected:** The edited run panics with `client success` because `err == nil && v == "ready"` no longer holds.

**Verify:** Restoring `v, err := fetch(context.Background(), 200, "ready", 8)` makes the check pass again with the worked observation: the client helper returns ready without error.

The fake isolates policy from the network. A live connection test would establish additional behavior and requires a separate owned target.

## 2. Reject an HTTP failure status: diagnose an edited check

A careless edit rewrote the check in worked example 2 as `check(err == nil, "HTTP status")`. Explain the failure, then restore it.

The unchanged code is worked example 2:

```go
_, err := fetch(context.Background(), 404, "missing", 8)
check(err != nil, "HTTP status")
```

**Expected:** The defective run panics with `HTTP status`; after restoring `check(err != nil, "HTTP status")`, the helper returns an error despite transport success.

**Verify:** The edited check fails with message `HTTP status` for a state that `err != nil` accepts.

Client.Do does not classify every non-2xx response as a transport failure. Application status policy belongs in the consuming code.

## 3. Detect an oversized body

Return five bytes with a maximum of four.

```go
_, err := fetch(context.Background(), 200, "abcde", 4)
check(err != nil, "body limit")
```

**Expected:** The helper rejects the response.

**Verify:** Your solution must keep `err != nil` true. Control: changing `_, err := fetch(context.Background(), 200, "abcde", 4)` to `_, err := fetch(context.Background(), 200, "abcde", 5)` panics with message `body limit`; revert it.

Reading one extra byte makes the limit observable. Silently truncating to four would make an oversized response look like valid short content.

## 4. Honor cancellation

Cancel the context before invoking the fake transport.

```go
ctx, cancel := context.WithCancel(context.Background())
cancel()
_, err := fetch(ctx, 200, "ready", 8)
check(errors.Is(err, context.Canceled), "cancellation")
```

**Expected:** The returned error matches context.Canceled.

**Verify:** Your solution must keep `errors.Is(err, context.Canceled)` true. Control: an input that falsifies it fails with message `cancellation`; revert it.

The fake explicitly honors the request context. This demonstrates the contract required from a cooperating transport, not a universal guarantee for arbitrary blocking code.

## 5. Allow exact size

Return four bytes with a maximum of four.

```go
v, err := fetch(context.Background(), 200, "abcd", 4)
check(err == nil && v == "abcd", "exact size")
```

**Expected:** The helper accepts all four bytes.

**Verify:** Your solution must keep `err == nil && v == "abcd"` true. Control: changing `v, err := fetch(context.Background(), 200, "abcd", 4)` to `v, err := fetch(context.Background(), 201, "abcd", 4)` panics with message `exact size`; revert it.

An inclusive byte budget should accept exactly its maximum. This case distinguishes a correct greater-than check from an off-by-one rejection.

## 6. Transfer an empty body

Return 200 with an empty body under a positive budget.

```go
v, err := fetch(context.Background(), 200, "", 4)
check(err == nil && v == "", "empty response")
```

**Expected:** The transport helper returns an empty string successfully.

**Verify:** Your solution must keep `err == nil && v == ""` true. Control: changing `v, err := fetch(context.Background(), 200, "", 4)` to `v, err := fetch(context.Background(), 201, "", 4)` panics with message `empty response`; revert it.

Transport completion and domain validity are separate. A caller that requires JSON or a nonempty document should validate that after the bounded read.

## Transfer after comparison

Every remote call in later lessons has three failure layers: the transport, the protocol status and the payload. The Kubernetes client wraps HTTP the same way, so an API conflict or a not-found object is a status, not a broken connection. Keep a context deadline on every call, bound what you read and make the caller decide which statuses count as success.
