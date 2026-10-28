## An error policy is part of an API

A calculation can fail because its input is outside the intended domain, because information is absent, or because the implementation has a defect. These situations deserve different handling. Returning an ordinary numeric value for every failure can make an invalid result look scientifically meaningful.

`throw` raises an exception. `try` and `catch` can handle an expected failure at a boundary. `rethrow` preserves an unexpected exception rather than replacing it with a misleading success. The standard `Test` library provides checks for values and expected exceptions. Tests should state the contract using inputs that expose normal and boundary behavior.

An assertion in a reference program is evidence about that declared fixture. It is not a substitute for validating external data at runtime. Conversely, a validator should check a meaningful invariant rather than merely catch every possible error and continue with a fabricated default.

## Worked case A: a finite nonempty mean

The helper requires a nonempty collection of finite numerical values. It rejects an empty input with `ArgumentError` and nonfinite measurements with `DomainError`. This policy differs deliberately from a function that returns an absent-value sentinel. The caller can distinguish a valid zero mean from a rejected calculation.

{{WORKED_A}}

## Worked case B: a bounded outcome record

A boundary function converts only the two declared validation failures into a rejected outcome record. An unexpected method error is rethrown. The record retains a readable diagnostic and does not insert a numeric result for rejected input. This makes it possible to count rejected records without silently adding them to a valid-result denominator.

{{WORKED_B}}

## Build useful tests

Include a normal case, a boundary case and an input that must fail. Test exact integer or identity properties exactly. Use numerical tolerances only when a representation or algorithm justifies approximation. A tolerance should have a reason related to the quantity and its units, not simply be large enough to hide a mismatch.

When a test fails, inspect the expected value independently. Copying an implementation's formula into the assertion can reproduce the same mistake twice. Hand calculations, algebraic invariants, alternative formulations and known limiting cases provide stronger checks. Tests also need to verify that an expected error actually occurred rather than swallowing an arbitrary exception.

## Diagnosis and transfer

A stack trace identifies the sequence of calls leading to failure. Begin with the first relevant location in your own source and trace its inputs. A broad catch that replaces every exception with zero removes that evidence and can contaminate downstream statistics. Handle expected input failures deliberately and allow unexpected defects to remain visible.

For a real data pipeline, retain rejected-row counts, reasons and the input contract version. Do not reveal sensitive raw data unnecessarily in production diagnostics. The authored fixture here contains no personal data and uses very small values so the failure mechanism is inspectable.

The examples establish a specific error contract and test strategy. They do not provide a universal policy for missing or nonfinite measurements. A scientific workflow must decide how those cases relate to its estimand, then keep the decision visible in both code and reported denominators.
