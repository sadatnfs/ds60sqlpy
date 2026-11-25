// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Create independent accounts: change one input
    // Change `Account first = new Account(100);` to `Account first = new Account(101);` in
    // Example A and predict which assertion fails and why.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `first.balance() == 150 && second.balance() == 100`.

    // Exercise 2: Withdraw within the contract: debug a regression
    // A regression in Example B's new code makes one line read `first.withdraw(41);`. Repair it
    // using the failing assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on
    // `first.balance() == 110`; the repaired line reads `first.withdraw(40);`.

    // Exercise 3: Reject overdraft atomically
    // Attempt to withdraw 111 from balance 110.
    // Expected: IllegalArgumentException; balance still 110.

    // Exercise 4: Reject negative input
    // Attempt a deposit of -1.
    // Expected: IllegalArgumentException; balance unchanged.

    // Exercise 5: Reject invalid construction
    // Construct an account with -1 cents.
    // Expected: constructor throws IllegalArgumentException.

    // Exercise 6: Protect against overflow
    // Create an account at Integer.MAX_VALUE and deposit 1.
    // Expected: ArithmeticException; original maximum balance preserved.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
