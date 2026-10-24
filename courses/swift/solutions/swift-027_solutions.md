# swift-027: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-027_solution.swift](swift-027_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Check independently derived cases:** Literal expected results are derived from the domain rule rather than a duplicated implementation. Normal and boundary values satisfy the clamp contract.

**Catch a plausible wrong boundary:** A property adds evidence while the boundary example remains decisive. The zero case catches the wrong default and clamping is idempotent.

## Reason through the six tasks

1. **Predict and explain.** Name a wrong implementation rejected by each fixture.

2. **Guided modification.** Add the minimum Int case without unsafe negation.

3. **Independent construction.** Add a real JourneyCore test for rejected negative quantity.

4. **Diagnose a defect.** Diagnose a test comparing the same function call on both sides.

5. **Boundary evidence.** Test empty, duplicate and malformed inputs separately.

6. **Transfer and justify.** Create a verification plan distinguishing unit, package, UI and device evidence.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A meaningful test rejects a plausible wrong implementation. Examples should include independently derived expected values, boundaries and a known misconception. Properties such as idempotence can cover a wider family, but they complement concrete expected cases rather than replacing them.

The pad uses precondition for dependency-free executable checks. The JourneyCore package includes XCTest tests available with the prepared Swift toolchain. Swift Testing is another modern test framework and its macro-based API has a distinct project/toolchain requirement. Keep whichever test surface is actually prepared explicit. Unit tests do not prove UI interaction, signing or remote service availability.

Table-driven checks separate input fixtures from execution. XCTest test methods use XCTAssertEqual and XCTAssertThrowsError in the package. Async tests should await owned work rather than sleep and guess.

Random tests need reproducible seeds and an oracle. A test that catches its own precondition failure is not valid verification. Avoid narrow elapsed-time assertions on shared machines.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
