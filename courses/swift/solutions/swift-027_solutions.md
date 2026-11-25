# swift-027: explanation and comparison

Reference program: [swift-027_solution.swift](swift-027_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Check independently derived cases:** Literal expected results are derived from the domain rule rather than a duplicated implementation. Normal and boundary values satisfy the clamp contract.

**Catch a plausible wrong boundary:** A property adds evidence while the boundary example remains decisive. The zero case catches the wrong default and clamping is idempotent.

## Task answers

### Task 1: Predict and explain

Name a wrong implementation rejected by each fixture.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let cases = [(-2, 0), (0, 0), (3, 3)]
func passes(_ candidate: (Int) -> Int) -> Bool {
  cases.allSatisfy { candidate($0.0) == $0.1 }
}
precondition(passes { max(0, $0) })
precondition(!passes { $0 })
precondition(!passes { abs($0) })
precondition(!passes { _ in 0 })
```

**Observe:** The real clamp passes, identity and abs fail on -2, and always-zero fails on 3.

Each fixture earns its place by rejecting some wrong implementation: the negative row catches missing clamping or sign flipping, and the positive row catches a constant result.

### Task 2: Guided modification

Add the minimum Int case without unsafe negation.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
precondition(max(0, Int.min) == 0)
precondition(Int.min.magnitude == UInt(Int.max) + 1)
precondition(Int.min.addingReportingOverflow(-1).overflow)
```

**Observe:** Clamping Int.min gives 0, and its magnitude is one more than Int.max.

max(0, Int.min) never negates, so it is safe; -Int.min or abs(Int.min) would trap because the positive value does not fit in Int.

### Task 3: Independent construction

Add a real JourneyCore test that rejects a blank item title.

**Written answer.** Add this method to PlanTests: func testBlankTitleIsRejected() throws { XCTAssertThrowsError(try StudyItem(id: "two", title: "   ")) { error in XCTAssertEqual(error as? PlanError, .invalidItem) } }. In the reference copy, swift test then reported Executed 5 tests, with 0 failures. The test fails if the initializer stops trimming whitespace or reports a different error.

### Task 4: Diagnose a defect

Diagnose a test comparing the same function call on both sides.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
func wrongClamp(_ value: Int) -> Int { value <= 0 ? 1 : value }
precondition(wrongClamp(0) == wrongClamp(0))
precondition(wrongClamp(0) != 0)
```

**Observe:** Comparing wrongClamp(0) with itself passes, while comparing it with the literal 0 exposes the defect.

A test whose two sides call the same code can never fail, so it proves nothing; the expected side must come from an independent oracle such as a literal derived from the rule.

### Task 5: Boundary evidence

Test empty, duplicate and malformed inputs separately.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
func clampAll(_ texts: [String]) -> [Int]? {
  var result: [Int] = []
  for text in texts {
    guard let value = Int(text) else { return nil }
    result.append(max(0, value))
  }
  return result
}
precondition(clampAll([]) == [])
precondition(clampAll(["-1", "-1"]) == [0, 0])
precondition(clampAll(["2", "x"]) == nil)
```

**Observe:** Empty input gives [], duplicates keep both entries as [0, 0], and a malformed entry makes the whole result nil.

Separate checks name separate contracts: empty is not an error, duplicates are preserved rather than merged, and malformed text is rejected rather than clamped.

### Task 6: Transfer and justify

Create a verification plan distinguishing unit, package, UI and device evidence.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** Example A checks a clamp-at-zero rule, `max(0, input)`, against a table of inputs and literal expected outputs: -2 to 0, 0 to 0 and 3 to 3. Example B writes a deliberately wrong clamp that returns 1 for zero and shows the table would catch it, then checks that clamping twice equals clamping once.

**Why it is correct.** The expected values in the table come from the rule itself, not from calling the function, so they are an independent oracle. The zero row is decisive: the wrong function returns 1 there while the rule requires 0. Idempotence holds because `max(0, -4)` is 0 and `max(0, 0)` is still 0, giving a property check that covers more than one input.

**A plausible wrong approach.** Writing `precondition(max(0, x) == max(0, x))` always passes, because both sides call the same code; it would accept the wrong clamp too. This self-comparison is task 4's defect. Testing only -2 and 3 would also pass the wrong implementation, since it only misbehaves at zero.

**How to verify.** Replace `max(0, input)` in the table loop with `wrong(input)` and confirm the zero row fails. For task 2, add `(Int.min, 0)` and confirm it passes without negating `Int.min`, which would overflow. Run the JourneyCore test separately with `swift test` and record its output.

## Mechanism and diagnostic reasoning

A meaningful test rejects a plausible wrong implementation. Examples should include independently derived expected values, boundaries and a known misconception. Properties such as idempotence can cover a wider family, but they complement concrete expected cases rather than replacing them.

The pad uses precondition for dependency-free executable checks. The JourneyCore package includes XCTest tests available with the prepared Swift toolchain. Swift Testing (import Testing, @Test, #expect) also ships with Swift 6 toolchains, including the Linux toolchain used here, and swift test runs it alongside XCTest without an extra package dependency. This fixture keeps XCTest so its existing tests stay unchanged. Keep whichever test surface is actually prepared explicit. Unit tests do not prove UI interaction, signing or remote service availability.

Table-driven checks separate input fixtures from execution. XCTest test methods use XCTAssertEqual and XCTAssertThrowsError in the package. Async tests should await owned work rather than sleep and guess.

Random tests need reproducible seeds and an oracle. A test that catches its own precondition failure is not valid verification. Avoid narrow elapsed-time assertions on shared machines.

## Review before continuing

Run the reference and confirm it prints `swift-027: passed`, then rerun the guide's counterexample.
