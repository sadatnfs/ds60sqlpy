# java-009: Exceptions and resource lifetime

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-008`

## Learning objectives

Manage resources with try-with-resources and read close order, suppressed exceptions and translated causes.

The six exercises practice these steps:

- Close on normal completion.
- Close in reverse order.
- Close after body failure.
- Preserve suppressed close failure.
- Observe close-only failure.
- Retain a translated cause.

## Purpose and mental model

Exceptions separate normal return values from failure. A checked exception is declared or handled by callers; an unchecked exception often signals an invalid argument or programming error. Resource lifetime is a different concern: a resource must close whether the body succeeds or fails. try-with-resources closes resources in reverse declaration order. If the body throws and closing also throws, the body exception remains primary and close failures are attached as suppressed exceptions. Catching everything and returning a default would erase that information. This lesson uses tiny in-memory AutoCloseable probes to make lifetime order and suppression observable without opening external files.

## Vocabulary and concepts

**Checked exception:** A failure type that callers must declare or handle.

**Resource lifetime:** The interval during which an owned resource is usable.

**Suppressed exception:** A secondary close failure retained beside a primary exception.

## How to run this lesson

`Probe` is a small `AutoCloseable` declared inside `Main` that appends events to a list and can be told to fail in `close`, so the lesson observes resource lifetime without opening any file.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

A try(resource declarations) block owns the declared resources until control exits. AutoCloseable.close may throw Exception. getSuppressed exposes secondary close failures. Use a specific catch when a failure is expected, and preserve the original cause when translating to a domain exception. A finally block is useful for cleanup patterns not covered by resources, but throwing from finally can replace an important earlier failure.

## Worked example / walkthrough

### Example A: Close on normal completion

Leaving the block triggers close even without an explicit call in the body. Ownership is visible in the block structure.

```java
import java.util.*;

public class Main {

  static final class Probe implements AutoCloseable {

    private final String name;
    private final List<String> events;
    private final boolean fail;

    Probe(String name, List<String> events, boolean fail) {
      this.name = name;
      this.events = events;
      this.fail = fail;
    }

    public void close() throws java.io.IOException {
      events.add("close" + name);
      if (fail) throw new java.io.IOException("close" + name);
    }
  }

  public static void main(String[] args) throws Exception {
    List<String> events = new ArrayList<>();
    try (Probe resource = new Probe("A", events, false)) {
      events.add("body");
    }
    assert events.equals(List.of("body", "closeA"));
  }
}
```

**Expected:** events `body` then `closeA`.

### Example B: Close in reverse order

Later resources often depend on earlier ones, so reverse closure is deliberate. The event trace proves the actual order for this fixture.

```java
import java.util.*;

public class Main {

  static final class Probe implements AutoCloseable {

    private final String name;
    private final List<String> events;
    private final boolean fail;

    Probe(String name, List<String> events, boolean fail) {
      this.name = name;
      this.events = events;
      this.fail = fail;
    }

    public void close() throws java.io.IOException {
      events.add("close" + name);
      if (fail) throw new java.io.IOException("close" + name);
    }
  }

  public static void main(String[] args) throws Exception {
    List<String> events = new ArrayList<>();
    try (Probe resource = new Probe("A", events, false)) {
      events.add("body");
    }
    assert events.equals(List.of("body", "closeA"));

    events.clear();
    try (Probe a = new Probe("A", events, false); Probe b = new Probe("B", events, false)) {
      events.add("body");
    }
    assert events.equals(List.of("body", "closeB", "closeA"));
  }
}
```

**Expected:** `closeB` is recorded before `closeA`.

## Prediction before your attempt

Before running Example A, list the events in order for a body that records `body` and a resource named A. For Example B, predict whether B or A closes first, and why that order is deliberate. Before Exercise 4, decide which exception the `catch` receives when both the body and `close` throw, and where the other exception ends up.

## Exercises

1. **Close on normal completion: change one input.** Change `try (Probe resource = new Probe("A", events, false)) {` to `try (Probe resource = new Probe("A!", events, false)) {` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `events.equals(List.of("body", "closeA"))`.
   **Verify:** Name the value that makes `events.equals(List.of("body", "closeA"))` false, then restore the line.

2. **Close in reverse order: debug a regression.** A regression in Example B's new code makes one line read `try (Probe a = new Probe("A!", events, false); Probe b = new Probe("B", events, false)) {`. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `events.equals(List.of("body", "closeB", "closeA"))`; the repaired line reads `try (Probe a = new Probe("A", events, false); Probe b = new Probe("B", events, false)) {`.
   **Verify:** Explain how the changed token alters the value that `events.equals(List.of("body", "closeB", "closeA"))` tests.

3. **Close after body failure.** Throw IllegalStateException in the body and inspect events after catching it.
   **Expected:** `closeA` is still recorded.
   **Verify:** Control: changing `bodyFailed = true;` to `bodyFailed = false;` must fail the assertion on `bodyFailed && events.equals(List.of("closeA"))`.

4. **Preserve suppressed close failure.** Make the body throw and the resource close throw too.
   **Expected:** primary message `body`; one suppressed exception `closeA`.
   **Verify:** Control: changing `try (Probe a = new Probe("A", events, true)) {` to `try (Probe a = new Probe("A!", events, true)) {` must fail the assertion on `expected.getSuppressed()[0].getMessage().equals("closeA")`.

5. **Observe close-only failure.** Let the body succeed but close throw IOException.
   **Expected:** IOException `closeA` is primary.
   **Verify:** Control: changing `try (Probe a = new Probe("A", events, true)) {} catch (java.io.IOException expected) {` to `try (Probe a = new Probe("A", events, false)) {} catch (java.io.IOException expected) {` must fail the assertion on `closeFailed`.

6. **Retain a translated cause.** Wrap an IOException in IllegalStateException with a domain message and inspect cause.
   **Expected:** cause remains the original IOException.
   **Verify:** Control: changing `assert translated.getCause() == original && translated.getMessage().contains("fixture");` to `assert translated.getCause() == original && translated.getMessage().contains("fixture!");` inside the assertion must make it fail.

## Common pitfalls and diagnosis

Calling `close()` by hand at the end of a `try` block skips it whenever the body throws; try-with-resources runs it on both paths. Do not catch `Exception` and return a default, because that hides which failure happened. When translating an exception, pass the original as the cause; a new exception built from only `e.getMessage()` loses the type and stack trace. And a close failure without a body failure becomes the primary exception, not a suppressed one.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the edit renames the resource, so its `close` records `closeA!`. Then write the event list the block produces. Finally, compare it with `List.of("body", "closeA")` and say which element differs.
- **Exercise 2:** First write the events for resources A! and B, remembering that they close in reverse declaration order. Then compare your list with the one the assertion expects. Finally, decide whether the edit changed the closing order or only a name.
- **Exercise 3:** First throw `IllegalStateException` inside the body of a try-with-resources block for Probe A. Then catch it after the block and set `bodyFailed`. Finally, assert that `closeA` was still recorded, which proves cleanup ran on the failure path.
- **Exercise 4:** First create a Probe that fails in `close` and throw from the body as well. Then catch the body's exception and read its message. Finally, inspect `getSuppressed()` and confirm that the close failure was attached rather than lost.
- **Exercise 5:** First leave the body empty while the Probe fails in `close`. Then catch `IOException` around the block and set `closeFailed`. Finally, explain why the close failure is primary here: there is no body failure to attach it to.
- **Exercise 6:** First create an `IOException` and wrap it with `new IllegalStateException(message, original)`. Then compare `getCause()` with the original object using `==`. Finally, confirm that the domain message mentions the fixture, and explain what copying only the message would lose.

## Self-check and retrieval

From memory, describe the event order for two resources and a body that throws, including which exception is primary and which is suppressed. Explain the difference between a checked `IOException` and an unchecked `IllegalStateException`, and why a translated exception should keep its cause.

## Next step

Continue with `java-010`: Interfaces and polymorphism. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-009: Exceptions and resource lifetime.
Read courses/java/guides/java-009.md and courses/java/lessons/java-009.java. Direct prerequisites: `java-008`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
