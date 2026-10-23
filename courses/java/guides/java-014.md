# java-014: Streams and collectors

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-013`

## Learning objectives

Explain lazy pipeline, terminal operation, associative reduction using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Keep even values from 1,2,3,4 and sum their squares. The final exercise transfers the mechanism to expose nonassociative subtraction.

## Purpose and mental model

A stream is a single-use computation pipeline over a source. Intermediate operations such as filter and map are lazy: defining them does not necessarily process elements. A terminal operation such as collect or sum triggers the computation. The pipeline describes transformations, not a mutable container. Reduction requires an identity and an associative combination rule if it is to behave predictably under partitioning. Side effects in stream operations can make execution order and parallel behavior difficult to reason about. Prefer collectors and pure mappings over appending to a shared list from a parallelforEach.

## Vocabulary and concepts

**Lazy pipeline:** A computation whose intermediate stages wait for a terminal operation.

**Terminal operation:** An operation that consumes a stream and produces a result or action.

**Associative reduction:** A combination rule unaffected by regrouping operands.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-014/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

stream() creates a pipeline,filter keeps matching elements,andmapToInt selects a primitive numeric stream. sum is a terminal reduction with identity0. groupingBy collects rows into groups;counting or summingInt defines the group aggregate. A stream cannot be reused after a terminal operation. In a parallel reduction, the identity must be neutral for every partition, and subtraction is not associative.

## Worked example / walkthrough

### Example A: Filter and sum

The pipeline preserves the order of conceptual operations: selection happens before squaring and reduction. The result is a scalar rather than a modified source list.

```java
import java.util.*;

public class Main {

    public static void main(String[] args) throws Exception {
        int total = List.of(1,2,3,4).stream().filter(value -> value % 2 == 0).mapToInt(value -> value * value).sum();
        assert total == 20;
    }
}

```

**Expected:** 20.

### Example B: Observe laziness with an explicit terminal

The counter is a teaching probe, not a recommended business side effect. toList requires mapped values, while some terminals may optimize away unnecessary stages.

```java
import java.util.*;

public class Main {

    public static void main(String[] args) throws Exception {
        int total = List.of(1,2,3,4).stream().filter(value -> value % 2 == 0).mapToInt(value -> value * value).sum();
        assert total == 20;

        var calls = new java.util.concurrent.atomic.AtomicInteger();
        var pipeline = List.of(1,2,3).stream().map(value -> { calls.incrementAndGet(); return value * 2; });
        assert calls.get() == 0;
        assert pipeline.toList().equals(List.of(2,4,6)) && calls.get() == 3;
    }
}

```

**Expected:** counter0 before terminal and3 after.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Filter and sum.** Keep even values from 1,2,3,4 and sum their squares.
   **Expected:** 20.
   **Verify:** Compare your assertion values or captured diagnostic with 20.

2. **Observe laziness with an explicit terminal.** Create a mapped stream that increments a counter,then consumetoList.
   **Expected:** counter0 before terminal and3 after.
   **Verify:** Compare your assertion values or captured diagnostic with counter0 before terminal and3 after.

3. **Group with a collector.** Count red,blue,red withgroupingBy and counting.
   **Expected:** red2L,blue1L.
   **Verify:** Compare your assertion values or captured diagnostic with red2L,blue1L.

4. **Reject stream reuse.** Consume a stream once,then attempt another terminal operation.
   **Expected:** IllegalStateException.
   **Verify:** Compare your assertion values or captured diagnostic with IllegalStateException.

5. **Check the reduction identity.** Compare sum reduction with identity0 against a deliberately wrong identity10.
   **Expected:** correct6;wrong16 in the sequential fixture.
   **Verify:** Compare your assertion values or captured diagnostic with correct6;wrong16 in the sequential fixture.

6. **Expose nonassociative subtraction.** Compare(10-3)-2 with10-(3-2),then use an associative sum for a parallel fixture.
   **Expected:** 5 versus 9; parallel sum 5050.
   **Verify:** Compare your assertion values or captured diagnostic with 5 versus 9; parallel sum 5050.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Lazy pipeline, Terminal operation, Associative reduction in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/Stream.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Consult `docs/implementation/java-content-status.md` for the actual compile/run receipts. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-014: Streams and collectors.
Read courses/java/guides/java-014.md and courses/java/lessons/java-014.java. Direct prerequisites: `java-013`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
