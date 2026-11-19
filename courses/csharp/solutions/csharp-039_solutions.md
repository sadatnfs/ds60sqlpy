# csharp-039: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-039_solution.cs](csharp-039_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Decode a successful offline response:** A reserved invalid domain makes the fixture identity clear, while the custom handler prevents any actual connection. The handler supplies count 3 without network access.

**Preserve unsuccessful status:** Response arrival and application success are separate facts. 503 remains an observable failure rather than a default successful count.

## Task answers

### Task 1: Predict and explain

Trace transport, status, decoding and schema validation boundaries.

No separate reference answer has been written for this task. Example A is the evidence to compare with: A reserved invalid domain makes the fixture identity clear, while the custom handler prevents any actual connection. The handler supplies count 3 without network access.

### Task 2: Guided modification

Return valid JSON with a missing count property and classify the failure.

No separate reference answer has been written for this task. Start from Example B: Response arrival and application success are separate facts. 503 remains an observable failure rather than a default successful count.

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

### Task 4: Diagnose a defect

Diagnose converting every non-2xx response into an empty success result.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A fake transport does not validate certificates or server availability. Do not retry all status codes blindly. Bound request and response lifetimes and redact credentials from diagnostic logs.

### Task 5: Boundary evidence

Test malformed JSON and an unexpected count type.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Decode a successful offline response) and Example B (Preserve unsuccessful status).

### Task 6: Transfer and justify

Design a retry policy that distinguishes safe reads from writes with unknown outcomes.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Transport**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

HTTP separates transport completion from application success. Receiving a response does not imply a 2xx status, and a 2xx response does not guarantee a valid application payload. Inspect status, bound the response, decode it and validate its schema. Cancellation should flow through the request and body processing.

HttpClient is intended for reuse under a deliberate lifetime policy. Repeatedly creating clients for every request can waste connection resources. The classroom uses a custom HttpMessageHandler, so it exercises real request/response APIs without contacting a network. This proves application handling, not DNS, TLS or remote availability.

A message handler is the transport boundary beneath HttpClient. A fake handler returns HttpResponseMessage deterministically. EnsureSuccessStatusCode throws for unsuccessful status; validate the body afterward.

A fake transport does not validate certificates or server availability. Do not retry all status codes blindly. Bound request and response lifetimes and redact credentials from diagnostic logs.

## Review before continuing

Run the reference and confirm that it prints `csharp-039: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
