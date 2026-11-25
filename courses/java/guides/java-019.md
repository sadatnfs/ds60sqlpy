# java-019: Data structures and complexity

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-018`

## Learning objectives

Choose a queue, stack or priority queue for a task and measure the work a linear search performs.

The six exercises practice these steps:

- Use a FIFO queue.
- Use a LIFO stack.
- Poll a priority queue.
- Count linear-search work.
- Preserve duplicate priorities.
- Handle empty removal explicitly.

## Purpose and mental model

A data structure is a set of operations with representation and cost tradeoffs. An ArrayList supports constant-time indexed access but shifting elements after a front insertion costs linear work. A HashMap offers expected constant-time lookup under appropriate hashing assumptions, not a promise that every operation always costs one step. A Deque supports queue and stack operations without shifting an array prefix. A PriorityQueue keeps the smallest element available but does not expose a fully sorted iteration order. Big O describes how work grows with input size, not a measured wall-clock time or a guarantee about constants.

## Vocabulary and concepts

**Big O:** An asymptotic upper-bound description of growth in work or space.

**Deque:** A double-ended queue supporting insertion and removal at both ends.

**Heap:** A partial ordering that keeps a minimum or maximum at the root.

## How to run this lesson

The comparison counter in Exercise 4 measures work by counting comparisons, not by timing, so the results are the same on any machine and with any JIT warm-up.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

ArrayDeque.addLast/removeFirst implements a queue; push/pop implements a stack. PriorityQueue.add and poll maintain a heap ordering, and repeated poll produces sorted removal order. Iterating the heap is not a sorted traversal. Count comparisons in a simple linear search to connect an algorithmic model to observations. A hash-based membership result must use stable equality and hashing contracts.

## Worked example / walkthrough

### Example A: Use a FIFO queue

The queue preserves arrival order. Choosing removeLast instead would create a stack-like policy.

```java
import java.util.*;

public class Main {

  record Task(int priority, int sequence, String name) {}

  static int comparisons(int[] values, int target) {
    int count = 0;
    for (int value : values) {
      count++;
      if (value == target) break;
    }
    return count;
  }

  public static void main(String[] args) throws Exception {
    Deque<String> queue = new ArrayDeque<>();
    queue.addLast("a");
    queue.addLast("b");
    queue.addLast("c");
    List<String> fifo = List.of(queue.removeFirst(), queue.removeFirst(), queue.removeFirst());
    assert fifo.equals(List.of("a", "b", "c"));
  }
}
```

**Expected:** a, b, c order.

### Example B: Use a LIFO stack

The most recently pushed value is removed first. Stack behavior is useful for nested traversal or undo histories but differs from fair arrival-order processing.

```java
import java.util.*;

public class Main {

  record Task(int priority, int sequence, String name) {}

  static int comparisons(int[] values, int target) {
    int count = 0;
    for (int value : values) {
      count++;
      if (value == target) break;
    }
    return count;
  }

  public static void main(String[] args) throws Exception {
    Deque<String> queue = new ArrayDeque<>();
    queue.addLast("a");
    queue.addLast("b");
    queue.addLast("c");
    List<String> fifo = List.of(queue.removeFirst(), queue.removeFirst(), queue.removeFirst());
    assert fifo.equals(List.of("a", "b", "c"));

    Deque<Integer> stack = new ArrayDeque<>();
    stack.push(1);
    stack.push(2);
    stack.push(3);
    List<Integer> lifo = List.of(stack.pop(), stack.pop(), stack.pop());
    assert lifo.equals(List.of(3, 2, 1));
  }
}
```

**Expected:** 3, 2, 1.

## Prediction before your attempt

Before running Example A, write the removal order for a, b and c added with `addLast` and removed with `removeFirst`. For Example B, predict the pop order after pushing 1, 2 and 3 onto a `Deque`. Before Exercise 3, decide whether printing a `PriorityQueue` that holds 5, 1, 4 and 2 shows the values sorted (it does not; only repeated `remove` yields 1, 2, 4, 5).

## Exercises

1. **Use a FIFO queue: change one input.** Change `queue.addLast("a");` to `queue.addLast("a!");` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `fifo.equals(List.of("a", "b", "c"))`.
   **Verify:** Name the value that makes `fifo.equals(List.of("a", "b", "c"))` false, then restore the line.

2. **Use a LIFO stack: debug a regression.** A regression changed `stack.push(1);` to `stack.push(2);` in Example B's new code. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `lifo.equals(List.of(3, 2, 1))`; the repaired line reads `stack.push(1);`.
   **Verify:** Explain how the changed token alters the value that `lifo.equals(List.of(3, 2, 1))` tests.

3. **Poll a priority queue.** Insert 5, 1, 4, 2 and repeatedly poll.
   **Expected:** 1, 2, 4, 5.
   **Verify:** Control: changing `while (!heap.isEmpty()) removed.add(heap.remove());` to `while (heap.isEmpty()) removed.add(heap.remove());` must fail the assertion on `removed.equals(List.of(1, 2, 4, 5))`.

4. **Count linear-search work.** Search for the final item in arrays of length 4 and 8 using a comparison counter.
   **Expected:** 4 and 8 comparisons.
   **Verify:** Control: changing `assert comparisons(new int[] { 1, 2, 3, 4 }, 4) == 4;` to `assert comparisons(new int[] { 1, 2, 4, 4 }, 4) == 4;` inside the assertion must make it fail.

5. **Preserve duplicate priorities.** Insert tasks with equal priority and a stable sequence tie-breaker.
   **Expected:** earlier sequence removed first.
   **Verify:** Control: changing `tasks.add(new Task(1, 1, "earlier"));` to `tasks.add(new Task(2, 1, "earlier"));` must fail the assertion on `firstName.equals("earlier")`.

6. **Handle empty removal explicitly.** Compare Deque.pollFirst with removeFirst on an empty queue.
   **Expected:** poll returns null; remove throws NoSuchElementException.
   **Verify:** Control: changing `failed = true;` to `failed = false;` must fail the assertion on `failed`.

## Common pitfalls and diagnosis

Using an `ArrayList` as a queue with `remove(0)` shifts every remaining element, which is linear per removal; `ArrayDeque` removes from either end in constant time. A `PriorityQueue` iterates in heap order, not sorted order, so `toString` or a for-each loop misleads. Big O describes growth, not speed: a linear scan of eight items can beat a hash lookup in practice. Finally, `removeFirst` on an empty deque throws while `pollFirst` returns null, so pick the method whose absence contract fits the caller.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First write the queue contents after the edit: a!, b, c. Then remove from the front and record the order. Finally, compare it with a, b, c and explain why the ordering policy is still FIFO even though the check fails.
- **Exercise 2:** First note that the edit pushes 2 where 1 was pushed, so the stack holds 3, 2, 2 from the top. Then write the pop order. Finally, compare it with 3, 2, 1 and decide whether LIFO behavior or the data changed.
- **Exercise 3:** First add 5, 1, 4 and 2 to a `PriorityQueue`. Then remove elements while the heap is not empty and collect them in a list. Finally, compare the list with 1, 2, 4, 5 and explain why the loop condition must test `!heap.isEmpty()`.
- **Exercise 4:** First count one comparison per element visited until the target is found. Then search for the last element of arrays of length 4 and 8. Finally, assert 4 and 8 and explain why searching for the first element would not show linear growth.
- **Exercise 5:** First order the queue by priority and then by sequence with `Comparator.comparingInt(...).thenComparingInt(...)`. Then add two tasks with equal priority, the later one first. Finally, remove one task and assert that the earlier sequence comes out first.
- **Exercise 6:** First call `pollFirst()` on an empty `ArrayDeque` and assert null. Then call `removeFirst()` inside a `try` block and catch `NoSuchElementException`. Finally, explain which method fits a caller that treats empty as normal.

## Self-check and retrieval

Without the guide, explain FIFO and LIFO with the deque methods that implement each, what a heap guarantees about `peek` and what it does not guarantee about iteration, why doubling the input doubles the comparisons in the worst-case linear search, and how a sequence field makes equal priorities deterministic.

## Next step

Continue with `java-020`: Search, sorting and dynamic programming. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/PriorityQueue.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-019: Data structures and complexity.
Read courses/java/guides/java-019.md and courses/java/lessons/java-019.java. Direct prerequisites: `java-018`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
