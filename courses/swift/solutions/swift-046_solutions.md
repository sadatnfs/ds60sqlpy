# swift-046: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-046_solution.swift](swift-046_solution.swift). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Separate acceptance categories:** A release checklist should retain missing evidence instead of inferring it from a lower layer. Domain and package evidence do not imply UI or device qualification.

**Require every declared release gate:** Set difference is a simple portable model of honest acceptance accounting. Save/reload remains an explicit incomplete gate.

## Task answers

### Task 1: Predict and explain

Explain what each evidence category proves.

No separate reference answer has been written for this task. Example A is the evidence to compare with: A release checklist should retain missing evidence instead of inferring it from a lower layer. Domain and package evidence do not imply UI or device qualification.

### Task 2: Guided modification

Add save/reload evidence only after actually performing it.

No separate reference answer has been written for this task. Start from Example B: Set difference is a simple portable model of honest acceptance accounting. Save/reload remains an explicit incomplete gate.

### Task 3: Independent construction

Generate JourneyApp, list destinations and run its provided test scheme on an available simulator or macOS destination.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Scheme** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose using a successful archive build as proof of screen-reader usability.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Never commit a personal development team, certificate or provisioning profile. A simulator is not a physical device. Keep test-state cleanup scoped to the app-owned test location.

### Task 5: Boundary evidence

Test fresh launch, saved-state reload and malformed saved-state recovery.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Separate acceptance categories) and Example B (Require every declared release gate).

### Task 6: Transfer and justify

Prepare a release note listing platform, SDK, destination, test results and remaining device/signing limitations.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Scheme**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

App verification has several layers. Domain tests establish rules. Package builds establish module compilation. UI tests establish navigation and interaction in a selected simulator or device configuration. Signing establishes an installable identity under an Apple development team. None of these steps substitutes for the others.

A simulator build can run without provisioning a physical device, while distribution and device installation introduce team, certificate and entitlement requirements. Keep personal signing identifiers out of the shared fixture. The app project is generated locally from an exact reviewed specification, then the learner selects a team only in their own Xcode environment. Record the scheme, destination and observed tests rather than claiming universal platform acceptance.

Xcode schemes choose build/test actions and destinations. xcodebuild -list and -showdestinations reveal actual available options. The fixture provides domain tests plus a UI smoke source to add to the generated project targets.

Never commit a personal development team, certificate or provisioning profile. A simulator is not a physical device. Keep test-state cleanup scoped to the app-owned test location.

## Review before continuing

Run the reference and confirm that it prints `swift-046: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
