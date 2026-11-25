# swift-047: explanation and comparison

Reference program: [swift-047_solution.swift](swift-047_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Keep portable policy independent:** A portable core should not import a platform framework merely to format its basic domain outcome. The same domain summary works without a UI framework.

**Declare a capability rather than guess:** Capability descriptions should follow actual prepared runtime evidence. The Linux capability set does not invent SwiftUI support.

## Task answers

### Task 1: Predict and explain

Identify which code belongs in the portable core.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
struct PortablePlan {
  let completed: Int
  let total: Int
  var summary: String { "\(completed)/\(total) complete" }
}
let plan = PortablePlan(completed: 1, total: 2)
precondition(plan.summary == "1/2 complete")
```

**Observe:** The summary 1/2 complete comes from a type that imports no UI framework.

Counting, validation and summaries belong in the portable core because they behave the same everywhere. Views, platform bridges and file locations belong in the app targets.

### Task 2: Guided modification

Add a platform-neutral derived statistic.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
func percentComplete(completed: Int, total: Int) -> Int {
  guard total > 0 else { return 0 }
  return completed * 100 / total
}
precondition(percentComplete(completed: 1, total: 4) == 25)
precondition(percentComplete(completed: 0, total: 0) == 0)
```

**Observe:** One of four complete is 25 percent, and an empty plan reports 0 instead of dividing by zero.

The statistic uses only integers and a stated empty policy, so it needs no platform API and gives the same answer on Linux and Apple systems.

### Task 3: Independent construction

Build JourneyCore on a prepared Linux Swift environment and separately build JourneyApp on macOS.

**Written answer.** The Linux half was run: in a copy of JourneyCore on swift:6.3.3-noble, swift build ended with Build complete! and swift test reported Executed 4 tests, with 0 failures. The macOS half was not run for this reference; on a prepared Mac, follow the JourneyApp README and build JourneyMac with xcodebuild. Record the two results separately, since one does not prove the other.

### Task 4: Diagnose a defect

Diagnose importing UIKit in a shared domain target.

**Written answer.** UIKit exists only on Apple platforms, so a shared target that imports it stops compiling everywhere else. In the reference container, a one-line file with import UIKit failed with error: no such module 'UIKit'. Keep the domain target on Foundation or the standard library, and put UIKit code in the iOS app target or behind canImport(UIKit).

### Task 5: Boundary evidence

Test unavailable capabilities with a clear message rather than a broken Run action.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
let capabilities: Set<String> = ["portable-core", "foundation-files"]
func runAction(_ capability: String) -> String {
  capabilities.contains(capability)
    ? "Running \(capability)" : "\(capability) is not available on this platform"
}
precondition(runAction("portable-core") == "Running portable-core")
precondition(runAction("swiftui-preview") == "swiftui-preview is not available on this platform")
```

**Observe:** A supported capability runs, and an unsupported one returns a sentence saying it is not available.

Checking the declared capability set before acting turns a missing platform feature into a clear message rather than a crash or a Run button that does nothing.

### Task 6: Transfer and justify

Create a platform support matrix listing compiled, executed and manually inspected surfaces separately.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** Example A writes `summary`, a formatter that needs no UI framework, and checks "2/3 complete". Example B records the capabilities actually prepared on Linux as a set and checks that it contains the portable core but not SwiftUI. The tasks build JourneyCore on Linux and JourneyApp separately on macOS.

**Why it is correct.** `summary` uses only string interpolation from the standard library, so it compiles unchanged on Linux, macOS and iOS and returns "2/3 complete" for 2 and 3. The capability set holds only the two strings inserted, so `contains("swiftui-linux")` is false. That keeps the support matrix tied to what was actually built and run rather than to what the code appears to allow.

**A plausible wrong approach.** Adding `import UIKit` to the shared domain target so a model can use `UIColor` is the task 4 defect: the core no longer builds on macOS without Catalyst or on Linux at all, and every consumer inherits a UI dependency. Treating `#if canImport(SwiftUI)` as proof that each API is available at the deployment target is also wrong; availability still depends on OS version.

**How to verify.** For task 2, add `remaining(completed:total:)` and check 1 for 2 and 3. For task 3, run `swift build` for JourneyCore on Linux and build JourneyApp on macOS, and record the two results in separate rows of the support matrix with the toolchain version.

## Mechanism and diagnostic reasoning

Sharing Swift code does not mean every platform has the same frameworks or user expectations. A domain package can compile on Linux and Apple platforms, while UI adapters differ. Conditional compilation is useful at a narrow boundary; scattering platform checks throughout domain logic makes the core harder to reason about.

Deployment targets state the oldest platform APIs an app promises to support. Runtime availability checks can gate newer functionality, but the fallback must still be useful. Resource paths, permissions and application lifecycle also vary. Treat cross-platform support as a matrix of actual builds and runs, not a claim inferred from the language name.

#if canImport selects compile-time framework availability. #available guards runtime API availability on Apple platforms. Package platform declarations and Xcode deployment settings are related project contracts.

CanImport proves a module is available to the compiler, not that every API is available at the deployment target. Do not assume Foundation APIs have identical availability everywhere. Keep unsupported surfaces explicit.

## Review before continuing

Run the reference and confirm it prints `swift-047: passed`, then rerun the guide's counterexample.
