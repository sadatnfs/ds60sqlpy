# swift-017: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-017_solution.swift](swift-017_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use a capability:** The interface preserves units and result meaning while hiding representation. The consumer calls the pricing capability without needing its storage details.

**Substitute another policy:** Substitution allows variation within the documented contract, not arbitrary semantic disagreement. Two conforming policies produce different valid prices.

## Reason through the six tasks

1. **Predict and explain.** Trace the protocol call to each concrete implementation.

2. **Guided modification.** Add a second flat price without changing the consumer.

3. **Independent construction.** Define a protocol for a deterministic label formatter.

4. **Diagnose a defect.** Diagnose two conformers using incompatible units.

5. **Boundary evidence.** Test zero units and the exact cap.

6. **Transfer and justify.** Choose a dependency worth abstracting in the importer and explain why a protocol helps.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A protocol declares capabilities that a conforming type must supply. It lets a consumer depend on a behavior rather than one storage representation. Both structs and classes can conform, which separates the choice of value or reference semantics from the public capability.

A conforming type must preserve the behavioral contract, not just compile with the right method names. Specify units, invalid inputs and mutation. Protocol extensions can share default behavior, but dispatch differences matter when a method is not a protocol requirement. Begin with explicit requirements and test the consumer with distinct implementations.

`protocol Pricer` declares a required method. A type lists conformance after a colon. `any Pricer` is an existential container that can hold differing conforming concrete types behind the protocol interface.

A protocol is not automatically a good abstraction for every type. Default extension methods not declared as requirements can have surprising static dispatch. Preserve behavior and error semantics across conformers.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
