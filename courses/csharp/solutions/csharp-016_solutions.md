# csharp-016: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-016_solution.cs](csharp-016_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Aggregate repeated valid items:** Repeated identities accumulate after validation rather than creating ambiguous duplicate dictionary entries. Pear totals 6 and apple totals 3.

**Retain rejection evidence:** Malformed and negative quantities remain excluded, and empty input produces an empty report rather than an invented item. Three rejected lines do not alter the valid pear total.

## Task answers

### Task 1: Predict and explain

Trace each input through validation and accumulation.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Repeated identities accumulate after validation rather than creating ambiguous duplicate dictionary entries. Pear totals 6 and apple totals 3.

### Task 2: Guided modification

Add one valid duplicate and predict the new total before running.

No separate reference answer has been written for this task. Start from Example B: Malformed and negative quantities remain excluded, and empty input produces an empty report rather than an invented item. Three rejected lines do not alter the valid pear total.

### Task 3: Independent construction

Build a sorted text report from the accepted dictionary and the rejection count.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
var result = Import(new[] { "pear,2", "apple,3", "bad", "pear,1" });
var comparer = StringComparer.Ordinal;
var names = result.Counts.Keys.OrderBy(key => key, comparer);
var lines = new List<string>();
foreach (string name in names) {
  lines.Add($"{name}: {result.Counts[name]}");
}
lines.Add($"rejected: {result.Rejected}");
string report = string.Join("\n", lines);
Check(report == "apple: 3\npear: 3\nrejected: 1", "sorted report");
```

**Observe:** The report lists apple: 3, pear: 3 and rejected: 1 in that order.

Ordinal ordering makes the report deterministic, and the rejection count is reported beside the accepted totals instead of being hidden.

### Task 4: Diagnose a defect

Diagnose an importer that ignores TryParse failure and inserts zero.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Checking field count after indexing is too late. Case policy affects identity and must be documented. Extremely large totals can overflow, so checked accumulation belongs in a production input contract.

### Task 5: Boundary evidence

Test empty item names, extra fields, zero quantity and empty input.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Aggregate repeated valid items) and Example B (Retain rejection evidence).

### Task 6: Transfer and justify

Design a reusable import result that retains per-line rejection reasons without exposing sensitive raw input.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Pipeline**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A useful first project combines parsing, representation and aggregation while keeping their responsibilities separate. The input boundary rejects malformed quantities. The domain representation preserves item identity. The report stage summarizes only accepted records. Mixing these stages often creates a subtle bug: a failed parse becomes zero and then appears as valid data.

This project uses in-memory fixture lines so it runs offline without interactive input. It reports accepted totals and rejected line counts independently. A real importer would also record line identity and a safe reason. Build the smallest end-to-end path first, then introduce invalid and duplicate inputs. The final result must explain what happened, not merely produce a total that looks plausible.

`Split` produces fields; check the field count before indexing. `TryParse` separates syntax from a valid integer. `TryGetValue` supports accumulating repeated keys. Sorting keys before display gives a stable report.

Checking field count after indexing is too late. Case policy affects identity and must be documented. Extremely large totals can overflow, so checked accumulation belongs in a production input contract.

## Review before continuing

Run the reference and confirm that it prints `csharp-016: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
