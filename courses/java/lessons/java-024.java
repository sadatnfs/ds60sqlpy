// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Observe virtual identity: predict an edited check
    // Change Example A's assertion to `assert task.isAlive() && virtual.get();`, predict whether
    // it holds, then run and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `!task.isAlive() && virtual.get()`.

    // Exercise 2: Use a scoped virtual executor: debug a regression
    // A regression in Example B's new code makes one line read `for (int value = 1; value < 4;
    // value++) {`. Repair it using the failing assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on
    // `results.equals(List.of(1, 4, 9, 16))`; the repaired line reads `for (int value = 1; value
    // <= 4; value++) {`.

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
