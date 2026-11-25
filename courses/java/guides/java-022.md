# java-022: Executors, futures and cancellation

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-021`

## Learning objectives

Run tasks with executors and futures that use bounded waits, cooperative cancellation and bounded queues.

The six exercises practice these steps:

- Retrieve a bounded result.
- Preserve task failure identity.
- Separate wait timeout from task completion.
- Cancel cooperatively.
- Reject work after shutdown.
- Enforce a bounded queue.

## Purpose and mental model

An ExecutorService owns task scheduling and worker lifetime. A Future represents an eventual result or failure, not proof that the task has already completed. get can block, so a bounded caller should use a timeout and decide what to do when the result is still unknown. Cancellation requests interruption when allowed, but the task must cooperate. A cancelled Future and a terminated task are related but distinct observations.

A fixed thread pool normally has an unbounded queue, which can retain more work than the application can process. A bounded ThreadPoolExecutor makes overload policy explicit through a finite queue and a rejection handler. This lesson uses latches to hold work at known points, then checks timeout, cancellation, failure propagation and shutdown without external services or arbitrary sleeps.

## Vocabulary and concepts

**Future:** A handle for an asynchronous result, failure or cancellation state.

**Timeout:** A bound on waiting, not proof that the underlying work stopped.

**Backpressure:** A policy limiting admitted work when capacity is exhausted.

## How to run this lesson

Each exercise opens its own executor in try-with-resources and every `get` or latch wait carries a timeout, so a regression shows up as a failed check within seconds instead of a hung JVM. Exercise 2 has no recorded edit.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



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

Before running Example A, decide whether `future.get(2, SECONDS)` returns immediately or waits, and what it would throw if the task had not finished in time. For Example B, predict the exact exception type `get` throws when the callable throws `IllegalArgumentException`, and where the original exception ends up. Before Exercise 3, decide whether a `TimeoutException` from `get` stops the task or only stops the caller's wait.

## Exercises

1. **Retrieve a bounded result: change one input.** Change `var future = executor.submit(() -> 42);` to `var future = executor.submit(() -> 43);` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `value == 42`.
   **Verify:** Name the value that makes `value == 42` false, then restore the line.

2. **Preserve task failure identity: debug a regression.** Add one defect to Example B's new code that fails the assertion on `observed`, then repair it.
   **Expected:** The defective copy fails its assertion and the repaired copy passes.
   **Verify:** Name the first statement whose value differs between the failing and repaired runs.

3. **Separate wait timeout from task completion.** Hold a task on a latch, wait with a short timeout, then release and obtain the result.
   **Expected:** TimeoutException first; later result 7.
   **Verify:** Control: changing `return 7;` to `return 8;` must fail the assertion on `timedOut && value == 7`.

4. **Cancel cooperatively.** Cancel a running latch-waiting task with interruption and observe its exit signal.
   **Expected:** Future cancelled and task catches interruption.
   **Verify:** Control: changing `var exited = new java.util.concurrent.CountDownLatch(1);` to `var exited = new java.util.concurrent.CountDownLatch(2);` must fail the assertion on `finished && future.isCancelled()`.

5. **Reject work after shutdown.** Shut down an idle executor and submit another task.
   **Expected:** RejectedExecutionException.
   **Verify:** Control: changing `rejected = true;` to `rejected = false;` must fail the assertion on `rejected && terminated`.

6. **Enforce a bounded queue.** Use one worker and one queue slot, hold the worker, fill the queue, then submit a third task.
   **Expected:** third submission rejected; admitted tasks finish after release.
   **Verify:** Control: changing `1,` to `2,` must fail the assertion on `overloaded && first.get(2, java.util.concurrent.TimeUnit.SECONDS) == 1 && second.get(2, java.util.concurrent.TimeUnit.SECONDS) == 2`.

## Common pitfalls and diagnosis

An unbounded `get()` turns a stuck task into a stuck caller, so give every wait a timeout and a plan for the unknown outcome. Catching `ExecutionException` and logging only its message loses the real failure; read `getCause()`. `cancel(true)` only sets the interrupt flag, so a task that swallows `InterruptedException` keeps running. `Executors.newFixedThreadPool` queues without limit, which hides overload until memory runs out. And forgetting to shut an executor down leaves non-daemon threads that keep the JVM alive.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the edit makes the callable return 43. Then follow the value through `future.get(2, SECONDS)`, which returns the task result unchanged. Finally, compare 43 with the 42 in the assertion and say why the executor and timeout were not at fault.
- **Exercise 2:** First change `instanceof IllegalArgumentException` in the `catch` block to `instanceof IllegalStateException`. Then run it: `get` still throws `ExecutionException`, but `observed` is now false and `assert observed` fails. Finally, restore the type and explain why the test inspects `getCause()` rather than the `ExecutionException` wrapper.
- **Exercise 3:** First submit a task that waits on a gate latch before returning 7. Then call `get` with a 20 millisecond timeout, record the `TimeoutException`, and release the gate in a `finally` block. Finally, call `get` again with a longer timeout and assert 7.
- **Exercise 4:** First start a task that counts down `started`, waits forever on a fresh latch, and counts down `exited` in a `finally` block. Then wait for `started` and call `cancel(true)`. Finally, wait for `exited` and assert both it and `isCancelled()`.
- **Exercise 5:** First create a single-thread executor and call `shutdown()`. Then submit another task inside a `try` block and catch `RejectedExecutionException`. Finally, assert that the executor reports termination and explain why creating a replacement pool silently would hide a lifecycle bug.
- **Exercise 6:** First build a `ThreadPoolExecutor` with one worker, an `ArrayBlockingQueue` of capacity 1 and `AbortPolicy`. Then hold the first task on a latch, queue a second, and submit a third inside a `try` block. Finally, release the latch and assert that only the third was rejected.

## Self-check and retrieval

From memory, explain what a `Future` represents before and after completion, how `ExecutionException` preserves a task failure, why a timeout on `get` does not cancel the task, and what a bounded `ThreadPoolExecutor` with `AbortPolicy` does when its single worker and single queue slot are both busy.

## Next step

Continue with `java-023`: Locks, atomics and concurrent collections. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ExecutorService.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

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
