# swift-018: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-018_solution.swift](swift-018_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Reuse an ordering mechanism:** The Comparable requirement makes ordering available without dynamic casts. One implementation preserves Int and String results.

**Preserve container element type:** The relationship is encoded in the type rather than a runtime convention. Swapping retains the same concrete element type.

## Reason through the six tasks

1. **Predict and explain.** Identify inferred generic types at every call.

2. **Guided modification.** Use larger with Double values and a tie.

3. **Independent construction.** Create a generic immutable triple with a rotation operation.

4. **Diagnose a defect.** Diagnose calling an unavailable method on an unconstrained T.

5. **Boundary evidence.** State tie behavior and test equal inputs.

6. **Transfer and justify.** Choose generic or existential abstraction for an API that must preserve concrete result type.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Generics preserve type relationships across an algorithm or container. A generic pair stores two values of the same chosen type. The compiler rejects mixing unrelated types unless the API explicitly models that possibility. This is stronger and clearer than storing Any and casting later.

Constraints expose the capabilities an algorithm needs. Comparable permits ordering, while Equatable permits equality. Use the narrowest useful constraint and state behavior for ties and empty inputs. Generic abstraction is valuable when it removes duplicated mechanisms without erasing domain meaning.

`func larger<T: Comparable>` introduces a constrained type parameter. The return type T preserves the input relationship. Generic structs use the same parameter syntax.

Any discards useful type information. Excessively broad constraints make reuse harder. A generic algorithm still needs domain-specific failure and ordering policies.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
