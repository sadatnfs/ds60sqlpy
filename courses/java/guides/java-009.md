# java-009: Exceptions and resource lifetime

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-008`

## Learning objectives

Explain checked exception, resource lifetime, suppressed exception using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Open a Probe resource,recordbody,then inspect closure order. The final exercise transfers the mechanism to retain a translated cause.

## Purpose and mental model

Exceptions separate normal return values from failure. A checked exception is declared or handled by callers; an unchecked exception often signals an invalid argument or programming error. Resource lifetime is a different concern: a resource must close whether the body succeeds or fails. try-with-resources closes resources in reverse declaration order. If the body throws and closing also throws, the body exception remains primary and close failures are attached as suppressed exceptions. Catching everything and returning a default would erase that information. This lesson uses tiny in-memory AutoCloseable probes to make lifetime order and suppression observable without opening external files.

## Vocabulary and concepts

**Checked exception:** A failure type that callers must declare or handle.

**Resource lifetime:** The interval during which an owned resource is usable.

**Suppressed exception:** A secondary close failure retained beside a primary exception.

## How to run this lesson

Open the Docker classroom, choose the prepared Java21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-009/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

A try(resource declarations) block owns the declared resources until control exits. AutoCloseable.close may throwException. getSuppressed exposes secondary close failures. Use a specific catch when a failure is expected, and preserve the original cause when translating to a domain exception. A finally block is useful for cleanup patterns not covered by resources, but throwing fromfinally can replace an important earlier failure.

## Worked example / walkthrough

### Example A: Close on normal completion

Leaving the block triggers close even without an explicit call in the body. Ownership is visible in the block structure.

```java
import java.util.*;

public class Main {
    static final class Probe implements AutoCloseable {
        private final String name; private final List<String> events; private final boolean fail;
        Probe(String name, List<String> events, boolean fail) { this.name=name; this.events=events; this.fail=fail; }
        public void close() throws java.io.IOException { events.add("close"+name); if(fail) throw new java.io.IOException("close"+name); }
    }
    public static void main(String[] args) throws Exception {
        List<String> events = new ArrayList<>();
        try (Probe resource = new Probe("A", events, false)) { events.add("body"); }
        assert events.equals(List.of("body", "closeA"));
    }
}

```

**Expected:** eventsbody,closeA.

### Example B: Close in reverse order

Later resources often depend on earlier ones, so reverse closure is deliberate. The event trace proves the actual order for this fixture.

```java
import java.util.*;

public class Main {
    static final class Probe implements AutoCloseable {
        private final String name; private final List<String> events; private final boolean fail;
        Probe(String name, List<String> events, boolean fail) { this.name=name; this.events=events; this.fail=fail; }
        public void close() throws java.io.IOException { events.add("close"+name); if(fail) throw new java.io.IOException("close"+name); }
    }
    public static void main(String[] args) throws Exception {
        List<String> events = new ArrayList<>();
        try (Probe resource = new Probe("A", events, false)) { events.add("body"); }
        assert events.equals(List.of("body", "closeA"));

        events.clear();
        try (Probe a = new Probe("A", events, false); Probe b = new Probe("B", events, false)) { events.add("body"); }
        assert events.equals(List.of("body", "closeB", "closeA"));
    }
}

```

**Expected:** closeB beforecloseA.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Close on normal completion.** Open a Probe resource,recordbody,then inspect closure order.
   **Expected:** eventsbody,closeA.
   **Verify:** Compare your assertion values or captured diagnostic with eventsbody,closeA.

2. **Close in reverse order.** Declare resourcesA thenB and leave the block.
   **Expected:** closeB beforecloseA.
   **Verify:** Compare your assertion values or captured diagnostic with closeB beforecloseA.

3. **Close after body failure.** ThrowIllegalStateException in the body and inspect events after catching it.
   **Expected:** closeA stillrecorded.
   **Verify:** Compare your assertion values or captured diagnostic with closeA stillrecorded.

4. **Preserve suppressed close failure.** Make the body throw and the resource close throw too.
   **Expected:** primary messagebody;one suppressed exceptioncloseA.
   **Verify:** Compare your assertion values or captured diagnostic with primary messagebody;one suppressed exceptioncloseA.

5. **Observe close-only failure.** Let the body succeed butclose throwIOException.
   **Expected:** IOExceptioncloseA is primary.
   **Verify:** Compare your assertion values or captured diagnostic with IOExceptioncloseA is primary.

6. **Retain a translated cause.** Wrap anIOException inIllegalStateException with a domain message and inspectcause.
   **Expected:** cause remains the originalIOException.
   **Verify:** Compare your assertion values or captured diagnostic with cause remains the originalIOException.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Checked exception, Resource lifetime, Suppressed exception in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Consult `docs/implementation/java-content-status.md` for the actual compile/run receipts. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning for java-009: Exceptions and resource lifetime.
Read courses/java/guides/java-009.md and courses/java/lessons/java-009.java. Direct prerequisites: `java-008`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
