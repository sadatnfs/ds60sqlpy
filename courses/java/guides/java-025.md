# java-025: JVM memory, GC and allocation

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-024`

## Learning objectives

Explain object reachability and retention and measure allocation and memory use without misleading claims. Along the way, explain reachability, retention, garbage collection, allocation rate using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Create a WeakReference to the still-strongly-referenced array. The final exercise transfers the mechanism to record process memory cautiously.

## Purpose and mental model

The JVM manages heap memory through reachability, not by immediately freeing an object when a local variable changes. References in collections, static fields, thread locals or listeners can keep objects alive after a caller no longer needs them. Stack frames hold local execution state and references, while objects and arrays generally live in managed heap storage. An unreachable object becomes eligible for collection, but collection timing is not a deterministic application contract.

System.gc is a request rather than proof that a particular object was reclaimed. Memory counters are observations affected by allocation, collection and implementation details. This lesson uses bounded arrays and explicit ownership changes to explain retention without allocating until failure or relying on a forced collection. Weak references can observe optional reachability, but application correctness should not depend on when a weakly reachable object disappears.

## Vocabulary and concepts

**Reachability:** Whether an object can be reached through active reference paths.

**Retention:** Keeping an object alive through a reference that still exists.

**Garbage collection:** Reclaiming managed memory according to runtime policy.

**Allocation rate:** The amount of new storage created over a period of work.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-025/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

A collection holding an array retains a strong reference. Clearing the collection removes that particular ownership path, but other references may remain. WeakReference.get may return the referent or null depending on reachability and collection. Runtime memory values describe the current process and should not be treated as exact per-object size measurements. Avoid finalizers as a resource-lifetime mechanism; use explicit close for files, sockets and executors.

## Worked example / walkthrough

### Example A: Expose a strong retention path

The local reference disappearing does not remove the list's ownership path. This is a common source of unbounded cache or listener retention.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    List<byte[]> retained = new ArrayList<>();
    byte[] payload = new byte[1024];
    payload[0] = 7;
    retained.add(payload);
    payload = null;
    assert retained.get(0)[0] == 7 && retained.get(0).length == 1024;
  }
}
```

**Expected:** list still exposes the same array contents.

### Example B: Remove one ownership path deliberately

Clearing a container removes its references, but another strong reference can keep the object reachable. Reachability is a graph property.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    List<byte[]> retained = new ArrayList<>();
    byte[] payload = new byte[1024];
    payload[0] = 7;
    retained.add(payload);
    payload = null;
    assert retained.get(0)[0] == 7 && retained.get(0).length == 1024;

    byte[] separate = retained.get(0);
    retained.clear();
    assert retained.isEmpty() && separate[0] == 7;
  }
}
```

**Expected:** list empty; separate array still valid.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Expose a strong retention path: change one input.** Copy Example A into a scratch `Main.java` and change `byte[] payload = new byte[1024];` to `byte[] payload = new byte[1025];`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `retained.get(0)[0] == 7 && retained.get(0).length == 1024`. Restoring the original line brings back the worked observation: list still exposes the same array contents.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `retained.get(0)[0] == 7 && retained.get(0).length == 1024` false. After restoring the line, the program completes without an `AssertionError` again.

2. **Remove one ownership path deliberately: diagnose an edited check.** A careless edit changed the assertion that Example B adds after Example A so that it reads `assert retained.isEmpty() && separate[1] == 7;`. Run Example B with that line, explain why the edited assertion now fails for the same program state, and restore it.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `retained.isEmpty() && separate[0] == 7`; after it the line reads `assert retained.isEmpty() && separate[0] == 7;` again and list empty; separate array still valid.
   **Verify:** Keep the failing and the repaired runs. Explain why the edited assertion rejects the same program state that `retained.isEmpty() && separate[0] == 7` accepts.

3. **Inspect a weak reference without timing assumptions.** Create a WeakReference to the still-strongly-referenced array.
   **Expected:** weak get returns the same object while strong reference exists.
   **Verify:** Keep an assertion equivalent to `weak.get() == separate`. As a control, change `assert weak.get() == separate;` to `assert weak.get() != separate;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

4. **Separate value size from allocation count.** Create ten arrays of 128 bytes and count logical payload bytes.
   **Expected:** 1280 logical bytes; no exact heap-overhead claim.
   **Verify:** Keep an assertion equivalent to `logical == 1280`. As a control, change `for (int i = 0; i < 10; i++) blocks.add(new byte[128]);` to `for (int i = 0; i <= 10; i++) blocks.add(new byte[128]);`: the run must fail with an `AssertionError` from the assertion on `logical == 1280`. Restore the line before continuing.

5. **Reuse a bounded working buffer.** Fill one array repeatedly rather than retaining every intermediate array.
   **Expected:** same buffer identity; final value 9.
   **Verify:** Keep an assertion equivalent to `System.identityHashCode(buffer) == identity && buffer[0] == 9`. As a control, change `for (int i = 0; i < 10; i++) Arrays.fill(buffer, (byte) i);` to `for (int i = 0; i <= 10; i++) Arrays.fill(buffer, (byte) i);`: the run must fail with an `AssertionError` from the assertion on `System.identityHashCode(buffer) == identity && buffer[0] == 9`. Restore the line before continuing.

6. **Record process memory cautiously.** Read Runtime total/free/max memory and check only valid ordering relationships.
   **Expected:** nonnegative counters; max at least total; no claim of exact object size.
   **Verify:** Keep an assertion equivalent to `total >= 0 && free >= 0 && maximum >= total` and confirm that `java -ea Main` completes. Then name an input that would make it fail and explain which value changes.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: list still exposes the same array contents. Then list the values read by `retained.get(0)[0] == 7 && retained.get(0).length == 1024` and trace each one from its declaration. Finally, compute the asserted value with `byte[] payload = new byte[1025];` in place before running.
- **Exercise 2:** First restate the expected observation: list empty; separate array still valid. Then list the values read by `retained.isEmpty() && separate[0] == 7` and trace each one from its declaration. Finally, compare `assert retained.isEmpty() && separate[1] == 7;` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: weak get returns the same object while strong reference exists. Then list the values read by `weak.get() == separate` and trace each one from its declaration. Finally, name one input that would make `weak.get() == separate` false.
- **Exercise 4:** First restate the expected observation: 1280 logical bytes; no exact heap-overhead claim. Then list the values read by `logical == 1280` and trace each one from its declaration. Finally, predict the effect of changing `for (int i = 0; i < 10; i++) blocks.add(new byte[128]);` to `for (int i = 0; i <= 10; i++) blocks.add(new byte[128]);` before running anything.
- **Exercise 5:** First restate the expected observation: same buffer identity; final value 9. Then list the values read by `System.identityHashCode(buffer) == identity && buffer[0] == 9` and trace each one from its declaration. Finally, predict the effect of changing `for (int i = 0; i < 10; i++) Arrays.fill(buffer, (byte) i);` to `for (int i = 0; i <= 10; i++) Arrays.fill(buffer, (byte) i);` before running anything.
- **Exercise 6:** First restate the expected observation: nonnegative counters; max at least total; no claim of exact object size. Then list the values read by `total >= 0 && free >= 0 && maximum >= total` and trace each one from its declaration. Finally, name one input that would make `total >= 0 && free >= 0 && maximum >= total` false.

## Self-check and retrieval

Close the solution and explain Reachability, Retention, Garbage collection in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/ref/Reference.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-025: JVM memory, GC and allocation.
Read courses/java/guides/java-025.md and courses/java/lessons/java-025.java. Direct prerequisites: `java-024`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
