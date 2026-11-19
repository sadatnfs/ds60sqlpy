// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Expose a strong retention path: change one input
    // Copy Example A into a scratch `Main.java` and change `byte[] payload = new byte[1024];` to
    // `byte[] payload = new byte[1025];`. Before running it with `java -ea Main`, predict which
    // assertion fails and which value it now sees; then run it and restore the original line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `retained.get(0)[0] == 7 && retained.get(0).length == 1024`. Restoring the original line
    // brings back the worked observation: list still exposes the same array contents.

    // Exercise 2: Remove one ownership path deliberately: diagnose an edited check
    // A careless edit changed the assertion that Example B adds after Example A so that it reads
    // `assert retained.isEmpty() && separate[1] == 7;`. Run Example B with that line, explain
    // why the edited assertion now fails for the same program state, and restore it.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `retained.isEmpty() && separate[0] == 7`; after it the line reads `assert
    // retained.isEmpty() && separate[0] == 7;` again and list empty; separate array still valid.

    // Exercise 3: Inspect a weak reference without timing assumptions
    // Create a WeakReference to the still-strongly-referenced array.
    // Expected: weak get returns the same object while strong reference exists.

    // Exercise 4: Separate value size from allocation count
    // Create ten arrays of 128 bytes and count logical payload bytes.
    // Expected: 1280 logical bytes; no exact heap-overhead claim.

    // Exercise 5: Reuse a bounded working buffer
    // Fill one array repeatedly rather than retaining every intermediate array.
    // Expected: same buffer identity; final value 9.

    // Exercise 6: Record process memory cautiously
    // Read Runtime total/free/max memory and check only valid ordering relationships.
    // Expected: nonnegative counters; max at least total; no claim of exact object size.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
