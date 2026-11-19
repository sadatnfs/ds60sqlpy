// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Protect a compound counter: change one input
    // Copy Example A into a scratch `Main.java` and change `for (int i = 0; i < 1000; i++)
    // counter.increment();` to `for (int i = 1; i < 1000; i++) counter.increment();`. Before
    // running it with `java -ea Main`, predict which assertion fails and which value it now
    // sees; then run it and restore the original line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `counter.value() == 2000`. Restoring the original line brings back the worked observation:
    // counter 2000.

    // Exercise 2: Use an atomic increment: debug a regression
    // A regression changed one token in the code that Example B adds after Example A, so one
    // line now reads `for (int i = 0; i <= 1000; i++) atomic.incrementAndGet();`. Run Example B
    // with that line, use the failing assertion to locate the defect and repair it without
    // changing the assertion.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `atomic.get() == 2000`; after it the line reads `for (int i = 0; i < 1000; i++)
    // atomic.incrementAndGet();` again and value 2000.

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
