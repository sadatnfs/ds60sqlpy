# csharp-019: Delegates, closures and events

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-018`

## Learning objectives

Write a transformation method accepting Func<int,int>. Then design ownership for subscriptions in a screen or service that can be disposed.

## Purpose and mental model

A delegate is a typed reference to callable behavior. Passing behavior lets a reusable algorithm vary one decision, such as filtering or transformation, while keeping traversal unchanged. A closure also carries access to variables from its surrounding scope. It captures the variable relationship, which can make later mutations visible when the function eventually executes.

Events build a publish-and-subscribe boundary. The publisher controls when to raise an event; subscribers supply reactions. Subscriptions also create reference relationships and lifetime obligations. A long-lived publisher can retain subscribers unless they unsubscribe. Start with short, deterministic delegate examples before adding event-driven application lifetime.

## Vocabulary and concepts

**Delegate:** A typed callable reference.

**Closure:** A function together with captured surrounding variables.

**Subscription:** A registered callback relationship.

## How to run this lesson

The Linux Docker classroom compiles your saved pad as `Program.cs` in its fixed .NET 10 project. C# 14 is the matching language generation. This route uses the prepared framework libraries; it does not accept arbitrary project files, NuGet packages, command arguments or interactive input. The explicit `Program.Main` entrypoint makes compilation and execution visible. `Check` throws on a false condition in every build configuration, unlike conditional debugging assertions.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`Func<int,int>` represents a callable taking int and returning int. `x => x * factor` is a lambda. An event uses `+=` to subscribe and `-=` to remove the same handler instance.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: A closure observes its captured variable

The closure refers to the variable, not a permanently copied value from creation time.

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
      int factor = 2;
      Func<int, int> scale = value => value * factor;
      Check(scale(3) == 6, "initial capture");
      factor = 4;
      Check(scale(3) == 12, "capture is not frozen");
    }
    Console.WriteLine("csharp-019: passed");
    await Task.CompletedTask;
  }

  public sealed class Signal {
    public event EventHandler? Raised;
    public void Emit() => Raised?.Invoke(this, EventArgs.Empty);
  }
}
```

**Observe:** Changing factor changes later calls through the closure.

### Example B: Manage an event subscription

Keeping the handler reference makes unsubscription precise and prevents a lingering callback.

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
      var source = new Signal();
      int calls = 0;
      EventHandler handler = (_, _) => calls++;
      source.Raised += handler;
      source.Emit();
      source.Raised -= handler;
      source.Emit();
      Check(calls == 1, "unsubscribe ends observation");
    }
    Console.WriteLine("csharp-019: passed");
    await Task.CompletedTask;
  }

  public sealed class Signal {
    public event EventHandler? Raised;
    public void Emit() => Raised?.Invoke(this, EventArgs.Empty);
  }
}
```

**Observe:** Only the first emission reaches the removed handler.

## Exercises

1. **Predict and explain.** Predict both scale results before running.

2. **Guided modification.** Capture a separate local snapshot and compare its behavior after factor changes.

3. **Independent construction.** Write a transformation method accepting Func<int,int>.

4. **Diagnose a defect.** Diagnose unsubscribing with a newly created lambda instead of the subscribed delegate.

5. **Boundary evidence.** Test no subscribers and two subscribers.

6. **Transfer and justify.** Design ownership for subscriptions in a screen or service that can be disposed.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Closure capture can retain large objects or unexpected mutable state. Event handlers should avoid hiding failures. A new lambda with similar source is not necessarily the same delegate needed for unsubscription.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Delegate, Closure, Subscription without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://learn.microsoft.com/en-us/dotnet/csharp/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for csharp-019: Delegates, closures and events.
Read courses/csharp/guides/csharp-019.md and courses/csharp/lessons/csharp-019.cs. Prerequisites: csharp-018.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/csharp/solutions/csharp-019_solution.cs and
courses/csharp/solutions/csharp-019_solutions.md closed until I request comparison or show an attempt.
Use csharp-dotnet for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
