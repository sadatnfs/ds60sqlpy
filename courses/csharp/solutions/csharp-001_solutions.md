# csharp-001: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-001_solution.cs](csharp-001_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**A checked greeting:** The length check establishes a specific claim before printing. Spaces and punctuation count as characters in this ASCII fixture. Hello, C# appears before the lesson marker.

**A calculation instead of a hardcoded message:** The second condition rejects a plausible wrong operator. This is stronger evidence than printing an unexplained success word. The total is 12, while adding the two inputs gives 7.

## Reason through the six tasks

1. **Predict and explain.** Predict the greeting length, including its space and punctuation, before running Example A.

2. **Guided modification.** Change the greeting and update its independently counted expected length.

3. **Independent construction.** Write a program calculating the number of seats in four rows of six seats. Check 24 explicitly.

4. **Diagnose a defect.** Temporarily remove a semicolon and classify the diagnostic as compilation rather than runtime failure. Restore it.

5. **Boundary evidence.** Compare zero rows with one row and explain why multiplication handles both without a branch.

6. **Transfer and justify.** Model boxes containing packets containing items. Explain each intermediate value and check the final product.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A program is text until a compiler translates it into a form the runtime can execute. In .NET, the SDK supplies build tools; the runtime loads managed code and supplies services such as allocation and exceptions. Installing only a runtime is insufficient for compiling new source. The classroom prepares the SDK inside Linux Docker, so the host browser does not need a C# compiler.

The first skill is distinguishing three outcomes: a compiler diagnostic means the program did not start; an exception means execution reached a failing operation; the expected printed result means a particular path completed. A message saying success proves nothing about an unchecked calculation. We therefore attach a small explicit condition to every reference and make false conditions terminate unsuccessfully.

`using System;` makes framework names available without their namespace prefix. `class Program` groups members. `static Main` is an entrypoint that needs no object instance. Braces delimit a body; a semicolon ends a statement. `Console.WriteLine` prints one line. The wrapper uses `async Task Main` to keep one entrypoint shape throughout the route; asynchronous work is explained later. For now, trace the statements from top to bottom.

Printing a copied expected number skips the calculation. A missing brace can produce several later diagnostics, so repair the first structural problem before interpreting the rest. Do not treat the lesson marker as a replacement for inspecting the greeting or invariant.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
