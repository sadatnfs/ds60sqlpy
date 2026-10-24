# csharp-041: API design and the prepared ASP.NET project

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-040`

## Learning objectives

Run the separately prepared ApiLab project and inspect GET and POST responses. Then design idempotent update behavior and explain how duplicate creation differs.

## Purpose and mental model

An API exposes a contract over a transport. A useful endpoint specifies resource identity, accepted input, status outcomes and response schema. Domain validation must run before a successful status is returned. HTTP method names also communicate semantics: a safe read should not unexpectedly mutate server state.

The browser pad exercises a pure endpoint decision kernel. The checked-in ApiLab fixture supplies a real ASP.NET Core minimal API project using only the shared framework, with an in-memory catalog and explicit validation. It is a separately prepared multi-file workflow, not source accepted by the single Program.cs pad. Running its web host is deliberate and should bind loopback for local learning.

## Vocabulary and concepts

**Endpoint:** A named request contract exposed by a service.

**Status mapping:** Translation of a domain outcome into HTTP semantics.

**Idempotency:** Repeating a request has the same intended effect as one request.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

Continue with [ApiLab preparation and commands](../fixtures/ApiLab/README.md). Its complete project is separate from the classroom pad and needs a prepared .NET 10 SDK.

## Syntax anatomy and execution trace

A pure mapping can return a status and body record. In the external project, MapGet and MapPost connect routes to handlers. Results.Ok, BadRequest and NotFound make transport outcomes explicit.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

internal static class Program
{
    private static void Check(bool condition, string reason)
    {
        if (!condition) throw new InvalidOperationException(reason);
    }

    private static async Task Main()
    {
        {
            var result = ValidateCreate("pear", 3);
            Check(result.Status == 201 && result.Message == "accepted", "created contract");
        }
        Console.WriteLine("csharp-041: passed");
        await Task.CompletedTask;
    }

    public record ApiDecision(int Status, string Message);
    public static ApiDecision ValidateCreate(string name, int quantity) => string.IsNullOrWhiteSpace(name) || quantity < 0 ? new(400, "invalid") : new(201, "accepted");
}
```

**Observe:** Valid input maps to the created outcome.

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

internal static class Program
{
    private static void Check(bool condition, string reason)
    {
        if (!condition) throw new InvalidOperationException(reason);
    }

    private static async Task Main()
    {
        {
            Check(ValidateCreate("", 3).Status == 400, "empty identity");
            Check(ValidateCreate("pear", -1).Status == 400, "negative quantity");
        }
        Console.WriteLine("csharp-041: passed");
        await Task.CompletedTask;
    }

    public record ApiDecision(int Status, string Message);
    public static ApiDecision ValidateCreate(string name, int quantity) => string.IsNullOrWhiteSpace(name) || quantity < 0 ? new(400, "invalid") : new(201, "accepted");
}
```

**Observe:** Invalid requests produce 400 decisions.

## Exercises

1. **Predict and explain.** Describe the valid request and its status/body contract.

2. **Guided modification.** Add a maximum quantity rule and document its rejection.

3. **Independent construction.** Run the separately prepared ApiLab project and inspect GET and POST responses.

4. **Diagnose a defect.** Diagnose returning 200 before input validation finishes.

5. **Boundary evidence.** Test missing identity, zero quantity and unknown resource lookup.

6. **Transfer and justify.** Design idempotent update behavior and explain how duplicate creation differs.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

An offline kernel test does not prove endpoint routing, serialization or host startup. The external project intentionally uses in-memory state, so restarting loses its sample inventory. It is not a persistence claim.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Endpoint, Status mapping, Idempotency without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
