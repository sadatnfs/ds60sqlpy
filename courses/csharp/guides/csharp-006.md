# csharp-006: Loops, invariants and termination

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `csharp-005`

## Learning objectives

Write loops with a stated invariant and termination condition, including empty and not-found cases. The central exercise is task 3: Implement a first-match search returning a separate not-found representation.

## Purpose and mental model

A loop repeats a state transition. To understand it, state what is true before the first iteration and what remains true after each iteration. This repeated truth is an invariant. A second argument explains termination: some bounded quantity moves toward a stopping condition. A correct-looking body can still fail because its boundary executes once too often or never stops.

`foreach` expresses traversal of an existing sequence and usually avoids manual index bookkeeping. Use an index when the position itself matters, but relate the valid index range to the collection length. Empty inputs are especially revealing because the initial state becomes the final result without any iteration.

## Vocabulary and concepts

**Invariant:** A property maintained across iterations.

**Accumulator:** State summarizing the values seen so far.

**Termination:** An argument that repetition eventually stops.

## How to run this lesson

Example A calls LINQ's `Sum()` on an empty array; the classroom's implicit usings already import `System.Linq`. Task 4's off-by-one loop compiles and fails only at runtime with `IndexOutOfRangeException`, which tells you the bad index came from the loop condition rather than from the data.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`for (initial; condition; update)` initializes once, checks before each body, and updates after each body. For an array of Length n, valid indices are zero through n minus one. `break` exits the loop; `continue` skips the remainder of one iteration.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Sum with a maintained invariant

Before each iteration, sum equals the sum of values already visited. Zero is the identity that makes the invariant true initially.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using System.Globalization;
using System.Collections.Concurrent;
using System.Threading.Channels;
using System.Net;
using System.Net.Http;
using System.Text.RegularExpressions;
using System.Buffers;

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      int[] values = { 2, 4, 6 };
      int sum = 0;
      foreach (int value in values)
        sum += value;
      Check(sum == 12, "sum of all values");
      Check(Array.Empty<int>().Sum() == 0, "empty sum identity");
    }
    Console.WriteLine("csharp-006: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The sum is 12 and the empty sum is zero.

**Trace.** Before the loop, `sum` is 0, the total of no values. The first iteration adds 2, so sum is 2, the total of the one value visited. The second adds 4 for 6, and the third adds 6 for 12. After every step the invariant holds: sum equals the total of the values visited so far. `Array.Empty<int>().Sum()` returns 0, the same starting value.

### Example B: Locate the first match

Stopping at the first match is part of the contract. Without break, the same loop could return the last match.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using System.Globalization;
using System.Collections.Concurrent;
using System.Threading.Channels;
using System.Net;
using System.Net.Http;
using System.Text.RegularExpressions;
using System.Buffers;

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      int[] values = { 3, 8, 8 };
      int found = -1;
      for (int i = 0; i < values.Length; i++) {
        if (values[i] == 8) {
          found = i;
          break;
        }
      }
      Check(found == 1, "first matching position");
      Check(!Array.Exists(values, value => value == 9), "absent target");
    }
    Console.WriteLine("csharp-006: passed");
    await Task.CompletedTask;
  }
}
```

**Observe:** The first 8 is at index 1; 9 is absent.

**Trace.** `found` starts at -1, meaning not yet found. At index 0 the value 3 does not match. At index 1 the value is 8, so `found` becomes 1 and `break` leaves the loop at once; index 2 is never examined. Without `break`, the loop would continue to index 2 and overwrite found with 2, the last match. `Array.Exists` confirms that 9 is absent.

## Exercises

1. **Predict and explain.** Write the accumulator value before and after every iteration in Example A.

2. **Guided modification.** Skip negative values while preserving the sum invariant.

3. **Independent construction.** Implement a first-match search returning a separate not-found representation.

4. **Diagnose a defect.** Diagnose the condition i <= values.Length using a one-element array.

5. **Boundary evidence.** Check empty, singleton, no-match and repeated-match inputs.

6. **Transfer and justify.** Design a bounded retry loop and explain both its invariant and its stopping argument.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Loop indices count from zero while lengths count elements. A sentinel such as -1 must be checked before indexing. Mutating a collection during enumeration can invalidate the traversal contract.

For task 4, the one-element array `{ 5 }` is the smallest counterexample: with `i <= values.Length` the loop runs for 0 and then for 1, and the second access throws `IndexOutOfRangeException`. For task 5, the input `{ 8, 8 }` separates first match from last match, and an empty array checks that -1 comes back without any element access.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Sum with a maintained invariant) before changing anything, and confirm its observation: The sum is 12 and the empty sum is zero.
2. Compare Example B (Locate the first match) with Example A and name the first line whose behavior differs. Its observation is: The first 8 is at index 1; 9 is absent.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Loop indices count from zero while lengths count elements.

## Self-check and next step

Write the value of `sum` before and after each iteration of Example A, then state the invariant in one sentence. Explain what `found` means when the loop ends holding -1. For task 6's bounded retry loop, name the quantity that decreases on every attempt and the condition that stops the loop.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The reference describes `for`, `foreach`, `break` and `continue` in its iteration statements and jump statements articles.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-006: Loops, invariants and termination.
Read courses/csharp/guides/csharp-006.md and courses/csharp/lessons/csharp-006.cs. Prerequisites: csharp-005.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-006_solution.cs and
courses/csharp/solutions/csharp-006_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
