# csharp-039: HTTP clients, status contracts and offline transport tests

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-038`

## Learning objectives

Call HTTP services through an injected HttpClient and test status and content contracts offline. The central exercise is task 3: Write a client method accepting a supplied HttpClient and CancellationToken.

## Purpose and mental model

HTTP separates transport completion from application success. Receiving a response does not imply a 2xx status, and a 2xx response does not guarantee a valid application payload. Inspect status, bound the response, decode it and validate its schema. Cancellation should flow through the request and body processing.

HttpClient is intended for reuse under a deliberate lifetime policy. Repeatedly creating clients for every request can waste connection resources. The classroom uses a custom HttpMessageHandler, so it exercises real request/response APIs without contacting a network. This proves application handling, not DNS, TLS or remote availability.

## Vocabulary and concepts

**Transport:** The mechanism carrying a request and response.

**Status code:** The protocol-level response category.

**Test double:** A controlled dependency used to exercise a consumer contract.

## How to run this lesson

The fake transport is `FixtureHandler`, declared after `Main`, and the run uses no network: example.invalid is a reserved name that never resolves, and the handler answers before any connection would be attempted. The worked examples already import `System.Net`, `System.Net.Http` and `System.Text.Json`, which supply the status codes, client and parser.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

A message handler is the transport boundary beneath HttpClient. A fake handler returns HttpResponseMessage deterministically. EnsureSuccessStatusCode throws for unsuccessful status; validate the body afterward.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Decode a successful offline response

A reserved invalid domain makes the fixture identity clear, while the custom handler prevents any actual connection.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using System.Globalization;
using System.Collections.Concurrent;
using System.Threading.Channels;
using System.Net;
using System.Net.Http;
using System.Text.RegularExpressions;
using System.Buffers;

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      using var client = new HttpClient(
          new FixtureHandler(HttpStatusCode.OK, "{\"count\":3}"));
      using var response =
          await client.GetAsync("https://example.invalid/count");
      response.EnsureSuccessStatusCode();
      using var json =
          JsonDocument.Parse(await response.Content.ReadAsStringAsync());
      Check(json.RootElement.GetProperty("count").GetInt32() == 3,
            "validated fixture response");
    }
    Console.WriteLine("csharp-039: passed");
    await Task.CompletedTask;
  }

  public sealed class FixtureHandler(HttpStatusCode status, string body)
      : HttpMessageHandler {
    protected override Task<HttpResponseMessage>
    SendAsync(HttpRequestMessage request, CancellationToken token) {
      token.ThrowIfCancellationRequested();
      return Task.FromResult(new HttpResponseMessage(
          status) { Content = new StringContent(body) });
    }
  }
}
```

**Observe:** The handler supplies count 3 without network access.

**Trace.** `HttpClient` passes the GET request to `FixtureHandler`, which returns status 200 with the body `{"count":3}`. `EnsureSuccessStatusCode` returns normally because 200 is a success code. `ReadAsStringAsync` reads the body, `JsonDocument.Parse` builds a document, and `GetProperty("count").GetInt32()` returns 3. Each `using` disposes its response or document at the end of the scope, in reverse order.

### Example B: Preserve unsuccessful status

Response arrival and application success are separate facts.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using System.Globalization;
using System.Collections.Concurrent;
using System.Threading.Channels;
using System.Net;
using System.Net.Http;
using System.Text.RegularExpressions;
using System.Buffers;

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      using var client = new HttpClient(
          new FixtureHandler(HttpStatusCode.ServiceUnavailable, "unavailable"));
      using var response =
          await client.GetAsync("https://example.invalid/count");
      bool rejected = false;
      try {
        response.EnsureSuccessStatusCode();
      } catch (HttpRequestException) {
        rejected = true;
      }
      Check(rejected, "503 is not success");
    }
    Console.WriteLine("csharp-039: passed");
    await Task.CompletedTask;
  }

  public sealed class FixtureHandler(HttpStatusCode status, string body)
      : HttpMessageHandler {
    protected override Task<HttpResponseMessage>
    SendAsync(HttpRequestMessage request, CancellationToken token) {
      token.ThrowIfCancellationRequested();
      return Task.FromResult(new HttpResponseMessage(
          status) { Content = new StringContent(body) });
    }
  }
}
```

**Observe:** 503 remains an observable failure rather than a default successful count.

**Trace.** This time the handler returns 503 with the plain text unavailable. The response arrives normally, so `GetAsync` does not throw. `EnsureSuccessStatusCode` does, raising `HttpRequestException` whose `StatusCode` is `ServiceUnavailable` and whose message reads: Response status code does not indicate success: 503 (Service Unavailable). The catch sets `rejected`, and the body is never parsed.

## Exercises

1. **Predict and explain.** Trace transport, status, decoding and schema validation boundaries.

2. **Guided modification.** Return valid JSON with a missing count property and classify the failure.

3. **Independent construction.** Write a client method accepting a supplied HttpClient and CancellationToken.

4. **Diagnose a defect.** Diagnose converting every non-2xx response into an empty success result.

5. **Boundary evidence.** Test malformed JSON and an unexpected count type.

6. **Transfer and justify.** Design a retry policy that distinguishes safe reads from writes with unknown outcomes.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A fake transport does not validate certificates or server availability. Do not retry all status codes blindly. Bound request and response lifetimes and redact credentials from diagnostic logs.

In task 4, an adapter that maps every non-2xx response to an empty success hides the 503 behind a count of 0. For task 2, valid JSON without count makes `GetProperty` throw `KeyNotFoundException`. For task 5, malformed text throws a `JsonException` subtype, and a count sent as the string 3 makes `GetInt32` throw `InvalidOperationException`.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Decode a successful offline response) before changing anything, and confirm its observation: The handler supplies count 3 without network access.
2. Compare Example B (Preserve unsuccessful status) with Example A and name the first line whose behavior differs. Its observation is: 503 remains an observable failure rather than a default successful count.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: A fake transport does not validate certificates or server availability.

## Self-check and next step

List the four boundaries a response crosses in Example A and say which call guards each one. Explain why the fake handler proves decoding but not certificate validation or server availability. For task 6, state which requests your policy retries automatically and why a POST with an unknown outcome needs an identity first.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The `HttpClient` guidance and the `System.Text.Json` articles explain message handlers, status checks and document parsing.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-039: HTTP clients, status contracts and offline transport tests.
Read courses/csharp/guides/csharp-039.md and courses/csharp/lessons/csharp-039.cs. Prerequisites: csharp-038.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-039_solution.cs and
courses/csharp/solutions/csharp-039_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
