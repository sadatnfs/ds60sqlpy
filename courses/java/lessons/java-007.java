// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Create independent accounts
    // Construct accounts with 100 and 100 cents,deposit 50 into the first.
    // Expected: balances 150 and 100.

    // Exercise 2: Withdraw within the contract
    // Withdraw40 cents from the first account.
    // Expected: balance110.

    // Exercise 3: Reject overdraft atomically
    // Attempt to withdraw111 from balance110.
    // Expected: IllegalArgumentException;balance still110.

    // Exercise 4: Reject negative input
    // Attempt a deposit of-1.
    // Expected: IllegalArgumentException;balance unchanged.

    // Exercise 5: Reject invalid construction
    // Construct an account with-1 cents.
    // Expected: constructor throwsIllegalArgumentException.

    // Exercise 6: Protect against overflow
    // Create an account atInteger.MAX_VALUE and deposit1.
    // Expected: ArithmeticException;original maximum balance preserved.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
