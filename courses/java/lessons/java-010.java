// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Call through an interface: change one input
    // Change `return amount / 2;` to `return amount / 3;` in Example A and predict which
    // assertion fails and why.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `regular.price(100) == 100 && half.price(100) == 50`.

    // Exercise 2: Compose a fee policy: debug a regression
    // A regression in Example B's new code makes one line read `Pricing withFee = new Fee(half,
    // 11);`. Repair it using the failing assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on
    // `withFee.price(100) == 60`; the repaired line reads `Pricing withFee = new Fee(half,
    // 10);`.

    // Exercise 3: Switch exhaustively over a sealed type
    // Price 200 cents with NoDiscount, Percent(25) and Fixed(250) through one pattern-matching
    // switch over the sealed Discount interface.
    // Expected: 200, 150 and 0.

    // Exercise 4: Validate every implementation
    // Call regular, half and fee policy with -1.
    // Expected: all throw IllegalArgumentException.

    // Exercise 5: Change a collaborator without changing caller code
    // Iterate over the three policies and collect prices for 100.
    // Expected: results 100, 50, 60.

    // Exercise 6: Reject an invalid wrapper
    // Construct a fee wrapper with a negative fee or null delegate.
    // Expected: negative fee IllegalArgumentException; null delegate NullPointerException.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
