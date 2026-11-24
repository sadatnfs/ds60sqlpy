# csharp-001: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-001_solution.cs](csharp-001_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**A checked greeting:** The length check establishes a specific claim before printing. Spaces and punctuation count as characters in this ASCII fixture. Hello, C# appears before the lesson marker.

**A calculation instead of a hardcoded message:** The second condition rejects a plausible wrong operator. This is stronger evidence than printing an unexplained success word. The total is 12, while adding the two inputs gives 7.

## Task answers

### Task 1: Predict and explain

Predict the greeting length, including its space and punctuation, before running Example A.

**Written answer.** `"Hello, C#"` has nine characters: the five letters of `Hello`, the comma, one space, `C` and `#`. Example A checks `greeting.Length == 9` before printing, so a correct prediction is 9.

**Why it is correct.** `string.Length` counts UTF-16 code units, and every character in this ASCII fixture is one unit. The comma and the space are characters like any letter, so they add 2 to the 7 visible letters and symbols.

**Plausible wrong approach.** Counting only letters gives 6 (`Hello` plus `C`) and counting letters and symbols but not the space gives 8. Either guess, written into the check, makes the program stop with `greeting length` before anything prints.

**How to verify.** Run Example A unchanged: `Hello, C#` prints and the marker follows. Then change the expected value in the check to 8 and confirm the run fails with the reason `greeting length`.

### Task 2: Guided modification

Change the greeting and update its independently counted expected length.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
string greeting = "Hi there, Ada!";
Check(greeting.Length == 14, "changed greeting length");
```

**Observe:** The new greeting has 14 characters and the check passes silently.

This task starts from Example A, the greeting. The expected 14 was counted by hand before running: `Hi` (2), a space (1), `there,` (6), a space (1) and `Ada!` (4). The check compares the program's count with that independent count, not with a value copied from output.

**Plausible wrong approach.** Running the program, reading the length it prints and pasting that number into the check makes the check agree with whatever the code does. It can no longer catch a typo such as a doubled space in the new greeting.

**How to verify.** Add a second space after the comma and rerun: the program must stop with `changed greeting length`, because the text now has 15 characters. Remove the extra space and the check passes again.

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

**Written answer.** Delete the semicolon after `string greeting = "Hello, C#"` and build. The compiler reports error CS1002, `; expected`, and positions it at the end of that statement, just after the closing quote. The build stops, so no program runs: nothing prints, not even the greeting. That makes it a compilation failure, not a runtime failure. Restore the semicolon and the run succeeds again.

**Why it is correct.** C# requires a semicolon to end each declaration statement. The parser notices the problem only when it reaches the end of the statement without one, which is why the diagnostic points at the end of the line rather than at any earlier word. A runtime failure, by contrast, needs a compiled program that starts and then throws.

**Plausible wrong approach.** Treating it as a runtime crash and looking for an exception or a stack trace finds nothing, because no executable was produced. Searching the next line for the mistake is also misleading: the error belongs to the statement that ends where the diagnostic points.

**How to verify.** With the semicolon removed, confirm the build output contains `CS1002` with the line of the greeting declaration and that the run produces no `Hello, C#` and no lesson marker. Put the semicolon back and confirm both lines print.

### Task 5: Boundary evidence

Compare zero rows with one row and explain why multiplication handles both without a branch.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
int seatsPerRow = 6;
int noRows = 0 * seatsPerRow;
int oneRow = 1 * seatsPerRow;
Check(noRows == 0, "zero rows hold no seats");
Check(oneRow == seatsPerRow, "one row holds one row of seats");
```

**Observe:** Zero rows give 0 seats and one row gives 6 seats, both from the same formula.

Zero times any count is zero and one times a count is that count, so `rows * seatsPerRow` is already correct at both edges. No `if (rows == 0)` branch is needed, and the formula from task 3 needs no special case for small halls.

**Plausible wrong approach.** Adding `if (rows == 0) seats = 0; else seats = rows * seatsPerRow;` produces the same numbers with an extra path that must be tested and maintained. Worse, a special case written as `seats = 1` for an empty hall would quietly disagree with the formula.

**How to verify.** Also check two rows: `2 * seatsPerRow` must be 12. If the three results 0, 6 and 12 grow by the same step, the formula is linear in rows, as the seat plan expects.

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
