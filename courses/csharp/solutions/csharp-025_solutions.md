# csharp-025: explanation and comparison

Reference program: [csharp-025_solution.cs](csharp-025_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Round-trip an owned text file:** The random name prevents collisions while the observable content remains deterministic. `new UTF8Encoding(false)` writes UTF-8 without a byte order mark: `é` takes two bytes, so `café` is five bytes. `Encoding.UTF8` would prepend the three-byte BOM EF BB BF and make the file eight bytes long. The file holds exactly five bytes, the Unicode text round-trips and the owned directory is removed.

**Separate logical and filesystem names:** These lexical checks teach path structure; they are not a complete traversal or symlink security boundary. A simple leaf name and a nested path are recognized as different shapes.

## Task answers

### Task 1: Predict and explain

Trace directory creation, write, read and cleanup ownership.

**Written answer.** Example A builds a unique directory name under `Path.GetTempPath()` and creates it, so this run owns that directory and nothing else. Inside the try it writes `note.txt` with UTF-8 without a BOM, checks the file holds five bytes and reads the same text back. The finally block deletes the directory recursively whether the checks passed or threw, and the final check confirms it no longer exists.

**Why it is correct.** The GUID makes collisions with other runs practically impossible, which is what makes recursive deletion safe: the operation removes only what it created. Placing the cleanup in finally ties it to leaving the try block on any path.

**Plausible wrong approach.** Deleting the directory after the try instead of in finally leaves it behind whenever a check throws. Using a fixed name such as `lesson` lets two concurrent runs delete each other's files.

**How to verify.** Temporarily make the round-trip check fail and confirm the program stops but `Directory.Exists(root)` is false afterwards. Print `root` once to see that each run gets a different name.

### Task 2: Guided modification

Write two lines and preserve their explicit newline policy.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
string id = Guid.NewGuid().ToString("N");
string folder = Path.Combine(Path.GetTempPath(), "lines-" + id);
Directory.CreateDirectory(folder);
try {
  string path = Path.Combine(folder, "lines.txt");
  string text = "first\nsecond\n";
  File.WriteAllText(path, text, new UTF8Encoding(false));
  Check(File.ReadAllBytes(path).Length == 13, "13 bytes with two LF");
  string read = File.ReadAllText(path);
  Check(read == text && !read.Contains('\r'), "LF policy preserved");
  var lines = File.ReadAllLines(path);
  Check(lines.Length == 2 && lines[1] == "second", "two lines");
} finally {
  Directory.Delete(folder, true);
}
```

**Observe:** The file holds 13 bytes, first, a line feed, second and a final line feed, with no carriage returns.

This task builds on Example A, the file round trip. The policy is LF line endings with a final newline, written explicitly as `\n` instead of `Environment.NewLine`, so the bytes are the same on Linux and Windows. The expected 13 is 5 + 1 + 6 + 1, and reading the text back unchanged shows nothing translated the line endings.

**Plausible wrong approach.** `File.WriteAllLines(path, new[] { "first", "second" })` uses `Environment.NewLine`, which is CRLF on Windows. The same program would then write 15 bytes there, and a byte-level comparison with a Linux run fails.

**How to verify.** Replace the text with `string.Join(Environment.NewLine, "first", "second") + Environment.NewLine` and compare the byte count on Linux (13) with Windows (15). The explicit `\n` version gives 13 on both.

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

**Written answer.** `File.ReadAllText("data/input.csv")` resolves the relative path against `Environment.CurrentDirectory`, the process working directory, not against the source file or the folder of the compiled program. Run from the project folder it finds the file; run from `bin/Debug/net10.0`, a test runner or a container whose working directory is elsewhere, it throws `FileNotFoundException` or reads a different file. Print `Path.GetFullPath("data/input.csv")` to see the real target, then build paths from an explicit base such as a command-line argument or `AppContext.BaseDirectory` with `Path.Combine`.

**Why it is correct.** The operating system interprets every relative path against the current directory of the process, which the launcher chooses. `Path.GetFullPath` applies the same rule, so it shows exactly which file the program would open.

**Plausible wrong approach.** Copying the data file into every possible working directory makes the symptom disappear on one machine without fixing the assumption. Hardcoding an absolute path from your own computer breaks on every other machine and in the worker.

**How to verify.** Check `Path.GetFullPath("data/input.csv") == Path.Combine(Environment.CurrentDirectory, "data", "input.csv")`. Then set `Environment.CurrentDirectory` to a temporary directory and confirm the same relative name now points inside it.

### Task 5: Boundary evidence

Test empty content and non-ASCII text.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
string id = Guid.NewGuid().ToString("N");
string folder = Path.Combine(Path.GetTempPath(), "text-" + id);
Directory.CreateDirectory(folder);
var utf8 = new UTF8Encoding(false);
try {
  string empty = Path.Combine(folder, "empty.txt");
  File.WriteAllText(empty, "", utf8);
  Check(new FileInfo(empty).Length == 0, "empty file has no bytes");
  Check(File.ReadAllText(empty, utf8) == "", "empty round trip");
  string named = Path.Combine(folder, "names.txt");
  string text = "Zoë, Łódź, 東京";
  File.WriteAllText(named, text, utf8);
  Check(text.Length == 13, "13 UTF-16 code units");
  Check(new FileInfo(named).Length == 21, "21 UTF-8 bytes");
  Check(File.ReadAllText(named, utf8) == text, "non-ASCII round trip");
} finally {
  Directory.Delete(folder, true);
}
```

**Observe:** The empty file has 0 bytes and reads back as empty; the non-ASCII text is 13 code units, 21 bytes and round-trips exactly.

An empty write still creates the file, and without a BOM it contains no bytes at all. For the second file the expected sizes were counted independently: `Zoë` is 4 bytes, `Łódź` is 7, `東京` is 6 and the two `, ` separators add 4, giving 21. The round trip proves the same encoding was used for writing and reading.

**Plausible wrong approach.** Writing with `Encoding.UTF8` makes the empty file 3 bytes long, because it starts with a byte order mark even when there is no text. Reading the second file with `Encoding.Latin1` returns mojibake such as `ZoÃ«` instead of `Zoë`.

**How to verify.** Write the empty file with `Encoding.UTF8` and check its length is 3. Then read the names file with `Encoding.Latin1` and confirm the comparison with `text` fails.

### Task 6: Transfer and justify

Explain what must change to make a persistent report update crash-recoverable.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Mechanism and diagnostic reasoning

A path is a name in a filesystem, not the data itself. Relative paths are interpreted against a working directory, which may differ between an editor, test runner and container. Construct owned paths explicitly and avoid assuming the repository is writable from learner code. The classroom retains saved pads separately from temporary worker files.

Writing a file creates a side effect with a lifetime. Tiny examples should create a unique temporary directory, operate only inside it, and remove it in finally. Production persistence requires more decisions: atomic replacement, backups, permissions and recovery after interruption. An in-memory assertion proves content logic but cannot establish durable storage behavior after a crash.

`Path.Combine` constructs a platform path. `File.WriteAllText` encodes text; `ReadAllText` decodes it. A try/finally protects cleanup, while recursive removal is safe only for a directory this operation uniquely owns.

Path normalization alone does not solve symlink attacks or concurrent replacement. Do not delete arbitrary user-provided directories. Worker temporary files are not the durable learner progress store.

## Review before continuing

Run the reference and confirm it prints `csharp-025: passed`, then rerun the guide's counterexample.
