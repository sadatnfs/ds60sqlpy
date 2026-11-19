# csharp-037: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-037_solution.cs](csharp-037_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Count a linear search:** The deterministic count illustrates the algorithm independently of machine speed. Finding the last element needs four comparisons.

**Trade memory for repeated membership:** Building and retaining the index has a cost that should be amortized across enough queries. The index answers membership while storing four identities.

## Task answers

### Task 1: Predict and explain

Count comparisons for first, last and absent targets.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The deterministic count illustrates the algorithm independently of machine speed. Finding the last element needs four comparisons.

### Task 2: Guided modification

Double the input size and predict worst-case linear comparisons.

No separate reference answer has been written for this task. Start from Example B: Building and retaining the index has a cost that should be amortized across enough queries. The index answers membership while storing four identities.

### Task 3: Independent construction

Compare repeated list scans with one built index while preserving equality policy.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
string[] names = { "Pear", "apple", "Fig" };
string[] queries = { "PEAR", "fig", "kiwi" };
var policy = StringComparison.OrdinalIgnoreCase;
bool Scan(string q) => names.Any(n => string.Equals(n, q, policy));
int scanHits = queries.Count(Scan);
var index = new HashSet<string>(names, StringComparer.OrdinalIgnoreCase);
int indexHits = queries.Count(index.Contains);
Check(scanHits == 2 && indexHits == scanHits, "same answers");
```

**Observe:** Both approaches find 2 of the 3 queries.

The index uses the same OrdinalIgnoreCase policy as the scan, so it answers identically while replacing a linear search per query with one hash lookup.

### Task 4: Diagnose a defect

Diagnose a benchmark that excludes index construction from a one-shot workload.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A single stopwatch sample is not reliable evidence. Expected hash lookup cost depends on hashing behavior. Do not optimize a micro-operation before identifying the dominant algorithm or I/O cost.

### Task 5: Boundary evidence

Test duplicate inputs and empty queries.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Count a linear search) and Example B (Trade memory for repeated membership).

### Task 6: Transfer and justify

Write a benchmark plan specifying workload, correctness checks, warmup and allocation measurements.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Complexity**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Performance begins with an explicit workload and cost model. A nested search can perform quadratically many comparisons, while an indexed lookup may trade memory for near-constant expected lookup cost. Big-O describes growth, not an exact elapsed time or a universal ranking. Constant factors, data layout and input size matter.

Measure correctness separately from speed. A benchmark that computes a different result is irrelevant. Warmup, allocation, runtime optimization and background load can distort tiny timings. The classroom counts deterministic operations to explain growth; a prepared external benchmark project is the right place for statistically meaningful elapsed-time comparisons.

HashSet membership can avoid repeated linear scans. Distinct and grouping have equality-policy assumptions. Count comparisons in a fixture instead of asserting a fragile timing threshold.

A single stopwatch sample is not reliable evidence. Expected hash lookup cost depends on hashing behavior. Do not optimize a micro-operation before identifying the dominant algorithm or I/O cost.

## Review before continuing

Run the reference and confirm that it prints `csharp-037: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
