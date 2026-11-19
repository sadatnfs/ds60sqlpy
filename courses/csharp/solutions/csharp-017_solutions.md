# csharp-017: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-017_solution.cs](csharp-017_solution.cs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use a declared contract:** The consumer depends on the interface rather than the concrete class. Four units cost 12 and zero units cost zero.

**Change policy without changing the consumer:** An implementation can change the pricing rule while preserving units and accepted inputs. The same consumer applies a capped or uncapped policy.

## Task answers

### Task 1: Predict and explain

Trace the interface call to the selected implementation.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The consumer depends on the interface rather than the concrete class. Four units cost 12 and zero units cost zero.

### Task 2: Guided modification

Add a second flat rate and keep Total unchanged.

No separate reference answer has been written for this task. Start from Example B: An implementation can change the pricing rule while preserving units and accepted inputs. The same consumer applies a capped or uncapped policy.

### Task 3: Independent construction

Define a small interface for a deterministic label formatter.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Interface** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose an implementation returning cents where the contract requires whole currency units.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Identical signatures do not imply compatible semantics. Avoid interfaces that expose every private implementation detail. Validate domain ranges consistently across implementations.

### Task 5: Boundary evidence

Test zero and a value exactly at the cap.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Use a declared contract) and Example B (Change policy without changing the consumer).

### Task 6: Transfer and justify

Choose one dependency worth injecting in the inventory importer and explain the testing benefit.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Interface**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

An interface states what a consumer may ask a component to do. It does not promise that every implementation has the same internal representation. A useful interface captures a stable responsibility: calculating a price, reading a record or producing a time value. Interfaces invented for every class can add indirection without improving the design.

Substitution is behavioral. Two implementations with the same method signature can still disagree about nulls, errors or units. Write those contracts and test the consumer with more than one implementation. This is also the beginning of dependency injection: a caller supplies the collaborator instead of letting the consumer construct an invisible global dependency.

`interface IRate` declares a method contract. A class implements that interface and supplies the method body. A variable typed as the interface exposes the contract, while dynamic dispatch chooses the implementation.

Identical signatures do not imply compatible semantics. Avoid interfaces that expose every private implementation detail. Validate domain ranges consistently across implementations.

## Review before continuing

Run the reference and confirm that it prints `csharp-017: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
