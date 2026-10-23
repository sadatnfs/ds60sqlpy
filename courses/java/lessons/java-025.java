// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {
    public static void main(String[] args) throws Exception {
        // Exercise 1: Expose a strong retention path
        // Store a small byte array in a list anddrop the local variable reference.
        // Expected: list still exposes the same array contents.

        // Exercise 2: Remove one ownership path deliberately
        // Keep a separate reference,clear the list,andinspect the separate reference.
        // Expected: list empty;separate array stillvalid.

        // Exercise 3: Inspect a weak reference without timing assumptions
        // Create aWeakReference to the still-strongly-referenced array.
        // Expected: weakget returns the same object while strong reference exists.

        // Exercise 4: Separate value size from allocation count
        // Create ten arrays of128bytes andcount logical payload bytes.
        // Expected: 1280 logical bytes;no exact heap-overhead claim.

        // Exercise 5: Reuse a bounded working buffer
        // Fill one array repeatedly rather than retaining every intermediate array.
        // Expected: same buffer identity;final value9.

        // Exercise 6: Record process memory cautiously
        // ReadRuntime total/free/max memory andcheck only valid ordering relationships.
        // Expected: nonnegative counters;max at leasttotal;no claim of exact object size.
        System.out.println("Implement and check the six exercises in your saved copy.");
    }
}
