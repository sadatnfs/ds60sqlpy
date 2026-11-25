# java-019: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

A data structure is a set of operations with representation and cost tradeoffs. An ArrayList supports constant-time indexed access but shifting elements after a front insertion costs linear work. A HashMap offers expected constant-time lookup under appropriate hashing assumptions, not a promise that every operation always costs one step. A Deque supports queue and stack operations without shifting an array prefix. A PriorityQueue keeps the smallest element available but does not expose a fully sorted iteration order. Big O describes how work grows with input size, not a measured wall-clock time or a guarantee about constants.

**Big O:** An asymptotic upper-bound description of growth in work or space.

**Deque:** A double-ended queue supporting insertion and removal at both ends.

**Heap:** A partial ordering that keeps a minimum or maximum at the root.

## Reading the reference

ArrayDeque.addLast/removeFirst implements a queue; push/pop implements a stack. PriorityQueue.add and poll maintain a heap ordering, and repeated poll produces sorted removal order. Iterating the heap is not a sorted traversal. Count comparisons in a simple linear search to connect an algorithmic model to observations. A hash-based membership result must use stable equality and hashing contracts.

## Exercise 1: Use a FIFO queue: change one input

Task: Change `queue.addLast("a");` to `queue.addLast("a!");` in Example A and predict which assertion fails and why.

The queue preserves arrival order. Choosing removeLast instead would create a stack-like policy.

The unchanged code is the part that Example A adds:

```java
Deque<String> queue = new ArrayDeque<>();
queue.addLast("a");
queue.addLast("b");
queue.addLast("c");
List<String> fifo = List.of(queue.removeFirst(), queue.removeFirst(), queue.removeFirst());
assert fifo.equals(List.of("a", "b", "c"));
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `fifo.equals(List.of("a", "b", "c"))`.

**Verify:** Name the value that makes `fifo.equals(List.of("a", "b", "c"))` false, then restore the line.

## Exercise 2: Use a LIFO stack: debug a regression

Task: A regression changed `stack.push(1);` to `stack.push(2);` in Example B's new code. Repair it using the failing assertion.

The most recently pushed value is removed first. Stack behavior is useful for nested traversal or undo histories but differs from fair arrival-order processing.

The unchanged code is the part that Example B adds:

```java
Deque<Integer> stack = new ArrayDeque<>();
stack.push(1);
stack.push(2);
stack.push(3);
List<Integer> lifo = List.of(stack.pop(), stack.pop(), stack.pop());
assert lifo.equals(List.of(3, 2, 1));
```

**Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `lifo.equals(List.of(3, 2, 1))`; the repaired line reads `stack.push(1);`.

**Verify:** Explain how the changed token alters the value that `lifo.equals(List.of(3, 2, 1))` tests.

## Exercise 3: Poll a priority queue

Task: Insert 5, 1, 4, 2 and repeatedly poll.

The heap guarantees the next minimum, not that its backing iteration is sorted. Repeated removal establishes the sorted sequence.

```java
PriorityQueue<Integer> heap = new PriorityQueue<>(List.of(5, 1, 4, 2));
List<Integer> removed = new ArrayList<>();
while (!heap.isEmpty()) removed.add(heap.remove());
assert removed.equals(List.of(1, 2, 4, 5));
```

**Expected:** 1, 2, 4, 5.

**Verify:** Control: changing `while (!heap.isEmpty()) removed.add(heap.remove());` to `while (heap.isEmpty()) removed.add(heap.remove());` must fail the assertion on `removed.equals(List.of(1, 2, 4, 5))`.

## Exercise 4: Count linear-search work

Task: Search for the final item in arrays of length 4 and 8 using a comparison counter.

Doubling this worst-case input doubles observed comparisons. This supports the linear growth model for this algorithm without making a hardware timing claim.

```java
assert comparisons(new int[] { 1, 2, 3, 4 }, 4) == 4;
assert comparisons(new int[] { 1, 2, 3, 4, 5, 6, 7, 8 }, 8) == 8;
```

**Expected:** 4 and 8 comparisons.

**Verify:** Control: changing `assert comparisons(new int[] { 1, 2, 3, 4 }, 4) == 4;` to `assert comparisons(new int[] { 1, 2, 4, 4 }, 4) == 4;` inside the assertion must make it fail.

## Exercise 5: Preserve duplicate priorities

Task: Insert tasks with equal priority and a stable sequence tie-breaker.

A priority alone may not define a deterministic order among ties. The explicit sequence field preserves a declared policy.

```java
PriorityQueue<Task> tasks = new PriorityQueue<>(
  Comparator.comparingInt(Task::priority).thenComparingInt(Task::sequence)
);
tasks.add(new Task(1, 2, "later"));
tasks.add(new Task(1, 1, "earlier"));
String firstName = tasks.remove().name();
assert firstName.equals("earlier");
```

**Expected:** earlier sequence removed first.

**Verify:** Control: changing `tasks.add(new Task(1, 1, "earlier"));` to `tasks.add(new Task(2, 1, "earlier"));` must fail the assertion on `firstName.equals("earlier")`.

## Exercise 6: Handle empty removal explicitly

Task: Compare Deque.pollFirst with removeFirst on an empty queue.

The two APIs express different absence contracts. Choosing one deliberately is clearer than catching an exception that the caller expected as normal control flow.

```java
Deque<Integer> empty = new ArrayDeque<>();
Integer polled = empty.pollFirst();
assert polled == null;
boolean failed = false;
try {
  empty.removeFirst();
} catch (NoSuchElementException expected) {
  failed = true;
}
assert failed;
```

**Expected:** poll returns null; remove throws NoSuchElementException.

**Verify:** Control: changing `failed = true;` to `failed = false;` must fail the assertion on `failed`.

## After comparing the answer

Add a second worst-case search over 16 elements to your copy and predict the count before running it; then search for the first element and explain why the best case is constant.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
