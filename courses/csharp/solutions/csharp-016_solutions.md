# csharp-016: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-016_solution.cs](csharp-016_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Aggregate repeated valid items:** Repeated identities accumulate after validation rather than creating ambiguous duplicate dictionary entries. Pear totals 6 and apple totals 3.

**Retain rejection evidence:** Malformed and negative quantities remain excluded, and empty input produces an empty report rather than an invented item. Three rejected lines do not alter the valid pear total.

## Reason through the six tasks

1. **Predict and explain.** Trace each input through validation and accumulation.

2. **Guided modification.** Add one valid duplicate and predict the new total before running.

3. **Independent construction.** Build a sorted text report from the accepted dictionary and the rejection count.

4. **Diagnose a defect.** Diagnose an importer that ignores TryParse failure and inserts zero.

5. **Boundary evidence.** Test empty item names, extra fields, zero quantity and empty input.

6. **Transfer and justify.** Design a reusable import result that retains per-line rejection reasons without exposing sensitive raw input.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A useful first project combines parsing, representation and aggregation while keeping their responsibilities separate. The input boundary rejects malformed quantities. The domain representation preserves item identity. The report stage summarizes only accepted records. Mixing these stages often creates a subtle bug: a failed parse becomes zero and then appears as valid data.

This project uses in-memory fixture lines so it runs offline without interactive input. It reports accepted totals and rejected line counts independently. A real importer would also record line identity and a safe reason. Build the smallest end-to-end path first, then introduce invalid and duplicate inputs. The final result must explain what happened, not merely produce a total that looks plausible.

`Split` produces fields; check the field count before indexing. `TryParse` separates syntax from a valid integer. `TryGetValue` supports accumulating repeated keys. Sorting keys before display gives a stable report.

Checking field count after indexing is too late. Case policy affects identity and must be documented. Extremely large totals can overflow, so checked accumulation belongs in a production input contract.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
