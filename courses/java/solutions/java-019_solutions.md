# java-019: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A data structure is a set of operations with representation and cost tradeoffs. An ArrayList supports constant-time indexed access but shifting elements after a front insertion costs linear work. A HashMap offers expected constant-time lookup under appropriate hashing assumptions, not a promise that every operation always costs one step. A Deque supports queue and stack operations without shifting an array prefix. A PriorityQueue keeps the smallest element available but does not expose a fully sorted iteration order. Big O describes how work grows with input size, not a measured wall-clock time or a guarantee about constants.

**Big O:** An asymptotic upper-bound description of growth in work or space.

**Deque:** A double-ended queue supporting insertion and removal at both ends.

**Heap:** A partial ordering that keeps a minimum or maximum at the root.

## Reading the reference

ArrayDeque.addLast/removeFirst implements a queue; push/pop implements a stack. PriorityQueue.add and poll maintain a heap ordering, and repeated poll produces sorted removal order. Iterating the heap is not a sorted traversal. Count comparisons in a simple linear search to connect an algorithmic model to observations. A hash-based membership result must use stable equality and hashing contracts.

## Exercise 1: Use a FIFO queue: change one input

Task: Copy Example A into a scratch `Main.java` and change `queue.addLast("a");` to `queue.addLast("a!");`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.

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

**Expected:** The changed run fails with an `AssertionError` from the assertion on `fifo.equals(List.of("a", "b", "c"))`. Restoring the original line brings back the worked observation: a, b, c order.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `fifo.equals(List.of("a", "b", "c"))` false. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Use a LIFO stack: debug a regression

Task: A regression changed `stack.push(1);` to `stack.push(2);` in the code that Example B adds after Example A. Run Example B with that change, use the failing assertion to explain the defect and repair it without changing the assertion.

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

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `lifo.equals(List.of(3, 2, 1))`; after it the line reads `stack.push(1);` again and 3, 2, 1.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `lifo.equals(List.of(3, 2, 1))` for this input.

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

**Verify:** Keep an assertion equivalent to `removed.equals(List.of(1, 2, 4, 5))`. As a control, change `while (!heap.isEmpty()) removed.add(heap.remove());` to `while (heap.isEmpty()) removed.add(heap.remove());`: the run must fail with an `AssertionError` from the assertion on `removed.equals(List.of(1, 2, 4, 5))`. Restore the line before continuing.

## Exercise 4: Count linear-search work

Task: Search for the final item in arrays of length 4 and 8 using a comparison counter.

Doubling this worst-case input doubles observed comparisons. This supports the linear growth model for this algorithm without making a hardware timing claim.

```java
assert comparisons(new int[] { 1, 2, 3, 4 }, 4) == 4;
assert comparisons(new int[] { 1, 2, 3, 4, 5, 6, 7, 8 }, 8) == 8;
```

**Expected:** 4 and 8 comparisons.

**Verify:** Keep an assertion equivalent to `comparisons(new int[] { 1, 2, 3, 4 }, 4) == 4`. As a control, change `assert comparisons(new int[] { 1, 2, 3, 4 }, 4) == 4;` to `assert comparisons(new int[] { 1, 2, 4, 4 }, 4) == 4;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

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

**Verify:** Keep an assertion equivalent to `firstName.equals("earlier")`. As a control, change `tasks.add(new Task(1, 1, "earlier"));` to `tasks.add(new Task(2, 1, "earlier"));`: the run must fail with an `AssertionError` from the assertion on `firstName.equals("earlier")`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `failed`. As a control, change `failed = true;` to `failed = false;`: the run must fail with an `AssertionError` from the assertion on `failed`. Restore the line before continuing.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
