// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Publish a result through join: change one input
    // Change `Thread worker = Thread.ofPlatform().start(() -> result[0] = 42);` to `Thread
    // worker = Thread.ofPlatform().start(() -> result[1] = 42);` in Example A and predict which
    // assertion fails and why.
    // Expected: The edited run fails with an `AssertionError` from the assertion on `result[0]
    // == 42`.

    // Exercise 2: Publish initial state through start: debug a regression
    // A regression in Example B's new code makes one line read `int[] input = { 8 };`. Repair it
    // using the failing assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on
    // `observed.get() == 7`; the repaired line reads `int[] input = { 7 };`.

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
