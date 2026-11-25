# java-021: Threads and the memory model

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-020`

## Learning objectives

Create threads, publish results safely through start, join or volatile, and respond correctly to interruption.

The six exercises practice these steps:

- Publish a result through join.
- Publish initial state through start.
- Force a lost update.
- Use a volatile publication flag.
- Distinguish run from start.
- Respond to interruption.

## Purpose and mental model

Threads can execute concurrently while sharing memory. Correct communication requires a happens-before relationship, not an assumption that another thread has probably finished. Starting a thread publishes prior actions to it, and a successful join makes its completed actions visible to the joining thread. Volatile writes and reads establish a publication relationship for associated state, but volatile does not make a compound read-modify-write atomic. A counter increment reads, adds and writes, so two threads can lose an update even if each individual access is visible.

This lesson uses bounded joins, latches and a barrier to make ordering deliberate. A controlled lost-update fixture forces both workers to read the same starting value before either writes. That demonstrates the mechanism without hoping a random stress run happens to fail. Interruption is a cooperative request, not forcible termination; blocking code should respond or preserve the interrupt status when it cannot complete its work.

## Vocabulary and concepts

**Happens-before:** A memory-ordering relationship guaranteeing visibility of earlier actions.

**Atomic operation:** An operation that cannot be observed as separate interleaved steps.

**Interruption:** A cooperative signal requesting that a thread stop or change its work.

## How to run this lesson

Every wait in this lesson is bounded: `joinBounded`, latch waits and the spin deadline all give up after about two seconds, so a broken check fails quickly instead of hanging the classroom.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

Thread.start begins a new execution; calling run directly is an ordinary method call. join(timeout) waits only up to a bound, so check isAlive afterward. CountDownLatch coordinates a one-time event, and CyclicBarrier can align two reads before their writes. A volatile ready flag can publish a preceding data assignment. InterruptedException clears the interrupted status, so a handler that propagates cancellation through state should restore it with interrupt().

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

**Expected:** worker observes 7.

## Prediction before your attempt

Before running Example A, decide whether the main thread is guaranteed to see 42 after `joinBounded(worker)` returns, and whether a `Thread.sleep` of the same length would give the same guarantee. For Example B, predict the value the worker observes when 7 is stored before `start()`. Before Exercise 3, decide the final counter when two workers both read 0, wait at a barrier, and then each write their saved value plus 1.

## Exercises

1. **Publish a result through join: change one input.** Change `Thread worker = Thread.ofPlatform().start(() -> result[0] = 42);` to `Thread worker = Thread.ofPlatform().start(() -> result[1] = 42);` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `result[0] == 42`.
   **Verify:** Name the value that makes `result[0] == 42` false, then restore the line.

2. **Publish initial state through start: debug a regression.** A regression in Example B's new code makes one line read `int[] input = { 8 };`. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `observed.get() == 7`; the repaired line reads `int[] input = { 7 };`.
   **Verify:** Explain how the changed token alters the value that `observed.get() == 7` tests.

3. **Force a lost update.** Make two workers read counter 0, wait at a barrier, then each write its saved value plus 1.
   **Expected:** final counter 1 despite two increments.
   **Verify:** Control: changing `counter[0] = saved + 1;` to `counter[0] = saved - 1;` must fail the assertion on `failure.get() == null && counter[0] == 1`.

4. **Use a volatile publication flag.** Write data 99 before setting a volatile ready flag; read after observing that flag.
   **Expected:** reader sees 99 and finishes within the bound.
   **Verify:** Control: changing `long deadline = System.nanoTime() + 2_000_000_000L;` to `long deadline = System.nanoTime() - 2_000_000_000L;` must fail the assertion on `seen.get() == 99`.

5. **Distinguish run from start.** Invoke a Runnable directly and compare its thread identity with the caller.
   **Expected:** same thread identity for direct run.
   **Verify:** Control: changing `assert identity.get() == caller;` to `assert identity.get() != caller;` inside the assertion must make it fail.

6. **Respond to interruption.** Interrupt a worker waiting on a latch, restore its flag in the catch, and verify termination.
   **Expected:** interruption observed and worker terminated.
   **Verify:** Name an input that would make `interrupted.get()` false and the value that changes.

## Common pitfalls and diagnosis

The memory model surprises people in both directions. A sleep is not synchronization: without `join`, `start`, a `volatile` field or a lock there is no happens-before edge, and the reader may see stale data. `volatile` fixes visibility but not atomicity, so `count++` on a volatile field still loses updates. Calling `run()` instead of `start()` runs the task on the caller's thread with no concurrency. And catching `InterruptedException` without restoring the flag erases a cancellation request.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the edited worker writes to `result[1]`, but the array has length 1. Then predict what happens inside the worker: it throws `ArrayIndexOutOfBoundsException` and the stack trace appears on the error stream. Finally, explain why `result[0]` is still 0 after the join.
- **Exercise 2:** First note that the edit stores 8 before the worker starts. Then apply the start rule: everything written before `start()` is visible to the new thread. Finally, compare the observed 8 with the 7 in the assertion and say why the publication itself worked.
- **Exercise 3:** First let each worker read the shared counter into a local variable. Then make both wait at a `CyclicBarrier` before writing their saved value plus 1. Finally, assert that the counter is 1 and explain which interleaving the barrier forces.
- **Exercise 4:** First write the data and then set the `volatile` ready flag in the producer. Then spin in the consumer until it sees the flag or a deadline passes, and read the data only after the flag. Finally, assert 99 and explain which write the volatile store published.
- **Exercise 5:** First record the caller thread with `Thread.currentThread()`. Then call `run()` directly on a `Runnable` that records its own current thread. Finally, compare the two identities and explain why no new thread was involved.
- **Exercise 6:** First start a worker that counts down a `started` latch and then waits on a second latch. Then interrupt it after it has started, and in its `catch` block restore the flag with `Thread.currentThread().interrupt()`. Finally, join it with a bound and assert that the interruption was observed.

## Self-check and retrieval

Without notes, list three actions that create happens-before edges and the one each example relies on. Explain why the lost-update fixture ends at 1, why `volatile` would not fix it, and what a worker should do with an `InterruptedException` it cannot propagate.

## Next step

Continue with `java-022`: Executors, futures and cancellation. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Thread.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-021: Threads and the memory model.
Read courses/java/guides/java-021.md and courses/java/lessons/java-021.java. Direct prerequisites: `java-020`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
