// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Publish a result through join: change one input
    // Copy Example A into a scratch `Main.java` and change `Thread worker =
    // Thread.ofPlatform().start(() -> result[0] = 42);` to `Thread worker =
    // Thread.ofPlatform().start(() -> result[1] = 42);`. Before running it with `java -ea Main`,
    // predict which assertion fails and which value it now sees; then run it and restore the
    // original line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on `result[0]
    // == 42`. Restoring the original line brings back the worked observation: worker terminated;
    // result 42.

    // Exercise 2: Publish initial state through start: debug a regression
    // A regression changed one token in the code that Example B adds after Example A, so one
    // line now reads `int[] input = { 8 };`. Run Example B with that line, use the failing
    // assertion to locate the defect and repair it without changing the assertion.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `observed.get() == 7`; after it the line reads `int[] input = { 7 };` again and worker
    // observes 7.

    // Exercise 3: Force a lost update
    // Make two workers read counter 0, wait at a barrier, then each write its saved value plus
    // 1.
    // Expected: final counter 1 despite two increments.

    // Exercise 4: Use a volatile publication flag
    // Write data 99 before setting a volatile ready flag; read after observing that flag.
    // Expected: reader sees 99 and finishes within the bound.

    // Exercise 5: Distinguish run from start
    // Invoke a Runnable directly and compare its thread identity with the caller.
    // Expected: same thread identity for direct run.

    // Exercise 6: Respond to interruption
    // Interrupt a worker waiting on a latch, restore its flag in the catch, and verify
    // termination.
    // Expected: interruption observed and worker terminated.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
