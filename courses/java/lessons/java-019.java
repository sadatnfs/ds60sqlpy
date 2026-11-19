// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Use a FIFO queue: change one input
    // Copy Example A into a scratch `Main.java` and change `queue.addLast("a");` to
    // `queue.addLast("a!");`. Before running it with `java -ea Main`, predict which assertion
    // fails and which value it now sees; then run it and restore the original line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `fifo.equals(List.of("a", "b", "c"))`. Restoring the original line brings back the worked
    // observation: a, b, c order.

    // Exercise 2: Use a LIFO stack: debug a regression
    // A regression changed `stack.push(1);` to `stack.push(2);` in the code that Example B adds
    // after Example A. Run Example B with that change, use the failing assertion to explain the
    // defect and repair it without changing the assertion.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `lifo.equals(List.of(3, 2, 1))`; after it the line reads `stack.push(1);` again and 3, 2,
    // 1.

    // Exercise 3: Poll a priority queue
    // Insert 5, 1, 4, 2 and repeatedly poll.
    // Expected: 1, 2, 4, 5.

    // Exercise 4: Count linear-search work
    // Search for the final item in arrays of length 4 and 8 using a comparison counter.
    // Expected: 4 and 8 comparisons.

    // Exercise 5: Preserve duplicate priorities
    // Insert tasks with equal priority and a stable sequence tie-breaker.
    // Expected: earlier sequence removed first.

    // Exercise 6: Handle empty removal explicitly
    // Compare Deque.pollFirst with removeFirst on an empty queue.
    // Expected: poll returns null; remove throws NoSuchElementException.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
