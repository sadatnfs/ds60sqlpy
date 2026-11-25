# csharp-016: explanation and comparison

Reference program: [csharp-016_solution.cs](csharp-016_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Aggregate repeated valid items:** Repeated identities accumulate after validation rather than creating ambiguous duplicate dictionary entries. Pear totals 6 and apple totals 3.

**Retain rejection evidence:** Malformed and negative quantities remain excluded, and empty input produces an empty report rather than an invented item. Three rejected lines do not alter the valid pear total.

## Task answers

### Task 1: Predict and explain

Trace each input through validation and accumulation.

**Written answer.** Example B: `"pear,2"` splits into two fields, the name is not blank, `2` parses and is not negative, so `pear` goes from 0 to 2. `"pear,no"` has two fields but `no` fails `TryParse`, so `Rejected` becomes 1. `"apple,-1"` parses to -1, which fails `quantity < 0`, so `Rejected` becomes 2 and `apple` is never added. `"broken"` splits into one field, so the field-count test rejects it before any index is read and `Rejected` becomes 3. The result is one entry, `pear` 2, and 3 rejections.

**Why it is correct.** Every line passes through the same ordered tests: field count, name, number, sign. A line contributes to `Counts` only if it passes all four, and every failed line increments `Rejected` exactly once because of the `continue`.

**Plausible wrong approach.** Assuming `apple,-1` creates an `apple` entry with 0 misses that the sign test runs before the dictionary update. Assuming `broken` throws `IndexOutOfRangeException` misses that the field count is checked before `fields[1]` is read.

**How to verify.** Example B checks `Rejected == 3` and `Counts.Count == 1`. Add `Check(!totals.Counts.ContainsKey("apple"), ...)` to confirm the rejected apple line left no entry.

### Task 2: Guided modification

Add one valid duplicate and predict the new total before running.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
var totals = Import(new[] { "pear,2", "apple,3", "pear,4", "apple,5" });
Check(totals.Rejected == 0, "duplicate line accepted");
Check(totals.Counts["apple"] == 8, "predicted apple total");
Check(totals.Counts["pear"] == 6, "pear unchanged");
Check(totals.Counts.Count == 2, "no new key");
```

**Observe:** The added apple,5 is accepted: apple becomes 8, pear stays 6 and there are still two keys.

The prediction written before running was 3 + 5 = 8 for apple, with pear and the key count unchanged. `Import` reads the existing total with `TryGetValue` and adds the new quantity, so a repeated valid name accumulates instead of replacing or being rejected.

**Plausible wrong approach.** Predicting apple 5 assumes the later line overwrites the earlier one, which is what `counts[name] = quantity` would do. Predicting a rejection treats a repeated name as a duplicate-key error, which is a policy this importer does not have.

**How to verify.** Add `"Apple,1"` and confirm it creates a third key, because the dictionary uses `StringComparer.Ordinal`. That shows the case policy the pitfalls say must be documented.

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

**Written answer.** `int.TryParse(fields[1], out int quantity); counts[name] = before + quantity;` ignores the returned bool. For `"pear,no"` the parse fails, `quantity` is set to 0, and the importer inserts `pear` with 0 and counts no rejection. Bad data now looks like a real zero-quantity line. The fix is to branch on the result, as `Import` does: `if (!int.TryParse(...)) { rejected++; continue; }`.

**Why it is correct.** `TryParse` reports failure only through its return value; the `out` value is always assigned and is 0 on failure. Discarding the bool removes the only signal that separates `"pear,0"` from `"pear,no"`.

**Plausible wrong approach.** Checking afterwards with `if (quantity == 0) rejected++` rejects the legitimate `"pear,0"` too, and still lets nothing distinguish a typo from a real zero.

**How to verify.** Import `"pear,no"` with the faulty version and observe `Counts["pear"] == 0` and `Rejected == 0`. With the real `Import`, check `Counts.Count == 0` and `Rejected == 1`.

### Task 5: Boundary evidence

Test empty item names, extra fields, zero quantity and empty input.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
var blank = Import(new[] { ",3", "  ,3" });
Check(blank.Rejected == 2, "empty and blank names rejected");
Check(blank.Counts.Count == 0, "no entry for a blank name");
var extra = Import(new[] { "pear,2,box" });
Check(extra.Rejected == 1, "extra field rejected");
var zero = Import(new[] { "pear,0" });
Check(zero.Rejected == 0 && zero.Counts["pear"] == 0, "zero accepted");
var none = Import(Array.Empty<string>());
Check(none.Rejected == 0 && none.Counts.Count == 0, "empty input");
```

**Observe:** Blank names and the extra field are rejected, pear,0 is accepted with total 0 and empty input gives no counts and no rejections.

`",3"` and `"  ,3"` reach `IsNullOrWhiteSpace` and fail it. `"pear,2,box"` splits into three fields and fails the length test, so `2` is never parsed. `"pear,0"` passes every test because the rule rejects only negative quantities, so it records a real zero. No lines means no iterations, and both outputs keep their starting values.

**Plausible wrong approach.** Treating zero as invalid because it adds nothing would make `pear,0` a rejection and lose the evidence that pear was reported. Accepting `pear,2,box` by reading only the first two fields would hide a format change in the source file.

**How to verify.** Add `"pear, 2"` with a space before the number and decide: `int.TryParse` allows leading whitespace, so it is accepted as 2. If the contract forbids spaces, tighten the parse and confirm the check flips.

### Task 6: Transfer and justify

Design a reusable import result that retains per-line rejection reasons without exposing sensitive raw input.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Mechanism and diagnostic reasoning

A useful first project combines parsing, representation and aggregation while keeping their responsibilities separate. The input boundary rejects malformed quantities. The domain representation preserves item identity. The report stage summarizes only accepted records. Mixing these stages often creates a subtle bug: a failed parse becomes zero and then appears as valid data.

This project uses in-memory fixture lines so it runs offline without interactive input. It reports accepted totals and rejected line counts independently. A real importer would also record line identity and a safe reason. Build the smallest end-to-end path first, then introduce invalid and duplicate inputs. The final result must explain what happened, not merely produce a total that looks plausible.

`Split` produces fields; check the field count before indexing. `TryParse` separates syntax from a valid integer. `TryGetValue` supports accumulating repeated keys. Sorting keys before display gives a stable report.

Checking field count after indexing is too late. Case policy affects identity and must be documented. Extremely large totals can overflow, so checked accumulation belongs in a production input contract.

## Review before continuing

Run the reference and confirm it prints `csharp-016: passed`, then rerun the guide's counterexample.
