# csharp-025: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-025_solution.cs](csharp-025_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Round-trip an owned text file:** The random name prevents collisions while the observable content remains deterministic. The Unicode text round-trips and the owned directory is removed.

**Separate logical and filesystem names:** These lexical checks teach path structure; they are not a complete traversal or symlink security boundary. A simple leaf name and a nested path are recognized as different shapes.

## Task answers

### Task 1: Predict and explain

Trace directory creation, write, read and cleanup ownership.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The random name prevents collisions while the observable content remains deterministic. The Unicode text round-trips and the owned directory is removed.

### Task 2: Guided modification

Write two lines and preserve their explicit newline policy.

No separate reference answer has been written for this task. Start from Example B: These lexical checks teach path structure; they are not a complete traversal or symlink security boundary. A simple leaf name and a nested path are recognized as different shapes.

### Task 3: Independent construction

Build a temporary-file round trip for a small inventory report.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
string name = "inventory-" + Guid.NewGuid().ToString("N");
string folder = Path.Combine(Path.GetTempPath(), name);
Directory.CreateDirectory(folder);
try {
  string path = Path.Combine(folder, "report.txt");
  string report = "pear: 3\napple: 5";
  File.WriteAllText(path, report, Encoding.UTF8);
  Check(File.ReadAllText(path, Encoding.UTF8) == report, "round trip");
} finally {
  Directory.Delete(folder, true);
}
Check(!Directory.Exists(folder), "temporary folder removed");
```

**Observe:** The report reads back unchanged and the temporary folder is gone afterward.

A unique folder under the temp path is owned by this code alone, and finally removes it whether or not the check passes.

### Task 4: Diagnose a defect

Diagnose resolving a relative path against an unexpected working directory.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Path normalization alone does not solve symlink attacks or concurrent replacement. Do not delete arbitrary user-provided directories. Worker temporary files are not the durable learner progress store.

### Task 5: Boundary evidence

Test empty content and non-ASCII text.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Round-trip an owned text file) and Example B (Separate logical and filesystem names).

### Task 6: Transfer and justify

Explain what must change to make a persistent report update crash-recoverable.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Working directory**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A path is a name in a filesystem, not the data itself. Relative paths are interpreted against a working directory, which may differ between an editor, test runner and container. Construct owned paths explicitly and avoid assuming the repository is writable from learner code. The classroom retains saved pads separately from temporary worker files.

Writing a file creates a side effect with a lifetime. Tiny examples should create a unique temporary directory, operate only inside it, and remove it in finally. Production persistence requires more decisions: atomic replacement, backups, permissions and recovery after interruption. An in-memory assertion proves content logic but cannot establish durable storage behavior after a crash.

`Path.Combine` constructs a platform path. `File.WriteAllText` encodes text; `ReadAllText` decodes it. A try/finally protects cleanup, while recursive removal is safe only for a directory this operation uniquely owns.

Path normalization alone does not solve symlink attacks or concurrent replacement. Do not delete arbitrary user-provided directories. Worker temporary files are not the durable learner progress store.

## Review before continuing

Run the reference and confirm that it prints `csharp-025: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
