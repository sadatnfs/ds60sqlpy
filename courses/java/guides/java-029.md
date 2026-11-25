# java-029: JDBC and transactions

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-028`

## Learning objectives

Use JDBC prepared statements and transactions against H2, binding untrusted values and rolling back failures.

The six exercises practice these steps:

- Verify a real local database.
- Bind an injection-shaped value as data.
- Roll back a transfer.
- Commit and read from a second session.
- Handle a constraint failure and rollback.
- Observe committed visibility under the declared isolation.

## Purpose and mental model

JDBC is Java's database-access API. A Connection represents a database session, PreparedStatement separates SQL structure from bound values, and ResultSet exposes rows returned by a query. A connection normally starts in auto-commit mode, where each completed statement is committed independently. A multi-statement business operation needs an explicit transaction when its changes must succeed or fail together. Commit makes the transaction durable under the database contract; rollback discards its uncommitted changes.

This lesson uses a real embedded H2 database in memory through the prepared H2 JDBC driver. Every exercise creates its own named in-memory database and closes all connections. It does not connect to PostgreSQL, Oracle, a shared service ora file-backed database. The tiny account table has a nonnegative-balance constraint. Actual prepared queries, commit, rollback, constraint failure and READ_COMMITTED visibility are tested. H2 behavior on this fixture is not presented as universal behavior of every database engine.

## Vocabulary and concepts

**Connection:** A database session carrying transaction and statement state.

**Prepared statement:** SQL structure with separately bound parameter values.

**Transaction:** A group of changes committed or rolled back as one declared unit.

**Isolation:** Rules governing which concurrent transaction changes are visible.

## How to run this lesson

`database()` opens a fresh in-memory H2 database with a unique name, creates the accounts table with a `CHECK(balance>=0)` constraint, and inserts Alice with 100 and Bob with 50; the H2 driver JAR must be on the classpath.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).

## Required prepared JDBC dependency

The classroom Java 21 image includes the pinned H2 driver at `/opt/course-libs/h2-2.5.252.jar` and adds it to the fixed runtime classpath. This lesson needs that real driver; it does not simulate JDBC when the driver is missing. The database URL is always an owned `jdbc:h2:mem:` fixture. No external database setup or reset is performed.

For an already prepared native JDK and H2 JAR, compile with `javac --release 21 Main.java`. Run on POSIX with `java -ea -cp ".:/path/to/h2-2.5.252.jar" Main`; on Windows use the classpath separator semicolon: `java -ea -cp ".;C:\course-libs\h2-2.5.252.jar" Main`. Substitute the actual prepared JAR path. Do not download or install a driver from inside the lesson.


## Syntax anatomy and execution trace

DriverManager.getConnection selects a loaded driver for the jdbc:h2:mem URL. Bind values with setInt or setString rather than concatenating them into SQL. Use setAutoCommit(false), commit and rollback for transaction control. Close ResultSet, PreparedStatement and Connection with try-with-resources. Check executeUpdate row counts so an unknown account is not silently treated as a successful transfer. Setup DDL occurs before the tested transactions because DDL transaction behavior is engine-specific.

## Worked example / walkthrough

### Example A: Verify a real local database

Metadata and query execution establish actualJDBCbehavior. A map pretending to be a database would not exercise driver loading, SQL parsing or transaction state.

```java
import java.util.*;

public class Main {

  static final java.util.concurrent.atomic.AtomicInteger DATABASE_IDS =
    new java.util.concurrent.atomic.AtomicInteger();

  static java.sql.Connection database() throws java.sql.SQLException {
    java.sql.Connection connection;
    try {
      connection = java.sql.DriverManager.getConnection(
        "jdbc:h2:mem:ds60_java29_" + DATABASE_IDS.incrementAndGet()
      );
    } catch (java.sql.SQLException error) {
      throw new java.sql.SQLException(
        "Prepared H2 2.5.252 JDBC driver required on the classpath",
        error
      );
    }
    try (var statement = connection.createStatement()) {
      statement.execute(
        "CREATE TABLE accounts(id INTEGER PRIMARY KEY,name VARCHAR(40) NOT NULL,balance INTEGER NOT NULL CHECK(balance>=0))"
      );
      statement.executeUpdate("INSERT INTO accounts VALUES(1,'Alice',100),(2,'Bob',50)");
    } catch (java.sql.SQLException error) {
      connection.close();
      throw error;
    }
    return connection;
  }

  static int balance(java.sql.Connection connection, int id) throws java.sql.SQLException {
    try (var statement = connection.prepareStatement("SELECT balance FROM accounts WHERE id=?")) {
      statement.setInt(1, id);
      try (var rows = statement.executeQuery()) {
        if (!rows.next()) throw new java.sql.SQLException("unknown account");
        return rows.getInt(1);
      }
    }
  }

  static void change(java.sql.Connection connection, int id, int delta)
    throws java.sql.SQLException {
    try (
      var statement = connection.prepareStatement(
        "UPDATE accounts SET balance=balance+? WHERE id=?"
      )
    ) {
      statement.setInt(1, delta);
      statement.setInt(2, id);
      if (statement.executeUpdate() != 1) throw new java.sql.SQLException(
        "expected one account update"
      );
    }
  }

  public static void main(String[] args) throws Exception {
    try (java.sql.Connection connection = database()) {
      assert connection.getMetaData().getDatabaseProductName().equals("H2") &&
      connection.getAutoCommit();
      try (
        var statement = connection.prepareStatement("SELECT COUNT(*) FROM accounts");
        var rows = statement.executeQuery()
      ) {
        boolean hasRow = rows.next();
        assert hasRow && rows.getInt(1) == 2;
      }
    }
  }
}
```

**Expected:** database product H2; 2 rows; auto-commit initially true.

### Example B: Bind an injection-shaped value as data

The driver receives the value separately from the query structure. The test uses a valid normal lookup as well as the adversarial-looking value so blanket rejection is not mistaken for correct binding.

```java
import java.util.*;

public class Main {

  static final java.util.concurrent.atomic.AtomicInteger DATABASE_IDS =
    new java.util.concurrent.atomic.AtomicInteger();

  static java.sql.Connection database() throws java.sql.SQLException {
    java.sql.Connection connection;
    try {
      connection = java.sql.DriverManager.getConnection(
        "jdbc:h2:mem:ds60_java29_" + DATABASE_IDS.incrementAndGet()
      );
    } catch (java.sql.SQLException error) {
      throw new java.sql.SQLException(
        "Prepared H2 2.5.252 JDBC driver required on the classpath",
        error
      );
    }
    try (var statement = connection.createStatement()) {
      statement.execute(
        "CREATE TABLE accounts(id INTEGER PRIMARY KEY,name VARCHAR(40) NOT NULL,balance INTEGER NOT NULL CHECK(balance>=0))"
      );
      statement.executeUpdate("INSERT INTO accounts VALUES(1,'Alice',100),(2,'Bob',50)");
    } catch (java.sql.SQLException error) {
      connection.close();
      throw error;
    }
    return connection;
  }

  static int balance(java.sql.Connection connection, int id) throws java.sql.SQLException {
    try (var statement = connection.prepareStatement("SELECT balance FROM accounts WHERE id=?")) {
      statement.setInt(1, id);
      try (var rows = statement.executeQuery()) {
        if (!rows.next()) throw new java.sql.SQLException("unknown account");
        return rows.getInt(1);
      }
    }
  }

  static void change(java.sql.Connection connection, int id, int delta)
    throws java.sql.SQLException {
    try (
      var statement = connection.prepareStatement(
        "UPDATE accounts SET balance=balance+? WHERE id=?"
      )
    ) {
      statement.setInt(1, delta);
      statement.setInt(2, id);
      if (statement.executeUpdate() != 1) throw new java.sql.SQLException(
        "expected one account update"
      );
    }
  }

  public static void main(String[] args) throws Exception {
    try (java.sql.Connection connection = database()) {
      assert connection.getMetaData().getDatabaseProductName().equals("H2") &&
      connection.getAutoCommit();
      try (
        var statement = connection.prepareStatement("SELECT COUNT(*) FROM accounts");
        var rows = statement.executeQuery()
      ) {
        boolean hasRow = rows.next();
        assert hasRow && rows.getInt(1) == 2;
      }
    }

    try (
      java.sql.Connection connection = database();
      var statement = connection.prepareStatement("SELECT COUNT(*) FROM accounts WHERE name = ?")
    ) {
      statement.setString(1, "Alice");
      try (var rows = statement.executeQuery()) {
        boolean hasRow = rows.next();
        assert hasRow && rows.getInt(1) == 1;
      }
      statement.setString(1, "Alice' OR '1'='1");
      try (var rows = statement.executeQuery()) {
        boolean hasRow = rows.next();
        assert hasRow && rows.getInt(1) == 0;
      }
    }
  }
}
```

**Expected:** Alice matches 1 row; the injection-shaped value matches 0.

## Prediction before your attempt

Before running Example A, decide what `getDatabaseProductName()` returns and whether a new connection starts with auto-commit on. For Example B, predict the row count for the name Alice and for `Alice' OR '1'='1` bound through the same `?` parameter. Before Exercise 3, write both balances after moving 20 from account 1 to 2 inside a transaction, and again after `rollback()`.

## Exercises

1. **Verify a real local database: predict an edited check.** Change Example A's assertion to `assert connection.getMetaData().getDatabaseProductName().equals("H3") &&`, predict whether it holds, then run and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `connection.getMetaData().getDatabaseProductName().equals("H2") && connection.getAutoCommit()`.
   **Verify:** Explain why the edited assertion is false for the values that satisfy `connection.getMetaData().getDatabaseProductName().equals("H2") && connection.getAutoCommit()`.

2. **Bind an injection-shaped value as data: debug a regression.** A regression in Example B's new code makes one line read `statement.setString(1, "Alice!");`. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `hasRow && rows.getInt(1) == 1`; the repaired line reads `statement.setString(1, "Alice");`.
   **Verify:** Explain how the changed token alters the value that `hasRow && rows.getInt(1) == 1` tests.

3. **Roll back a transfer.** Disable auto-commit, move 20 cents from account 1 to 2, inspect intermediate balances, and rollback.
   **Expected:** inside 80, 70; after rollback 100, 50.
   **Verify:** Control: changing `assert balance(connection, 1) == 100 && balance(connection, 2) == 50;` to `assert balance(connection, 2) == 100 && balance(connection, 2) == 50;` inside the assertion must make it fail.

4. **Commit and read from a second session.** Transfer 10 cents, commit, and open another connection to the same owned memory database.
   **Expected:** second connection sees 90, 60 and total 150.
   **Verify:** Control: changing `balance(second, 1) + balance(second, 2) == 150;` to `balance(second, 1) - balance(second, 2) == 150;` inside the assertion must make it fail.

5. **Handle a constraint failure and rollback.** Attempt to subtract 200 from balance 100, catch the SQL integrity error, and rollback.
   **Expected:** SQLState class 23; balance remains 100 after rollback.
   **Verify:** Control: changing `constraint = expected.getSQLState() != null && expected.getSQLState().startsWith("23");` to `constraint = expected.getSQLState() == null && expected.getSQLState().startsWith("23");` must fail the assertion on `constraint && balance(connection, 1) == 100`.

6. **Observe committed visibility under the declared isolation.** Use two H2 connections at READ_COMMITTED; update account 1 without commit, read from the other, then commit and read again.
   **Expected:** second session sees 100 before commit and 95 after commit.
   **Verify:** Control: changing `change(first, 1, -5);` to `change(first, 2, -5);` must fail the assertion on `balance(second, 1) == 95`.

## Common pitfalls and diagnosis

Building SQL by concatenating user text lets a quote change the query's structure; a bound parameter is always data. Leaving auto-commit on makes each statement of a transfer commit separately, so a failure between them leaves money missing. After a `SQLException` inside a transaction, roll back before reusing the connection. Forgetting to close `ResultSet`, `PreparedStatement` and `Connection` leaks database resources. And isolation behavior varies by engine, so a result observed in H2 is not a promise about every database.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the in-check edit compares the product name with "H3". Then recall that the H2 driver reports "H2". Finally, explain why the connection and query worked and only the metadata comparison fails.
- **Exercise 2:** First note that the edit binds "Alice!" instead of "Alice". Then count the rows whose name equals that exact text. Finally, compare 0 with the expected 1 and explain why binding treated the extra character as data.
- **Exercise 3:** First call `setAutoCommit(false)` and apply both balance changes with `change`. Then read the balances on the same connection and assert 80 and 70. Finally, call `rollback()` and assert that the original 100 and 50 are back.
- **Exercise 4:** First transfer 10 from account 1 to account 2 with auto-commit off and call `commit()`. Then open a second connection with the first connection's URL. Finally, assert 90, 60 and a total of 150 from the second session.
- **Exercise 5:** First subtract 200 from account 1 inside a transaction and catch the `SQLException`. Then check that `getSQLState()` starts with "23" and call `rollback()`. Finally, assert that the balance is still 100 and name the constraint that refused the update.
- **Exercise 6:** First set both connections to `TRANSACTION_READ_COMMITTED` and turn auto-commit off on the first. Then subtract 5 on the first and read account 1 from the second before and after `commit()`. Finally, assert 100 and then 95.

## Self-check and retrieval

Without notes, explain how a prepared statement keeps `Alice' OR '1'='1` from matching every row, why a transfer needs auto-commit off, what SQLState class 23 means, and what the second connection sees before and after the first commits under `READ_COMMITTED`.

## Next step

Continue with `java-030`: Serialization and schema evolution. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.sql/java/sql/Connection.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-029: JDBC and transactions.
Read courses/java/guides/java-029.md and courses/java/lessons/java-029.java. Direct prerequisites: `java-028`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
