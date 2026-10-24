# csharp-037: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-037_solution.cs](csharp-037_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Count a linear search:** The deterministic count illustrates the algorithm independently of machine speed. Finding the last element needs four comparisons.

**Trade memory for repeated membership:** Building and retaining the index has a cost that should be amortized across enough queries. The index answers membership while storing four identities.

## Reason through the six tasks

1. **Predict and explain.** Count comparisons for first, last and absent targets.

2. **Guided modification.** Double the input size and predict worst-case linear comparisons.

3. **Independent construction.** Compare repeated list scans with one built index while preserving equality policy.

4. **Diagnose a defect.** Diagnose a benchmark that excludes index construction from a one-shot workload.

5. **Boundary evidence.** Test duplicate inputs and empty queries.

6. **Transfer and justify.** Write a benchmark plan specifying workload, correctness checks, warmup and allocation measurements.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Performance begins with an explicit workload and cost model. A nested search can perform quadratically many comparisons, while an indexed lookup may trade memory for near-constant expected lookup cost. Big-O describes growth, not an exact elapsed time or a universal ranking. Constant factors, data layout and input size matter.

Measure correctness separately from speed. A benchmark that computes a different result is irrelevant. Warmup, allocation, runtime optimization and background load can distort tiny timings. The classroom counts deterministic operations to explain growth; a prepared external benchmark project is the right place for statistically meaningful elapsed-time comparisons.

HashSet membership can avoid repeated linear scans. Distinct and grouping have equality-policy assumptions. Count comparisons in a fixture instead of asserting a fragile timing threshold.

A single stopwatch sample is not reliable evidence. Expected hash lookup cost depends on hashing behavior. Do not optimize a micro-operation before identifying the dominant algorithm or I/O cost.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
