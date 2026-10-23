// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {
    public static void main(String[] args) throws Exception {
        // Exercise 1: Retrieve a bounded result
        // Submit a callable returning42 and get it within2seconds.
        // Expected: result42.

        // Exercise 2: Preserve task failure identity
        // Submit a callable throwingIllegalArgumentException and inspectFuture.get.
        // Expected: ExecutionException cause isIllegalArgumentException.

        // Exercise 3: Separate wait timeout from task completion
        // Hold a task on a latch,wait with a short timeout,then release and obtain the result.
        // Expected: TimeoutException first;later result7.

        // Exercise 4: Cancel cooperatively
        // Cancel a running latch-waiting task with interruption and observe its exit signal.
        // Expected: Future cancelled and task catches interruption.

        // Exercise 5: Reject work after shutdown
        // Shut down an idle executor and submit another task.
        // Expected: RejectedExecutionException.

        // Exercise 6: Enforce a bounded queue
        // Use one worker and one queue slot,hold the worker,fill the queue,then submit a third task.
        // Expected: third submission rejected;admitted tasks finish after release.
        System.out.println("Implement and check the six exercises in your saved copy.");
    }
}
