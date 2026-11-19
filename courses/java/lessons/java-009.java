// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Close on normal completion: change one input
    // Copy Example A into a scratch `Main.java` and change `try (Probe resource = new Probe("A",
    // events, false)) {` to `try (Probe resource = new Probe("A!", events, false)) {`. Before
    // running it with `java -ea Main`, predict which assertion fails and which value it now
    // sees; then run it and restore the original line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `events.equals(List.of("body", "closeA"))`. Restoring the original line brings back the
    // worked observation: events body, close A.

    // Exercise 2: Close in reverse order: debug a regression
    // A regression changed one token in the code that Example B adds after Example A, so one
    // line now reads `try (Probe a = new Probe("A!", events, false); Probe b = new Probe("B",
    // events, false)) {`. Run Example B with that line, use the failing assertion to locate the
    // defect and repair it without changing the assertion.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `events.equals(List.of("body", "closeB", "closeA"))`; after it the line reads `try (Probe
    // a = new Probe("A", events, false); Probe b = new Probe("B", events, false)) {` again and
    // closeB before closeA.

    // Exercise 3: Close after body failure
    // Throw IllegalStateException in the body and inspect events after catching it.
    // Expected: close A still recorded.

    // Exercise 4: Preserve suppressed close failure
    // Make the body throw and the resource close throw too.
    // Expected: primary message body; one suppressed exception closeA.

    // Exercise 5: Observe close-only failure
    // Let the body succeed but close throw IOException.
    // Expected: IOException closeA is primary.

    // Exercise 6: Retain a translated cause
    // Wrap an IOException in IllegalStateException with a domain message and inspect cause.
    // Expected: cause remains the original IOException.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
