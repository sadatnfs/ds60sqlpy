# csharp-032: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-032_solution.cs](csharp-032_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Import valid and invalid records:** Validation remains visible in the result instead of silently converting bad records into ordinary data. The service returns total 2 and one rejected record.

**Cancellation is not an empty report:** The result category carries meaning beyond a numeric total. A cancelled request and a successful empty import have different outcomes.

## Task answers

### Task 1: Predict and explain

Trace syntax, validation and aggregation as separate stages.

**Written answer.** In Example A the syntax stage is `JsonSerializer.Deserialize<ImportItem[]>`: it turns the text into two `ImportItem` values, and it would throw `JsonException` for malformed text or produce null for the literal `null`, which `ImportAsync` turns into `ArgumentException`. The validation stage looks at each item: `pear` with 2 passes, and the item with an empty name fails, so `rejected` becomes 1. The aggregation stage adds only validated quantities with `checked`, giving `Total` 2.

**Why it is correct.** Each stage answers a different question: is this JSON of the right shape, is each record acceptable, and what do the accepted records add up to. Keeping them separate makes each kind of failure visible in its own way.

**Plausible wrong approach.** Merging validation into aggregation, for example summing everything and subtracting invalid quantities afterwards, makes a negative quantity look like a correction instead of a rejection.

**How to verify.** Feed `[{]` (syntax failure), an item with a negative quantity (validation failure) and two valid items (aggregation) and confirm the three different outcomes.

### Task 2: Guided modification

Add a duplicate valid name and document whether total quantity or distinct count is reported.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
string pear2 = "{\"Name\":\"pear\",\"Quantity\":2}";
string pear3 = "{\"Name\":\"pear\",\"Quantity\":3}";
string json = $"[{pear2},{pear3}]";
var result = await ImportAsync(json, CancellationToken.None);
Check(result.Total == 5 && result.Rejected == 0, "quantities summed");
var items = JsonSerializer.Deserialize<ImportItem[]>(json)!;
var names = items.Select(item => item.Name);
int distinct = names.Distinct(StringComparer.Ordinal).Count();
Check(distinct == 1, "distinct item count is a separate measure");
```

**Observe:** Two valid pear records give Total 5 with no rejections, while the number of distinct names is 1.

The documented decision is that `Total` reports total quantity: a repeated valid name is a second delivery of the same item, so its quantity is added, not rejected and not deduplicated. The distinct item count is a different measure, 1 here, and is computed separately when a report needs it. Writing both down prevents a reader from interpreting `Total` 5 as five distinct items.

**Plausible wrong approach.** Deduplicating by name before summing would report 2 or 3 depending on which record wins, silently discarding a real delivery. Reporting `Total` as the number of records would conflate quantity with rows.

**How to verify.** Add a third record named `Pear` with quantity 1 and confirm `Total` becomes 6 while the ordinal distinct count becomes 2, which shows the case policy also has to be stated.

### Task 3: Independent construction

Build a per-item result while preserving the rejected count.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
string pear = "{\"Name\":\"pear\",\"Quantity\":2}";
string blank = "{\"Name\":\"\",\"Quantity\":1}";
string json = $"[{pear},{blank}]";
var items = JsonSerializer.Deserialize<ImportItem[]>(json)!;
var accepted = new Dictionary<string, int>(StringComparer.Ordinal);
int rejected = 0;
foreach (var item in items) {
  if (string.IsNullOrWhiteSpace(item.Name) || item.Quantity < 0) {
    rejected++;
    continue;
  }
  accepted.TryGetValue(item.Name, out int before);
  accepted[item.Name] = checked(before + item.Quantity);
}
Check(accepted["pear"] == 2 && accepted.Count == 1, "per-item result");
Check(rejected == 1, "rejection preserved");
```

**Observe:** pear has 2 accepted units and one rejected record is counted.

Valid records update their own item total while invalid ones only increment the rejected count, so neither result hides the other.

### Task 4: Diagnose a defect

Diagnose catch-all logic returning an empty report after cancellation.

**Written answer.** `try { return await ImportAsync(json, token); } catch (Exception) { return new ImportResult(0, 0); }` catches `OperationCanceledException` along with every other failure and returns the same value as a successful import of an empty array. Example B shows that these must differ: a cancelled request did not produce a report at all. Let cancellation propagate, for example with `catch (Exception error) when (error is not OperationCanceledException)`, and represent invalid input with its own outcome instead of an empty report.

**Why it is correct.** The caller decides what to do from the outcome. A user who cancelled should see a cancellation, a broken file should be reported as invalid, and only a valid empty array should produce `Total` 0 with no rejections.

**Plausible wrong approach.** Logging the exception inside the catch-all and still returning the empty report does not fix it: the caller still publishes a report claiming the import succeeded with nothing in it.

**How to verify.** Call the catch-all wrapper with a cancelled token and with `[]` and observe identical results. With the narrowed catch, check that the cancelled call throws `OperationCanceledException` and the `[]` call returns `Total` 0.

### Task 5: Boundary evidence

Test malformed JSON, JSON null, an empty list and invalid quantities.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
async Task<string> Outcome(string json) {
  try {
    var result = await ImportAsync(json, CancellationToken.None);
    return $"total {result.Total} rejected {result.Rejected}";
  } catch (JsonException) {
    return "malformed";
  } catch (ArgumentException) {
    return "not an array";
  }
}
string negative = "[{\"Name\":\"pear\",\"Quantity\":-1}]";
string fraction = "[{\"Name\":\"pear\",\"Quantity\":2.5}]";
Check(await Outcome("[{") == "malformed", "malformed JSON");
Check(await Outcome("null") == "not an array", "JSON null");
Check(await Outcome("[]") == "total 0 rejected 0", "empty list");
Check(await Outcome(negative) == "total 0 rejected 1", "negative");
Check(await Outcome(fraction) == "malformed", "non-integer quantity");
```

**Observe:** Malformed text and a fractional quantity are malformed, null is not an array, the empty list is a successful empty report and a negative quantity is one rejection.

Each input reaches a different stage. `[{` and `2.5` fail during decoding, because a fraction cannot be read as an `int`. `null` decodes to a null array, which the service rejects with `ArgumentException`. `[]` passes every stage and produces a real empty report. `-1` decodes but fails validation, so it is counted as rejected instead of stopping the whole import.

**Plausible wrong approach.** Treating `2.5` as a validation rejection, or `null` as an empty list, would merge different failures into one outcome. Those are exactly the distinctions the service is designed to keep.

**How to verify.** Add an item with quantity `2147483647` next to one with quantity 1 and confirm the `checked` addition throws `OverflowException`, a fourth outcome the wrapper does not catch.

### Task 6: Transfer and justify

Design an adapter boundary for a file or HTTP source without putting I/O inside the pure aggregation.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Transport model**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

The intermediate project separates a transport representation, validation, a pure aggregation and an asynchronous service boundary. This makes failure location visible. JSON syntax errors belong to decoding; invalid records belong to domain validation; a cancelled operation must not be presented as an empty successful import.

A complete service also owns its dependency lifetime and result shape. The classroom version uses an in-memory JSON payload, avoiding external I/O while preserving the same boundary decisions. A production adapter can load bytes from a file or HTTP response, then call the same pure core. Keep the core deterministic so integration failures do not obscure calculation errors.

An async method can validate cancellation before admitting work and return a record describing accepted totals and rejected counts. Immutable result fields make it easier to store a receipt without later mutation.

A transport DTO is not automatically a trusted domain object. Do not merge cancelled, invalid and successfully empty results into one representation. An async signature alone does not make CPU work asynchronous.

## Review before continuing

Run the reference and confirm that it prints `csharp-032: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
