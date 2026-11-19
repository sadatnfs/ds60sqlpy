# csharp-011: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-011_solution.cs](csharp-011_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Carry absence through a computation:** Conditional access propagates missing information until a boundary deliberately chooses a display representation. The optional length is absent, not zero.

**Distinguish zero from missing:** Pattern matching unwraps only the present case, giving a nonnullable variable inside that branch. A measured zero and an unknown measurement produce distinct descriptions.

## Task answers

### Task 1: Predict and explain

Predict nullable length and its fallback for null and empty text.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Conditional access propagates missing information until a boundary deliberately chooses a display representation. The optional length is absent, not zero.

### Task 2: Guided modification

Use a visible unknown label rather than a numeric sentinel.

No separate reference answer has been written for this task. Start from Example B: Pattern matching unwraps only the present case, giving a nonnullable variable inside that branch. A measured zero and an unknown measurement produce distinct descriptions.

### Task 3: Independent construction

Write a formatter preserving missing, zero and positive measurements.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
string Format(int? value) {
  if (value is null) {
    return "missing";
  }
  return value.Value == 0 ? "zero" : $"{value.Value} units";
}
Check(Format(null) == "missing", "missing stays missing");
Check(Format(0) == "zero", "zero is a measurement");
Check(Format(5) == "5 units", "positive measurement");
```

**Observe:** null, 0 and 5 are formatted as missing, zero and 5 units.

The nullable parameter keeps absence separate from zero, and each of the three cases has its own text.

### Task 4: Diagnose a defect

Diagnose using ! to suppress a warning on an actually null value.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A warning suppression is not validation. Null, empty and whitespace-only text are different states. Returning a fallback too early can irreversibly discard useful information.

### Task 5: Boundary evidence

Test whitespace-only text separately from null and empty text.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Carry absence through a computation) and Example B (Distinguish zero from missing).

### Task 6: Transfer and justify

Design an import field whose missing value has different meaning from an explicit zero or empty value.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Null**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Missing information should be visible in a type and a control-flow policy. Nullable reference annotations let the compiler warn when a value may be null; they are static analysis, not a new runtime container. An annotation cannot validate data arriving from another language, reflection or an external format. Keep runtime validation where that data enters.

A nullable value type such as int? represents either an int or no value. Choosing a fallback is a domain decision. Replacing missing age with zero means something very different from reporting unknown age. Prefer explicit branches when a default would blur those meanings.

`string?` permits null in static analysis; `int?` is Nullable<int>. `?.` conditionally accesses a member and preserves absence. `??` supplies a fallback. The null-forgiving operator `!` silences analysis but performs no check.

A warning suppression is not validation. Null, empty and whitespace-only text are different states. Returning a fallback too early can irreversibly discard useful information.

## Review before continuing

Run the reference and confirm that it prints `csharp-011: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
