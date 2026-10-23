# java-024: Virtual threads and blocking work

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-023`

## Learning objectives

Explain virtual thread, carrier, backpressure, pinning in java21 using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Start a virtual thread that recordsisVirtual andjoin it. The final exercise transfers the mechanism to keep a blocking wait outside a monitor.

## Purpose and mental model

Virtual threads are lightweight Java threads intended to make large numbers of blocking tasks easier to express. They still run on carrier operating-system threads and do not create additional CPU cores. A CPU-bound calculation does not become faster merely because it is placed in a virtual thread. Resource limits such as database connections,remote quotas andmemory still need backpressure. A virtual-thread-per-task executor is therefore not permission to admit unlimited work.

Java21 has pinning cases where a virtual thread blocks while holding a synchronized monitor or during certain native operations,preventing its carrier from being reused for other virtual threads. Later JDK behavior can differ,so version the explanation. Keep blocking work outside a monitor when the state contract permits it,or redesign the synchronization carefully. This lesson checks thread identity,lifetime,cancellation and a semaphore admission limit without making throughput claims.

## Vocabulary and concepts

**Virtual thread:** A lightweight Java thread scheduled over carrier threads.

**Carrier:** An operating-system thread executing virtual-thread work.

**Backpressure:** A limit on admitted resource-consuming operations.

**Pinning in Java21:** A condition preventing a blocked virtual thread from releasing its carrier.

## How to run this lesson

Open the Docker classroom, choose the prepared Java21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-024/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

Thread.ofVirtual starts a virtual thread;isVirtual identifies it. Executors.newVirtualThreadPerTaskExecutor creates a new virtual thread for each admitted task. A Semaphore can bound simultaneous access to a scarce resource independently of thread count. Future.get andlatches provide bounded completion evidence. Cooperative interruption remains necessary,just as with platform threads.

## Worked example / walkthrough

### Example A: Observe virtual identity

The identity check establishes the actual thread type. It does not measure performance or the number of carrier threads used.

```java
import java.util.*;

public class Main {

    public static void main(String[] args) throws Exception {
        var virtual=new java.util.concurrent.atomic.AtomicBoolean();Thread task=Thread.ofVirtual().start(() -> virtual.set(Thread.currentThread().isVirtual()));task.join(2000);
        assert !task.isAlive() && virtual.get();
    }
}

```

**Expected:** true and terminated.

### Example B: Use a scoped virtual executor

The executor lifetime encloses its tasks. Capturing a separate effectively-final input per submission avoids confusing loop-state ownership.

```java
import java.util.*;

public class Main {

    public static void main(String[] args) throws Exception {
        var virtual=new java.util.concurrent.atomic.AtomicBoolean();Thread task=Thread.ofVirtual().start(() -> virtual.set(Thread.currentThread().isVirtual()));task.join(2000);
        assert !task.isAlive() && virtual.get();

        try(var executor=java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
            List<java.util.concurrent.Future<Integer>> futures=new ArrayList<>();for(int value=1;value<=4;value++){int input=value;futures.add(executor.submit(() -> input*input));}
            List<Integer> results=new ArrayList<>();for(var future:futures)results.add(future.get(2,java.util.concurrent.TimeUnit.SECONDS));
            assert results.equals(List.of(1,4,9,16));
        }
    }
}

```

**Expected:** 1,4,9,16.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Observe virtual identity.** Start a virtual thread that recordsisVirtual andjoin it.
   **Expected:** true and terminated.
   **Verify:** Compare your assertion values or captured diagnostic with true and terminated.

2. **Use a scoped virtual executor.** Submit four square calculations and retrieve their results with timeouts.
   **Expected:** 1,4,9,16.
   **Verify:** Compare your assertion values or captured diagnostic with 1,4,9,16.

3. **Limit a scarce resource with a semaphore.** Run six tasks but allow only two inside a gated resource section.
   **Expected:** maximum active count2;all six complete.
   **Verify:** Compare your assertion values or captured diagnostic with maximum active count2;all six complete.

4. **Preserve a CPU calculation contract.** Compare a sequential sum1..1000 with four partitioned virtual tasks.
   **Expected:** both500500;no speed claim.
   **Verify:** Compare your assertion values or captured diagnostic with both500500;no speed claim.

5. **Cancel a blocked virtual task.** Interrupt a virtual task waiting on a latch and observe its cleanup signal.
   **Expected:** Future cancelled;task exits cooperatively.
   **Verify:** Compare your assertion values or captured diagnostic with Future cancelled;task exits cooperatively.

6. **Keep a blocking wait outside a monitor.** Read a state snapshot inside a synchronized block,then wait on a latch after leaving it.
   **Expected:** caller can acquire the monitor while the worker is waiting.
   **Verify:** Compare your assertion values or captured diagnostic with caller can acquire the monitor while the worker is waiting.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Virtual thread, Carrier, Backpressure in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Consult `docs/implementation/java-content-status.md` for the actual compile/run receipts. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning for java-024: Virtual threads and blocking work.
Read courses/java/guides/java-024.md and courses/java/lessons/java-024.java. Direct prerequisites: `java-023`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
