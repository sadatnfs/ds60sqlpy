# java-025: JVM memory, GC and allocation

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-024`

## Learning objectives

Explain object reachability and retention and measure allocation and memory use without misleading claims.

The six exercises practice these steps:

- Expose a strong retention path.
- Remove one ownership path deliberately.
- Inspect a weak reference without timing assumptions.
- Separate value size from allocation count.
- Reuse a bounded working buffer.
- Record process memory cautiously.

## Purpose and mental model

The JVM manages heap memory through reachability, not by immediately freeing an object when a local variable changes. References in collections, static fields, thread locals or listeners can keep objects alive after a caller no longer needs them. Stack frames hold local execution state and references, while objects and arrays generally live in managed heap storage. An unreachable object becomes eligible for collection, but collection timing is not a deterministic application contract.

System.gc is a request rather than proof that a particular object was reclaimed. Memory counters are observations affected by allocation, collection and implementation details. This lesson uses bounded arrays and explicit ownership changes to explain retention without allocating until failure or relying on a forced collection. Weak references can observe optional reachability, but application correctness should not depend on when a weakly reachable object disappears.

## Vocabulary and concepts

**Reachability:** Whether an object can be reached through active reference paths.

**Retention:** Keeping an object alive through a reference that still exists.

**Garbage collection:** Reclaiming managed memory according to runtime policy.

**Allocation rate:** The amount of new storage created over a period of work.

## How to run this lesson

Every allocation in this lesson is tiny and bounded: kilobyte arrays and a few runtime counters. Nothing calls `System.gc()` or depends on when a collection happens, and Exercise 6 has no recorded edit.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

A collection holding an array retains a strong reference. Clearing the collection removes that particular ownership path, but other references may remain. WeakReference.get may return the referent or null depending on reachability and collection. Runtime memory values describe the current process and should not be treated as exact per-object size measurements. Avoid finalizers as a resource-lifetime mechanism; use explicit close for files, sockets and executors.

## Worked example / walkthrough

### Example A: Expose a strong retention path

The local reference disappearing does not remove the list's ownership path. This is a common source of unbounded cache or listener retention.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    List<byte[]> retained = new ArrayList<>();
    byte[] payload = new byte[1024];
    payload[0] = 7;
    retained.add(payload);
    payload = null;
    assert retained.get(0)[0] == 7 && retained.get(0).length == 1024;
  }
}
```

**Expected:** list still exposes the same array contents.

### Example B: Remove one ownership path deliberately

Clearing a container removes its references, but another strong reference can keep the object reachable. Reachability is a graph property.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    List<byte[]> retained = new ArrayList<>();
    byte[] payload = new byte[1024];
    payload[0] = 7;
    retained.add(payload);
    payload = null;
    assert retained.get(0)[0] == 7 && retained.get(0).length == 1024;

    byte[] separate = retained.get(0);
    retained.clear();
    assert retained.isEmpty() && separate[0] == 7;
  }
}
```

**Expected:** list empty; separate array still valid.

## Prediction before your attempt

Before running Example A, decide whether setting the local `payload` to null frees the 1,024-byte array that was also added to `retained`. For Example B, predict what `separate[0]` holds after `retained.clear()` when `separate` was taken from the list first. Before Exercise 4, compute the logical payload of ten 128-byte arrays and list what the real heap cost adds on top.

## Exercises

1. **Expose a strong retention path: change one input.** Change `byte[] payload = new byte[1024];` to `byte[] payload = new byte[1025];` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `retained.get(0)[0] == 7 && retained.get(0).length == 1024`.
   **Verify:** Name the value that makes `retained.get(0)[0] == 7 && retained.get(0).length == 1024` false, then restore the line.

2. **Remove one ownership path deliberately: diagnose an edited check.** Example B's new assertion was edited to `assert retained.isEmpty() && separate[1] == 7;`. Explain why it fails for unchanged state and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `retained.isEmpty() && separate[0] == 7`; the restored assertion passes.
   **Verify:** Explain why the edited assertion rejects the state that `retained.isEmpty() && separate[0] == 7` accepts.

3. **Inspect a weak reference without timing assumptions.** Create a WeakReference to the still-strongly-referenced array.
   **Expected:** weak get returns the same object while strong reference exists.
   **Verify:** Control: changing `assert weak.get() == separate;` to `assert weak.get() != separate;` inside the assertion must make it fail.

4. **Separate value size from allocation count.** Create ten arrays of 128 bytes and count logical payload bytes.
   **Expected:** 1280 logical bytes; no exact heap-overhead claim.
   **Verify:** Control: changing `for (int i = 0; i < 10; i++) blocks.add(new byte[128]);` to `for (int i = 0; i <= 10; i++) blocks.add(new byte[128]);` must fail the assertion on `logical == 1280`.

5. **Reuse a bounded working buffer.** Fill one array repeatedly rather than retaining every intermediate array.
   **Expected:** same buffer identity; final value 9.
   **Verify:** Control: changing `for (int i = 0; i < 10; i++) Arrays.fill(buffer, (byte) i);` to `for (int i = 0; i <= 10; i++) Arrays.fill(buffer, (byte) i);` must fail the assertion on `System.identityHashCode(buffer) == identity && buffer[0] == 9`.

6. **Record process memory cautiously.** Read Runtime total/free/max memory and check only valid ordering relationships.
   **Expected:** nonnegative counters; max at least total; no claim of exact object size.
   **Verify:** Name an input that would make `total >= 0 && free >= 0 && maximum >= total` false and the value that changes.

## Common pitfalls and diagnosis

The usual leak in Java is retention, not a missing `free`: a static map, a cache without eviction, or a listener that is never removed keeps objects reachable forever. Setting a local variable to null rarely helps, because the reference that matters is somewhere else. `System.gc()` is only a request, so a test that calls it and then expects a `WeakReference` to be cleared is flaky. `Runtime` memory figures change between reads and include objects you did not create.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the edit allocates 1,025 bytes instead of 1,024. Then check the two conditions: the first byte is still 7, but the length differs. Finally, explain why the retention path is intact and only the size assertion detects the edit.
- **Exercise 2:** First note that the edited check reads `separate[1]`, which was never written. Then recall that a new byte array starts filled with zeros. Finally, compare 0 with 7 and confirm that clearing the list did not affect the array.
- **Exercise 3:** First create a `WeakReference` to the array that `separate` still holds strongly. Then assert that `weak.get()` returns the same object. Finally, call `Reference.reachabilityFence(separate)` after the check and explain why the fence keeps the strong reference alive until that point.
- **Exercise 4:** First add ten 128-byte arrays to a list. Then sum their `length` fields into a logical byte count. Finally, assert 1,280 and list the headers, alignment and list storage that a heap measurement would add.
- **Exercise 5:** First allocate one buffer and record its `System.identityHashCode`. Then fill it with each value from 0 to 9 using `Arrays.fill`. Finally, assert that the identity is unchanged and the first byte is 9, and say what a caller expecting snapshots would lose.
- **Exercise 6:** First read `totalMemory`, `freeMemory` and `maxMemory` from `Runtime.getRuntime()`. Then assert that each is nonnegative and that the maximum is at least the total. Finally, explain why asserting an exact free figure would make the check flaky.

## Self-check and retrieval

Without notes, define reachability and explain why clearing a list does not free an array that another variable still references. Say what a `WeakReference` can and cannot promise, why `reachabilityFence` appears in Exercise 3, and which relationships between `totalMemory`, `freeMemory` and `maxMemory` are safe to assert.

## Next step

Continue with `java-026`: Packages, classpaths and modules. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/ref/Reference.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-025: JVM memory, GC and allocation.
Read courses/java/guides/java-025.md and courses/java/lessons/java-025.java. Direct prerequisites: `java-024`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
