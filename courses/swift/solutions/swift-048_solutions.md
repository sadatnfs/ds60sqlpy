# swift-048: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-048_solution.swift](swift-048_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Produce a stable completion summary:** The report checks state and identity rather than only a formatted label. One of two uniquely identified items is complete.

**Preserve identity across a value update:** These are the core semantics needed by undo, navigation and persistence. The update retains identity and the prior snapshot.

## Reason through the six tasks

1. **Predict and explain.** Trace one user action from view through model to domain state.

2. **Guided modification.** Add a derived progress summary without duplicating stored completion counts.

3. **Independent construction.** Build and test JourneyCore, then run the complete JourneyApp on a prepared Apple destination.

4. **Diagnose a defect.** Introduce and repair a stale-binding, duplicate-identity or failed-save defect.

5. **Boundary evidence.** Verify empty state, long titles, duplicate IDs, malformed storage and save/reload.

6. **Transfer and justify.** Deliver a project README with architecture, actual platform evidence, accessibility observations, recovery policy and one independently implemented extension.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

The final project connects a portable domain package, a SwiftUI application, stable navigation, editable state and versioned persistence. It remains offline by default so a learner can inspect every meaningful behavior without credentials or a remote service. The architecture has deliberate extension points for networking and additional data models.

A complete capstone includes evidence and limits. Explain which invariants the Linux kernel establishes, which package tests ran, which Apple destination rendered the UI and how saved-state recovery was checked. Keep an unsuccessful observation visible until it is resolved. Expertise grows through independent extensions and diagnosis, not through copying the final source or declaring every possible app scenario covered.

A stable item identity connects domain actions, navigation and saved data. A reducer updates values; a MainActor presentation model owns view state; a persistence adapter encodes the versioned document. Each layer has its own test boundary.

A passing portable reference does not qualify simulator interaction or app signing. Preserve user data when testing failure recovery. Keep scope and evidence honest when adding new frameworks or deployment targets.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
