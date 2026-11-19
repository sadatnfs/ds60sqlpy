# csharp-023: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-023_solution.cs](csharp-023_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Catch only the expected invalid format:** The catch does not accidentally classify every possible programming error as bad user text. Malformed numeric text is caught as a format error.

**Retain an inner cause:** A public description can add context without erasing the lower-level failure category. The outer domain failure still contains the I/O cause.

## Task answers

### Task 1: Predict and explain

Identify which failure category each catch handles.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The catch does not accidentally classify every possible programming error as bad user text. Malformed numeric text is caught as a format error.

### Task 2: Guided modification

Add a separate negative-count case without classifying it as FormatException.

No separate reference answer has been written for this task. Start from Example B: A public description can add context without erasing the lower-level failure category. The outer domain failure still contains the I/O cause.

### Task 3: Independent construction

Define an import API with distinct invalid-input and storage-failure outcomes.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
int Import(string text, bool storageAvailable) {
  if (!int.TryParse(text, out int quantity) || quantity < 0) {
    throw new ArgumentException("invalid quantity", nameof(text));
  }
  if (!storageAvailable) {
    throw new IOException("storage unavailable");
  }
  return quantity;
}
Check(Import("3", true) == 3, "success");
string outcome = "none";
try {
  Import("x", true);
} catch (ArgumentException) {
  outcome = "invalid input";
}
Check(outcome == "invalid input", "input failure");
try {
  Import("3", false);
} catch (IOException) {
  outcome = "storage";
}
Check(outcome == "storage", "storage failure");
```

**Observe:** Valid input returns 3; bad text and unavailable storage end in different exception types.

ArgumentException describes the caller's input and IOException the environment, so a caller can retry one and correct the other.

### Task 4: Diagnose a defect

Diagnose catch-all code that returns an empty successful report.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A catch-all that returns a default can turn data loss into apparent success. Throwing the caught variable instead of using bare throw changes stack-trace behavior. Cleanup should not accidentally replace the original failure.

### Task 5: Boundary evidence

Test success, expected rejection and an unexpected exception separately.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Catch only the expected invalid format) and Example B (Retain an inner cause).

### Task 6: Transfer and justify

Decide which layer owns user-facing error translation and which details should remain private diagnostics.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Exception**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Exceptions carry an abnormal control-flow result across method boundaries. Catch an exception where the program can make a meaningful recovery decision, add context or translate it into a public error contract. Catching everything at every layer often destroys the reason the operation failed.

A normal absence can be represented without an exception when it is expected. A malformed argument or failed invariant should remain visible. When rethrowing in a catch block, use `throw;` to preserve the original stack relationship. When adding a domain exception, retain the original as InnerException. Logging the same exception at every layer can multiply noise without adding evidence.

`try` encloses an operation; typed catch selects a failure category; finally runs cleanup when control leaves the protected region. `throw;` rethrows the current exception. A catch filter with `when` narrows recovery policy.

A catch-all that returns a default can turn data loss into apparent success. Throwing the caught variable instead of using bare throw changes stack-trace behavior. Cleanup should not accidentally replace the original failure.

## Review before continuing

Run the reference and confirm that it prints `csharp-023: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
