// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Retrieve a bounded result: change one input
    // Change `var future = executor.submit(() -> 42);` to `var future = executor.submit(() ->
    // 43);` in Example A and predict which assertion fails and why.
    // Expected: The edited run fails with an `AssertionError` from the assertion on `value ==
    // 42`.

    // Exercise 2: Preserve task failure identity: debug a regression
    // Add one defect to Example B's new code that fails the assertion on `observed`, then repair
    // it.
    // Expected: The defective copy fails its assertion and the repaired copy passes.

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
