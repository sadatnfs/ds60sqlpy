# swift-008: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-008_solution.swift](swift-008_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Name the dimensions:** Readable call sites reduce accidental parameter swaps and reveal the function purpose. Labels show which dimension each argument supplies.

**Make mutation explicit:** The ampersand makes the mutation boundary visible instead of hiding it behind a normal-looking value call. The caller explicitly grants mutation and observes 5.

## Reason through the six tasks

1. **Predict and explain.** Explain each argument label and local parameter name.

2. **Guided modification.** Add a depth label for a volume function.

3. **Independent construction.** Write a pure function normalizing a quantity without mutating its caller.

4. **Diagnose a defect.** Diagnose an inout call missing the ampersand and explain the compiler rule.

5. **Boundary evidence.** Test zero and negative dimensions under a documented validation policy.

6. **Transfer and justify.** Choose return values or inout for an API and justify who owns state changes.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A function groups a computation behind a contract. Swift distinguishes the argument label read at the call site from the parameter name used inside the body. Labels can make an API read as a clear operation rather than an unexplained list of positional values. Use the underscore label only when the surrounding context already makes the meaning clear.

Ordinary value arguments are passed with value semantics. An inout parameter explicitly grants temporary mutation of the caller value under Swift exclusivity rules. Prefer returned values for pure transformations and use inout when mutation is the actual interface. A function contract should state invalid-input behavior and whether any state changes before failure.

`func area(width: Int, height: Int) -> Int` exposes labels. `_ value` removes the external label. `inout` in a declaration pairs with `&` at the call site. `return` supplies the result and exits.

Labels are part of API usability. Inout access cannot overlap conflicting access to the same storage. Do not use mutation merely to avoid returning a small value.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
