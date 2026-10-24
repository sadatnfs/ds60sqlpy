# swift-012: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-012_solution.swift](swift-012_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Keep copied value state independent:** The struct contains value state and its mutation is explicit. Reserving from the copied inventory does not change the original.

**Reject without partial mutation:** Checking every rejection condition before subtraction preserves failure atomicity. Rejected requests retain the previous valid stock.

## Reason through the six tasks

1. **Predict and explain.** Trace both inventory copies through reservation.

2. **Guided modification.** Add a validated restock operation.

3. **Independent construction.** Build a bounded counter with private mutation.

4. **Diagnose a defect.** Diagnose subtracting stock before checking the requested amount.

5. **Boundary evidence.** Test zero, exact-stock and excess reservations.

6. **Transfer and justify.** Choose a value model for an editable form and explain how cancel can restore an earlier snapshot.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A struct models a value with named properties and operations. Assignment follows value semantics, making independent state snapshots straightforward when its stored members also have appropriate semantics. A mutating method explicitly changes self or its stored properties. Methods without mutating cannot silently alter a value-type instance.

Constructors should establish valid state, and operations should preserve it. Do not expose unrestricted writable fields if they allow callers to bypass the rule. A small value type can be a strong domain boundary, but wrapping a primitive without adding meaning or validation is only extra syntax.

`struct Inventory` defines a value type. `private(set)` exposes reading but restricts assignment. A `mutating func` may update stored state. An initializer can reject invalid input with a throwing or failable contract in later chapters.

A struct can contain shared class references. Private setters are useful only when methods enforce invariants. The public memberwise initializer in a small fixture is not a substitute for validating external state.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
