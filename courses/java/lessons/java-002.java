// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Compare integer and decimal division: change one input
    // Change `int whole = 7 / 2;` to `int whole = 8 / 2;` in Example A and predict which
    // assertion fails and why.
    // Expected: The edited run fails with an `AssertionError` from the assertion on `whole == 3
    // && fractional == 3.5`.

    // Exercise 2: Widen before multiplication: debug a regression
    // A regression in Example B's new code makes one line read `long safe = (long) 50_000 +
    // 50_000;`. Repair it using the failing assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on `safe ==
    // 2_500_000_000L`; the repaired line reads `long safe = (long) 50_000 * 50_000;`.

    // Exercise 3: Detect overflow explicitly
    // Add 1 to Integer.MAX_VALUE with Math.addExact.
    // Expected: ArithmeticException.

    // Exercise 4: Preserve decimal source meaning
    // Add BigDecimal values constructed from strings 0.10 and 0.20.
    // Expected: exact decimal 0.30.

    // Exercise 5: Distinguish value from scale
    // Compare BigDecimal 1.0 and 1.00 with compareTo and equals.
    // Expected: compareTo 0; equals false.

    // Exercise 6: Reject an unsupported exact division
    // Divide decimal 1 by 3 without a rounding policy, then supply scale 2 and HALF_UP.
    // Expected: exact division throws; rounded result 0.33.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
