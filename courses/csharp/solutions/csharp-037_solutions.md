# csharp-037: explanation and comparison

Reference program: [csharp-037_solution.cs](csharp-037_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Count a linear search:** The deterministic count illustrates the algorithm independently of machine speed. Finding the last element needs four comparisons.

**Trade memory for repeated membership:** Building and retaining the index has a cost that should be amortized across enough queries. The index answers membership while storing four identities.

## Task answers

### Task 1: Predict and explain

Count comparisons for first, last and absent targets.

**Written answer.** For `{ 2, 4, 6, 8 }`: target 2 takes 1 comparison, target 8 takes 4, and an absent target such as 9 also takes 4, because the loop must check every element before it can report absence.

**Why it is correct.** `comparisons++` runs once per visited element and `break` stops on the first match, so the count equals the matched position, or the length when nothing matches.

**Plausible wrong approach.** Predicting that an absent target is cheap because nothing is found treats absence as an early exit. Without a match there is no `break`, so absence is a worst case.

**How to verify.** Wrap the loop as `int Count(int target)` and check `Count(2) == 1`, `Count(8) == 4` and `Count(9) == 4`.

### Task 2: Guided modification

Double the input size and predict worst-case linear comparisons.

**Written answer.** With 8 values `{ 2, 4, ..., 16 }`, the worst case, last element or absent, needs 8 comparisons. Doubling the input from 4 to 8 doubles the worst case: linear growth.

**Why it is correct.** Each element is compared at most once, and the worst case visits all of them, so the count grows in proportion to the length.

**Plausible wrong approach.** Predicting 5 comparisons assumes the search halves its range like binary search. This loop has no ordering logic, and on unsorted data halving would not even be correct.

**How to verify.** Check `Count(16) == 8` and `Count(17) == 8` on the 8-element array, and `Count(2) == 1` still.

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

**Plausible wrong approach.** Building the index with `new HashSet<string>(names)` uses the default ordinal, case-sensitive comparer. `"PEAR"` and `"fig"` are then not found, `indexHits` is 0 while `scanHits` is 2, and the `same answers` check throws.

**How to verify.** The block checks both approaches find 2. Add `"APPLE"` to the queries and expect 3 from both; that shows the comparer, not the data, decides membership.

### Task 4: Diagnose a defect

Diagnose a benchmark that excludes index construction from a one-shot workload.

**Written answer.** For a one-shot workload, one query against 1,000 names, a benchmark that builds the `HashSet` outside the timed region and times only `Contains` shows the index winning. The real job must also pay for construction: 1,000 hashes and inserts, versus at most 1,000 comparisons for one scan.

**Why it is correct.** The measured region must match the workload. Construction is amortized only across many queries; with one query it is the dominant cost.

**Plausible wrong approach.** Running the timed `Contains` call 1,000 times to get a steadier number measures a many-query workload. The figure is more stable but still answers a different question.

**How to verify.** Count operations instead of timing: include the 1,000 insertions with the single lookup and compare with the scan's comparison count. The scan wins for one query; the index wins once queries are numerous.

### Task 5: Boundary evidence

Test duplicate inputs and empty queries.

**Written answer.** With `names = { "a", "A", "a" }` and `OrdinalIgnoreCase`, the set holds 1 entry, yet the scan and the index both find `"A"`. With an empty query array both report 0 hits, and a query of `""` is not found.

**Why it is correct.** The set collapses duplicates under its comparer, but membership answers are unchanged, so hit counts still agree.

**Plausible wrong approach.** Using `index.Count` as the number of names loaded reports 1 instead of 3. A check `index.Count == names.Length` fails on any input with duplicates under the comparer.

**How to verify.** Check `index.Count == 1`, that `scanHits == indexHits` for queries `{ "A", "" }`, and that both are 0 for `Array.Empty<string>()`.

### Task 6: Transfer and justify

Write a benchmark plan specifying workload, correctness checks, warmup and allocation measurements.

**Written answer.** Workload: 10,000 names with 1, 100 and 10,000 queries, half of them hits. Correctness: before any timing, check the scan and the index return identical hit counts for each case. Warmup: run each method before measuring, ideally with BenchmarkDotNet in a separate project. Allocations: record bytes per operation for each method.

**Why it is correct.** Each element removes one distortion: wrong answers, JIT compilation and tiering, and allocation costs that show up later as collections. Reporting the median of many iterations avoids trusting one sample.

**Plausible wrong approach.** Timing the first call of each method with one `Stopwatch` measures JIT compilation as much as the algorithm, and the order in which the methods run can decide the winner.

**How to verify.** Break the index comparer on purpose and confirm the plan's correctness check fails before any time is reported.

## Mechanism and diagnostic reasoning

Performance begins with an explicit workload and cost model. A nested search can perform quadratically many comparisons, while an indexed lookup may trade memory for near-constant expected lookup cost. Big-O describes growth, not an exact elapsed time or a universal ranking. Constant factors, data layout and input size matter.

Measure correctness separately from speed. A benchmark that computes a different result is irrelevant. Warmup, allocation, runtime optimization and background load can distort tiny timings. The classroom counts deterministic operations to explain growth; a prepared external benchmark project is the right place for statistically meaningful elapsed-time comparisons.

HashSet membership can avoid repeated linear scans. Distinct and grouping have equality-policy assumptions. Count comparisons in a fixture instead of asserting a fragile timing threshold.

A single stopwatch sample is not reliable evidence. Expected hash lookup cost depends on hashing behavior. Do not optimize a micro-operation before identifying the dominant algorithm or I/O cost.

## Review before continuing

Run the reference and confirm it prints `csharp-037: passed`, then rerun the guide's counterexample.
