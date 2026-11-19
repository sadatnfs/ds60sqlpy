# swift-019: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-019_solution.swift](swift-019_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Retain a produced type:** The associated type relationship survives through the generic function. The generic consumer knows the produced value is an Int.

**Hide representation with an opaque result:** The function selects one underlying result type while exposing its element relationship. The caller uses sequence behavior without naming the concrete array type.

## Task answers

### Task 1: Predict and explain

Trace the associated Item type through read.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The associated type relationship survives through the generic function. The generic consumer knows the produced value is an Int.

### Task 2: Guided modification

Add a String-producing conformance.

No separate reference answer has been written for this task. Start from Example B: The function selects one underlying result type while exposing its element relationship. The caller uses sequence behavior without naming the concrete array type.

### Task 3: Independent construction

Write a generic transformation preserving the producer item type.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
func transformed<P: Producer>(_ producer: P, _ change: (P.Item) -> P.Item) -> P.Item {
  change(producer.produce())
}
let value: Int = transformed(IntegerSource()) { $0 + 1 }
precondition(value == 8)
```

**Observe:** Transforming the produced 7 gives 8, still an Int.

The signature uses P.Item for both input and output, so the compiler guarantees the item type is preserved.

### Task 4: Diagnose a defect

Explain why returning unrelated concrete types from one opaque-return function is invalid.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Some does not mean any arbitrary type at each return. Existential containers can lose relationships needed by generic operations. Compiler diagnostics often point to a missing type relationship rather than a missing cast.

### Task 5: Boundary evidence

Test empty and nonempty opaque sequences.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Retain a produced type) and Example B (Hide representation with an opaque result).

### Task 6: Transfer and justify

Choose opaque output or existential storage for an API and document the preserved relationships.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Associated type**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

An associated type names a type relationship inside a protocol. A producer can declare the type of item it produces without fixing that type for every conformer. A generic consumer retains this relationship. Opaque `some` results hide a concrete implementation while preserving one consistent underlying type selected by the function.

Existential `any` values erase more concrete information and can hold different conforming types. These tools solve different problems. Use generics or opaque types when preserving relationships helps the compiler and consumer; use existentials when heterogeneous storage or runtime substitution is the intended feature. Do not choose based only on which spelling makes an error disappear.

`associatedtype Item` names a conformer-selected type. `P.Item` refers to that relationship in generic code. `some Protocol` hides one concrete return type; `any Protocol` stores an existential value.

Some does not mean any arbitrary type at each return. Existential containers can lose relationships needed by generic operations. Compiler diagnostics often point to a missing type relationship rather than a missing cast.

## Review before continuing

Run the reference and confirm that it prints `swift-019: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
