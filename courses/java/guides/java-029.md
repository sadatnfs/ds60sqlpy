# java-029: JDBC and transactions

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-028`

## Learning objectives

Use JDBC prepared statements and transactions against H2, binding untrusted values and rolling back failures. Along the way, explain connection, prepared statement, transaction, isolation using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: Disable auto-commit, move 20 cents from account 1 to 2, inspect intermediate balances, and rollback. The final exercise transfers the mechanism to observe committed visibility under the declared isolation.

## Purpose and mental model

JDBC is Java's database-access API. A Connection represents a database session, PreparedStatement separates SQL structure from bound values, and ResultSet exposes rows returned by a query. A connection normally starts in auto-commit mode, where each completed statement is committed independently. A multi-statement business operation needs an explicit transaction when its changes must succeed or fail together. Commit makes the transaction durable under the database contract; rollback discards its uncommitted changes.

This lesson uses a real embedded H2 database in memory through the prepared H2 JDBC driver. Every exercise creates its own named in-memory database and closes all connections. It does not connect to PostgreSQL, Oracle, a shared service ora file-backed database. The tiny account table has a nonnegative-balance constraint. Actual prepared queries, commit, rollback, constraint failure and READ_COMMITTED visibility are tested. H2 behavior on this fixture is not presented as universal behavior of every database engine.

## Vocabulary and concepts

**Connection:** A database session carrying transaction and statement state.

**Prepared statement:** SQL structure with separately bound parameter values.

**Transaction:** A group of changes committed or rolled back as one declared unit.

**Isolation:** Rules governing which concurrent transaction changes are visible.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-029/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.

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

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Verify a real local database: predict an edited check.** Copy Example A into a scratch `Main.java` and change `assert connection.getMetaData().getDatabaseProductName().equals("H2") &&` to `assert connection.getMetaData().getDatabaseProductName().equals("H3") &&` inside its assertion. Before running it with `java -ea Main`, predict whether the assertion still holds and explain why; then restore it.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `connection.getMetaData().getDatabaseProductName().equals("H2") && connection.getAutoCommit()`. Restoring the original line brings back the worked observation: database product H2; 2 rows; auto-commit initially true.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and explain why the edited condition is false for the values that satisfy `connection.getMetaData().getDatabaseProductName().equals("H2") && connection.getAutoCommit()`. After restoring the line, the program completes without an `AssertionError` again.

2. **Bind an injection-shaped value as data: debug a regression.** A regression changed one token in the code that Example B adds after Example A, so one line now reads `statement.setString(1, "Alice!");`. Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `hasRow && rows.getInt(1) == 1`; after it the line reads `statement.setString(1, "Alice");` again and alice matches 1 row; the injection-shaped value matches 0.
   **Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `hasRow && rows.getInt(1) == 1` for this input.

3. **Roll back a transfer.** Disable auto-commit, move 20 cents from account 1 to 2, inspect intermediate balances, and rollback.
   **Expected:** inside 80, 70; after rollback 100, 50.
   **Verify:** Keep an assertion equivalent to `balance(connection, 1) == 100 && balance(connection, 2) == 50`. As a control, change `assert balance(connection, 1) == 100 && balance(connection, 2) == 50;` to `assert balance(connection, 2) == 100 && balance(connection, 2) == 50;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

4. **Commit and read from a second session.** Transfer 10 cents, commit, and open another connection to the same owned memory database.
   **Expected:** second connection sees 90, 60 and total 150.
   **Verify:** Keep an assertion equivalent to `balance(second, 1) == 90 && balance(second, 2) == 60 && balance(second, 1) + balance(second, 2) == 150`. As a control, change `balance(second, 1) + balance(second, 2) == 150;` to `balance(second, 1) - balance(second, 2) == 150;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

5. **Handle a constraint failure and rollback.** Attempt to subtract 200 from balance 100, catch the SQL integrity error, and rollback.
   **Expected:** SQLState class 23; balance remains 100 after rollback.
   **Verify:** Keep an assertion equivalent to `constraint && balance(connection, 1) == 100`. As a control, change `constraint = expected.getSQLState() != null && expected.getSQLState().startsWith("23");` to `constraint = expected.getSQLState() == null && expected.getSQLState().startsWith("23");`: the run must fail with an `AssertionError` from the assertion on `constraint && balance(connection, 1) == 100`. Restore the line before continuing.

6. **Observe committed visibility under the declared isolation.** Use two H2 connections at READ_COMMITTED; update account 1 without commit, read from the other, then commit and read again.
   **Expected:** second session sees 100 before commit and 95 after commit.
   **Verify:** Keep an assertion equivalent to `balance(second, 1) == 95`. As a control, change `change(first, 1, -5);` to `change(first, 2, -5);`: the run must fail with an `AssertionError` from the assertion on `balance(second, 1) == 95`. Restore the line before continuing.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: database product H2; 2 rows; auto-commit initially true. Then list the values read by `connection.getMetaData().getDatabaseProductName().equals("H2") && connection.getAutoCommit()` and trace each one from its declaration. Finally, compute the asserted value with `assert connection.getMetaData().getDatabaseProductName().equals("H3") &&` in place before running.
- **Exercise 2:** First restate the expected observation: alice matches 1 row; the injection-shaped value matches 0. Then list the values read by `hasRow && rows.getInt(1) == 1` and trace each one from its declaration. Finally, compare `statement.setString(1, "Alice!");` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: inside 80, 70; after rollback 100, 50. Then list the values read by `balance(connection, 1) == 100 && balance(connection, 2) == 50` and trace each one from its declaration. Finally, name one input that would make `balance(connection, 1) == 100 && balance(connection, 2) == 50` false.
- **Exercise 4:** First restate the expected observation: second connection sees 90, 60 and total 150. Then list the values read by `balance(second, 1) == 90 && balance(second, 2) == 60 && balance(second, 1) + balance(second, 2) == 150` and trace each one from its declaration. Finally, name one input that would make `balance(second, 1) == 90 && balance(second, 2) == 60 && balance(second, 1) + balance(second, 2) == 150` false.
- **Exercise 5:** First restate the expected observation: SQLState class 23; balance remains 100 after rollback. Then list the values read by `constraint && balance(connection, 1) == 100` and trace each one from its declaration. Finally, predict the effect of changing `constraint = expected.getSQLState() != null && expected.getSQLState().startsWith("23");` to `constraint = expected.getSQLState() == null && expected.getSQLState().startsWith("23");` before running anything.
- **Exercise 6:** First restate the expected observation: second session sees 100 before commit and 95 after commit. Then list the values read by `balance(second, 1) == 95` and trace each one from its declaration. Finally, predict the effect of changing `change(first, 1, -5);` to `change(first, 2, -5);` before running anything.

## Self-check and retrieval

Close the solution and explain Connection, Prepared statement, Transaction in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.sql/java/sql/Connection.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

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
