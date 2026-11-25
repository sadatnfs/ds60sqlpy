# csharp-025: Files, paths and local data ownership

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-024`

## Learning objectives

Read and write files with explicit encodings inside an owned temporary folder that is always cleaned up. The central exercise is task 3: Build a temporary-file round trip for a small inventory report.

## Purpose and mental model

A path is a name in a filesystem, not the data itself. Relative paths are interpreted against a working directory, which may differ between an editor, test runner and container. Construct owned paths explicitly and avoid assuming the repository is writable from learner code. The classroom retains saved pads separately from temporary worker files.

Writing a file creates a side effect with a lifetime. Tiny examples should create a unique temporary directory, operate only inside it, and remove it in finally. Production persistence requires more decisions: atomic replacement, backups, permissions and recovery after interruption. An in-memory assertion proves content logic but cannot establish durable storage behavior after a crash.

## Vocabulary and concepts

**Working directory:** The base for resolving relative paths.

**Encoding:** The rule converting text to bytes.

**Owned temporary directory:** A uniquely created area this operation may clean up.

## How to run this lesson

Example A creates a fresh directory under the system temporary folder with a random name and deletes it in `finally`, so repeated runs never collide or leave files behind. A relative path such as note.txt resolves against `Environment.CurrentDirectory`, the process working directory, not against the folder that holds Program.cs.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`Path.Combine` constructs a platform path. `File.WriteAllText` encodes text; `ReadAllText` decodes it. A try/finally protects cleanup, while recursive removal is safe only for a directory this operation uniquely owns.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Round-trip an owned text file

The random name prevents collisions while the observable content remains deterministic. `new UTF8Encoding(false)` writes UTF-8 without a byte order mark: `é` takes two bytes, so `café` is five bytes. `Encoding.UTF8` would prepend the three-byte BOM EF BB BF and make the file eight bytes long.

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
      string root = Path.Combine(Path.GetTempPath(),
                                 "lesson-" + Guid.NewGuid().ToString("N"));
      Directory.CreateDirectory(root);
      var utf8 = new UTF8Encoding(false);
      try {
        string path = Path.Combine(root, "note.txt");
        File.WriteAllText(path, "café", utf8);
        Check(File.ReadAllBytes(path).Length == 5, "five UTF-8 bytes, no BOM");
        Check(File.ReadAllText(path, utf8) == "café", "UTF-8 round trip");
      } finally {
        Directory.Delete(root, true);
      }
      Check(!Directory.Exists(root), "owned cleanup");
    }
    Console.WriteLine("csharp-025: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The file holds exactly five bytes, the Unicode text round-trips and the owned directory is removed.

**Trace.** `root` combines the temporary folder with lesson- and a random hexadecimal suffix, and `CreateDirectory` makes it. `WriteAllText` encodes café with the no-BOM UTF-8 encoding: four ASCII-range bytes would be four, but é needs two, so the file holds five bytes. `ReadAllText` with the same encoding decodes café again. `finally` deletes the directory recursively, which is safe only because this run created it.

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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      string fileName = "report.csv";
      Check(Path.GetFileName(fileName) == fileName, "simple leaf name");
      Check(Path.GetFileName("nested/report.csv") != "nested/report.csv",
            "nested name is not a leaf");
      Check(Path.GetExtension(fileName) == ".csv", "extension classification");
    }
    Console.WriteLine("csharp-025: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** A simple leaf name and a nested path are recognized as different shapes.

**Trace.** `Path.GetFileName("report.csv")` returns the whole string, because it has no directory part. For nested/report.csv the method returns only report.csv, which differs from the input, so the second check passes. `GetExtension` returns .csv including the dot. These calls inspect the text of a path; none of them touches the disk or checks that the file exists.

## Exercises

1. **Predict and explain.** Trace directory creation, write, read and cleanup ownership.

2. **Guided modification.** Write two lines and preserve their explicit newline policy.

3. **Independent construction.** Build a temporary-file round trip for a small inventory report.

4. **Diagnose a defect.** Diagnose resolving a relative path against an unexpected working directory.

5. **Boundary evidence.** Test empty content and non-ASCII text.

6. **Transfer and justify.** Explain what must change to make a persistent report update crash-recoverable.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Path normalization alone does not solve symlink attacks or concurrent replacement. Do not delete arbitrary user-provided directories. Worker temporary files are not the durable learner progress store.

For task 4, remember that `Path.Combine(root, "/etc/y")` returns /etc/y: a rooted second argument discards the first, so combining a base folder with user text is not containment. For task 5, writing empty text produces a zero-byte file, while `GetExtension` on a name with two dots, such as a.tar.gz, returns only .gz.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Round-trip an owned text file) before changing anything, and confirm its observation: The file holds exactly five bytes, the Unicode text round-trips and the owned directory is removed.
2. Compare Example B (Separate logical and filesystem names) with Example A and name the first line whose behavior differs. Its observation is: A simple leaf name and a nested path are recognized as different shapes.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Path normalization alone does not solve symlink attacks or concurrent replacement.

## Self-check and next step

Predict the byte count of the file after writing café with `Encoding.UTF8` instead of the no-BOM encoding, and explain the difference. Say which directories your code may delete and why. For task 6, describe a write to a temporary file followed by a replace, and what a crash leaves behind at each step.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The .NET file and stream I/O articles, along with the `Path` class reference, cover path composition, encodings and directory operations.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
