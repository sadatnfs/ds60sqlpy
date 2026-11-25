# java-024: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

Virtual threads are lightweight Java threads intended to make large numbers of blocking tasks easier to express. They still run on carrier operating-system threads and do not create additional CPU cores. A CPU-bound calculation does not become faster merely because it is placed in a virtual thread. Resource limits such as database connections, remote quotas and memory still need backpressure. A virtual-thread-per-task executor is therefore not permission to admit unlimited work.

Java 21 has pinning cases where a virtual thread blocks while holding a synchronized monitor or during certain native operations, preventing its carrier from being reused for other virtual threads. Later JDK behavior can differ, so version the explanation. Keep blocking work outside a monitor when the state contract permits it, or redesign the synchronization carefully. This lesson checks thread identity, lifetime, cancellation and a semaphore admission limit without making throughput claims.

**Virtual thread:** A lightweight Java thread scheduled over carrier threads.

**Carrier:** An operating-system thread executing virtual-thread work.

**Backpressure:** A limit on admitted resource-consuming operations.

**Pinning in Java 21:** A condition preventing a blocked virtual thread from releasing its carrier.

## Reading the reference

Thread.ofVirtual starts a virtual thread; isVirtual identifies it. Executors.newVirtualThreadPerTaskExecutor creates a new virtual thread for each admitted task. A Semaphore can bound simultaneous access to a scarce resource independently of thread count. Future.get and latches provide bounded completion evidence. Cooperative interruption remains necessary, just as with platform threads.

## Exercise 1: Observe virtual identity: predict an edited check

Task: Change Example A's assertion to `assert task.isAlive() && virtual.get();`, predict whether it holds, then run and restore it.

The identity check establishes the actual thread type. It does not measure performance or the number of carrier threads used.

The unchanged code is the part that Example A adds:

```java
var virtual = new java.util.concurrent.atomic.AtomicBoolean();
Thread task = Thread.ofVirtual().start(() -> virtual.set(Thread.currentThread().isVirtual()));
task.join(2000);
assert !task.isAlive() && virtual.get();
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `!task.isAlive() && virtual.get()`.

**Verify:** Explain why the edited assertion is false for the values that satisfy `!task.isAlive() && virtual.get()`.

## Exercise 2: Use a scoped virtual executor: debug a regression

Task: A regression in Example B's new code makes one line read `for (int value = 1; value < 4; value++) {`. Repair it using the failing assertion.

The executor lifetime encloses its tasks. Capturing a separate effectively-final input per submission avoids confusing loop-state ownership.

The unchanged code is the part that Example B adds:

```java
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
```

**Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `results.equals(List.of(1, 4, 9, 16))`; the repaired line reads `for (int value = 1; value <= 4; value++) {`.

**Verify:** Explain how the changed token alters the value that `results.equals(List.of(1, 4, 9, 16))` tests.

## Exercise 3: Limit a scarce resource with a semaphore

Task: Run six tasks but allow only two inside a gated resource section.

Thread creation is separate from resource admission. The semaphore protects the scarce section even when many virtual threads exist.

```java
var permits = new java.util.concurrent.Semaphore(2);
var active = new java.util.concurrent.atomic.AtomicInteger();
var maximum = new java.util.concurrent.atomic.AtomicInteger();
var entered = new java.util.concurrent.CountDownLatch(2);
var release = new java.util.concurrent.CountDownLatch(1);
try (var executor = java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
  List<java.util.concurrent.Future<Integer>> futures = new ArrayList<>();
  for (int i = 0; i < 6; i++) futures.add(
    executor.submit(() -> {
      if (
        !permits.tryAcquire(2, java.util.concurrent.TimeUnit.SECONDS)
      ) throw new IllegalStateException("admission timeout");
      try {
        int now = active.incrementAndGet();
        maximum.accumulateAndGet(now, Math::max);
        entered.countDown();
        if (
          !release.await(2, java.util.concurrent.TimeUnit.SECONDS)
        ) throw new IllegalStateException("gate timeout");
        return 1;
      } finally {
        active.decrementAndGet();
        permits.release();
      }
    })
  );
  boolean allEntered;
  try {
    allEntered = entered.await(2, java.util.concurrent.TimeUnit.SECONDS);
  } finally {
    release.countDown();
  }
  assert allEntered;
  int completed = 0;
  for (var future : futures) completed += future.get(3, java.util.concurrent.TimeUnit.SECONDS);
  assert completed == 6 && maximum.get() == 2;
}
```

**Expected:** maximum active count 2; all six complete.

**Verify:** Control: changing `for (int i = 0; i < 6; i++) futures.add(` to `for (int i = 0; i <= 6; i++) futures.add(` must fail the assertion on `completed == 6 && maximum.get() == 2`.

## Exercise 4: Preserve a CPU calculation contract

Task: Compare a sequential sum 1..1000 with four partitioned virtual tasks.

Correct partitioning is checked independently of timing. Virtual threads do not promise to accelerate CPU-bound arithmetic.

```java
int sequential = java.util.stream.IntStream.rangeClosed(1, 1000).sum();
try (var executor = java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
  List<java.util.concurrent.Future<Integer>> parts = new ArrayList<>();
  for (int p = 0; p < 4; p++) {
    int start = p * 250 + 1,
      end = (p + 1) * 250;
    parts.add(executor.submit(() -> java.util.stream.IntStream.rangeClosed(start, end).sum()));
  }
  int total = 0;
  for (var future : parts) total += future.get(2, java.util.concurrent.TimeUnit.SECONDS);
  assert total == sequential && total == 500500;
}
```

**Expected:** both 500500; no speed claim.

**Verify:** Control: changing `for (int p = 0; p < 4; p++) {` to `for (int p = 0; p <= 4; p++) {` must fail the assertion on `total == sequential && total == 500500`.

## Exercise 5: Cancel a blocked virtual task

Task: Interrupt a virtual task waiting on a latch and observe its cleanup signal.

Lightweight scheduling does not change cancellation into forcible termination. Task code still owns resource cleanup and interruption response.

```java
var started = new java.util.concurrent.CountDownLatch(1);
var exited = new java.util.concurrent.CountDownLatch(1);
try (var executor = java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
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
  assert finished;
}
```

**Expected:** Future cancelled; task exits cooperatively.

**Verify:** Control: changing `var exited = new java.util.concurrent.CountDownLatch(1);` to `var exited = new java.util.concurrent.CountDownLatch(2);` must fail the assertion on `finished`.

## Exercise 6: Keep a blocking wait outside a monitor

Task: Read a state snapshot inside a synchronized block, then wait on a latch after leaving it.

This design releases the monitor before blocking. It avoids the illustrated Java 21 monitor-held blocking pattern, but it does not measure carrier pinning or prove a general performance improvement.

```java
Object monitor = new Object();
var waiting = new java.util.concurrent.CountDownLatch(1);
var finish = new java.util.concurrent.CountDownLatch(1);
int[] state = { 7 };
var snapshot = new java.util.concurrent.atomic.AtomicInteger();
Thread worker = Thread.ofVirtual().start(() -> {
  synchronized (monitor) {
    snapshot.set(state[0]);
  }
  waiting.countDown();
  try {
    finish.await(2, java.util.concurrent.TimeUnit.SECONDS);
  } catch (InterruptedException error) {
    Thread.currentThread().interrupt();
  }
});
boolean workerWaiting = waiting.await(2, java.util.concurrent.TimeUnit.SECONDS);
assert workerWaiting;
synchronized (monitor) {
  state[0] = 8;
}
finish.countDown();
worker.join(2000);
assert !worker.isAlive() && snapshot.get() == 7 && state[0] == 8;
```

**Expected:** caller can acquire the monitor while the worker is waiting.

**Verify:** Control: changing `var finish = new java.util.concurrent.CountDownLatch(1);` to `var finish = new java.util.concurrent.CountDownLatch(2);` must fail the assertion on `!worker.isAlive() && snapshot.get() == 7 && state[0] == 8`.

## After comparing the answer

Raise the semaphore in your copy of Exercise 3 to three permits and change `entered` to wait for three tasks; predict the new maximum and then verify that every task still completes.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
