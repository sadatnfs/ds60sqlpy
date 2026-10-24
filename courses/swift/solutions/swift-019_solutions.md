# swift-019: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-019_solution.swift](swift-019_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Retain a produced type:** The associated type relationship survives through the generic function. The generic consumer knows the produced value is an Int.

**Hide representation with an opaque result:** The function selects one underlying result type while exposing its element relationship. The caller uses sequence behavior without naming the concrete array type.

## Reason through the six tasks

1. **Predict and explain.** Trace the associated Item type through read.

2. **Guided modification.** Add a String-producing conformance.

3. **Independent construction.** Write a generic transformation preserving the producer item type.

4. **Diagnose a defect.** Explain why returning unrelated concrete types from one opaque-return function is invalid.

5. **Boundary evidence.** Test empty and nonempty opaque sequences.

6. **Transfer and justify.** Choose opaque output or existential storage for an API and document the preserved relationships.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

An associated type names a type relationship inside a protocol. A producer can declare the type of item it produces without fixing that type for every conformer. A generic consumer retains this relationship. Opaque `some` results hide a concrete implementation while preserving one consistent underlying type selected by the function.

Existential `any` values erase more concrete information and can hold different conforming types. These tools solve different problems. Use generics or opaque types when preserving relationships helps the compiler and consumer; use existentials when heterogeneous storage or runtime substitution is the intended feature. Do not choose based only on which spelling makes an error disappear.

`associatedtype Item` names a conformer-selected type. `P.Item` refers to that relationship in generic code. `some Protocol` hides one concrete return type; `any Protocol` stores an existential value.

Some does not mean any arbitrary type at each return. Existential containers can lose relationships needed by generic operations. Compiler diagnostics often point to a missing type relationship rather than a missing cast.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
