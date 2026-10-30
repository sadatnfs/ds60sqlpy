// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Call through an interface
    // Use Pricing references to identity and half-price implementations on 100 cents.
    // Expected: 100 and 50.

    // Exercise 2: Compose a fee policy
    // Wrap the half-price policy with a10-cent fee.
    // Expected: price100 becomes60.

    // Exercise 3: Inspect rounding semantics
    // Apply integer half-price to101 cents under truncation-toward-zero.
    // Expected: 50 cents before fee.

    // Exercise 4: Validate every implementation
    // Call regular,half and fee policy with-1.
    // Expected: all throwIllegalArgumentException.

    // Exercise 5: Change a collaborator without changing caller code
    // Iterate over the three policies and collect prices for100.
    // Expected: results100,50,60.

    // Exercise 6: Reject an invalid wrapper
    // Construct a fee wrapper with a negative fee or null delegate.
    // Expected: negative fee IllegalArgumentException;null delegate NullPointerException.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
