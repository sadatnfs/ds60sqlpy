# java-022: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

An ExecutorService owns task scheduling and worker lifetime. A Future represents an eventual result or failure, not proof that the task has already completed. get can block, so a bounded caller should use a timeout and decide what to do when the result is still unknown. Cancellation requests interruption when allowed, but the task must cooperate. A cancelled Future and a terminated task are related but distinct observations.

A fixed thread pool normally has an unbounded queue, which can retain more work than the application can process. A bounded ThreadPoolExecutor makes overload policy explicit through a finite queue and a rejection handler. This lesson uses latches to hold work at known points, then checks timeout, cancellation, failure propagation and shutdown without external services or arbitrary sleeps.

**Future:** A handle for an asynchronous result, failure or cancellation state.

**Timeout:** A bound on waiting, not proof that the underlying work stopped.

**Backpressure:** A policy limiting admitted work when capacity is exhausted.

## Reading the reference

submit returns a Future; get(timeout, unit) returns a value or throws a named completion/timeout exception. ExecutionException wraps the task failure in getCause. cancel(true) requests interruption. try-with-resources closes the executor in Java 21, but tasks still need bounded cooperative behavior. A ThreadPoolExecutor with an ArrayBlockingQueue and AbortPolicy rejects excess submissions rather than silently growing memory.

## Exercise 1: Retrieve a bounded result: change one input

Task: Change `var future = executor.submit(() -> 42);` to `var future = executor.submit(() -> 43);` in Example A and predict which assertion fails and why.

The executor owns worker lifetime. The timeout makes the caller waiting policy explicit even though this fixture should finish immediately.

The unchanged code is the part that Example A adds:

```java
try (var executor = java.util.concurrent.Executors.newFixedThreadPool(2)) {
  var future = executor.submit(() -> 42);
  int value = future.get(2, java.util.concurrent.TimeUnit.SECONDS);
  assert value == 42;
}
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `value == 42`.

**Verify:** Name the value that makes `value == 42` false, then restore the line.

## Exercise 2: Preserve task failure identity: debug a regression

Task: Add one defect to Example B's new code that fails the assertion on `observed`, then repair it.

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

**Expected:** The defective copy fails its assertion and the repaired copy passes.

**Verify:** Name the first statement whose value differs between the failing and repaired runs.

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

**Verify:** Control: changing `return 7;` to `return 8;` must fail the assertion on `timedOut && value == 7`.

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

**Verify:** Control: changing `var exited = new java.util.concurrent.CountDownLatch(1);` to `var exited = new java.util.concurrent.CountDownLatch(2);` must fail the assertion on `finished && future.isCancelled()`.

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

**Verify:** Control: changing `rejected = true;` to `rejected = false;` must fail the assertion on `rejected && terminated`.

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

**Verify:** Control: changing `1,` to `2,` must fail the assertion on `overloaded && first.get(2, java.util.concurrent.TimeUnit.SECONDS) == 1 && second.get(2, java.util.concurrent.TimeUnit.SECONDS) == 2`.

## After comparing the answer

Swap `AbortPolicy` in your copy of Exercise 6 for `CallerRunsPolicy` and predict which thread runs the third task; then confirm it by recording `Thread.currentThread()` inside that task.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
