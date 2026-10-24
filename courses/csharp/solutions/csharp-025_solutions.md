# csharp-025: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-025_solution.cs](csharp-025_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Round-trip an owned text file:** The random name prevents collisions while the observable content remains deterministic. The Unicode text round-trips and the owned directory is removed.

**Separate logical and filesystem names:** These lexical checks teach path structure; they are not a complete traversal or symlink security boundary. A simple leaf name and a nested path are recognized as different shapes.

## Reason through the six tasks

1. **Predict and explain.** Trace directory creation, write, read and cleanup ownership.

2. **Guided modification.** Write two lines and preserve their explicit newline policy.

3. **Independent construction.** Build a temporary-file round trip for a small inventory report.

4. **Diagnose a defect.** Diagnose resolving a relative path against an unexpected working directory.

5. **Boundary evidence.** Test empty content and non-ASCII text.

6. **Transfer and justify.** Explain what must change to make a persistent report update crash-recoverable.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A path is a name in a filesystem, not the data itself. Relative paths are interpreted against a working directory, which may differ between an editor, test runner and container. Construct owned paths explicitly and avoid assuming the repository is writable from learner code. The classroom retains saved pads separately from temporary worker files.

Writing a file creates a side effect with a lifetime. Tiny examples should create a unique temporary directory, operate only inside it, and remove it in finally. Production persistence requires more decisions: atomic replacement, backups, permissions and recovery after interruption. An in-memory assertion proves content logic but cannot establish durable storage behavior after a crash.

`Path.Combine` constructs a platform path. `File.WriteAllText` encodes text; `ReadAllText` decodes it. A try/finally protects cleanup, while recursive removal is safe only for a directory this operation uniquely owns.

Path normalization alone does not solve symlink attacks or concurrent replacement. Do not delete arbitrary user-provided directories. Worker temporary files are not the durable learner progress store.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
