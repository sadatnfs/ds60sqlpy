# csharp-011: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-011_solution.cs](csharp-011_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Carry absence through a computation:** Conditional access propagates missing information until a boundary deliberately chooses a display representation. The optional length is absent, not zero.

**Distinguish zero from missing:** Pattern matching unwraps only the present case, giving a nonnullable variable inside that branch. A measured zero and an unknown measurement produce distinct descriptions.

## Task answers

### Task 1: Predict and explain

Predict nullable length and its fallback for null and empty text.

**Written answer.** For `string? label = null`, `label?.Length` short-circuits to `null`, so `length` is an absent `int?` and `length ?? -1` yields -1. For `label = ""` the access runs and `length` is a present 0, so `length ?? -1` is 0, not -1.

**Why it is correct.** `?.` lifts the result to `int?` and produces null only when the receiver is null. An empty string is a real object with `Length` 0, so the fallback operator `??` has nothing to replace and passes the 0 through.

**Plausible wrong approach.** Predicting -1 for both inputs treats empty text as missing. That merges two states the lesson keeps apart: a caller reading -1 could not tell an absent label from one that exists but has no characters.

**How to verify.** Add `string? empty = ""; int? emptyLength = empty?.Length;` and check `emptyLength == 0 && (emptyLength ?? -1) == 0` next to the existing `absence remains absent` check. All of them pass silently.

### Task 2: Guided modification

Use a visible unknown label rather than a numeric sentinel.

**Written answer.** Replace the sentinel with a label at the display boundary: `string shown = length is int n ? n.ToString() : "unknown";`. For the null label `shown` is `unknown`; for `"ok"` it is `2`.

**Why it is correct.** The pattern `length is int n` succeeds only for a present value and binds a nonnullable `n`. The missing case gets a word that cannot be mistaken for a length, unlike -1, which a later sum or average would happily include.

**Plausible wrong approach.** Formatting with `(length ?? 0).ToString()` produces `0` for the missing label. A report then shows zero characters for text that never existed, the early fallback the pitfalls warn against.

**How to verify.** Check `shown == "unknown"` for the null label and `shown == "2"` after assigning `"ok"`. Then feed an empty string and confirm it shows `0`, not `unknown`.

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

**Plausible wrong approach.** Declaring the parameter as plain `int` and having callers pass `value ?? 0` collapses missing into zero before `Format` runs. `Format(null)` then cannot even be written, and the data that reaches the method prints `zero` for a missing reading.

**How to verify.** The block checks null, 0 and 5. Also probe `Format(-3)`: it returns `-3 units`, which shows the formatter treats negative readings as measurements; decide whether the domain should reject them instead.

### Task 4: Diagnose a defect

Diagnose using ! to suppress a warning on an actually null value.

**Written answer.** `string? name = null; int size = name!.Length;` compiles without warning because `!` tells the flow analysis to trust you, but at run time the dereference still throws `NullReferenceException`. Fix it with a real branch: `int size = name is null ? 0 : name.Length;` or reject the input.

**Why it is correct.** Nullable annotations and the `!` operator exist only at compile time. They change which warnings appear and emit no runtime check, so the generated code is the same dereference as without the operator.

**Plausible wrong approach.** Moving the suppression earlier, as in `string checkedName = name!;`, silences the same warning one line sooner. The null now travels further into the program and fails at a later `.Length`, farther from its cause.

**How to verify.** Run the `!` version with `name = null` and observe `NullReferenceException`. With the branch, check `size == 0` for null and `size == 3` for `"Ada"`; both pass.

### Task 5: Boundary evidence

Test whitespace-only text separately from null and empty text.

**Written answer.** Classify text with `string Kind(string? s) => s is null ? "null" : s.Length == 0 ? "empty" : string.IsNullOrWhiteSpace(s) ? "blank" : "text";` and check null, `""`, `"   "` and `"a"` separately.

**Why it is correct.** Each test isolates one state. `"   "` has `Length` 3, so it passes an emptiness test, yet `IsNullOrWhiteSpace` reports true. Ordering null, then empty, then whitespace keeps every arm reachable.

**Plausible wrong approach.** Using `string.IsNullOrEmpty(s)` as the only guard lets `"   "` through as valid text. A required-name field would then accept three spaces as a real name.

**How to verify.** Check `Kind(null) == "null"`, `Kind("") == "empty"`, `Kind("   ") == "blank"` and `Kind("a") == "text"`. Also add a tab, `"\t"`, and confirm it is `blank`.

### Task 6: Transfer and justify

Design an import field whose missing value has different meaning from an explicit zero or empty value.

**Written answer.** For a discount field in an import, use `decimal? Discount` where a missing column means no discount data was supplied, `0` means the supplier explicitly offers none, and an empty cell is rejected as malformed. Parse each case into its own outcome before computing prices.

**Why it is correct.** Keeping three outcomes stops a missing field from silently pricing an item at full rate. The limitation is that downstream reports must handle `null`, for example by showing `unknown` and excluding it from averages.

**Plausible wrong approach.** Parsing every blank or missing cell with `decimal.TryParse(cell, out var d) ? d : 0` makes an absent discount indistinguishable from an explicit zero, so audits cannot find suppliers who never sent the field.

**How to verify.** Feed three rows: one without the column, one with `0` and one with an empty cell. Check the results are `null`, `0m` and a rejection, then confirm an average over the rows uses only the explicit zero.

## Mechanism and diagnostic reasoning

Missing information should be visible in a type and a control-flow policy. Nullable reference annotations let the compiler warn when a value may be null; they are static analysis, not a new runtime container. An annotation cannot validate data arriving from another language, reflection or an external format. Keep runtime validation where that data enters.

A nullable value type such as int? represents either an int or no value. Choosing a fallback is a domain decision. Replacing missing age with zero means something very different from reporting unknown age. Prefer explicit branches when a default would blur those meanings.

`string?` permits null in static analysis; `int?` is Nullable<int>. `?.` conditionally accesses a member and preserves absence. `??` supplies a fallback. The null-forgiving operator `!` silences analysis but performs no check.

A warning suppression is not validation. Null, empty and whitespace-only text are different states. Returning a fallback too early can irreversibly discard useful information.

## Review before continuing

Run the reference and confirm that it prints `csharp-011: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
