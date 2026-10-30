# java-023: Locks, atomics and concurrent collections

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-022`

## Learning objectives

Explain critical section, compare-and-set, lock ordering using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Run two workers making 1000 synchronized increments each. The final exercise transfers the mechanism to use one global order for two locks.

## Purpose and mental model

Synchronization protects a state transition,not merely a variable name. A synchronized block uses a monitor and provides mutual exclusion plus visibility when all participants follow the same locking policy. AtomicInteger supports individual atomic operations such as increment and compare-and-set. ConcurrentHashMap provides thread-safe operations,but a separate get followed by put is still a compound sequence unless a method such as compute or merge makes it atomic for a key.

Locks also create lifetime and ordering obligations. Always release an explicit lock in finally. Acquiring multiple locks in inconsistent order can deadlock;using one global order removes that cycle for the declared lock set. A timed tryLock can make contention a bounded outcome rather than an indefinite wait. This lesson tests exact counts and controlled contention,not a universal concurrency performance claim.

## Vocabulary and concepts

**Critical section:** The state transition protected by one mutual-exclusion policy.

**Compare-and-set:** An atomic conditional update based on an expected current value.

**Lock ordering:** A consistent acquisition order preventing a declared class of cycles.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-023/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

Use synchronized around the entire read-modify-write. AtomicInteger.incrementAndGet performs one atomic increment. compareAndSet succeeds only when the current value matches the expected value. ConcurrentHashMap.merge combines updates atomically for a key. ReentrantLock.tryLock(timeout,unit) returns false on bounded contention;unlock belongs in finally after a successful acquisition.

## Worked example / walkthrough

### Example A: Protect a compound counter

The lock covers the complete increment. Synchronizing only a read or only a write would still permit lost updates.

```java
import java.util.*;

public class Main {

  static final class Counter {

    private int value;

    synchronized void increment() {
      value++;
    }

    synchronized int value() {
      return value;
    }
  }

  static void join(Thread thread) throws InterruptedException {
    thread.join(2500);
    if (thread.isAlive()) {
      thread.interrupt();
      throw new AssertionError("worker did not stop");
    }
  }

  static void runTwo(Runnable action) throws Exception {
    var failure = new java.util.concurrent.atomic.AtomicReference<Throwable>();
    Runnable checked = () -> {
      try {
        action.run();
      } catch (Throwable error) {
        failure.set(error);
      }
    };
    Thread a = Thread.ofPlatform().start(checked),
      b = Thread.ofPlatform().start(checked);
    join(a);
    join(b);
    if (failure.get() != null) throw new AssertionError("worker failed", failure.get());
  }

  public static void main(String[] args) throws Exception {
    Counter counter = new Counter();
    runTwo(() -> {
      for (int i = 0; i < 1000; i++) counter.increment();
    });
    assert counter.value() == 2000;
  }
}
```

**Expected:** counter 2000.

### Example B: Use an atomic increment

The atomic operation matches this simple counter contract. More complex multi-field invariants may still require a larger critical section.

```java
import java.util.*;

public class Main {

  static final class Counter {

    private int value;

    synchronized void increment() {
      value++;
    }

    synchronized int value() {
      return value;
    }
  }

  static void join(Thread thread) throws InterruptedException {
    thread.join(2500);
    if (thread.isAlive()) {
      thread.interrupt();
      throw new AssertionError("worker did not stop");
    }
  }

  static void runTwo(Runnable action) throws Exception {
    var failure = new java.util.concurrent.atomic.AtomicReference<Throwable>();
    Runnable checked = () -> {
      try {
        action.run();
      } catch (Throwable error) {
        failure.set(error);
      }
    };
    Thread a = Thread.ofPlatform().start(checked),
      b = Thread.ofPlatform().start(checked);
    join(a);
    join(b);
    if (failure.get() != null) throw new AssertionError("worker failed", failure.get());
  }

  public static void main(String[] args) throws Exception {
    Counter counter = new Counter();
    runTwo(() -> {
      for (int i = 0; i < 1000; i++) counter.increment();
    });
    assert counter.value() == 2000;

    var atomic = new java.util.concurrent.atomic.AtomicInteger();
    runTwo(() -> {
      for (int i = 0; i < 1000; i++) atomic.incrementAndGet();
    });
    assert atomic.get() == 2000;
  }
}
```

**Expected:** value2000.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Protect a compound counter.** Run two workers making 1000 synchronized increments each.
   **Expected:** counter 2000.
   **Verify:** Compare your assertion values or captured diagnostic with counter 2000.

2. **Use an atomic increment.** Repeat the workload withAtomicInteger.incrementAndGet.
   **Expected:** value2000.
   **Verify:** Compare your assertion values or captured diagnostic with value2000.

3. **Inspect compare-and-set.** Change0to1 with CAS,then retry expecting0.
   **Expected:** first true;second false;value1.
   **Verify:** Compare your assertion values or captured diagnostic with first true;second false;value1.

4. **Combine map updates atomically.** UseConcurrentHashMap.merge for2000 total increments ofkeyx.
   **Expected:** stored count2000.
   **Verify:** Compare your assertion values or captured diagnostic with stored count2000.

5. **Bound lock contention.** Hold a ReentrantLock in the caller while a worker tries to acquire it with a short timeout.
   **Expected:** worker returns false;lock released in finally.
   **Verify:** Compare your assertion values or captured diagnostic with worker returns false;lock released in finally.

6. **Use one global order for two locks.** Have both workers acquire first then second before incrementing shared state.
   **Expected:** 2000 increments and no blocked worker after bounded joins.
   **Verify:** Compare your assertion values or captured diagnostic with 2000 increments and no blocked worker after bounded joins.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Critical section, Compare-and-set, Lock ordering in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/atomic/AtomicInteger.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-023: Locks, atomics and concurrent collections.
Read courses/java/guides/java-023.md and courses/java/lessons/java-023.java. Direct prerequisites: `java-022`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
