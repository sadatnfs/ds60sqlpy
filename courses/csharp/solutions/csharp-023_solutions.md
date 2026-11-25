# csharp-023: explanation and comparison

Reference program: [csharp-023_solution.cs](csharp-023_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Catch only the expected invalid format:** The catch does not accidentally classify every possible programming error as bad user text. Malformed numeric text is caught as a format error.

**Retain an inner cause:** A public description can add context without erasing the lower-level failure category. The outer domain failure still contains the I/O cause.

## Task answers

### Task 1: Predict and explain

Identify which failure category each catch handles.

**Written answer.** In Example A, `catch (FormatException)` handles malformed numeric text: `int.Parse("oops")` cannot read digits. It does not handle the negative case, which throws `ArgumentOutOfRangeException`, or text beyond the `int` range, which throws `OverflowException`; those still propagate. In Example B, the inner `catch (IOException)` handles the storage failure and translates it into a domain failure, and the outer `catch (InvalidOperationException)` handles that domain failure while keeping the I/O cause as `InnerException`.

**Why it is correct.** A catch clause matches by exception type, so each one names exactly the failure category it is prepared to handle. Everything else continues up the call stack unchanged.

**Plausible wrong approach.** Assuming the FormatException catch also covers `ParseCount("-1")` is wrong: `ArgumentOutOfRangeException` is not a `FormatException`, so that call would end the program unless another handler catches it.

**How to verify.** Call `ParseCount("-1")` inside the same try and confirm the program stops with `ArgumentOutOfRangeException`. In B, check `observed?.InnerException?.Message == "synthetic read failure"`.

### Task 2: Guided modification

Add a separate negative-count case without classifying it as FormatException.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
int ParseCount(string text) {
  int value = int.Parse(text, CultureInfo.InvariantCulture);
  if (value < 0)
    throw new ArgumentOutOfRangeException(nameof(text));
  return value;
}
string outcome = "none";
try {
  ParseCount("-2");
} catch (FormatException) {
  outcome = "format";
} catch (ArgumentOutOfRangeException) {
  outcome = "negative";
}
Check(outcome == "negative", "negative is not a format error");
```

**Observe:** -2 is reported as negative, not as a format error.

`-2` is well-formed numeric text, so `int.Parse` succeeds and returns -2. The domain rule then throws `ArgumentOutOfRangeException`, which the second catch clause handles. Keeping the clauses separate lets a caller tell a typing mistake from a valid number that breaks the business rule.

**Plausible wrong approach.** Throwing `FormatException` for the negative value, or catching both cases in one clause, tells the user that `-2` is not a number when the real problem is that counts cannot be negative.

**How to verify.** Run the same try with `"x"` and confirm `outcome` becomes `format`. Run it with `"3"` and confirm `outcome` stays `none`.

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

**Written answer.** `string Report(string path) { try { ... } catch (Exception) { return ""; } }` returns an empty string for a missing file, a permission error, malformed data and even a programming bug such as `NullReferenceException`. The caller cannot distinguish any of these from a real report with no rows, so a lost import looks like success. Catch only the failures you can handle and let the others propagate, or return an explicit failure outcome instead of an empty value.

**Why it is correct.** An empty report is a legitimate successful result for an empty data set. Returning it on failure reuses a valid value as a sentinel, which deletes the evidence the caller needs to retry, alert or stop.

**Plausible wrong approach.** Adding a log line inside the catch-all and still returning the empty report records the failure somewhere nobody is watching, while the caller continues to publish an empty report.

**How to verify.** Call the catch-all version with a path that does not exist and observe a successful empty result. With the narrowed version, check that the same call throws `FileNotFoundException`, while a real empty file still returns `""`.

### Task 5: Boundary evidence

Test success, expected rejection and an unexpected exception separately.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
string Classify(string text) {
  try {
    int value = int.Parse(text, CultureInfo.InvariantCulture);
    return "ok " + value;
  } catch (FormatException) {
    return "rejected";
  }
}
Check(Classify("4") == "ok 4", "success");
Check(Classify("four") == "rejected", "expected rejection");
bool escaped = false;
try {
  Classify(null!);
} catch (ArgumentNullException) {
  escaped = true;
}
Check(escaped, "unexpected exception is not swallowed");
```

**Observe:** 4 succeeds, four is rejected as expected and a null argument escapes as ArgumentNullException.

Each test targets one path. `"4"` reaches the return value. `"four"` reaches the FormatException clause, which is the expected rejection. Passing `null` makes `int.Parse` throw `ArgumentNullException`, a failure `Classify` was not written to handle, and the third test proves it propagates instead of being turned into `rejected`.

**Plausible wrong approach.** Changing the clause to `catch (Exception)` keeps the first two tests green and turns the null input into `rejected`. Without the third test, nobody would notice that bugs are now being reported as bad user input.

**How to verify.** Temporarily widen the clause to `catch (Exception)` and confirm the last check fails. Restore `catch (FormatException)` and all three pass.

### Task 6: Transfer and justify

Decide which layer owns user-facing error translation and which details should remain private diagnostics.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Mechanism and diagnostic reasoning

Exceptions carry an abnormal control-flow result across method boundaries. Catch an exception where the program can make a meaningful recovery decision, add context or translate it into a public error contract. Catching everything at every layer often destroys the reason the operation failed.

A normal absence can be represented without an exception when it is expected. A malformed argument or failed invariant should remain visible. When rethrowing in a catch block, use `throw;` to preserve the original stack relationship. When adding a domain exception, retain the original as InnerException. Logging the same exception at every layer can multiply noise without adding evidence.

`try` encloses an operation; typed catch selects a failure category; finally runs cleanup when control leaves the protected region. `throw;` rethrows the current exception. A catch filter with `when` narrows recovery policy.

A catch-all that returns a default can turn data loss into apparent success. Throwing the caught variable instead of using bare throw changes stack-trace behavior. Cleanup should not accidentally replace the original failure.

## Review before continuing

Run the reference and confirm it prints `csharp-023: passed`, then rerun the guide's counterexample.
