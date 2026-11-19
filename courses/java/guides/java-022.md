# java-022: Executors, futures and cancellation

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-021`

## Learning objectives

Run tasks with executors and futures that use bounded waits, cooperative cancellation and bounded queues. Along the way, explain future, timeout, backpressure using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Hold a task on a latch, wait with a short timeout, then release and obtain the result. The final exercise transfers the mechanism to enforce a bounded queue.

## Purpose and mental model

An ExecutorService owns task scheduling and worker lifetime. A Future represents an eventual result or failure, not proof that the task has already completed. get can block, so a bounded caller should use a timeout and decide what to do when the result is still unknown. Cancellation requests interruption when allowed, but the task must cooperate. A cancelled Future and a terminated task are related but distinct observations.

A fixed thread pool normally has an unbounded queue, which can retain more work than the application can process. A bounded ThreadPoolExecutor makes overload policy explicit through a finite queue and a rejection handler. This lesson uses latches to hold work at known points, then checks timeout, cancellation, failure propagation and shutdown without external services or arbitrary sleeps.

## Vocabulary and concepts

**Future:** A handle for an asynchronous result, failure or cancellation state.

**Timeout:** A bound on waiting, not proof that the underlying work stopped.

**Backpressure:** A policy limiting admitted work when capacity is exhausted.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-022/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

submit returns a Future; get(timeout, unit) returns a value or throws a named completion/timeout exception. ExecutionException wraps the task failure in getCause. cancel(true) requests interruption. try-with-resources closes the executor in Java 21, but tasks still need bounded cooperative behavior. A ThreadPoolExecutor with an ArrayBlockingQueue and AbortPolicy rejects excess submissions rather than silently growing memory.

## Worked example / walkthrough

### Example A: Retrieve a bounded result

The executor owns worker lifetime. The timeout makes the caller waiting policy explicit even though this fixture should finish immediately.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    try (var executor = java.util.concurrent.Executors.newFixedThreadPool(2)) {
      var future = executor.submit(() -> 42);
      int value = future.get(2, java.util.concurrent.TimeUnit.SECONDS);
      assert value == 42;
    }
  }
}
```

**Expected:** result 42.

### Example B: Preserve task failure identity

The asynchronous boundary wraps the failure but retains its cause. Replacing it with a generic successful default would hide the task outcome.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    try (var executor = java.util.concurrent.Executors.newFixedThreadPool(2)) {
      var future = executor.submit(() -> 42);
      int value = future.get(2, java.util.concurrent.TimeUnit.SECONDS);
      assert value == 42;
    }

    try (var executor = java.util.concurrent.Executors.newSingleThreadExecutor()) {
      var failed = executor.submit(() -> {
        throw new IllegalArgumentException("bad fixture");
      });
      boolean observed = false;
      try {
        failed.get(2, java.util.concurrent.TimeUnit.SECONDS);
      } catch (java.util.concurrent.ExecutionException expected) {
        observed = expected.getCause() instanceof IllegalArgumentException;
      }
      assert observed;
    }
  }
}
```

**Expected:** ExecutionException cause is IllegalArgumentException.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Retrieve a bounded result: change one input.** Copy Example A into a scratch `Main.java` and change `var future = executor.submit(() -> 42);` to `var future = executor.submit(() -> 43);`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `value == 42`. Restoring the original line brings back the worked observation: result 42.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `value == 42` false. After restoring the line, the program completes without an `AssertionError` again.

2. **Preserve task failure identity: debug a regression.** Introduce one deliberate defect into a copy of Example B that makes the assertion on `observed` fail, then explain how the stack trace leads back to the faulty statement.
   **Expected:** The defective copy fails the assertion on `observed`; the repaired copy reproduces the worked observation: executionException cause is IllegalArgumentException.
   **Verify:** Keep the failing and the repaired runs and name the first statement whose value differs between them.

3. **Separate wait timeout from task completion.** Hold a task on a latch, wait with a short timeout, then release and obtain the result.
   **Expected:** TimeoutException first; later result 7.
   **Verify:** Keep an assertion equivalent to `timedOut && value == 7`. As a control, change `return 7;` to `return 8;`: the run must fail with an `AssertionError` from the assertion on `timedOut && value == 7`. Restore the line before continuing.

4. **Cancel cooperatively.** Cancel a running latch-waiting task with interruption and observe its exit signal.
   **Expected:** Future cancelled and task catches interruption.
   **Verify:** Keep an assertion equivalent to `finished && future.isCancelled()`. As a control, change `var exited = new java.util.concurrent.CountDownLatch(1);` to `var exited = new java.util.concurrent.CountDownLatch(2);`: the run must fail with an `AssertionError` from the assertion on `finished && future.isCancelled()`. Restore the line before continuing.

5. **Reject work after shutdown.** Shut down an idle executor and submit another task.
   **Expected:** RejectedExecutionException.
   **Verify:** Keep an assertion equivalent to `rejected && terminated`. As a control, change `rejected = true;` to `rejected = false;`: the run must fail with an `AssertionError` from the assertion on `rejected && terminated`. Restore the line before continuing.

6. **Enforce a bounded queue.** Use one worker and one queue slot, hold the worker, fill the queue, then submit a third task.
   **Expected:** third submission rejected; admitted tasks finish after release.
   **Verify:** Keep an assertion equivalent to `overloaded && first.get(2, java.util.concurrent.TimeUnit.SECONDS) == 1 && second.get(2, java.util.concurrent.TimeUnit.SECONDS) == 2`. As a control, change `1,` to `2,`: the run must fail with an `AssertionError` from the assertion on `overloaded && first.get(2, java.util.concurrent.TimeUnit.SECONDS) == 1 && second.get(2, java.util.concurrent.TimeUnit.SECONDS) == 2`. Restore the line before continuing.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: result 42. Then list the values read by `value == 42` and trace each one from its declaration. Finally, compute the asserted value with `var future = executor.submit(() -> 43);` in place before running.
- **Exercise 2:** First restate the expected observation: executionException cause is IllegalArgumentException. Then list the values read by `observed` and trace each one from its declaration. Finally, name one input that would make `observed` false.
- **Exercise 3:** First restate the expected observation: timeoutException first; later result 7. Then list the values read by `timedOut && value == 7` and trace each one from its declaration. Finally, predict the effect of changing `return 7;` to `return 8;` before running anything.
- **Exercise 4:** First restate the expected observation: future cancelled and task catches interruption. Then list the values read by `finished && future.isCancelled()` and trace each one from its declaration. Finally, predict the effect of changing `var exited = new java.util.concurrent.CountDownLatch(1);` to `var exited = new java.util.concurrent.CountDownLatch(2);` before running anything.
- **Exercise 5:** First restate the expected observation: rejectedExecutionException. Then list the values read by `rejected && terminated` and trace each one from its declaration. Finally, predict the effect of changing `rejected = true;` to `rejected = false;` before running anything.
- **Exercise 6:** First restate the expected observation: third submission rejected; admitted tasks finish after release. Then list the values read by `overloaded && first.get(2, java.util.concurrent.TimeUnit.SECONDS) == 1 && second.get(2, java.util.concurrent.TimeUnit.SECONDS) == 2` and trace each one from its declaration. Finally, predict the effect of changing `1,` to `2,` before running anything.

## Self-check and retrieval

Close the solution and explain Future, Timeout, Backpressure in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ExecutorService.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-022: Executors, futures and cancellation.
Read courses/java/guides/java-022.md and courses/java/lessons/java-022.java. Direct prerequisites: `java-021`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
