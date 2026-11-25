# csharp-041: API design and the prepared ASP.NET project

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-040`

## Learning objectives

Design an HTTP API contract and run it in the prepared ASP.NET project with real responses. The central exercise is task 3: Run the separately prepared ApiLab project and inspect GET and POST responses.

## Purpose and mental model

An API exposes a contract over a transport. A useful endpoint specifies resource identity, accepted input, status outcomes and response schema. Domain validation must run before a successful status is returned. HTTP method names also communicate semantics: a safe read should not unexpectedly mutate server state.

The browser pad exercises a pure endpoint decision kernel. The checked-in ApiLab fixture supplies a real ASP.NET Core minimal API project using only the shared framework, with an in-memory catalog and explicit validation. It is a separately prepared multi-file workflow, not source accepted by the single Program.cs pad. Running its web host is deliberate and should bind loopback for local learning.

## Vocabulary and concepts

**Endpoint:** A named request contract exposed by a service.

**Status mapping:** Translation of a domain outcome into HTTP semantics.

**Idempotency:** Repeating a request has the same intended effect as one request.

## How to run this lesson

`ApiDecision` and `ValidateCreate` sit after `Main`, so the portable pad tests the decision logic without starting a web host. The note below links to ApiLab, a separate ASP.NET project with its own preparation steps; it maps routes with `MapGet` and `MapPost` and keeps inventory in memory, so restarting it resets the sample data.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).

Continue with [ApiLab preparation and commands](../fixtures/ApiLab/README.md). Its complete project is separate from the classroom pad and needs a prepared .NET 10 SDK.

## Syntax anatomy and execution trace

A pure mapping can return a status and body record. In the external project, MapGet and MapPost connect routes to handlers. Results.Ok, BadRequest and NotFound make transport outcomes explicit.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Map a valid request

The kernel isolates validation and status selection from host configuration.

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
      var result = ValidateCreate("pear", 3);
      Check(result.Status == 201 && result.Message == "accepted",
            "created contract");
    }
    Console.WriteLine("csharp-041: passed");
    await Task.CompletedTask;
  }

  public record ApiDecision(int Status, string Message);
  public static ApiDecision ValidateCreate(string name, int quantity) =>
      string.IsNullOrWhiteSpace(name) || quantity < 0 ? new(400, "invalid")
                                                      : new(201, "accepted");
}
```

**Observe:** Valid input maps to the created outcome.

**Trace.** `ValidateCreate("pear", 3)` evaluates the guard: the name is not blank and the quantity is not negative, so the conditional takes its second branch and returns `new(201, "accepted")`. The record exposes `Status` 201 and `Message` accepted, and the check reads both fields. Record value equality would also make it equal to a freshly built `ApiDecision(201, "accepted")`.

### Example B: Reject before claiming success

The response category is part of the public contract and must not disagree with domain acceptance.

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
      Check(ValidateCreate("", 3).Status == 400, "empty identity");
      Check(ValidateCreate("pear", -1).Status == 400, "negative quantity");
    }
    Console.WriteLine("csharp-041: passed");
    await Task.CompletedTask;
  }

  public record ApiDecision(int Status, string Message);
  public static ApiDecision ValidateCreate(string name, int quantity) =>
      string.IsNullOrWhiteSpace(name) || quantity < 0 ? new(400, "invalid")
                                                      : new(201, "accepted");
}
```

**Observe:** Invalid requests produce 400 decisions.

**Trace.** An empty name makes `string.IsNullOrWhiteSpace` true, and the `||` short-circuits straight to the 400 decision. With pear and -1, the name test is false but `quantity < 0` is true, so the result is again 400 with invalid. Neither call reaches the 201 branch, which is the property the check protects: rejection is decided before success is claimed.

## Exercises

1. **Predict and explain.** Describe the valid request and its status/body contract.

2. **Guided modification.** Add a maximum quantity rule and document its rejection.

3. **Independent construction.** Run the separately prepared ApiLab project and inspect GET and POST responses.

4. **Diagnose a defect.** Diagnose returning 200 before input validation finishes.

5. **Boundary evidence.** Test missing identity, zero quantity and unknown resource lookup.

6. **Transfer and justify.** Design idempotent update behavior and explain how duplicate creation differs.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

An offline kernel test does not prove endpoint routing, serialization or host startup. The external project intentionally uses in-memory state, so restarting loses its sample inventory. It is not a persistence claim.

For task 5, quantity 0 is accepted under the current rule, because the guard rejects only negative values; if zero should fail, change the comparison and add a test that pins it. A null name also takes the 400 branch, although the compiler warns about passing null to a non-nullable string. For task 4, compute the decision first and build the response from it.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Map a valid request) before changing anything, and confirm its observation: Valid input maps to the created outcome.
2. Compare Example B (Reject before claiming success) with Example A and name the first line whose behavior differs. Its observation is: Invalid requests produce 400 decisions.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: An offline kernel test does not prove endpoint routing, serialization or host startup.

## Self-check and next step

Write the status and message for pear with 0, for a name of spaces with 5, and for pear with -2. Explain what the kernel test proves and what only a running ApiLab request can prove. For task 6, describe what a repeated PUT with the same body returns and how a repeated create differs.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The C# guide covers records and conditional expressions; the ApiLab README covers the ASP.NET routing it uses.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-041: API design and the prepared ASP.NET project.
Read courses/csharp/guides/csharp-041.md and courses/csharp/lessons/csharp-041.cs. Prerequisites: csharp-040.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-041_solution.cs and
courses/csharp/solutions/csharp-041_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
