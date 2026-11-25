// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Close on normal completion: change one input
    // Change `try (Probe resource = new Probe("A", events, false)) {` to `try (Probe resource =
    // new Probe("A!", events, false)) {` in Example A and predict which assertion fails and why.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `events.equals(List.of("body", "closeA"))`.

    // Exercise 2: Close in reverse order: debug a regression
    // A regression in Example B's new code makes one line read `try (Probe a = new Probe("A!",
    // events, false); Probe b = new Probe("B", events, false)) {`. Repair it using the failing
    // assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on
    // `events.equals(List.of("body", "closeB", "closeA"))`; the repaired line reads `try (Probe
    // a = new Probe("A", events, false); Probe b = new Probe("B", events, false)) {`.

    // Exercise 3: Close after body failure
    // Throw IllegalStateException in the body and inspect events after catching it.
    // Expected: `closeA` is still recorded.

    // Exercise 4: Preserve suppressed close failure
    // Make the body throw and the resource close throw too.
    // Expected: primary message `body`; one suppressed exception `closeA`.

    // Exercise 5: Observe close-only failure
    // Let the body succeed but close throw IOException.
    // Expected: IOException `closeA` is primary.

    // Exercise 6: Retain a translated cause
    // Wrap an IOException in IllegalStateException with a domain message and inspect cause.
    // Expected: cause remains the original IOException.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
