# csharp-020: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-020_solution.cs](csharp-020_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Observe query timing:** Constructing Where does not copy the source values. The deferred query sees the subsequently appended 3.

**Capture a stable result:** Materialization creates a deliberate temporal boundary while preserving the original list separately. The earlier snapshot contains only 2 while a new projection sees three values.

## Task answers

### Task 1: Predict and explain

Predict whether adding an item before enumeration affects query and snapshot.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Constructing Where does not copy the source values. The deferred query sees the subsequently appended 3.

### Task 2: Guided modification

Add a projection from integers to labeled strings.

No separate reference answer has been written for this task. Start from Example B: Materialization creates a deliberate temporal boundary while preserving the original list separately. The earlier snapshot contains only 2 while a new projection sees three values.

### Task 3: Independent construction

Build a deterministic report selecting, transforming and ordering records.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
var stock = new Dictionary<string, int> { ["pear"] = 2, ["fig"] = 0 };
stock["apple"] = 5;
var kept = stock.Where(row => row.Value > 0);
var ordered = kept.OrderBy(row => row.Key, StringComparer.Ordinal);
var report = ordered.Select(row => $"{row.Key}={row.Value}");
Check(report.SequenceEqual(new[] { "apple=5", "pear=2" }), "report");
```

**Observe:** The report is apple=5 then pear=2; fig with quantity 0 is filtered out.

Filtering, ordering with an explicit comparer and projecting happen in one query, and ToArray materializes the result once.

### Task 4: Diagnose a defect

Diagnose a query with a side-effect counter enumerated twice.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: LINQ syntax does not imply database execution. IEnumerable and IQueryable have different providers and translation boundaries. A deferred query can also fail later than the line that constructed it.

### Task 5: Boundary evidence

Test empty input and a filter matching no rows.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Observe query timing) and Example B (Capture a stable result).

### Task 6: Transfer and justify

Choose streaming or materialization for a large import and explain memory and repeatability tradeoffs.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Deferred execution**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Language Integrated Query expresses sequence transformations such as filtering, projection and ordering. Many LINQ operators produce a recipe rather than immediately executing it. Enumeration runs that recipe. If the source changes before enumeration, the result can change too. This timing is part of the semantics, not an incidental optimization.

Materialization with ToArray or ToList executes a query and stores its current result. It consumes memory but creates a useful snapshot boundary. Repeatedly enumerating an expensive or stateful source can repeat work or observe different data. Decide whether the consumer needs a live recipe, a one-pass stream or a stable materialized result.

`Where` keeps matching elements; `Select` transforms each element. `OrderBy` chooses ordering. `ToArray` materializes. Lambdas used by deferred operators run during enumeration, so avoid hidden side effects.

LINQ syntax does not imply database execution. IEnumerable and IQueryable have different providers and translation boundaries. A deferred query can also fail later than the line that constructed it.

## Review before continuing

Run the reference and confirm that it prints `csharp-020: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
