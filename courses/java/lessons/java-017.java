// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {
    public static void main(String[] args) throws Exception {
        // Exercise 1: Represent a missing lookup
        // Look up knowna andunknownb in a fixed map throughOptional.
        // Expected: a present with7;b empty.

        // Exercise 2: Transform only present values
        // Map the known value todouble and apply the same mapping toempty.
        // Expected: 14 andempty.

        // Exercise 3: Compare eager and lazy fallback
        // Use a counter-producing fallback withorElse andorElseGet on a present value.
        // Expected: orElse increments;orElseGet does not.

        // Exercise 4: Reject malformed lookup input
        // Validate an empty identifier before consulting the map.
        // Expected: IllegalArgumentException rather thanempty.

        // Exercise 5: Flatten a nullable transformation
        // Parse an optional numeric string through a helper returningOptional<Integer>.
        // Expected: valid12 present;badtext empty under this declared parser policy.

        // Exercise 6: Expose unsafeget
        // Callget onempty and catchNoSuchElementException.
        // Expected: specific absence failure.
        System.out.println("Implement and check the six exercises in your saved copy.");
    }
}
