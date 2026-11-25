// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Verify a real local database: predict an edited check
    // Change Example A's assertion to `assert
    // connection.getMetaData().getDatabaseProductName().equals("H3") &&`, predict whether it
    // holds, then run and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `connection.getMetaData().getDatabaseProductName().equals("H2") &&
    // connection.getAutoCommit()`.

    // Exercise 2: Bind an injection-shaped value as data: debug a regression
    // A regression in Example B's new code makes one line read `statement.setString(1,
    // "Alice!");`. Repair it using the failing assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on `hasRow
    // && rows.getInt(1) == 1`; the repaired line reads `statement.setString(1, "Alice");`.

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
