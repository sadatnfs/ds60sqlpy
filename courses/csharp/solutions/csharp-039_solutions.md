# csharp-039: explanation and comparison

Reference program: [csharp-039_solution.cs](csharp-039_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Decode a successful offline response:** A reserved invalid domain makes the fixture identity clear, while the custom handler prevents any actual connection. The handler supplies count 3 without network access.

**Preserve unsuccessful status:** Response arrival and application success are separate facts. 503 remains an observable failure rather than a default successful count.

## Task answers

### Task 1: Predict and explain

Trace transport, status, decoding and schema validation boundaries.

**Written answer.** Transport: `GetAsync` returns the response produced by `FixtureHandler`, with no network. Status: `EnsureSuccessStatusCode` throws `HttpRequestException` for non-2xx. Decoding: `JsonDocument.Parse` throws `JsonException` for malformed text. Schema: `GetProperty("count")` throws `KeyNotFoundException` when missing, and `GetInt32` throws when the value is not a number.

**Why it is correct.** Each boundary has its own failure type, so a caller can report which fact failed: the response, the status, the syntax or the shape.

**Plausible wrong approach.** Catching `Exception` around the whole call and reporting `service unreachable` merges all four boundaries. A 503, a truncated body and a renamed field then look like the same outage.

**How to verify.** Run Example A with bodies `{`, `{}` and `{"count":"3"}` and catch `JsonException`, `KeyNotFoundException` and `InvalidOperationException` respectively; the 503 fixture gives `HttpRequestException`.

### Task 2: Guided modification

Return valid JSON with a missing count property and classify the failure.

**Written answer.** Use `new FixtureHandler(HttpStatusCode.OK, "{\"total\":3}")`. Status and parsing succeed, and `GetProperty("count")` throws `KeyNotFoundException`. Classify it as a contract failure: the server answered with valid JSON of the wrong shape.

**Why it is correct.** The transport and syntax layers both succeeded, so neither retrying nor reporting malformed JSON fits. The fix belongs with whoever owns the response schema.

**Plausible wrong approach.** `root.TryGetProperty("count", out var c) ? c.GetInt32() : 0` turns the broken contract into a valid-looking count of 0, which downstream code cannot distinguish from an empty store.

**How to verify.** Catch `KeyNotFoundException` and check it was thrown, or check `TryGetProperty` returns false and report `count missing`.

### Task 3: Independent construction

Write a client method accepting a supplied HttpClient and CancellationToken.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
async Task<int> GetCountAsync(HttpClient client, CancellationToken ct) {
  var address = "https://example.invalid/count";
  using var response = await client.GetAsync(address, ct);
  response.EnsureSuccessStatusCode();
  string body = await response.Content.ReadAsStringAsync(ct);
  using var json = JsonDocument.Parse(body);
  return json.RootElement.GetProperty("count").GetInt32();
}
var handler = new FixtureHandler(HttpStatusCode.OK, "{\"count\":4}");
using var client = new HttpClient(handler);
Check(await GetCountAsync(client, CancellationToken.None) == 4, "count");
```

**Observe:** The method returns 4 from the fixture handler without any network access.

The caller supplies both the HttpClient and the token, so tests can pass an offline handler and callers control cancellation.

**Plausible wrong approach.** Creating `new HttpClient()` inside `GetCountAsync` makes the fixture impossible to inject, so the test would resolve `example.invalid` and fail with `HttpRequestException`. Creating a client per call also wastes connections in production.

**How to verify.** The block checks 4. Add `using var cts = new CancellationTokenSource(); cts.Cancel();` and check that `GetCountAsync(client, cts.Token)` throws an `OperationCanceledException`, proving the token reaches the request.

### Task 4: Diagnose a defect

Diagnose converting every non-2xx response into an empty success result.

**Written answer.** `if (!response.IsSuccessStatusCode) return 0;` reports a 503 as a count of 0, so a dashboard shows an empty store during an outage. Let `EnsureSuccessStatusCode` throw, or return a result type that carries the status.

**Why it is correct.** Receiving a response and the request succeeding are separate facts. A count is meaningful only after the status confirms success.

**Plausible wrong approach.** Returning -1 instead of 0 is still a number in the count's range. Any caller that sums or averages counts treats the outage as data.

**How to verify.** With the Example B fixture, the buggy method returns 0 and a check expecting `HttpRequestException` throws. The fixed method raises the exception and the check passes.

### Task 5: Boundary evidence

Test malformed JSON and an unexpected count type.

**Written answer.** Body `{"count":` makes `JsonDocument.Parse` throw a `JsonException`. Body `{"count":"3"}` parses, but `GetInt32` throws `InvalidOperationException` because the value kind is `String`. Body `{"count":3.5}` throws `FormatException`.

**Why it is correct.** Syntax errors are detected by the parser; type errors are detected only when a value is read as a specific type. Tests need a fixture for each.

**Plausible wrong approach.** Reading with `int.Parse(c.ToString())` accepts the string `"3"` and returns 3, silently accepting a server that broke the numeric contract.

**How to verify.** Run the three fixtures through the Task 3 method and catch the three exception types separately.

### Task 6: Transfer and justify

Design a retry policy that distinguishes safe reads from writes with unknown outcomes.

**Written answer.** Retry reads (`GET`) on 503, 429 (honoring `Retry-After`), 408 and transport failures, up to 3 attempts with exponential backoff and jitter. Never retry 400, 401 or 404. For a `POST` that creates an order, a timeout leaves the outcome unknown: retry only with an idempotency key the server deduplicates, or query the order status first.

**Why it is correct.** Repeating a safe read cannot change server state. Repeating a write whose first attempt may have succeeded can create a second order.

**Plausible wrong approach.** Retrying every non-2xx and every timeout uniformly sends a second `POST` after a timeout, and the customer is charged twice when the first request had in fact succeeded.

**How to verify.** Write a handler that returns 503 twice and then 200: the `GET` succeeds with exactly 3 handler calls. For a `POST` without an idempotency key, a timeout fixture must produce exactly 1 handler call.

## Mechanism and diagnostic reasoning

HTTP separates transport completion from application success. Receiving a response does not imply a 2xx status, and a 2xx response does not guarantee a valid application payload. Inspect status, bound the response, decode it and validate its schema. Cancellation should flow through the request and body processing.

HttpClient is intended for reuse under a deliberate lifetime policy. Repeatedly creating clients for every request can waste connection resources. The classroom uses a custom HttpMessageHandler, so it exercises real request/response APIs without contacting a network. This proves application handling, not DNS, TLS or remote availability.

A message handler is the transport boundary beneath HttpClient. A fake handler returns HttpResponseMessage deterministically. EnsureSuccessStatusCode throws for unsuccessful status; validate the body afterward.

A fake transport does not validate certificates or server availability. Do not retry all status codes blindly. Bound request and response lifetimes and redact credentials from diagnostic logs.

## Review before continuing

Run the reference and confirm it prints `csharp-039: passed`, then rerun the guide's counterexample.
