# swift-017: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-017_solution.swift](swift-017_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use a capability:** The interface preserves units and result meaning while hiding representation. The consumer calls the pricing capability without needing its storage details.

**Substitute another policy:** Substitution allows variation within the documented contract, not arbitrary semantic disagreement. Two conforming policies produce different valid prices.

## Task answers

### Task 1: Predict and explain

Trace the protocol call to each concrete implementation.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The interface preserves units and result meaning while hiding representation. The consumer calls the pricing capability without needing its storage details.

### Task 2: Guided modification

Add a second flat price without changing the consumer.

No separate reference answer has been written for this task. Start from Example B: Substitution allows variation within the documented contract, not arbitrary semantic disagreement. Two conforming policies produce different valid prices.

### Task 3: Independent construction

Define a protocol for a deterministic label formatter.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
let formatter: any LabelFormatter = PluralFormatter()
precondition(formatter.label(for: 1) == "1 item")
precondition(formatter.label(for: 3) == "3 items")
precondition(formatter.label(for: 3) == formatter.label(for: 3))
```

**Observe:** The formatter produces 1 item and 3 items, identically on every call.

The protocol states the contract and the conforming type depends only on its input, so its labels are deterministic.

### Task 4: Diagnose a defect

Diagnose two conformers using incompatible units.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A protocol is not automatically a good abstraction for every type. Default extension methods not declared as requirements can have surprising static dispatch. Preserve behavior and error semantics across conformers.

### Task 5: Boundary evidence

Test zero units and the exact cap.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Use a capability) and Example B (Substitute another policy).

### Task 6: Transfer and justify

Choose a dependency worth abstracting in the importer and explain why a protocol helps.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Protocol**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A protocol declares capabilities that a conforming type must supply. It lets a consumer depend on a behavior rather than one storage representation. Both structs and classes can conform, which separates the choice of value or reference semantics from the public capability.

A conforming type must preserve the behavioral contract, not just compile with the right method names. Specify units, invalid inputs and mutation. Protocol extensions can share default behavior, but dispatch differences matter when a method is not a protocol requirement. Begin with explicit requirements and test the consumer with distinct implementations.

`protocol Pricer` declares a required method. A type lists conformance after a colon. `any Pricer` is an existential container that can hold differing conforming concrete types behind the protocol interface.

A protocol is not automatically a good abstraction for every type. Default extension methods not declared as requirements can have surprising static dispatch. Preserve behavior and error semantics across conformers.

## Review before continuing

Run the reference and confirm that it prints `swift-017: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
