# csharp-020: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-020_solution.cs](csharp-020_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Observe query timing:** Constructing Where does not copy the source values. The deferred query sees the subsequently appended 3.

**Capture a stable result:** Materialization creates a deliberate temporal boundary while preserving the original list separately. The earlier snapshot contains only 2 while a new projection sees three values.

## Task answers

### Task 1: Predict and explain

Predict whether adding an item before enumeration affects query and snapshot.

**Written answer.** In Example A the query is created over `{ 1, 2 }`, 3 is added, and enumeration later yields 2 and 3. In Example B `ToArray()` runs while the list is still `{ 1, 2 }`, so the snapshot holds only 2 and adding 3 afterward does not reach it.

**Why it is correct.** `Where` returns an object that remembers the source and predicate but reads no elements. `ToArray` enumerates immediately and copies the matches into a new array, which later list changes cannot alter.

**Plausible wrong approach.** Expecting Example A's query to contain only 2 treats `Where` as eager filtering. That would be true for `values.Where(...).ToList()`, but this query has not run when 3 is added.

**How to verify.** Check `query.Count() == 1` before `values.Add(3)` and `query.Count() == 2` after it. The same query object reports two counts at two moments, while an array from `ToArray()` taken before the add keeps `Length == 1`.

### Task 2: Guided modification

Add a projection from integers to labeled strings.

**Written answer.** Write `var labels = values.Select(value => $"item-{value}");` and check `labels.SequenceEqual(new[] { "item-1", "item-2", "item-3" })` after the three values exist.

**Why it is correct.** `Select` maps each element through the lambda in order, producing one string per integer without filtering, so the output length equals the input length.

**Plausible wrong approach.** Putting the projection in `Where`, as in `values.Where(value => $"item-{value}" != "")`, compiles but still yields integers, because `Where` keeps elements and never transforms them.

**How to verify.** Check the sequence of labels, then add 4 to `values` and check `labels.Last() == "item-4"`, showing the projection is also deferred.

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

Filtering, ordering with `StringComparer.Ordinal` and projecting are composed as one deferred query; nothing runs until `SequenceEqual` enumerates `report`. Add `.ToArray()` at the end when a stable snapshot is needed.

**Plausible wrong approach.** Ordering by `row.Key` without a comparer uses the current culture. That gives the same result for `apple` and `pear`, but with a key `"Banana"` a linguistic culture puts `apple` first while ordinal order puts `Banana` first, so the report can differ between machines.

**How to verify.** The `report` check expects `apple=5` then `pear=2`. Set `stock["fig"] = 1` just before the check and it throws, because the deferred query now yields `apple=5`, `fig=1`, `pear=2`. The report is computed when enumerated, not when built.

### Task 4: Diagnose a defect

Diagnose a query with a side-effect counter enumerated twice.

**Written answer.** With `int calls = 0; var query = values.Select(v => { calls++; return v * 2; });`, calling `query.Count()` and then `query.Sum()` runs the lambda twice per element, so `calls` is 6 for three values, not 3. Materialize once with `var doubled = query.ToArray();` and use `doubled` twice.

**Why it is correct.** A deferred query is a recipe. Each enumeration runs the whole pipeline again from the source, including any side effects in the lambdas.

**Plausible wrong approach.** Caching with `var cached = query;` copies only the reference to the same recipe. Calling `cached.Count()` and `cached.Sum()` still runs the lambda twice per element and `calls` is still 6.

**How to verify.** Check `calls == 6` after the two calls on `query`, then reset it, use `ToArray()` once and check `calls == 3` after both `doubled.Length` and `doubled.Sum()`.

### Task 5: Boundary evidence

Test empty input and a filter matching no rows.

**Written answer.** Check `Array.Empty<int>().Where(v => v > 1).ToArray().Length == 0` and that `new[] { 1 }.Where(v => v > 1)` has no elements. Also check `Sum()` returns 0 on both and `First()` throws `InvalidOperationException`.

**Why it is correct.** An empty source and a filter that matches nothing both produce an empty sequence. Aggregates such as `Sum` define 0 for empty input, while `First` has no element to return and throws.

**Plausible wrong approach.** Using `query.First()` to read the top row in a report assumes at least one match. With the filter matching nothing it throws `Sequence contains no elements`; `FirstOrDefault()` returns 0 instead, which must not be confused with a real value.

**How to verify.** Run the empty checks and wrap `First()` in `try` catching `InvalidOperationException`. Check `FirstOrDefault()` returns 0 and decide whether 0 is a valid data value in your report.

### Task 6: Transfer and justify

Choose streaming or materialization for a large import and explain memory and repeatability tradeoffs.

**Written answer.** For a large import, stream rows with `File.ReadLines(path).Select(Parse).Where(IsValid)` and consume them once with `foreach`, writing each accepted row as it arrives. Materialize only a small summary such as counts.

**Why it is correct.** Streaming keeps memory proportional to one row instead of the whole file. The tradeoff is repeatability: enumerating the query again rereads and reparses the file, and the file may have changed in between.

**Plausible wrong approach.** Calling `File.ReadAllLines(path)` and then `.ToList()` on the parsed rows makes two full in-memory copies of a large file. Leaving the query deferred and calling `Count()` before the import loop reads the whole file twice.

**How to verify.** Count calls to `Parse` with a counter: one streaming pass over a 1,000-row test file should increment it exactly 1,000 times. Calling `Count()` first should show 2,000.

## Mechanism and diagnostic reasoning

Language Integrated Query expresses sequence transformations such as filtering, projection and ordering. Many LINQ operators produce a recipe rather than immediately executing it. Enumeration runs that recipe. If the source changes before enumeration, the result can change too. This timing is part of the semantics, not an incidental optimization.

Materialization with ToArray or ToList executes a query and stores its current result. It consumes memory but creates a useful snapshot boundary. Repeatedly enumerating an expensive or stateful source can repeat work or observe different data. Decide whether the consumer needs a live recipe, a one-pass stream or a stable materialized result.

`Where` keeps matching elements; `Select` transforms each element. `OrderBy` chooses ordering. `ToArray` materializes. Lambdas used by deferred operators run during enumeration, so avoid hidden side effects.

LINQ syntax does not imply database execution. IEnumerable and IQueryable have different providers and translation boundaries. A deferred query can also fail later than the line that constructed it.

## Review before continuing

Run the reference and confirm that it prints `csharp-020: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
