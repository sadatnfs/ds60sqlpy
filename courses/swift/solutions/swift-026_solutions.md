# swift-026: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-026_solution.swift](swift-026_solution.swift). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Keep a pure core function:** A portable contract can be shared by an executable, tests and a later app adapter. The pure kernel is suitable for a reusable library.

**Separate presentation from calculation:** Moving this function into another target requires a deliberate public interface rather than copying implementation text. Presentation is independently testable.

## Task answers

### Task 1: Predict and explain

Identify the core and presentation responsibilities.

No separate reference answer has been written for this task. Example A is the evidence to compare with: A portable contract can be shared by an executable, tests and a later app adapter. The pure kernel is suitable for a reusable library.

### Task 2: Guided modification

Build the complete JourneyCore package with swift build.

No separate reference answer has been written for this task. Start from Example B: Moving this function into another target requires a deliberate public interface rather than copying implementation text. Presentation is independently testable.

### Task 3: Independent construction

Run swift test and the journey-demo executable.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Package** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose a symbol that is internal when another module needs public access.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A manifest is not executed by the classroom source pad. Do not assume adding a dependency is offline. Public API choices become compatibility obligations.

### Task 5: Boundary evidence

Perform a clean package build using only the lab-owned output directory.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Keep a pure core function) and Example B (Separate presentation from calculation).

### Task 6: Transfer and justify

Add a new target only when it creates a useful dependency boundary and document that direction.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Package**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A package describes targets, products and dependencies. A target is a compilation unit with a module boundary; a product exposes something consumers can build or import. Splitting a domain library from an executable lets tests and an app share the same core without duplicating source.

The single-file pad cannot accept Package.swift or install dependencies. The checked-in JourneyCore package is a separate complete project with a library, executable and tests, using only the Swift toolchain. Build it deliberately in a prepared environment. Package success on one platform does not establish Apple UI behavior or every deployment architecture.

Package.swift declares a tools-version header and target graph. import exposes another module public API. Internal is the usual default access level, while public members define cross-module contracts.

A manifest is not executed by the classroom source pad. Do not assume adding a dependency is offline. Public API choices become compatibility obligations.

## Review before continuing

Run the reference and confirm that it prints `swift-026: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
