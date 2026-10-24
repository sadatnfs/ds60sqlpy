# csharp-007: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-007_solution.cs](csharp-007_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Return a transformed value:** The parameter receives a value. Returning a transformed value does not reassign the caller variable. The result is 14 and the caller still holds 7.

**Expose rejection as part of the contract:** A precise function name and guard prevent accidental truncation from masquerading as a valid result. 12 divided by 3 returns 4; the exact-integer contract rejects 7 divided by 2.

## Reason through the six tasks

1. **Predict and explain.** Trace the caller and parameter values through Double.

2. **Guided modification.** Add a Triple function and test zero and a negative input.

3. **Independent construction.** Write a method computing an area from validated nonnegative dimensions.

4. **Diagnose a defect.** Diagnose a function whose name promises exact division but silently truncates.

5. **Boundary evidence.** Test zero divisors and non-divisible inputs separately.

6. **Transfer and justify.** Extract one computation from a larger program and state its input, output, mutation and failure contract.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A method gives a computation a name and a boundary. Its contract states accepted inputs, its result, state changes and failure behavior. Splitting code into methods helps only when those boundaries expose meaning. A helper that secretly edits unrelated state is harder to reason about than one returning a clearly defined result.

C# normally passes arguments by value. For a value type, that means a copied value; for an object reference, it means a copied reference to the same object. The distinction becomes important later. Start with small pure methods, which depend only on arguments and return a result without observable mutation. They are easy to test because the same inputs produce the same outputs.

`int Double(int value) => value * 2` declares a local function with a typed parameter and return. `return` ends the current method. `ref` and `out` are explicit parameter passing modes, not decorations; prefer ordinary return values until shared mutation is required.

A method name is part of the interface. A generic catch returning zero can make rejected input indistinguishable from a valid zero result. Prefer one clear responsibility over a long list of optional switches.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
