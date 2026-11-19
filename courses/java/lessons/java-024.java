// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Observe virtual identity: predict an edited check
    // Copy Example A into a scratch `Main.java` and change `assert !task.isAlive() &&
    // virtual.get();` to `assert task.isAlive() && virtual.get();` inside its assertion. Before
    // running it with `java -ea Main`, predict whether the assertion still holds and explain
    // why; then restore it.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `!task.isAlive() && virtual.get()`. Restoring the original line brings back the worked
    // observation: true and terminated.

    // Exercise 2: Use a scoped virtual executor: debug a regression
    // A regression changed one token in the code that Example B adds after Example A, so one
    // line now reads `for (int value = 1; value < 4; value++) {`. Run Example B with that line,
    // use the failing assertion to locate the defect and repair it without changing the
    // assertion.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `results.equals(List.of(1, 4, 9, 16))`; after it the line reads `for (int value = 1; value
    // <= 4; value++) {` again and 1, 4, 9, 16.

    // Exercise 3: Limit a scarce resource with a semaphore
    // Run six tasks but allow only two inside a gated resource section.
    // Expected: maximum active count 2; all six complete.

    // Exercise 4: Preserve a CPU calculation contract
    // Compare a sequential sum 1..1000 with four partitioned virtual tasks.
    // Expected: both 500500; no speed claim.

    // Exercise 5: Cancel a blocked virtual task
    // Interrupt a virtual task waiting on a latch and observe its cleanup signal.
    // Expected: Future cancelled; task exits cooperatively.

    // Exercise 6: Keep a blocking wait outside a monitor
    // Read a state snapshot inside a synchronized block, then wait on a latch after leaving it.
    // Expected: caller can acquire the monitor while the worker is waiting.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
