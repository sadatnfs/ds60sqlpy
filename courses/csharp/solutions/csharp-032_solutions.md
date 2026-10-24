# csharp-032: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-032_solution.cs](csharp-032_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Import valid and invalid records:** Validation remains visible in the result instead of silently converting bad records into ordinary data. The service returns total 2 and one rejected record.

**Cancellation is not an empty report:** The result category carries meaning beyond a numeric total. A cancelled request and a successful empty import have different outcomes.

## Reason through the six tasks

1. **Predict and explain.** Trace syntax, validation and aggregation as separate stages.

2. **Guided modification.** Add a duplicate valid name and document whether total quantity or distinct count is reported.

3. **Independent construction.** Build a per-item result while preserving the rejected count.

4. **Diagnose a defect.** Diagnose catch-all logic returning an empty report after cancellation.

5. **Boundary evidence.** Test malformed JSON, JSON null, an empty list and invalid quantities.

6. **Transfer and justify.** Design an adapter boundary for a file or HTTP source without putting I/O inside the pure aggregation.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

The intermediate project separates a transport representation, validation, a pure aggregation and an asynchronous service boundary. This makes failure location visible. JSON syntax errors belong to decoding; invalid records belong to domain validation; a cancelled operation must not be presented as an empty successful import.

A complete service also owns its dependency lifetime and result shape. The classroom version uses an in-memory JSON payload, avoiding external I/O while preserving the same boundary decisions. A production adapter can load bytes from a file or HTTP response, then call the same pure core. Keep the core deterministic so integration failures do not obscure calculation errors.

An async method can validate cancellation before admitting work and return a record describing accepted totals and rejected counts. Immutable result fields make it easier to store a receipt without later mutation.

A transport DTO is not automatically a trusted domain object. Do not merge cancelled, invalid and successfully empty results into one representation. An async signature alone does not make CPU work asynchronous.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
