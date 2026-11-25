# swift-046: App tests, simulator evidence and signing

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-045`

## Learning objectives

Run app tests on simulators or macOS destinations and explain signing requirements. The central exercise is task 3: Generate JourneyApp, list destinations and run its provided test scheme on an available simulator or macOS destination.

## Purpose and mental model

App verification has several layers. Domain tests establish rules. Package builds establish module compilation. UI tests establish navigation and interaction in a selected simulator or device configuration. Signing establishes an installable identity under an Apple development team. None of these steps substitutes for the others.

A simulator build can run without provisioning a physical device, while distribution and device installation introduce team, certificate and entitlement requirements. Keep personal signing identifiers out of the shared fixture. The app project is generated locally from an exact reviewed specification, then the learner selects a team only in their own Xcode environment. Record the scheme, destination and observed tests rather than claiming universal platform acceptance.

## Vocabulary and concepts

**Scheme:** A named set of Xcode build, test and run actions.

**Simulator:** A prepared Apple-platform execution environment for testing.

**Signing:** Associating an app artifact with a development or distribution identity.

## How to run this lesson

The pad checks only evidence accounting with sets. Task 3 runs `xcodebuild` on a Mac: list the schemes and destinations first and choose one that is actually installed. On Linux, record task 3 as not performed rather than marking it passed.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).

Follow [JourneyApp build and test commands](../fixtures/JourneyApp/README.md). The repository does not claim those Apple-platform commands have run merely because Linux references pass.

## Syntax anatomy and execution trace

Xcode schemes choose build/test actions and destinations. xcodebuild -list and -showdestinations reveal actual available options. The fixture provides domain tests plus a UI smoke source to add to the generated project targets.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** `evidence` holds the two categories that were actually produced, domain tests and a package build. The checks confirm that neither ui-tested nor device-signed is present. Nothing in the program infers a missing category from the ones that exist: a passing domain test says nothing about whether a screen renders, and a package build says nothing about code signing on a device.

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

**Trace.** `required` lists three gates and `observed` lists the two performed. `required.subtracting(observed)` removes every observed element and leaves save-reload. The check compares against that one-element set. Set difference gives an honest accounting rule: a release is complete only when the difference is empty, and the leftover names exactly which evidence is still missing.

## Exercises

1. **Predict and explain.** Explain what each evidence category proves.

2. **Guided modification.** Add save/reload evidence only after actually performing it.

3. **Independent construction.** Generate JourneyApp, list destinations and run its provided test scheme on an available simulator or macOS destination.

4. **Diagnose a defect.** Diagnose using a successful archive build as proof of screen-reader usability.

5. **Boundary evidence.** Test fresh launch, saved-state reload and malformed saved-state recovery.

6. **Transfer and justify.** Prepare a release note listing platform, SDK, destination, test results and remaining device/signing limitations.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Never commit a personal development team, certificate or provisioning profile. A simulator is not a physical device. Keep test-state cleanup scoped to the app-owned test location.

Task 4's mistake reads an archive build as proof of accessibility. An archive proves only that the code compiled and was packaged; the counterexample is a button with no label that archives cleanly and is unusable with VoiceOver. For task 2, add save-reload only after quitting and relaunching the app and seeing the saved item reappear.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Separate acceptance categories) before changing anything, and confirm its observation: Domain and package evidence do not imply UI or device qualification.
2. Compare Example B (Require every declared release gate) with Example A and name the first line whose behavior differs. Its observation is: Save/reload remains an explicit incomplete gate.
3. Before opening the explanation, check your task 3 attempt (Generate JourneyApp, list destinations and run its provided test scheme on an available simulator or macOS destination) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

State what each of domain tests, package build, UI smoke, save-reload and device signing proves, and what it does not. Explain how set difference reports missing gates. List the facts a release note must record about platform, SDK and destination so a reader can repeat the test.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://developer.apple.com/documentation/xcode/running-your-app-in-simulator-or-on-a-device): Apple's Xcode documentation covers schemes, test plans and running tests from the command line with `xcodebuild`.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
