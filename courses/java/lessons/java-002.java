// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {
    public static void main(String[] args) throws Exception {
        // Exercise 1: Compare integer and decimal division
        // Calculate7/2 and7/2.0.
        // Expected: integer3 and double3.5.

        // Exercise 2: Widen before multiplication
        // Compute50000 squared with an explicitly widened left operand.
        // Expected: 2500000000L;int product differs.

        // Exercise 3: Detect overflow explicitly
        // Add1 to Integer.MAX_VALUE withMath.addExact.
        // Expected: ArithmeticException.

        // Exercise 4: Preserve decimal source meaning
        // Add BigDecimal values constructed from strings0.10 and0.20.
        // Expected: exact decimal0.30.

        // Exercise 5: Distinguish value from scale
        // Compare BigDecimal1.0 and1.00 withcompareTo andequals.
        // Expected: compareTo0;equalsfalse.

        // Exercise 6: Reject an unsupported exact division
        // Divide decimal1 by3 without a rounding policy, then supply scale2 andHALF_UP.
        // Expected: exact division throws;rounded result0.33.
        System.out.println("Implement and check the six exercises in your saved copy.");
    }
}
