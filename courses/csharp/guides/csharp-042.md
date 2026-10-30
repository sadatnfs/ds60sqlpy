# csharp-042: Security boundaries, secrets and untrusted data

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `csharp-041`

## Learning objectives

Design an allowlist of fields safe to include in an import error. Then describe authorization checks for a resource owned by another user and the evidence each check needs.

## Purpose and mental model

A security boundary is where less-trusted input receives authority: a path reaches a filesystem, text becomes SQL, or a request chooses a resource. Validation must match that destination. A string being valid JSON does not make it a safe file path or a safe authorization decision. Keep data and instructions separate.

Authentication answers who the caller is; authorization answers what that caller may do to this resource. Neither should depend on a client-supplied role string. Secrets belong in a deliberate secret source, not committed examples or logs. The offline fixture teaches an explicit allowlist policy without pretending to implement a complete identity system.

## Vocabulary and concepts

**Authentication:** Establishing caller identity.

**Authorization:** Deciding permitted actions for an established identity.

**Default deny:** Rejecting access unless an explicit policy permits it.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

Use exact identity comparisons and explicit permission mappings. A default-deny decision rejects absent policy entries. Parsing and authorization should remain separate methods with separately testable outcomes.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

## Exercises

1. **Predict and explain.** Separate identity from permission in a request trace.

2. **Guided modification.** Add a second permitted read action without granting write access.

3. **Independent construction.** Design an allowlist of fields safe to include in an import error.

4. **Diagnose a defect.** Diagnose trusting an isAdmin value supplied in a request body.

5. **Boundary evidence.** Test missing permission and case variants according to the documented identity policy.

6. **Transfer and justify.** Describe authorization checks for a resource owned by another user and the evidence each check needs.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

This fixture is policy reasoning, not a complete authentication system. Do not invent cryptography or store passwords in reversible form. Parameter binding and destination-specific APIs are preferable to manual escaping.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Authentication, Authorization, Default deny without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
