// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Call through an interface: change one input
    // Copy Example A into a scratch `Main.java` and change `return amount / 2;` to `return
    // amount / 3;`. Before running it with `java -ea Main`, predict which assertion fails and
    // which value it now sees; then run it and restore the original line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `regular.price(100) == 100 && half.price(100) == 50`. Restoring the original line brings
    // back the worked observation: 100 and 50.

    // Exercise 2: Compose a fee policy: debug a regression
    // A regression changed one token in the code that Example B adds after Example A, so one
    // line now reads `Pricing withFee = new Fee(half, 11);`. Run Example B with that line, use
    // the failing assertion to locate the defect and repair it without changing the assertion.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `withFee.price(100) == 60`; after it the line reads `Pricing withFee = new Fee(half, 10);`
    // again and price 100 becomes 60.

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
