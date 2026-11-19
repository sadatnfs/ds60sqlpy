// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Verify a real local database: predict an edited check
    // Copy Example A into a scratch `Main.java` and change `assert
    // connection.getMetaData().getDatabaseProductName().equals("H2") &&` to `assert
    // connection.getMetaData().getDatabaseProductName().equals("H3") &&` inside its assertion.
    // Before running it with `java -ea Main`, predict whether the assertion still holds and
    // explain why; then restore it.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `connection.getMetaData().getDatabaseProductName().equals("H2") &&
    // connection.getAutoCommit()`. Restoring the original line brings back the worked
    // observation: database product H2; 2 rows; auto-commit initially true.

    // Exercise 2: Bind an injection-shaped value as data: debug a regression
    // A regression changed one token in the code that Example B adds after Example A, so one
    // line now reads `statement.setString(1, "Alice!");`. Run Example B with that line, use the
    // failing assertion to locate the defect and repair it without changing the assertion.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `hasRow && rows.getInt(1) == 1`; after it the line reads `statement.setString(1,
    // "Alice");` again and alice matches 1 row; the injection-shaped value matches 0.

    // Exercise 3: Roll back a transfer
    // Disable auto-commit, move 20 cents from account 1 to 2, inspect intermediate balances, and
    // rollback.
    // Expected: inside 80, 70; after rollback 100, 50.

    // Exercise 4: Commit and read from a second session
    // Transfer 10 cents, commit, and open another connection to the same owned memory database.
    // Expected: second connection sees 90, 60 and total 150.

    // Exercise 5: Handle a constraint failure and rollback
    // Attempt to subtract 200 from balance 100, catch the SQL integrity error, and rollback.
    // Expected: SQLState class 23; balance remains 100 after rollback.

    // Exercise 6: Observe committed visibility under the declared isolation
    // Use two H2 connections at READ_COMMITTED; update account 1 without commit, read from the
    // other, then commit and read again.
    // Expected: second session sees 100 before commit and 95 after commit.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
