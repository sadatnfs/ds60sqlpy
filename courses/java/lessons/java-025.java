// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Expose a strong retention path
    // Store a small byte array in a list and drop the local variable reference.
    // Expected: list still exposes the same array contents.

    // Exercise 2: Remove one ownership path deliberately
    // Keep a separate reference,clear the list,and inspect the separate reference.
    // Expected: list empty;separate array still valid.

    // Exercise 3: Inspect a weak reference without timing assumptions
    // Create a WeakReference to the still-strongly-referenced array.
    // Expected: weakget returns the same object while strong reference exists.

    // Exercise 4: Separate value size from allocation count
    // Create ten arrays of 128 bytes and count logical payload bytes.
    // Expected: 1280 logical bytes;no exact heap-overhead claim.

    // Exercise 5: Reuse a bounded working buffer
    // Fill one array repeatedly rather than retaining every intermediate array.
    // Expected: same buffer identity;final value9.

    // Exercise 6: Record process memory cautiously
    // ReadRuntime total/free/max memory and check only valid ordering relationships.
    // Expected: nonnegative counters; max at least total; no claim of exact object size.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
