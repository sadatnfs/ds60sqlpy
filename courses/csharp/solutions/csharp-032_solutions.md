# csharp-032: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-032_solution.cs](csharp-032_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Import valid and invalid records:** Validation remains visible in the result instead of silently converting bad records into ordinary data. The service returns total 2 and one rejected record.

**Cancellation is not an empty report:** The result category carries meaning beyond a numeric total. A cancelled request and a successful empty import have different outcomes.

## Task answers

### Task 1: Predict and explain

Trace syntax, validation and aggregation as separate stages.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Validation remains visible in the result instead of silently converting bad records into ordinary data. The service returns total 2 and one rejected record.

### Task 2: Guided modification

Add a duplicate valid name and document whether total quantity or distinct count is reported.

No separate reference answer has been written for this task. Start from Example B: The result category carries meaning beyond a numeric total. A cancelled request and a successful empty import have different outcomes.

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

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A transport DTO is not automatically a trusted domain object. Do not merge cancelled, invalid and successfully empty results into one representation. An async signature alone does not make CPU work asynchronous.

### Task 5: Boundary evidence

Test malformed JSON, JSON null, an empty list and invalid quantities.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Import valid and invalid records) and Example B (Cancellation is not an empty report).

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
