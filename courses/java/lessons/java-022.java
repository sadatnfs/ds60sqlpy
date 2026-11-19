// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Retrieve a bounded result: change one input
    // Copy Example A into a scratch `Main.java` and change `var future = executor.submit(() ->
    // 42);` to `var future = executor.submit(() -> 43);`. Before running it with `java -ea
    // Main`, predict which assertion fails and which value it now sees; then run it and restore
    // the original line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on `value ==
    // 42`. Restoring the original line brings back the worked observation: result 42.

    // Exercise 2: Preserve task failure identity: debug a regression
    // Introduce one deliberate defect into a copy of Example B that makes the assertion on
    // `observed` fail, then explain how the stack trace leads back to the faulty statement.
    // Expected: The defective copy fails the assertion on `observed`; the repaired copy
    // reproduces the worked observation: executionException cause is IllegalArgumentException.

    // Exercise 3: Separate wait timeout from task completion
    // Hold a task on a latch, wait with a short timeout, then release and obtain the result.
    // Expected: TimeoutException first; later result 7.

    // Exercise 4: Cancel cooperatively
    // Cancel a running latch-waiting task with interruption and observe its exit signal.
    // Expected: Future cancelled and task catches interruption.

    // Exercise 5: Reject work after shutdown
    // Shut down an idle executor and submit another task.
    // Expected: RejectedExecutionException.

    // Exercise 6: Enforce a bounded queue
    // Use one worker and one queue slot, hold the worker, fill the queue, then submit a third
    // task.
    // Expected: third submission rejected; admitted tasks finish after release.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
