# swift-027: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-027_solution.swift](swift-027_solution.swift). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Check independently derived cases:** Literal expected results are derived from the domain rule rather than a duplicated implementation. Normal and boundary values satisfy the clamp contract.

**Catch a plausible wrong boundary:** A property adds evidence while the boundary example remains decisive. The zero case catches the wrong default and clamping is idempotent.

## Task answers

### Task 1: Predict and explain

Name a wrong implementation rejected by each fixture.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Literal expected results are derived from the domain rule rather than a duplicated implementation. Normal and boundary values satisfy the clamp contract.

### Task 2: Guided modification

Add the minimum Int case without unsafe negation.

No separate reference answer has been written for this task. Start from Example B: A property adds evidence while the boundary example remains decisive. The zero case catches the wrong default and clamping is idempotent.

### Task 3: Independent construction

Add a real JourneyCore test for rejected negative quantity.

No reference answer has been written for this task yet. It needs a project or platform outside the single-file pad, so record your own build and run evidence and judge it against the vocabulary entry **Oracle** and the lesson notes.

### Task 4: Diagnose a defect

Diagnose a test comparing the same function call on both sides.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Random tests need reproducible seeds and an oracle. A test that catches its own precondition failure is not valid verification. Avoid narrow elapsed-time assertions on shared machines.

### Task 5: Boundary evidence

Test empty, duplicate and malformed inputs separately.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Check independently derived cases) and Example B (Catch a plausible wrong boundary).

### Task 6: Transfer and justify

Create a verification plan distinguishing unit, package, UI and device evidence.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Oracle**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A meaningful test rejects a plausible wrong implementation. Examples should include independently derived expected values, boundaries and a known misconception. Properties such as idempotence can cover a wider family, but they complement concrete expected cases rather than replacing them.

The pad uses precondition for dependency-free executable checks. The JourneyCore package includes XCTest tests available with the prepared Swift toolchain. Swift Testing (import Testing, @Test, #expect) also ships with Swift 6 toolchains, including the Linux toolchain used here, and swift test runs it alongside XCTest without an extra package dependency. This fixture keeps XCTest so its existing tests stay unchanged. Keep whichever test surface is actually prepared explicit. Unit tests do not prove UI interaction, signing or remote service availability.

Table-driven checks separate input fixtures from execution. XCTest test methods use XCTAssertEqual and XCTAssertThrowsError in the package. Async tests should await owned work rather than sleep and guess.

Random tests need reproducible seeds and an oracle. A test that catches its own precondition failure is not valid verification. Avoid narrow elapsed-time assertions on shared machines.

## Review before continuing

Run the reference and confirm that it prints `swift-027: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
