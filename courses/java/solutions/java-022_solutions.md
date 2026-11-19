# java-022: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

An ExecutorService owns task scheduling and worker lifetime. A Future represents an eventual result or failure, not proof that the task has already completed. get can block, so a bounded caller should use a timeout and decide what to do when the result is still unknown. Cancellation requests interruption when allowed, but the task must cooperate. A cancelled Future and a terminated task are related but distinct observations.

A fixed thread pool normally has an unbounded queue, which can retain more work than the application can process. A bounded ThreadPoolExecutor makes overload policy explicit through a finite queue and a rejection handler. This lesson uses latches to hold work at known points, then checks timeout, cancellation, failure propagation and shutdown without external services or arbitrary sleeps.

**Future:** A handle for an asynchronous result, failure or cancellation state.

**Timeout:** A bound on waiting, not proof that the underlying work stopped.

**Backpressure:** A policy limiting admitted work when capacity is exhausted.

## Reading the reference

submit returns a Future; get(timeout, unit) returns a value or throws a named completion/timeout exception. ExecutionException wraps the task failure in getCause. cancel(true) requests interruption. try-with-resources closes the executor in Java 21, but tasks still need bounded cooperative behavior. A ThreadPoolExecutor with an ArrayBlockingQueue and AbortPolicy rejects excess submissions rather than silently growing memory.

## Exercise 1: Retrieve a bounded result: change one input

Task: Copy Example A into a scratch `Main.java` and change `var future = executor.submit(() -> 42);` to `var future = executor.submit(() -> 43);`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.

The executor owns worker lifetime. The timeout makes the caller waiting policy explicit even though this fixture should finish immediately.

The unchanged code is the part that Example A adds:

```java
try (var executor = java.util.concurrent.Executors.newFixedThreadPool(2)) {
  var future = executor.submit(() -> 42);
  int value = future.get(2, java.util.concurrent.TimeUnit.SECONDS);
  assert value == 42;
}
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `value == 42`. Restoring the original line brings back the worked observation: result 42.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `value == 42` false. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Preserve task failure identity: debug a regression

Task: Introduce one deliberate defect into a copy of Example B that makes the assertion on `observed` fail, then explain how the stack trace leads back to the faulty statement.

The asynchronous boundary wraps the failure but retains its cause. Replacing it with a generic successful default would hide the task outcome.

The unchanged code is the part that Example B adds:

```java
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
```

**Expected:** The defective copy fails the assertion on `observed`; the repaired copy reproduces the worked observation: executionException cause is IllegalArgumentException.

**Verify:** Keep the failing and the repaired runs and name the first statement whose value differs between them.

## Exercise 3: Separate wait timeout from task completion

Task: Hold a task on a latch, wait with a short timeout, then release and obtain the result.

The timeout stops waiting, not the task. The explicit release demonstrates that the same Future can later complete successfully.

```java
var gate = new java.util.concurrent.CountDownLatch(1);
try (var executor = java.util.concurrent.Executors.newSingleThreadExecutor()) {
  var future = executor.submit(() -> {
    gate.await();
    return 7;
  });
  boolean timedOut = false;
  try {
    future.get(20, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (java.util.concurrent.TimeoutException expected) {
    timedOut = true;
  } finally {
    gate.countDown();
  }
  int value = future.get(2, java.util.concurrent.TimeUnit.SECONDS);
  assert timedOut && value == 7;
}
```

**Expected:** TimeoutException first; later result 7.

**Verify:** Keep an assertion equivalent to `timedOut && value == 7`. As a control, change `return 7;` to `return 8;`: the run must fail with an `AssertionError` from the assertion on `timedOut && value == 7`. Restore the line before continuing.

## Exercise 4: Cancel cooperatively

Task: Cancel a running latch-waiting task with interruption and observe its exit signal.

The exit latch is separate evidence that the task responded. Future cancellation alone does not prove arbitrary user code has stopped.

```java
var started = new java.util.concurrent.CountDownLatch(1);
var exited = new java.util.concurrent.CountDownLatch(1);
try (var executor = java.util.concurrent.Executors.newSingleThreadExecutor()) {
  var future = executor.submit(() -> {
    started.countDown();
    try {
      new java.util.concurrent.CountDownLatch(1).await();
    } catch (InterruptedException expected) {
      Thread.currentThread().interrupt();
    } finally {
      exited.countDown();
    }
  });
  boolean began = started.await(2, java.util.concurrent.TimeUnit.SECONDS);
  assert began;
  boolean cancelled = future.cancel(true);
  assert cancelled;
  boolean finished = exited.await(2, java.util.concurrent.TimeUnit.SECONDS);
  assert finished && future.isCancelled();
}
```

**Expected:** Future cancelled and task catches interruption.

**Verify:** Keep an assertion equivalent to `finished && future.isCancelled()`. As a control, change `var exited = new java.util.concurrent.CountDownLatch(1);` to `var exited = new java.util.concurrent.CountDownLatch(2);`: the run must fail with an `AssertionError` from the assertion on `finished && future.isCancelled()`. Restore the line before continuing.

## Exercise 5: Reject work after shutdown

Task: Shut down an idle executor and submit another task.

Shutdown closes admission. It is not a signal to silently create a replacement executor behind the caller's back.

```java
var closed = java.util.concurrent.Executors.newSingleThreadExecutor();
closed.shutdown();
boolean rejected = false;
try {
  closed.submit(() -> 1);
} catch (java.util.concurrent.RejectedExecutionException expected) {
  rejected = true;
}
boolean terminated = closed.awaitTermination(2, java.util.concurrent.TimeUnit.SECONDS);
assert rejected && terminated;
```

**Expected:** RejectedExecutionException.

**Verify:** Keep an assertion equivalent to `rejected && terminated`. As a control, change `rejected = true;` to `rejected = false;`: the run must fail with an `AssertionError` from the assertion on `rejected && terminated`. Restore the line before continuing.

## Exercise 6: Enforce a bounded queue

Task: Use one worker and one queue slot, hold the worker, fill the queue, then submit a third task.

The queue bound makes overload observable. A real application can reject, block or shed work under a documented policy, but should not pretend resources are unlimited.

```java
var hold = new java.util.concurrent.CountDownLatch(1);
var running = new java.util.concurrent.CountDownLatch(1);
try (
  var bounded = new java.util.concurrent.ThreadPoolExecutor(
    1,
    1,
    0,
    java.util.concurrent.TimeUnit.SECONDS,
    new java.util.concurrent.ArrayBlockingQueue<Runnable>(1),
    new java.util.concurrent.ThreadPoolExecutor.AbortPolicy()
  )
) {
  var first = bounded.submit(() -> {
    running.countDown();
    hold.await();
    return 1;
  });
  boolean firstRunning = running.await(2, java.util.concurrent.TimeUnit.SECONDS);
  assert firstRunning;
  var second = bounded.submit(() -> 2);
  boolean overloaded = false;
  try {
    bounded.submit(() -> 3);
  } catch (java.util.concurrent.RejectedExecutionException expected) {
    overloaded = true;
  } finally {
    hold.countDown();
  }
  assert overloaded &&
  first.get(2, java.util.concurrent.TimeUnit.SECONDS) == 1 &&
  second.get(2, java.util.concurrent.TimeUnit.SECONDS) == 2;
}
```

**Expected:** third submission rejected; admitted tasks finish after release.

**Verify:** Keep an assertion equivalent to `overloaded && first.get(2, java.util.concurrent.TimeUnit.SECONDS) == 1 && second.get(2, java.util.concurrent.TimeUnit.SECONDS) == 2`. As a control, change `1,` to `2,`: the run must fail with an `AssertionError` from the assertion on `overloaded && first.get(2, java.util.concurrent.TimeUnit.SECONDS) == 1 && second.get(2, java.util.concurrent.TimeUnit.SECONDS) == 2`. Restore the line before continuing.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
