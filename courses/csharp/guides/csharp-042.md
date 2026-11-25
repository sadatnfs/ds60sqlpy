# csharp-042: Security boundaries, secrets and untrusted data

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-041`

## Learning objectives

Apply allowlists and redaction at trust boundaries so errors stay useful without leaking secrets. The central exercise is task 3: Design an allowlist of fields safe to include in an import error.

## Purpose and mental model

A security boundary is where less-trusted input receives authority: a path reaches a filesystem, text becomes SQL, or a request chooses a resource. Validation must match that destination. A string being valid JSON does not make it a safe file path or a safe authorization decision. Keep data and instructions separate.

Authentication answers who the caller is; authorization answers what that caller may do to this resource. Neither should depend on a client-supplied role string. Secrets belong in a deliberate secret source, not committed examples or logs. The offline fixture teaches an explicit allowlist policy without pretending to implement a complete identity system.

## Vocabulary and concepts

**Authentication:** Establishing caller identity.

**Authorization:** Deciding permitted actions for an established identity.

**Default deny:** Rejecting access unless an explicit policy permits it.

## How to run this lesson

Both examples are pure policy code with no network, file or credential store. The permission set uses `StringComparer.Ordinal`, so letter case is part of an action's identity. The value synthetic-secret is a made-up placeholder; never paste a real token into the pad, a test or a tutor prompt.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

Use exact identity comparisons and explicit permission mappings. A default-deny decision rejects absent policy entries. Parsing and authorization should remain separate methods with separately testable outcomes.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Evaluate an explicit permission policy

Absence of an entry does not become implicit permission.

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
      var rights =
          new HashSet<string>(StringComparer.Ordinal) { "report:read" };
      Check(rights.Contains("report:read"), "allowed action");
      Check(!rights.Contains("report:delete"), "unlisted action denied");
    }
    Console.WriteLine("csharp-042: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** Read is allowed and delete is denied.

**Trace.** `rights` holds the single string report:read, compared ordinally. `Contains("report:read")` finds that exact entry and returns true. `Contains("report:delete")` finds nothing, and because the code treats absence as refusal, delete is denied without any rule having to mention it. Report:Read with capital letters would also return false under the ordinal comparer, so case variants grant nothing.

### Example B: Redact before producing diagnostics

A minimal example makes the diagnostic contract explicit; production structured logging should use an allowlist of safe fields.

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
      string Redact(string key, string value) =>
          key.Equals("token", StringComparison.OrdinalIgnoreCase) ? "[redacted]"
                                                                  : value;
      Check(Redact("TOKEN", "synthetic-secret") == "[redacted]",
            "secret omitted");
      Check(Redact("status", "failed") == "failed",
            "useful nonsecret context retained");
    }
    Console.WriteLine("csharp-042: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The token is replaced while a status remains visible.

**Trace.** `Redact` compares the key with token using `OrdinalIgnoreCase`. TOKEN matches, so the function returns the marker [redacted] instead of the secret. The key status does not match, so its value failed passes through unchanged and the log remains useful. The comparison is exact equality, which matters for keys that merely contain the word token.

## Exercises

1. **Predict and explain.** Separate identity from permission in a request trace.

2. **Guided modification.** Add a second permitted read action without granting write access.

3. **Independent construction.** Design an allowlist of fields safe to include in an import error.

4. **Diagnose a defect.** Diagnose trusting an isAdmin value supplied in a request body.

5. **Boundary evidence.** Test missing permission and case variants according to the documented identity policy.

6. **Transfer and justify.** Describe authorization checks for a resource owned by another user and the evidence each check needs.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

This fixture is policy reasoning, not a complete authentication system. Do not invent cryptography or store passwords in reversible form. Parameter binding and destination-specific APIs are preferable to manual escaping.

Task 4 is the classic bypass: a handler that reads `isAdmin` from the request body lets the caller grant itself rights, so derive roles from the authenticated identity instead. For task 3, notice that `Redact("access_token", value)` returns the secret unchanged, since only the exact key token is caught; an allowlist of safe fields avoids that denylist gap.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Evaluate an explicit permission policy) before changing anything, and confirm its observation: Read is allowed and delete is denied.
2. Compare Example B (Redact before producing diagnostics) with Example A and name the first line whose behavior differs. Its observation is: The token is replaced while a status remains visible.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: This fixture is policy reasoning, not a complete authentication system.

## Self-check and next step

Explain why absence from `rights` must mean denial rather than permission. Predict what `Redact` returns for the keys Token, auth and access_token. For task 6, list the checks for reading another user's resource: who the caller is, who owns the resource, which permission applies, and which log entry records the decision.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The .NET security articles and the C# guide's string comparison topics explain ordinal comparison, secret handling and validation boundaries.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-042: Security boundaries, secrets and untrusted data.
Read courses/csharp/guides/csharp-042.md and courses/csharp/lessons/csharp-042.cs. Prerequisites: csharp-041.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-042_solution.cs and
courses/csharp/solutions/csharp-042_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
