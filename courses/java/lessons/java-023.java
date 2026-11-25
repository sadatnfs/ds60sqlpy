// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Protect a compound counter: change one input
    // Change `for (int i = 0; i < 1000; i++) counter.increment();` to `for (int i = 1; i < 1000;
    // i++) counter.increment();` in Example A and predict which assertion fails and why.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `counter.value() == 2000`.

    // Exercise 2: Use an atomic increment: debug a regression
    // A regression in Example B's new code makes one line read `for (int i = 0; i <= 1000; i++)
    // atomic.incrementAndGet();`. Repair it using the failing assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on
    // `atomic.get() == 2000`; the repaired line reads `for (int i = 0; i < 1000; i++)
    // atomic.incrementAndGet();`.

    // Exercise 3: Inspect compare-and-set
    // Change 0 to 1 with CAS, then retry expecting 0.
    // Expected: first true; second false; value 1.

    // Exercise 4: Combine map updates atomically
    // Use ConcurrentHashMap.merge for 2000 total increments ofkeyx.
    // Expected: stored count 2000.

    // Exercise 5: Bound lock contention
    // Hold a ReentrantLock in the caller while a worker tries to acquire it with a short
    // timeout.
    // Expected: worker returns false; lock released in finally.

    // Exercise 6: Use one global order for two locks
    // Have both workers acquire first then second before incrementing shared state.
    // Expected: 2000 increments and no blocked worker after bounded joins.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
