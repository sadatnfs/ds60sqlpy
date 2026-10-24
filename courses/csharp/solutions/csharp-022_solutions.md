# csharp-022: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-022_solution.cs](csharp-022_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Consume only a prefix:** The producer does not need to allocate all four outputs before serving the first one. The consumer receives 5 and 6 and can stop before the full range.

**Validate before returning the sequence:** The outer method validates first; the local iterator performs only the admitted traversal. Negative count is rejected immediately, without enumeration.

## Reason through the six tasks

1. **Predict and explain.** Trace how many values Take(2) requests.

2. **Guided modification.** Generate every second integer with a bounded count.

3. **Independent construction.** Implement a lazy sequence of cumulative totals.

4. **Diagnose a defect.** Diagnose validation inside an iterator body that callers expect to run immediately.

5. **Boundary evidence.** Test count zero, one and negative.

6. **Transfer and justify.** Choose a sequence API for a large file and document repeated-enumeration and resource-lifetime behavior.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

An iterator describes a sequence whose values are produced as the consumer asks for them. It can avoid materializing a large collection and can stop work when the consumer stops early. `yield return` pauses the iterator with its local state retained; the next request resumes it. This is different from returning a fully constructed list.

Lazy code shifts both work and some errors into enumeration. If argument validation must happen at the call site, place it outside the iterator body and return a nested iterator. Resource-owning iterators must also release resources when enumeration is abandoned. Consumers using foreach receive disposal behavior; custom enumerator handling must preserve it.

`IEnumerable<int>` exposes an iterable sequence. `yield return value` supplies one element and suspends. A nested local iterator separates immediate argument validation from delayed generation.

A sequence is not necessarily repeatable or cheap to enumerate. Do not assume calling an iterator method executes its body. Overflow remains possible even in a lazy generator.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
