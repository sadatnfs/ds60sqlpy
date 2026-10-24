# go-023: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

An HTTP client owns a request lifecycle that can fail before any response exists or return a valid HTTP response describing an application failure. A 404 is usually not a transport error. Callers must inspect status, bound response bodies and close every acquired response body. Context cancellation propagates an explicit stop signal, while a client timeout bounds the overall operation. Reuse clients and transports in real services rather than constructing an unbounded pool of connections. This lesson injects a RoundTripper fake so the real client logic can be exercised without DNS, ports or external services.

RoundTrip(*http.Request) returns a response or a transport error. A function adapter can implement that interface for tests. NewRequestWithContext binds a request to cancellation. Client.Do follows client policy, including status-independent transport success. Read at most limit+1 bytes to detect oversized bodies. A response body must be closed even when its status is not accepted.

## 1. Read a successful response

Use a fake transport returning status 200 and body ready.

```go
v, err := fetch(context.Background(), 200, "ready", 8)
check(err == nil && v == "ready", "client success")
```

**Expected:** The client helper returns ready without error.

The fake isolates policy from the network. A live connection test would establish additional behavior and requires a separate owned target.

## 2. Reject an HTTP failure status

Return status 404 with a body.

```go
_, err := fetch(context.Background(), 404, "missing", 8)
check(err != nil, "HTTP status")
```

**Expected:** The helper returns an error despite transport success.

Client.Do does not classify every non-2xx response as a transport failure. Application status policy belongs in the consuming code.

## 3. Detect an oversized body

Return five bytes with a maximum of four.

```go
_, err := fetch(context.Background(), 200, "abcde", 4)
check(err != nil, "body limit")
```

**Expected:** The helper rejects the response.

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

The fake explicitly honors the request context. This demonstrates the contract required from a cooperating transport, not a universal guarantee for arbitrary blocking code.

## 5. Allow exact size

Return four bytes with a maximum of four.

```go
v, err := fetch(context.Background(), 200, "abcd", 4)
check(err == nil && v == "abcd", "exact size")
```

**Expected:** The helper accepts all four bytes.

An inclusive byte budget should accept exactly its maximum. This case distinguishes a correct greater-than check from an off-by-one rejection.

## 6. Transfer an empty body

Return 200 with an empty body under a positive budget.

```go
v, err := fetch(context.Background(), 200, "", 4)
check(err == nil && v == "", "empty response")
```

**Expected:** The transport helper returns an empty string successfully.

Transport completion and domain validity are separate. A caller that requires JSON or a nonempty document should validate that after the bounded read.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
