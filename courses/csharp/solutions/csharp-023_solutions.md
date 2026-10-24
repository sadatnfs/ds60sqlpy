# csharp-023: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-023_solution.cs](csharp-023_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Catch only the expected invalid format:** The catch does not accidentally classify every possible programming error as bad user text. Malformed numeric text is caught as a format error.

**Retain an inner cause:** A public description can add context without erasing the lower-level failure category. The outer domain failure still contains the I/O cause.

## Reason through the six tasks

1. **Predict and explain.** Identify which failure category each catch handles.

2. **Guided modification.** Add a separate negative-count case without classifying it as FormatException.

3. **Independent construction.** Define an import API with distinct invalid-input and storage-failure outcomes.

4. **Diagnose a defect.** Diagnose catch-all code that returns an empty successful report.

5. **Boundary evidence.** Test success, expected rejection and an unexpected exception separately.

6. **Transfer and justify.** Decide which layer owns user-facing error translation and which details should remain private diagnostics.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Exceptions carry an abnormal control-flow result across method boundaries. Catch an exception where the program can make a meaningful recovery decision, add context or translate it into a public error contract. Catching everything at every layer often destroys the reason the operation failed.

A normal absence can be represented without an exception when it is expected. A malformed argument or failed invariant should remain visible. When rethrowing in a catch block, use `throw;` to preserve the original stack relationship. When adding a domain exception, retain the original as InnerException. Logging the same exception at every layer can multiply noise without adding evidence.

`try` encloses an operation; typed catch selects a failure category; finally runs cleanup when control leaves the protected region. `throw;` rethrows the current exception. A catch filter with `when` narrows recovery policy.

A catch-all that returns a default can turn data loss into apparent success. Throwing the caught variable instead of using bare throw changes stack-trace behavior. Cleanup should not accidentally replace the original failure.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
