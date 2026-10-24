# csharp-013: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-013_solution.cs](csharp-013_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Preserve a nonnegative balance:** Validate affordability before subtraction so rejected requests cannot corrupt state. Spending 4 succeeds; spending 7 afterward fails without changing 6.

**Reject malformed operations:** These are separate boundary policies. Both preserve the invariant, but they communicate different meanings to the caller. Negative spending is rejected and zero is an accepted no-op.

## Reason through the six tasks

1. **Predict and explain.** Trace the wallet state through successful and rejected spending.

2. **Guided modification.** Add a validated deposit operation.

3. **Independent construction.** Implement a bounded inventory whose reservations never make stock negative.

4. **Diagnose a defect.** Diagnose subtracting before checking affordability.

5. **Boundary evidence.** Test exactly the available amount, zero and a negative request.

6. **Transfer and justify.** Explain whether a shared wallet needs synchronization when several tasks may spend concurrently.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A class can protect a state transition by admitting changes only through reviewed operations. A constructor establishes the initial invariant; methods preserve it. Private setters are useful only when the public operations actually enforce the domain rule. A property named Balance that any caller can replace with a negative number has no meaningful protection.

Model expected rejection distinctly from programming defects. A withdrawal larger than the available balance can be a normal false result. A negative withdrawal is malformed input and may merit an argument exception. State should remain unchanged on rejected operations. This failure atomicity is often more important than a compact implementation.

A constructor has the class name and no return type. `private set` permits mutation inside the class. `sealed` prevents inheritance when extension is not part of the design. Guard clauses reject invalid inputs before state changes.

Private fields alone do not establish a correct contract. A partially mutated object after failure can poison later operations. This class is intentionally single-threaded; encapsulation does not itself provide synchronization.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
