# swift-046: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-046_solution.swift](swift-046_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Separate acceptance categories:** A release checklist should retain missing evidence instead of inferring it from a lower layer. Domain and package evidence do not imply UI or device qualification.

**Require every declared release gate:** Set difference is a simple portable model of honest acceptance accounting. Save/reload remains an explicit incomplete gate.

## Reason through the six tasks

1. **Predict and explain.** Explain what each evidence category proves.

2. **Guided modification.** Add save/reload evidence only after actually performing it.

3. **Independent construction.** Generate JourneyApp, list destinations and run its provided test scheme on an available simulator or macOS destination.

4. **Diagnose a defect.** Diagnose using a successful archive build as proof of screen-reader usability.

5. **Boundary evidence.** Test fresh launch, saved-state reload and malformed saved-state recovery.

6. **Transfer and justify.** Prepare a release note listing platform, SDK, destination, test results and remaining device/signing limitations.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

App verification has several layers. Domain tests establish rules. Package builds establish module compilation. UI tests establish navigation and interaction in a selected simulator or device configuration. Signing establishes an installable identity under an Apple development team. None of these steps substitutes for the others.

A simulator build can run without provisioning a physical device, while distribution and device installation introduce team, certificate and entitlement requirements. Keep personal signing identifiers out of the shared fixture. The app project is generated locally from an exact reviewed specification, then the learner selects a team only in their own Xcode environment. Record the scheme, destination and observed tests rather than claiming universal platform acceptance.

Xcode schemes choose build/test actions and destinations. xcodebuild -list and -showdestinations reveal actual available options. The fixture provides domain tests plus a UI smoke source to add to the generated project targets.

Never commit a personal development team, certificate or provisioning profile. A simulator is not a physical device. Keep test-state cleanup scoped to the app-owned test location.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
