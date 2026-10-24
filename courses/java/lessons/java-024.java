// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {
    public static void main(String[] args) throws Exception {
        // Exercise 1: Observe virtual identity
        // Start a virtual thread that recordsisVirtual andjoin it.
        // Expected: true and terminated.

        // Exercise 2: Use a scoped virtual executor
        // Submit four square calculations and retrieve their results with timeouts.
        // Expected: 1,4,9,16.

        // Exercise 3: Limit a scarce resource with a semaphore
        // Run six tasks but allow only two inside a gated resource section.
        // Expected: maximum active count2;all six complete.

        // Exercise 4: Preserve a CPU calculation contract
        // Compare a sequential sum1..1000 with four partitioned virtual tasks.
        // Expected: both500500;no speed claim.

        // Exercise 5: Cancel a blocked virtual task
        // Interrupt a virtual task waiting on a latch and observe its cleanup signal.
        // Expected: Future cancelled;task exits cooperatively.

        // Exercise 6: Keep a blocking wait outside a monitor
        // Read a state snapshot inside a synchronized block,then wait on a latch after leaving it.
        // Expected: caller can acquire the monitor while the worker is waiting.
        System.out.println("Implement and check the six exercises in your saved copy.");
    }
}
