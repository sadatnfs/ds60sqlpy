# csharp-001: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-001_solution.cs](csharp-001_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**A checked greeting:** The length check establishes a specific claim before printing. Spaces and punctuation count as characters in this ASCII fixture. Hello, C# appears before the lesson marker.

**A calculation instead of a hardcoded message:** The second condition rejects a plausible wrong operator. This is stronger evidence than printing an unexplained success word. The total is 12, while adding the two inputs gives 7.

## Task answers

### Task 1: Predict and explain

Predict the greeting length, including its space and punctuation, before running Example A.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The length check establishes a specific claim before printing. Spaces and punctuation count as characters in this ASCII fixture. Hello, C# appears before the lesson marker.

### Task 2: Guided modification

Change the greeting and update its independently counted expected length.

No separate reference answer has been written for this task. Start from Example B: The second condition rejects a plausible wrong operator. This is stronger evidence than printing an unexplained success word. The total is 12, while adding the two inputs gives 7.

### Task 3: Independent construction

Write a program calculating the number of seats in four rows of six seats. Check 24 explicitly.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
int rows = 4;
int seatsPerRow = 6;
int seats = rows * seatsPerRow;
Check(seats == 24, "four rows of six seats");
```

**Observe:** The program computes 24 seats and the check passes silently.

Multiplication states the repeated rows directly, and the check compares the result with 24, a value written down independently of the formula.

### Task 4: Diagnose a defect

Temporarily remove a semicolon and classify the diagnostic as compilation rather than runtime failure. Restore it.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Printing a copied expected number skips the calculation. A missing brace can produce several later diagnostics, so repair the first structural problem before interpreting the rest. Do not treat the lesson marker as a replacement for inspecting the greeting or invariant.

### Task 5: Boundary evidence

Compare zero rows with one row and explain why multiplication handles both without a branch.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (A checked greeting) and Example B (A calculation instead of a hardcoded message).

### Task 6: Transfer and justify

Model boxes containing packets containing items. Explain each intermediate value and check the final product.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Source**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A program is text until a compiler translates it into a form the runtime can execute. In .NET, the SDK supplies build tools; the runtime loads managed code and supplies services such as allocation and exceptions. Installing only a runtime is insufficient for compiling new source. The classroom prepares the SDK inside Linux Docker, so the host browser does not need a C# compiler.

The first skill is distinguishing three outcomes: a compiler diagnostic means the program did not start; an exception means execution reached a failing operation; the expected printed result means a particular path completed. A message saying success proves nothing about an unchecked calculation. We therefore attach a small explicit condition to every reference and make false conditions terminate unsuccessfully.

`using System;` makes framework names available without their namespace prefix. `class Program` groups members. `static Main` is an entrypoint that needs no object instance. Braces delimit a body; a semicolon ends a statement. `Console.WriteLine` prints one line. The wrapper uses `async Task Main` to keep one entrypoint shape throughout the route; asynchronous work is explained later. For now, trace the statements from top to bottom.

Printing a copied expected number skips the calculation. A missing brace can produce several later diagnostics, so repair the first structural problem before interpreting the rest. Do not treat the lesson marker as a replacement for inspecting the greeting or invariant.

## Review before continuing

Run the reference and confirm that it prints `csharp-001: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
