# java-021: Threads and the memory model

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-020`

## Learning objectives

Explain happens-before, atomic operation, interruption using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Start a worker that writes 42 into a shared holder, join it with a bound, and inspect the result. The final exercise transfers the mechanism to respond to interruption.

## Purpose and mental model

Threads can execute concurrently while sharing memory. Correct communication requires a happens-before relationship,not an assumption that another thread has probably finished. Starting a thread publishes prior actions to it,and a successful join makes its completed actions visible to the joining thread. Volatile writes and reads establish a publication relationship for associated state,but volatile does not make a compound read-modify-write atomic. A counter increment reads,adds and writes,so two threads can lose an update even if each individual access is visible.

This lesson uses bounded joins,latches and a barrier to make ordering deliberate. A controlled lost-update fixture forces both workers to read the same starting value before either writes. That demonstrates the mechanism without hoping a random stress run happens to fail. Interruption is a cooperative request,not forcible termination;blocking code should respond or preserve the interrupt status when it cannot complete its work.

## Vocabulary and concepts

**Happens-before:** A memory-ordering relationship guaranteeing visibility of earlier actions.

**Atomic operation:** An operation that cannot be observed as separate interleaved steps.

**Interruption:** A cooperative signal requesting that a thread stop or change its work.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-021/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

Thread.start begins a new execution;calling run directly is an ordinary method call. join(timeout) waits only up to a bound,so check isAlive afterward. CountDownLatch coordinates a one-time event,and CyclicBarrier can align two reads before their writes. A volatile ready flag can publish a preceding data assignment. InterruptedException clears the interrupted status,so a handler that propagates cancellation through state should restore it with interrupt().

## Worked example / walkthrough

### Example A: Publish a result through join

The join establishes the required visibility after completion. A timed sleep would not provide the same guarantee.

```java
import java.util.*;

public class Main {

  static final class Publication {

    int data;
    volatile boolean ready;
  }

  static void joinBounded(Thread thread) throws InterruptedException {
    thread.join(2500);
    if (thread.isAlive()) {
      thread.interrupt();
      throw new AssertionError("thread did not terminate");
    }
  }

  public static void main(String[] args) throws Exception {
    int[] result = { 0 };
    Thread worker = Thread.ofPlatform().start(() -> result[0] = 42);
    joinBounded(worker);
    assert result[0] == 42;
  }
}
```

**Expected:** worker terminated; result 42.

### Example B: Publish initial state through start

Actions before start happen-before actions in the started thread. The fixture does not rely on the worker noticing an unsynchronized later mutation.

```java
import java.util.*;

public class Main {

  static final class Publication {

    int data;
    volatile boolean ready;
  }

  static void joinBounded(Thread thread) throws InterruptedException {
    thread.join(2500);
    if (thread.isAlive()) {
      thread.interrupt();
      throw new AssertionError("thread did not terminate");
    }
  }

  public static void main(String[] args) throws Exception {
    int[] result = { 0 };
    Thread worker = Thread.ofPlatform().start(() -> result[0] = 42);
    joinBounded(worker);
    assert result[0] == 42;

    int[] input = { 7 };
    var observed = new java.util.concurrent.atomic.AtomicInteger();
    Thread reader = Thread.ofPlatform().start(() -> observed.set(input[0]));
    joinBounded(reader);
    assert observed.get() == 7;
  }
}
```

**Expected:** worker observes7.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Publish a result through join.** Start a worker that writes 42 into a shared holder, join it with a bound, and inspect the result.
   **Expected:** worker terminated; result 42.
   **Verify:** Compare your assertion values or captured diagnostic with worker terminated; result 42.

2. **Publish initial state through start.** Assign7 before starting a worker that reads the holder.
   **Expected:** worker observes7.
   **Verify:** Compare your assertion values or captured diagnostic with worker observes7.

3. **Force a lost update.** Make two workers read counter0,wait at a barrier,then each write its saved value plus1.
   **Expected:** final counter1 despite two increments.
   **Verify:** Compare your assertion values or captured diagnostic with final counter1 despite two increments.

4. **Use a volatile publication flag.** Write data99 before setting a volatile ready flag;read after observing that flag.
   **Expected:** reader sees99 and finishes within the bound.
   **Verify:** Compare your assertion values or captured diagnostic with reader sees99 and finishes within the bound.

5. **Distinguish run from start.** Invoke a Runnable directly and compare its thread identity with the caller.
   **Expected:** same thread identity for directrun.
   **Verify:** Compare your assertion values or captured diagnostic with same thread identity for directrun.

6. **Respond to interruption.** Interrupt a worker waiting on a latch,restore its flag in the catch,and verify termination.
   **Expected:** interruption observed and worker terminated.
   **Verify:** Compare your assertion values or captured diagnostic with interruption observed and worker terminated.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Happens-before, Atomic operation, Interruption in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Thread.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-021: Threads and the memory model.
Read courses/java/guides/java-021.md and courses/java/lessons/java-021.java. Direct prerequisites: `java-020`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
