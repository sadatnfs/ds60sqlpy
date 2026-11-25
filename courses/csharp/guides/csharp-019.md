# csharp-019: Delegates, closures and events

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `csharp-018`

## Learning objectives

Use delegates, closures and events, including what a closure captures and how to unsubscribe. The central exercise is task 3: Write a transformation method accepting Func<int,int>.

## Purpose and mental model

A delegate is a typed reference to callable behavior. Passing behavior lets a reusable algorithm vary one decision, such as filtering or transformation, while keeping traversal unchanged. A closure also carries access to variables from its surrounding scope. It captures the variable relationship, which can make later mutations visible when the function eventually executes.

Events build a publish-and-subscribe boundary. The publisher controls when to raise an event; subscribers supply reactions. Subscriptions also create reference relationships and lifetime obligations. A long-lived publisher can retain subscribers unless they unsubscribe. Start with short, deterministic delegate examples before adding event-driven application lifetime.

## Vocabulary and concepts

**Delegate:** A typed callable reference.

**Closure:** A function together with captured surrounding variables.

**Subscription:** A registered callback relationship.

## How to run this lesson

`Signal` is the only helper; it raises its event with `Raised?.Invoke`, so emitting with no subscribers does nothing rather than throwing. For task 4, unsubscribe with a freshly written lambda that has the same text and run it: the handler stays attached and `calls` ends at 2.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`Func<int,int>` represents a callable taking int and returning int. `x => x * factor` is a lambda. An event uses `+=` to subscribe and `-=` to remove the same handler instance.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** `factor` starts at 2. The lambda `value => value * factor` captures the variable `factor` itself, not its current value. `scale(3)` reads factor, finds 2 and returns 6. After `factor = 4`, the same delegate reads the variable again and `scale(3)` returns 12. Capturing a variable means later writes are visible.

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

**Trace.** `handler` stores one delegate instance. `+=` adds it to the event's invocation list, and `Emit` calls it, so `calls` becomes 1. `-=` with the same instance removes it, so the second `Emit` finds no subscribers and `Raised?.Invoke` skips the call. The count stays at 1 because removal matched the stored delegate.

## Exercises

1. **Predict and explain.** Predict both scale results before running.

2. **Guided modification.** Capture a separate local snapshot and compare its behavior after factor changes.

3. **Independent construction.** Write a transformation method accepting Func<int,int>.

4. **Diagnose a defect.** Diagnose unsubscribing with a newly created lambda instead of the subscribed delegate.

5. **Boundary evidence.** Test no subscribers and two subscribers.

6. **Transfer and justify.** Design ownership for subscriptions in a screen or service that can be disposed.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Closure capture can retain large objects or unexpected mutable state. Event handlers should avoid hiding failures. A new lambda with similar source is not necessarily the same delegate needed for unsubscription.

Task 4's version writes `source.Raised -= (_, _) => calls++;`, which creates a new delegate. It matches nothing in the invocation list, so removal silently fails and the second emission increments calls to 2. For task 5, two subscribers must each run once per emission, and a source with none must not throw.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (A closure observes its captured variable) before changing anything, and confirm its observation: Changing factor changes later calls through the closure.
2. Compare Example B (Manage an event subscription) with Example A and name the first line whose behavior differs. Its observation is: Only the first emission reaches the removed handler.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Closure capture can retain large objects or unexpected mutable state.

## Self-check and next step

Predict `scale(3)` after `factor = 0`, and explain why. Describe what a local copy taken before the change, such as `int snapshot = factor;`, would capture instead. For task 6, say which object unsubscribes when a screen closes and what stays alive in memory if it never does.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/): The C# programming guide's articles on delegates, lambda expressions and events explain capture, invocation lists and subscription.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
