// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Publish a result through join
    // Start a worker that writes 42 into a shared holder, join it with a bound, and inspect the
    // result.
    // Expected: worker terminated; result 42.

    // Exercise 2: Publish initial state through start
    // Assign7 before starting a worker that reads the holder.
    // Expected: worker observes7.

    // Exercise 3: Force a lost update
    // Make two workers read counter0,wait at a barrier,then each write its saved value plus1.
    // Expected: final counter1 despite two increments.

    // Exercise 4: Use a volatile publication flag
    // Write data99 before setting a volatile ready flag;read after observing that flag.
    // Expected: reader sees99 and finishes within the bound.

    // Exercise 5: Distinguish run from start
    // Invoke a Runnable directly and compare its thread identity with the caller.
    // Expected: same thread identity for directrun.

    // Exercise 6: Respond to interruption
    // Interrupt a worker waiting on a latch,restore its flag in the catch,and verify
    // termination.
    // Expected: interruption observed and worker terminated.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
