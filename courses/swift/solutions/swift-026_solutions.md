# swift-026: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-026_solution.swift](swift-026_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Keep a pure core function:** A portable contract can be shared by an executable, tests and a later app adapter. The pure kernel is suitable for a reusable library.

**Separate presentation from calculation:** Moving this function into another target requires a deliberate public interface rather than copying implementation text. Presentation is independently testable.

## Task answers

### Task 1: Predict and explain

Identify the core and presentation responsibilities.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
func total(_ values: [Int]) -> Int { values.reduce(0, +) }
func render(_ total: Int) -> String { "total=\(total)" }
let sum = total([4, 6])
precondition(sum == 10)
precondition(render(sum) == "total=10")
```

**Observe:** The core returns the number 10, and presentation separately turns it into total=10.

total is the reusable calculation with no knowledge of text, while render only formats; that split is the library-versus-executable boundary a package makes explicit.

### Task 2: Guided modification

Build the complete JourneyCore package with swift build.

**Written answer.** Copy fixtures/JourneyCore into your own workspace and run swift build in the copied directory. It compiles the JourneyCore library and the journey-demo executable and ends with Build complete!; in the reference run on swift:6.3.3-noble the last steps were Linking journey-demo and Build complete! (3.01s). No dependency is fetched, because the manifest declares none.

### Task 3: Independent construction

Run swift test and the journey-demo executable.

**Written answer.** In the copied package run swift test, then swift run journey-demo. The reference run on swift:6.3.3-noble reported Executed 4 tests, with 0 failures and printed JourneyCore: 1/2 complete; round trip passed. The tests exercise the library through @testable import, and the executable consumes only its public API.

### Task 4: Diagnose a defect

Diagnose a symbol that is internal when another module needs public access.

**Written answer.** Removing public from StudyPlan.completedCount still compiles inside JourneyCore, but the JourneyDemo target then fails with 'completedCount' is inaccessible due to 'internal' protection level, as the reference build showed. Symbols default to internal, visible only within their module; anything another target must call needs public, which also makes it a compatibility promise.

### Task 5: Boundary evidence

Perform a clean package build using only the lab-owned output directory.

**Written answer.** Inside the copied package run swift package clean, then swift build. Clean removes build products under that package's .build directory and leaves sources alone; the rebuild recreates .build in the same place, which the reference run confirmed was the only output location. Never point cleanup at a directory you did not create.

### Task 6: Transfer and justify

Add a new target only when it creates a useful dependency boundary and document that direction.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Run swift test and the journey-demo executable) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** The portable part of this lesson splits a calculation, `total`, from presentation, `render`, so each can live in a different target of a Swift package. Example A checks the pure sum on `[2, 3]` and on an empty array. Example B checks that `render(5)` produces `total=5`. The package tasks then build and test JourneyCore outside the pad.

**Why it is correct.** `reduce(0, +)` starts from 0, so `[2, 3]` sums to 5 and an empty array returns 0 without special cases. `render` only formats a number it is given, so its output depends on nothing but its argument. Because neither function reads global state or files, both can move into a library target and be tested from a test target unchanged.

**A plausible wrong approach.** Putting `print("total=\(values.reduce(0, +))")` in one function mixes calculation with output; a test would then need to capture standard output. Moving `total` into a library target without marking it `public` compiles in that module but fails from the executable target with an inaccessible-symbol error, which is task 4.

**How to verify.** For the package tasks, run `swift build` and `swift test` in the JourneyCore directory with a lab-owned build path and record their actual output; the pad marker is not evidence that the package builds on your machine.

## Mechanism and diagnostic reasoning

A package describes targets, products and dependencies. A target is a compilation unit with a module boundary; a product exposes something consumers can build or import. Splitting a domain library from an executable lets tests and an app share the same core without duplicating source.

The single-file pad cannot accept Package.swift or install dependencies. The checked-in JourneyCore package is a separate complete project with a library, executable and tests, using only the Swift toolchain. Build it deliberately in a prepared environment. Package success on one platform does not establish Apple UI behavior or every deployment architecture.

Package.swift declares a tools-version header and target graph. import exposes another module public API. Internal is the usual default access level, while public members define cross-module contracts.

A manifest is not executed by the classroom source pad. Do not assume adding a dependency is offline. Public API choices become compatibility obligations.

## Review before continuing

Run the reference and confirm that it prints `swift-026: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
