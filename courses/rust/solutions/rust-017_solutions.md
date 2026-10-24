# rust-017: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-017_solution.rs](rust-017_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use a declared capability:** The consumer needs the capability rather than the concrete field layout. The borrowed trait object exposes pricing behavior.

**Substitute a second policy:** Both implementations preserve input and output units while varying the rule. The same interface admits an uncapped and capped policy.

## Reason through the six tasks

1. **Predict and explain.** Trace the method call to each implementation.

2. **Guided modification.** Add another flat-price value without changing the consumer.

3. **Independent construction.** Define a small trait for a deterministic formatter.

4. **Diagnose a defect.** Diagnose conforming implementations that disagree about units.

5. **Boundary evidence.** Test zero units and the exact cap.

6. **Transfer and justify.** Choose a trait boundary for a file adapter while keeping the domain core pure.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A trait describes capabilities a type provides. A consumer can depend on the capability instead of one representation. A trait implementation must preserve units, valid inputs and failure meaning, not merely compile with the right method names. This makes substitution a behavioral question.

Static dispatch through generics can retain concrete type information, while a trait object supports runtime substitution behind a pointer. Choose based on the API relationship and storage needs. Start with a small pricing capability whose implementations share one clear contract; avoid inventing a trait for every trivial function.

`trait Pricer` declares a method. `impl Pricer for FlatPrice` supplies behavior. `&dyn Pricer` borrows a trait object and uses dynamic dispatch. The receiver &self permits inspection without consuming the implementation.

A matching signature does not establish compatible semantics. Traits and inheritance are different mechanisms. Avoid exposing implementation details merely to make a trait larger.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
