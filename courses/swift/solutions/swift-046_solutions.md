# swift-046: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-046_solution.swift](swift-046_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Separate acceptance categories:** A release checklist should retain missing evidence instead of inferring it from a lower layer. Domain and package evidence do not imply UI or device qualification.

**Require every declared release gate:** Set difference is a simple portable model of honest acceptance accounting. Save/reload remains an explicit incomplete gate.

## Task answers

### Task 1: Predict and explain

Explain what each evidence category proves.

**Written answer.** domain-tests shows that the rules in JourneyCore hold for the tested inputs. package-build shows that the package compiles with this toolchain. ui-tested would show that an automated script drove real screens, and device-signed that a signed build installed on hardware. Each proves only its own claim; none implies the others.

### Task 2: Guided modification

Add save/reload evidence only after actually performing it.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
var observed: Set<String> = ["domain-tests", "ui-smoke"]
let saved = Data(#"{"titles":["Read"]}"#.utf8)
let reloaded = try JSONDecoder().decode([String: [String]].self, from: saved)
if reloaded["titles"] == ["Read"] { observed.insert("save-reload") }
let required: Set<String> = ["domain-tests", "ui-smoke", "save-reload"]
precondition(required.subtracting(observed).isEmpty)
```

**Observe:** save-reload is recorded only after the reload returns Read, and then no required gate is missing.

The evidence is inserted as a consequence of a check that ran, not typed in by hand, so the set cannot claim a gate nobody performed.

### Task 3: Independent construction

Generate JourneyApp, list destinations and run its provided test scheme on an available simulator or macOS destination.

**Written answer.** This task needs Xcode and XcodeGen on a Mac and was not run for this reference. From your copy of JourneyApp run xcodegen generate --spec project.yml, xcodebuild -list, then xcodebuild -showdestinations for JourneyMac, and pick a destination that list actually shows. Run the test action on that destination; it should execute JourneySmokeTests.testAddItemUpdatesProgress. Record the Xcode version, destination and result.

### Task 4: Diagnose a defect

Diagnose using a successful archive build as proof of screen-reader usability.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
let archiveEvidence: Set<String> = ["compiled", "archived"]
precondition(!archiveEvidence.contains("voiceover-checked"))
```

**Observe:** The archive evidence contains compiled and archived but nothing about VoiceOver.

An archive proves the code compiled and was packaged. Screen-reader usability depends on labels, order and focus at run time, which only a person or a UI test using VoiceOver can observe.

### Task 5: Boundary evidence

Test fresh launch, saved-state reload and malformed saved-state recovery.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
var disk: [String: Data] = [:]
func launch() -> (titles: [String], blocked: Bool) {
  guard let data = disk["plan"] else { return ([], false) }
  guard let titles = try? JSONDecoder().decode([String].self, from: data) else { return ([], true) }
  return (titles, false)
}
precondition(launch().titles.isEmpty && !launch().blocked)
disk["plan"] = try JSONEncoder().encode(["Read"])
precondition(launch().titles == ["Read"])
disk["plan"] = Data("{".utf8)
precondition(launch().blocked && disk["plan"] == Data("{".utf8))
```

**Observe:** A fresh launch is empty, a saved plan reloads as Read, and malformed data blocks saving while its bytes stay on disk.

This portable model follows PlanStore's policy. The same three launches still need checking in the real app on an Apple destination, using its --ui-testing directory and not your own data.

### Task 6: Transfer and justify

Prepare a release note listing platform, SDK, destination, test results and remaining device/signing limitations.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Generate JourneyApp, list destinations and run its provided test scheme on an available simulator or macOS destination) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** This lesson models release evidence as sets of named gates. Example A holds only domain-test and package-build evidence and checks that UI and device gates are absent. Example B subtracts the observed set from the required set to list what is still missing. The tasks then move to running JourneyApp's test scheme on a real simulator or macOS destination.

**Why it is correct.** A `Set` contains only what was inserted, so `contains("ui-tested")` is false until someone records a UI test. In Example B `required.subtracting(observed)` removes "domain-tests" and "ui-smoke" and leaves `["save-reload"]`, which is exactly the gate nobody has performed. The model never infers a higher gate from a lower one.

**A plausible wrong approach.** Treating a successful archive build as proof that VoiceOver works (task 4) confuses compilation with behavior: the build shows the code links and signs, not that labels are meaningful or focus order is right. Adding "save-reload" to `observed` before actually relaunching the app would make the subtraction empty while the gate is still unchecked.

**How to verify.** For task 3, list destinations with `xcodebuild -showdestinations`, run the provided test scheme on one, and copy the destination name and result into the release note. If no Apple toolchain is available, leave the gate in the missing set and say so instead of marking it done.

## Mechanism and diagnostic reasoning

App verification has several layers. Domain tests establish rules. Package builds establish module compilation. UI tests establish navigation and interaction in a selected simulator or device configuration. Signing establishes an installable identity under an Apple development team. None of these steps substitutes for the others.

A simulator build can run without provisioning a physical device, while distribution and device installation introduce team, certificate and entitlement requirements. Keep personal signing identifiers out of the shared fixture. The app project is generated locally from an exact reviewed specification, then the learner selects a team only in their own Xcode environment. Record the scheme, destination and observed tests rather than claiming universal platform acceptance.

Xcode schemes choose build/test actions and destinations. xcodebuild -list and -showdestinations reveal actual available options. The fixture provides domain tests plus a UI smoke source to add to the generated project targets.

Never commit a personal development team, certificate or provisioning profile. A simulator is not a physical device. Keep test-state cleanup scoped to the app-owned test location.

## Review before continuing

Run the reference and confirm that it prints `swift-046: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
