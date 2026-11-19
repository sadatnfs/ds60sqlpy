// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Create independent accounts: change one input
    // Copy Example A into a scratch `Main.java` and change `Account first = new Account(100);`
    // to `Account first = new Account(101);`. Before running it with `java -ea Main`, predict
    // which assertion fails and which value it now sees; then run it and restore the original
    // line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `first.balance() == 150 && second.balance() == 100`. Restoring the original line brings
    // back the worked observation: balances 150 and 100.

    // Exercise 2: Withdraw within the contract: debug a regression
    // A regression changed one token in the code that Example B adds after Example A, so one
    // line now reads `first.withdraw(41);`. Run Example B with that line, use the failing
    // assertion to locate the defect and repair it without changing the assertion.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `first.balance() == 110`; after it the line reads `first.withdraw(40);` again and balance
    // 110.

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
