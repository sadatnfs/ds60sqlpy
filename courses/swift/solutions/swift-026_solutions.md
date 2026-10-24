# swift-026: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-026_solution.swift](swift-026_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Keep a pure core function:** A portable contract can be shared by an executable, tests and a later app adapter. The pure kernel is suitable for a reusable library.

**Separate presentation from calculation:** Moving this function into another target requires a deliberate public interface rather than copying implementation text. Presentation is independently testable.

## Reason through the six tasks

1. **Predict and explain.** Identify the core and presentation responsibilities.

2. **Guided modification.** Build the complete JourneyCore package with swift build.

3. **Independent construction.** Run swift test and the journey-demo executable.

4. **Diagnose a defect.** Diagnose a symbol that is internal when another module needs public access.

5. **Boundary evidence.** Perform a clean package build using only the lab-owned output directory.

6. **Transfer and justify.** Add a new target only when it creates a useful dependency boundary and document that direction.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A package describes targets, products and dependencies. A target is a compilation unit with a module boundary; a product exposes something consumers can build or import. Splitting a domain library from an executable lets tests and an app share the same core without duplicating source.

The single-file pad cannot accept Package.swift or install dependencies. The checked-in JourneyCore package is a separate complete project with a library, executable and tests, using only the Swift toolchain. Build it deliberately in a prepared environment. Package success on one platform does not establish Apple UI behavior or every deployment architecture.

Package.swift declares a tools-version header and target graph. import exposes another module public API. Internal is the usual default access level, while public members define cross-module contracts.

A manifest is not executed by the classroom source pad. Do not assume adding a dependency is offline. Public API choices become compatibility obligations.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
