# csharp-017: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-017_solution.cs](csharp-017_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use a declared contract:** The consumer depends on the interface rather than the concrete class. Four units cost 12 and zero units cost zero.

**Change policy without changing the consumer:** An implementation can change the pricing rule while preserving units and accepted inputs. The same consumer applies a capped or uncapped policy.

## Reason through the six tasks

1. **Predict and explain.** Trace the interface call to the selected implementation.

2. **Guided modification.** Add a second flat rate and keep Total unchanged.

3. **Independent construction.** Define a small interface for a deterministic label formatter.

4. **Diagnose a defect.** Diagnose an implementation returning cents where the contract requires whole currency units.

5. **Boundary evidence.** Test zero and a value exactly at the cap.

6. **Transfer and justify.** Choose one dependency worth injecting in the inventory importer and explain the testing benefit.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

An interface states what a consumer may ask a component to do. It does not promise that every implementation has the same internal representation. A useful interface captures a stable responsibility: calculating a price, reading a record or producing a time value. Interfaces invented for every class can add indirection without improving the design.

Substitution is behavioral. Two implementations with the same method signature can still disagree about nulls, errors or units. Write those contracts and test the consumer with more than one implementation. This is also the beginning of dependency injection: a caller supplies the collaborator instead of letting the consumer construct an invisible global dependency.

`interface IRate` declares a method contract. A class implements that interface and supplies the method body. A variable typed as the interface exposes the contract, while dynamic dispatch chooses the implementation.

Identical signatures do not imply compatible semantics. Avoid interfaces that expose every private implementation detail. Validate domain ranges consistently across implementations.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
