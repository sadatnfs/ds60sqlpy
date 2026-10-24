# csharp-048: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-048_solution.cs](csharp-048_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Build a stable valid report:** Sorting and aggregation have independent responsibilities and both are observable. The sorted report is a=3;b=6.

**Preserve rejected data accounting:** A correct result preserves domain distinctions instead of hiding them behind a plausible total. A valid zero remains in the report while two invalid rows are counted.

## Reason through the six tasks

1. **Predict and explain.** Trace every input to an accepted total or a rejection.

2. **Guided modification.** Add an item and update only independently derived expected output.

3. **Independent construction.** Build the external DomainLab and expose the domain contract through the ApiLab adapter.

4. **Diagnose a defect.** Introduce and diagnose a duplicate-aggregation, nullability or cancellation defect.

5. **Boundary evidence.** Document and test empty, malformed, overflow and repeated-operation boundaries.

6. **Transfer and justify.** Deliver a project README with build commands, architecture, failure policies, tests, operational limits and a proposed next extension.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

The final project combines validated input, a pure domain core, deterministic reporting and explicit operational outcomes. A complete application is more than a successful algorithm: it needs a documented build, input contract, failure policy, resource ownership and evidence that its output remains meaningful after changes.

The classroom reference is the portable kernel, and the DomainLab and ApiLab fixtures provide actual multi-file boundaries. Extend them deliberately rather than pasting an entire server into the single source pad. Review normal, rejected and unknown outcomes separately. Expert practice means being able to explain the limits and diagnose an unfamiliar failure, not claiming that a finite tutorial covers every production circumstance.

Compose small functions around explicit record types. Keep parsing, validation, aggregation and presentation separate. Sort output when order is part of the contract; retain rejection evidence alongside accepted totals.

Do not equate a kernel assertion with API, persistence or deployment acceptance. Retain learner data and use owned temporary state for tests. A useful capstone documents what remains intentionally unsupported.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
