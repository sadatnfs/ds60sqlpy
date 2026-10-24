# csharp-039: HTTP clients, status contracts and offline transport tests

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-038`

## Learning objectives

Write a client method accepting a supplied HttpClient and CancellationToken. Then design a retry policy that distinguishes safe reads from writes with unknown outcomes.

## Purpose and mental model

HTTP separates transport completion from application success. Receiving a response does not imply a 2xx status, and a 2xx response does not guarantee a valid application payload. Inspect status, bound the response, decode it and validate its schema. Cancellation should flow through the request and body processing.

HttpClient is intended for reuse under a deliberate lifetime policy. Repeatedly creating clients for every request can waste connection resources. The classroom uses a custom HttpMessageHandler, so it exercises real request/response APIs without contacting a network. This proves application handling, not DNS, TLS or remote availability.

## Vocabulary and concepts

**Transport:** The mechanism carrying a request and response.

**Status code:** The protocol-level response category.

**Test double:** A controlled dependency used to exercise a consumer contract.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

A message handler is the transport boundary beneath HttpClient. A fake handler returns HttpResponseMessage deterministically. EnsureSuccessStatusCode throws for unsuccessful status; validate the body afterward.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

internal static class Program
{
    private static void Check(bool condition, string reason)
    {
        if (!condition) throw new InvalidOperationException(reason);
    }

    private static async Task Main()
    {
        {
            using var client = new HttpClient(new FixtureHandler(HttpStatusCode.OK, "{\"count\":3}"));
            using var response = await client.GetAsync("https://example.invalid/count");
            response.EnsureSuccessStatusCode();
            using var json = JsonDocument.Parse(await response.Content.ReadAsStringAsync());
            Check(json.RootElement.GetProperty("count").GetInt32() == 3, "validated fixture response");
        }
        Console.WriteLine("csharp-039: passed");
        await Task.CompletedTask;
    }

    public sealed class FixtureHandler(HttpStatusCode status, string body) : HttpMessageHandler { protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken token) { token.ThrowIfCancellationRequested(); return Task.FromResult(new HttpResponseMessage(status) { Content = new StringContent(body) }); } }
}
```

**Observe:** The handler supplies count 3 without network access.

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

internal static class Program
{
    private static void Check(bool condition, string reason)
    {
        if (!condition) throw new InvalidOperationException(reason);
    }

    private static async Task Main()
    {
        {
            using var client = new HttpClient(new FixtureHandler(HttpStatusCode.ServiceUnavailable, "unavailable"));
            using var response = await client.GetAsync("https://example.invalid/count");
            bool rejected = false;
            try { response.EnsureSuccessStatusCode(); } catch (HttpRequestException) { rejected = true; }
            Check(rejected, "503 is not success");
        }
        Console.WriteLine("csharp-039: passed");
        await Task.CompletedTask;
    }

    public sealed class FixtureHandler(HttpStatusCode status, string body) : HttpMessageHandler { protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken token) { token.ThrowIfCancellationRequested(); return Task.FromResult(new HttpResponseMessage(status) { Content = new StringContent(body) }); } }
}
```

**Observe:** 503 remains an observable failure rather than a default successful count.

## Exercises

1. **Predict and explain.** Trace transport, status, decoding and schema validation boundaries.

2. **Guided modification.** Return valid JSON with a missing count property and classify the failure.

3. **Independent construction.** Write a client method accepting a supplied HttpClient and CancellationToken.

4. **Diagnose a defect.** Diagnose converting every non-2xx response into an empty success result.

5. **Boundary evidence.** Test malformed JSON and an unexpected count type.

6. **Transfer and justify.** Design a retry policy that distinguishes safe reads from writes with unknown outcomes.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A fake transport does not validate certificates or server availability. Do not retry all status codes blindly. Bound request and response lifetimes and redact credentials from diagnostic logs.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Transport, Status code, Test double without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
