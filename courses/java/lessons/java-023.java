// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {
    public static void main(String[] args) throws Exception {
        // Exercise 1: Protect a compound counter
        // Run two workers making1000 synchronized increments each.
        // Expected: counter2000.

        // Exercise 2: Use an atomic increment
        // Repeat the workload withAtomicInteger.incrementAndGet.
        // Expected: value2000.

        // Exercise 3: Inspect compare-and-set
        // Change0to1 withCAS,then retry expecting0.
        // Expected: firsttrue;secondfalse;value1.

        // Exercise 4: Combine map updates atomically
        // UseConcurrentHashMap.merge for2000 total increments ofkeyx.
        // Expected: stored count2000.

        // Exercise 5: Bound lock contention
        // Hold aReentrantLock in the caller while a worker tries to acquire it with a short timeout.
        // Expected: worker returnsfalse;lock released in finally.

        // Exercise 6: Use one global order for two locks
        // Have both workers acquirefirst then second before incrementing shared state.
        // Expected: 2000 increments and no blocked worker after bounded joins.
        System.out.println("Implement and check the six exercises in your saved copy.");
    }
}
