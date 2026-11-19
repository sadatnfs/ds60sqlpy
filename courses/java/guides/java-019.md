# java-019: Data structures and complexity

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-018`

## Learning objectives

Choose a queue, stack or priority queue for a task and measure the work a linear search performs. Along the way, explain big o, deque, heap using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Insert 5, 1, 4, 2 and repeatedly poll. The final exercise transfers the mechanism to handle empty removal explicitly.

## Purpose and mental model

A data structure is a set of operations with representation and cost tradeoffs. An ArrayList supports constant-time indexed access but shifting elements after a front insertion costs linear work. A HashMap offers expected constant-time lookup under appropriate hashing assumptions, not a promise that every operation always costs one step. A Deque supports queue and stack operations without shifting an array prefix. A PriorityQueue keeps the smallest element available but does not expose a fully sorted iteration order. Big O describes how work grows with input size, not a measured wall-clock time or a guarantee about constants.

## Vocabulary and concepts

**Big O:** An asymptotic upper-bound description of growth in work or space.

**Deque:** A double-ended queue supporting insertion and removal at both ends.

**Heap:** A partial ordering that keeps a minimum or maximum at the root.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-019/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



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

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Use a FIFO queue: change one input.** Copy Example A into a scratch `Main.java` and change `queue.addLast("a");` to `queue.addLast("a!");`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `fifo.equals(List.of("a", "b", "c"))`. Restoring the original line brings back the worked observation: a, b, c order.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `fifo.equals(List.of("a", "b", "c"))` false. After restoring the line, the program completes without an `AssertionError` again.

2. **Use a LIFO stack: debug a regression.** A regression changed `stack.push(1);` to `stack.push(2);` in the code that Example B adds after Example A. Run Example B with that change, use the failing assertion to explain the defect and repair it without changing the assertion.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `lifo.equals(List.of(3, 2, 1))`; after it the line reads `stack.push(1);` again and 3, 2, 1.
   **Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `lifo.equals(List.of(3, 2, 1))` for this input.

3. **Poll a priority queue.** Insert 5, 1, 4, 2 and repeatedly poll.
   **Expected:** 1, 2, 4, 5.
   **Verify:** Keep an assertion equivalent to `removed.equals(List.of(1, 2, 4, 5))`. As a control, change `while (!heap.isEmpty()) removed.add(heap.remove());` to `while (heap.isEmpty()) removed.add(heap.remove());`: the run must fail with an `AssertionError` from the assertion on `removed.equals(List.of(1, 2, 4, 5))`. Restore the line before continuing.

4. **Count linear-search work.** Search for the final item in arrays of length 4 and 8 using a comparison counter.
   **Expected:** 4 and 8 comparisons.
   **Verify:** Keep an assertion equivalent to `comparisons(new int[] { 1, 2, 3, 4 }, 4) == 4`. As a control, change `assert comparisons(new int[] { 1, 2, 3, 4 }, 4) == 4;` to `assert comparisons(new int[] { 1, 2, 4, 4 }, 4) == 4;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

5. **Preserve duplicate priorities.** Insert tasks with equal priority and a stable sequence tie-breaker.
   **Expected:** earlier sequence removed first.
   **Verify:** Keep an assertion equivalent to `firstName.equals("earlier")`. As a control, change `tasks.add(new Task(1, 1, "earlier"));` to `tasks.add(new Task(2, 1, "earlier"));`: the run must fail with an `AssertionError` from the assertion on `firstName.equals("earlier")`. Restore the line before continuing.

6. **Handle empty removal explicitly.** Compare Deque.pollFirst with removeFirst on an empty queue.
   **Expected:** poll returns null; remove throws NoSuchElementException.
   **Verify:** Keep an assertion equivalent to `failed`. As a control, change `failed = true;` to `failed = false;`: the run must fail with an `AssertionError` from the assertion on `failed`. Restore the line before continuing.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: a, b, c order. Then list the values read by `fifo.equals(List.of("a", "b", "c"))` and trace each one from its declaration. Finally, compute the asserted value with `queue.addLast("a!");` in place before running.
- **Exercise 2:** First restate the expected observation: 3, 2, 1. Then list the values read by `lifo.equals(List.of(3, 2, 1))` and trace each one from its declaration. Finally, compare `stack.push(2);` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: 1, 2, 4, 5. Then list the values read by `removed.equals(List.of(1, 2, 4, 5))` and trace each one from its declaration. Finally, predict the effect of changing `while (!heap.isEmpty()) removed.add(heap.remove());` to `while (heap.isEmpty()) removed.add(heap.remove());` before running anything.
- **Exercise 4:** First restate the expected observation: 4 and 8 comparisons. Then list the values read by `comparisons(new int[] { 1, 2, 3, 4 }, 4) == 4` and trace each one from its declaration. Finally, name one input that would make `comparisons(new int[] { 1, 2, 3, 4 }, 4) == 4` false.
- **Exercise 5:** First restate the expected observation: earlier sequence removed first. Then list the values read by `firstName.equals("earlier")` and trace each one from its declaration. Finally, predict the effect of changing `tasks.add(new Task(1, 1, "earlier"));` to `tasks.add(new Task(2, 1, "earlier"));` before running anything.
- **Exercise 6:** First restate the expected observation: poll returns null; remove throws NoSuchElementException. Then list the values read by `failed` and trace each one from its declaration. Finally, predict the effect of changing `failed = true;` to `failed = false;` before running anything.

## Self-check and retrieval

Close the solution and explain Big O, Deque, Heap in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/PriorityQueue.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

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
