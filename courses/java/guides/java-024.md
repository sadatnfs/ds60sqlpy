# java-024: Virtual threads and blocking work

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-023`

## Learning objectives

Use virtual threads for blocking work, limit scarce resources with a semaphore and cancel blocked tasks.

The six exercises practice these steps:

- Observe virtual identity.
- Use a scoped virtual executor.
- Limit a scarce resource with a semaphore.
- Preserve a CPU calculation contract.
- Cancel a blocked virtual task.
- Keep a blocking wait outside a monitor.

## Purpose and mental model

Virtual threads are lightweight Java threads intended to make large numbers of blocking tasks easier to express. They still run on carrier operating-system threads and do not create additional CPU cores. A CPU-bound calculation does not become faster merely because it is placed in a virtual thread. Resource limits such as database connections, remote quotas and memory still need backpressure. A virtual-thread-per-task executor is therefore not permission to admit unlimited work.

Java 21 has pinning cases where a virtual thread blocks while holding a synchronized monitor or during certain native operations, preventing its carrier from being reused for other virtual threads. Later JDK behavior can differ, so version the explanation. Keep blocking work outside a monitor when the state contract permits it, or redesign the synchronization carefully. This lesson checks thread identity, lifetime, cancellation and a semaphore admission limit without making throughput claims.

## Vocabulary and concepts

**Virtual thread:** A lightweight Java thread scheduled over carrier threads.

**Carrier:** An operating-system thread executing virtual-thread work.

**Backpressure:** A limit on admitted resource-consuming operations.

**Pinning in Java 21:** A condition preventing a blocked virtual thread from releasing its carrier.

## How to run this lesson

Exercises 1 and 6 start a single `Thread.ofVirtual()` worker and the others use `newVirtualThreadPerTaskExecutor` in try-with-resources; every wait is bounded, and nothing in this lesson measures speed.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



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

Before running Example A, decide what `Thread.currentThread().isVirtual()` reports inside `Thread.ofVirtual().start(...)` and whether `task.isAlive()` is false after a bounded join. For Example B, predict the list of results from four submitted squares read back in submission order. Before Exercise 3, decide the highest number of tasks that can be inside the section at once when six virtual threads share a `Semaphore` with two permits.

## Exercises

1. **Observe virtual identity: predict an edited check.** Change Example A's assertion to `assert task.isAlive() && virtual.get();`, predict whether it holds, then run and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `!task.isAlive() && virtual.get()`.
   **Verify:** Explain why the edited assertion is false for the values that satisfy `!task.isAlive() && virtual.get()`.

2. **Use a scoped virtual executor: debug a regression.** A regression in Example B's new code makes one line read `for (int value = 1; value < 4; value++) {`. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `results.equals(List.of(1, 4, 9, 16))`; the repaired line reads `for (int value = 1; value <= 4; value++) {`.
   **Verify:** Explain how the changed token alters the value that `results.equals(List.of(1, 4, 9, 16))` tests.

3. **Limit a scarce resource with a semaphore.** Run six tasks but allow only two inside a gated resource section.
   **Expected:** maximum active count 2; all six complete.
   **Verify:** Control: changing `for (int i = 0; i < 6; i++) futures.add(` to `for (int i = 0; i <= 6; i++) futures.add(` must fail the assertion on `completed == 6 && maximum.get() == 2`.

4. **Preserve a CPU calculation contract.** Compare a sequential sum 1..1000 with four partitioned virtual tasks.
   **Expected:** both 500500; no speed claim.
   **Verify:** Control: changing `for (int p = 0; p < 4; p++) {` to `for (int p = 0; p <= 4; p++) {` must fail the assertion on `total == sequential && total == 500500`.

5. **Cancel a blocked virtual task.** Interrupt a virtual task waiting on a latch and observe its cleanup signal.
   **Expected:** Future cancelled; task exits cooperatively.
   **Verify:** Control: changing `var exited = new java.util.concurrent.CountDownLatch(1);` to `var exited = new java.util.concurrent.CountDownLatch(2);` must fail the assertion on `finished`.

6. **Keep a blocking wait outside a monitor.** Read a state snapshot inside a synchronized block, then wait on a latch after leaving it.
   **Expected:** caller can acquire the monitor while the worker is waiting.
   **Verify:** Control: changing `var finish = new java.util.concurrent.CountDownLatch(1);` to `var finish = new java.util.concurrent.CountDownLatch(2);` must fail the assertion on `!worker.isAlive() && snapshot.get() == 7 && state[0] == 8`.

## Common pitfalls and diagnosis

Virtual threads make blocking cheap, not computation: a CPU-bound sum split across virtual threads still needs CPU cores to go faster. Cheap threads also remove a natural limit, so ten thousand tasks can open ten thousand database connections unless a `Semaphore` or pool caps them. On Java 21, blocking while holding a `synchronized` monitor can pin the carrier thread. Pooling virtual threads defeats their purpose; create one per task. And capturing the loop variable directly in a lambda fails to compile, so copy it into an effectively final local.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the edit asserts `task.isAlive()` after the join. Then recall that the virtual thread only stores one boolean and finishes almost at once. Finally, explain why a terminated thread makes the edited check fail even though `virtual.get()` is true.
- **Exercise 2:** First note that the edit stops the loop at `value < 4`, so only three tasks are submitted. Then read back the results in order: 1, 4 and 9. Finally, compare that list with 1, 4, 9, 16 and say which value is missing.
- **Exercise 3:** First create a `Semaphore` with two permits and have each task call `tryAcquire` with a timeout before entering. Then track the active count and its maximum, releasing the permit in `finally`. Finally, submit six tasks and assert six completions and a maximum of 2.
- **Exercise 4:** First compute the sequential sum of 1 to 1,000 with `IntStream.rangeClosed`. Then split the range into four slices of 250 and sum each in its own virtual task. Finally, add the four futures and assert 500,500 without timing anything.
- **Exercise 5:** First submit a virtual task that counts down `started`, waits on a fresh latch, and counts down `exited` in `finally`. Then cancel it with `cancel(true)` once it has started. Finally, wait for `exited` with a bound and assert that the task left cooperatively.
- **Exercise 6:** First let a virtual worker copy the state inside `synchronized (monitor)` and leave the block before waiting on a latch. Then take the same monitor in the caller while the worker waits, and write 8. Finally, release the worker and assert that it saw 7.

## Self-check and retrieval

From memory, explain what a carrier thread is, why virtual threads help blocking work but not CPU work, how a semaphore separates admission from thread creation, and what Java 21 pinning is and how Exercise 6 avoids it by leaving the monitor before waiting.

## Next step

Continue with `java-025`: JVM memory, GC and allocation. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

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
