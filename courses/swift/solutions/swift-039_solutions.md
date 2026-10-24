# swift-039: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-039_solution.swift](swift-039_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Apply a domain action:** A pure transition supports undo, testing and separate UI rendering. The transformed item changes completion while retaining the original value.

**Keep identity stable during edits:** Stable identity lets navigation, persistence and UI reconciliation refer to the same domain item. Completion changes do not manufacture a new identity.

## Reason through the six tasks

1. **Predict and explain.** Identify domain and presentation responsibilities.

2. **Guided modification.** Add a pure rename operation with nonempty-title validation.

3. **Independent construction.** Build and test JourneyCore before opening the Apple app.

4. **Diagnose a defect.** Diagnose placing file access directly inside a model property getter.

5. **Boundary evidence.** Test unknown identity and duplicate identity admission.

6. **Transfer and justify.** Draw the dependency direction among core, persistence adapter, view model and SwiftUI views.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

An app is a set of responsibilities with different lifetimes: domain rules, presentation state, views, persistence and external services. A portable domain core lets Linux tests establish business behavior independently of Apple UI rendering. The app adapter then translates user actions into core operations and renders their outcomes.

The JourneyCore package and JourneyApp fixture implement this separation with a small study planner. A lesson item has stable identity, title and completion state. The core rejects empty titles and duplicate identities. SwiftUI presents and edits those values on Apple platforms. Linux can compile and test the core, but cannot qualify view layout, accessibility or simulator behavior.

A struct model conforms to Identifiable, Codable, Equatable and Sendable where appropriate. A pure reducer maps a state plus action to a new state. The app owns presentation and storage adapters.

A successful core test does not prove app rendering. Stable identity must survive edits and reloads. Keep domain validation outside UI-only button enablement.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
