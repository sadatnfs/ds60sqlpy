# java-024: Virtual threads and blocking work

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-023`

## Learning objectives

Use virtual threads for blocking work, limit scarce resources with a semaphore and cancel blocked tasks. Along the way, explain virtual thread, carrier, backpressure, pinning in java 21 using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Run six tasks but allow only two inside a gated resource section. The final exercise transfers the mechanism to keep a blocking wait outside a monitor.

## Purpose and mental model

Virtual threads are lightweight Java threads intended to make large numbers of blocking tasks easier to express. They still run on carrier operating-system threads and do not create additional CPU cores. A CPU-bound calculation does not become faster merely because it is placed in a virtual thread. Resource limits such as database connections, remote quotas and memory still need backpressure. A virtual-thread-per-task executor is therefore not permission to admit unlimited work.

Java 21 has pinning cases where a virtual thread blocks while holding a synchronized monitor or during certain native operations, preventing its carrier from being reused for other virtual threads. Later JDK behavior can differ, so version the explanation. Keep blocking work outside a monitor when the state contract permits it, or redesign the synchronization carefully. This lesson checks thread identity, lifetime, cancellation and a semaphore admission limit without making throughput claims.

## Vocabulary and concepts

**Virtual thread:** A lightweight Java thread scheduled over carrier threads.

**Carrier:** An operating-system thread executing virtual-thread work.

**Backpressure:** A limit on admitted resource-consuming operations.

**Pinning in Java 21:** A condition preventing a blocked virtual thread from releasing its carrier.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-024/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

Thread.ofVirtual starts a virtual thread; isVirtual identifies it. Executors.newVirtualThreadPerTaskExecutor creates a new virtual thread for each admitted task. A Semaphore can bound simultaneous access to a scarce resource independently of thread count. Future.get and latches provide bounded completion evidence. Cooperative interruption remains necessary, just as with platform threads.

## Worked example / walkthrough

### Example A: Observe virtual identity

The identity check establishes the actual thread type. It does not measure performance or the number of carrier threads used.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    var virtual = new java.util.concurrent.atomic.AtomicBoolean();
    Thread task = Thread.ofVirtual().start(() -> virtual.set(Thread.currentThread().isVirtual()));
    task.join(2000);
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
    var virtual = new java.util.concurrent.atomic.AtomicBoolean();
    Thread task = Thread.ofVirtual().start(() -> virtual.set(Thread.currentThread().isVirtual()));
    task.join(2000);
    assert !task.isAlive() && virtual.get();

    try (var executor = java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
      List<java.util.concurrent.Future<Integer>> futures = new ArrayList<>();
      for (int value = 1; value <= 4; value++) {
        int input = value;
        futures.add(executor.submit(() -> input * input));
      }
      List<Integer> results = new ArrayList<>();
      for (var future : futures) results.add(future.get(2, java.util.concurrent.TimeUnit.SECONDS));
      assert results.equals(List.of(1, 4, 9, 16));
    }
  }
}
```

**Expected:** 1, 4, 9, 16.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Observe virtual identity: predict an edited check.** Copy Example A into a scratch `Main.java` and change `assert !task.isAlive() && virtual.get();` to `assert task.isAlive() && virtual.get();` inside its assertion. Before running it with `java -ea Main`, predict whether the assertion still holds and explain why; then restore it.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `!task.isAlive() && virtual.get()`. Restoring the original line brings back the worked observation: true and terminated.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and explain why the edited condition is false for the values that satisfy `!task.isAlive() && virtual.get()`. After restoring the line, the program completes without an `AssertionError` again.

2. **Use a scoped virtual executor: debug a regression.** A regression changed one token in the code that Example B adds after Example A, so one line now reads `for (int value = 1; value < 4; value++) {`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `results.equals(List.of(1, 4, 9, 16))`; after it the line reads `for (int value = 1; value <= 4; value++) {` again and 1, 4, 9, 16.
   **Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `results.equals(List.of(1, 4, 9, 16))` for this input.

3. **Limit a scarce resource with a semaphore.** Run six tasks but allow only two inside a gated resource section.
   **Expected:** maximum active count 2; all six complete.
   **Verify:** Keep an assertion equivalent to `completed == 6 && maximum.get() == 2`. As a control, change `for (int i = 0; i < 6; i++) futures.add(` to `for (int i = 0; i <= 6; i++) futures.add(`: the run must fail with an `AssertionError` from the assertion on `completed == 6 && maximum.get() == 2`. Restore the line before continuing.

4. **Preserve a CPU calculation contract.** Compare a sequential sum 1..1000 with four partitioned virtual tasks.
   **Expected:** both 500500; no speed claim.
   **Verify:** Keep an assertion equivalent to `total == sequential && total == 500500`. As a control, change `for (int p = 0; p < 4; p++) {` to `for (int p = 0; p <= 4; p++) {`: the run must fail with an `AssertionError` from the assertion on `total == sequential && total == 500500`. Restore the line before continuing.

5. **Cancel a blocked virtual task.** Interrupt a virtual task waiting on a latch and observe its cleanup signal.
   **Expected:** Future cancelled; task exits cooperatively.
   **Verify:** Keep an assertion equivalent to `finished`. As a control, change `var exited = new java.util.concurrent.CountDownLatch(1);` to `var exited = new java.util.concurrent.CountDownLatch(2);`: the run must fail with an `AssertionError` from the assertion on `finished`. Restore the line before continuing.

6. **Keep a blocking wait outside a monitor.** Read a state snapshot inside a synchronized block, then wait on a latch after leaving it.
   **Expected:** caller can acquire the monitor while the worker is waiting.
   **Verify:** Keep an assertion equivalent to `!worker.isAlive() && snapshot.get() == 7 && state[0] == 8`. As a control, change `var finish = new java.util.concurrent.CountDownLatch(1);` to `var finish = new java.util.concurrent.CountDownLatch(2);`: the run must fail with an `AssertionError` from the assertion on `!worker.isAlive() && snapshot.get() == 7 && state[0] == 8`. Restore the line before continuing.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: true and terminated. Then list the values read by `!task.isAlive() && virtual.get()` and trace each one from its declaration. Finally, compute the asserted value with `assert task.isAlive() && virtual.get();` in place before running.
- **Exercise 2:** First restate the expected observation: 1, 4, 9, 16. Then list the values read by `results.equals(List.of(1, 4, 9, 16))` and trace each one from its declaration. Finally, compare `for (int value = 1; value < 4; value++) {` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: maximum active count 2; all six complete. Then list the values read by `completed == 6 && maximum.get() == 2` and trace each one from its declaration. Finally, predict the effect of changing `for (int i = 0; i < 6; i++) futures.add(` to `for (int i = 0; i <= 6; i++) futures.add(` before running anything.
- **Exercise 4:** First restate the expected observation: both 500500; no speed claim. Then list the values read by `total == sequential && total == 500500` and trace each one from its declaration. Finally, predict the effect of changing `for (int p = 0; p < 4; p++) {` to `for (int p = 0; p <= 4; p++) {` before running anything.
- **Exercise 5:** First restate the expected observation: future cancelled; task exits cooperatively. Then list the values read by `finished` and trace each one from its declaration. Finally, predict the effect of changing `var exited = new java.util.concurrent.CountDownLatch(1);` to `var exited = new java.util.concurrent.CountDownLatch(2);` before running anything.
- **Exercise 6:** First restate the expected observation: caller can acquire the monitor while the worker is waiting. Then list the values read by `!worker.isAlive() && snapshot.get() == 7 && state[0] == 8` and trace each one from its declaration. Finally, predict the effect of changing `var finish = new java.util.concurrent.CountDownLatch(1);` to `var finish = new java.util.concurrent.CountDownLatch(2);` before running anything.

## Self-check and retrieval

Close the solution and explain Virtual thread, Carrier, Backpressure in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-024: Virtual threads and blocking work.
Read courses/java/guides/java-024.md and courses/java/lessons/java-024.java. Direct prerequisites: `java-023`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
