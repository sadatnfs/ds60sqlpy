# swift-046: App tests, simulator evidence and signing

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-045`

## Learning objectives

Generate JourneyApp, list destinations and run its provided test scheme on an available simulator or macOS destination. Then prepare a release note listing platform, SDK, destination, test results and remaining device/signing limitations.

## Purpose and mental model

App verification has several layers. Domain tests establish rules. Package builds establish module compilation. UI tests establish navigation and interaction in a selected simulator or device configuration. Signing establishes an installable identity under an Apple development team. None of these steps substitutes for the others.

A simulator build can run without provisioning a physical device, while distribution and device installation introduce team, certificate and entitlement requirements. Keep personal signing identifiers out of the shared fixture. The app project is generated locally from an exact reviewed specification, then the learner selects a team only in their own Xcode environment. Record the scheme, destination and observed tests rather than claiming universal platform acceptance.

## Vocabulary and concepts

**Scheme:** A named set of Xcode build, test and run actions.

**Simulator:** A prepared Apple-platform execution environment for testing.

**Signing:** Associating an app artifact with a development or distribution identity.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

Follow [JourneyApp build and test commands](../fixtures/JourneyApp/README.md). The repository does not claim those Apple-platform commands have run merely because Linux references pass.

## Syntax anatomy and execution trace

Xcode schemes choose build/test actions and destinations. xcodebuild -list and -showdestinations reveal actual available options. The fixture provides domain tests plus a UI smoke source to add to the generated project targets.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Separate acceptance categories

A release checklist should retain missing evidence instead of inferring it from a lower layer.

```swift
import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            let evidence: Set<String> = ["domain-tests", "package-build"]
            precondition(!evidence.contains("ui-tested"))
            precondition(!evidence.contains("device-signed"))
        }
        print("swift-046: passed")
    }
}
```

**Observe:** Domain and package evidence do not imply UI or device qualification.

### Example B: Require every declared release gate

Set difference is a simple portable model of honest acceptance accounting.

```swift
import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            let required: Set<String> = ["domain-tests", "ui-smoke", "save-reload"]
            let observed: Set<String> = ["domain-tests", "ui-smoke"]
            precondition(required.subtracting(observed) == ["save-reload"])
        }
        print("swift-046: passed")
    }
}
```

**Observe:** Save/reload remains an explicit incomplete gate.

## Exercises

1. **Predict and explain.** Explain what each evidence category proves.

2. **Guided modification.** Add save/reload evidence only after actually performing it.

3. **Independent construction.** Generate JourneyApp, list destinations and run its provided test scheme on an available simulator or macOS destination.

4. **Diagnose a defect.** Diagnose using a successful archive build as proof of screen-reader usability.

5. **Boundary evidence.** Test fresh launch, saved-state reload and malformed saved-state recovery.

6. **Transfer and justify.** Prepare a release note listing platform, SDK, destination, test results and remaining device/signing limitations.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Never commit a personal development team, certificate or provisioning profile. A simulator is not a physical device. Keep test-state cleanup scoped to the app-owned test location.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Scheme, Simulator, Signing without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://developer.apple.com/documentation/xcode/running-your-app-in-simulator-or-on-a-device). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-046: App tests, simulator evidence and signing.
Read courses/swift/guides/swift-046.md and courses/swift/lessons/swift-046.swift. Prerequisites: swift-045.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-046_solution.swift and
courses/swift/solutions/swift-046_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
