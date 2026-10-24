# csharp-025: Files, paths and local data ownership

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-024`

## Learning objectives

Build a temporary-file round trip for a small inventory report. Then explain what must change to make a persistent report update crash-recoverable.

## Purpose and mental model

A path is a name in a filesystem, not the data itself. Relative paths are interpreted against a working directory, which may differ between an editor, test runner and container. Construct owned paths explicitly and avoid assuming the repository is writable from learner code. The classroom retains saved pads separately from temporary worker files.

Writing a file creates a side effect with a lifetime. Tiny examples should create a unique temporary directory, operate only inside it, and remove it in finally. Production persistence requires more decisions: atomic replacement, backups, permissions and recovery after interruption. An in-memory assertion proves content logic but cannot establish durable storage behavior after a crash.

## Vocabulary and concepts

**Working directory:** The base for resolving relative paths.

**Encoding:** The rule converting text to bytes.

**Owned temporary directory:** A uniquely created area this operation may clean up.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`Path.Combine` constructs a platform path. `File.WriteAllText` encodes text; `ReadAllText` decodes it. A try/finally protects cleanup, while recursive removal is safe only for a directory this operation uniquely owns.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Round-trip an owned text file

The random name prevents collisions while the observable content remains deterministic.

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
            string root = Path.Combine(Path.GetTempPath(), "lesson-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(root);
            try { string path = Path.Combine(root, "note.txt"); File.WriteAllText(path, "café", Encoding.UTF8); Check(File.ReadAllText(path, Encoding.UTF8) == "café", "UTF-8 round trip"); }
            finally { Directory.Delete(root, true); }
            Check(!Directory.Exists(root), "owned cleanup");
        }
        Console.WriteLine("csharp-025: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** The Unicode text round-trips and the owned directory is removed.

### Example B: Separate logical and filesystem names

These lexical checks teach path structure; they are not a complete traversal or symlink security boundary.

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
            string fileName = "report.csv";
            Check(Path.GetFileName(fileName) == fileName, "simple leaf name");
            Check(Path.GetFileName("nested/report.csv") != "nested/report.csv", "nested name is not a leaf");
            Check(Path.GetExtension(fileName) == ".csv", "extension classification");
        }
        Console.WriteLine("csharp-025: passed");
        await Task.CompletedTask;
    }


}
```

**Observe:** A simple leaf name and a nested path are recognized as different shapes.

## Exercises

1. **Predict and explain.** Trace directory creation, write, read and cleanup ownership.

2. **Guided modification.** Write two lines and preserve their explicit newline policy.

3. **Independent construction.** Build a temporary-file round trip for a small inventory report.

4. **Diagnose a defect.** Diagnose resolving a relative path against an unexpected working directory.

5. **Boundary evidence.** Test empty content and non-ASCII text.

6. **Transfer and justify.** Explain what must change to make a persistent report update crash-recoverable.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Path normalization alone does not solve symlink attacks or concurrent replacement. Do not delete arbitrary user-provided directories. Worker temporary files are not the durable learner progress store.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Working directory, Encoding, Owned temporary directory without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-025: Files, paths and local data ownership.
Read courses/csharp/guides/csharp-025.md and courses/csharp/lessons/csharp-025.cs. Prerequisites: csharp-024.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-025_solution.cs and
courses/csharp/solutions/csharp-025_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
