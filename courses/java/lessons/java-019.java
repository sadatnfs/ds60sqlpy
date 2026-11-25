// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Use a FIFO queue: change one input
    // Change `queue.addLast("a");` to `queue.addLast("a!");` in Example A and predict which
    // assertion fails and why.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `fifo.equals(List.of("a", "b", "c"))`.

    // Exercise 2: Use a LIFO stack: debug a regression
    // A regression changed `stack.push(1);` to `stack.push(2);` in Example B's new code. Repair
    // it using the failing assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on
    // `lifo.equals(List.of(3, 2, 1))`; the repaired line reads `stack.push(1);`.

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
