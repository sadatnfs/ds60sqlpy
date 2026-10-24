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
    // Exercise 1: Verify a real local database
    try (java.sql.Connection connection = database()) {
      assert connection.getMetaData().getDatabaseProductName().equals("H2") &&
      connection.getAutoCommit();
      try (
        var statement = connection.prepareStatement("SELECT COUNT(*) FROM accounts");
        var rows = statement.executeQuery()
      ) {
        assert rows.next() && rows.getInt(1) == 2;
      }
    }

    // Exercise 2: Bind an injection-shaped value as data
    try (
      java.sql.Connection connection = database();
      var statement = connection.prepareStatement("SELECT COUNT(*) FROM accounts WHERE name = ?")
    ) {
      statement.setString(1, "Alice");
      try (var rows = statement.executeQuery()) {
        assert rows.next() && rows.getInt(1) == 1;
      }
      statement.setString(1, "Alice' OR '1'='1");
      try (var rows = statement.executeQuery()) {
        assert rows.next() && rows.getInt(1) == 0;
      }
    }

    // Exercise 3: Roll back a transfer
    try (java.sql.Connection connection = database()) {
      connection.setAutoCommit(false);
      change(connection, 1, -20);
      change(connection, 2, 20);
      assert balance(connection, 1) == 80 && balance(connection, 2) == 70;
      connection.rollback();
      assert balance(connection, 1) == 100 && balance(connection, 2) == 50;
    }

    // Exercise 4: Commit andread from a second session
    try (java.sql.Connection connection = database()) {
      connection.setAutoCommit(false);
      change(connection, 1, -10);
      change(connection, 2, 10);
      connection.commit();
      try (var second = java.sql.DriverManager.getConnection(connection.getMetaData().getURL())) {
        assert balance(second, 1) == 90 &&
        balance(second, 2) == 60 &&
        balance(second, 1) + balance(second, 2) == 150;
      }
    }

    // Exercise 5: Handle a constraint failure androllback
    try (java.sql.Connection connection = database()) {
      connection.setAutoCommit(false);
      boolean constraint = false;
      try {
        change(connection, 1, -200);
      } catch (java.sql.SQLException expected) {
        constraint = expected.getSQLState() != null && expected.getSQLState().startsWith("23");
        connection.rollback();
      }
      assert constraint && balance(connection, 1) == 100;
    }

    // Exercise 6: Observe committed visibility under the declared isolation
    try (
      java.sql.Connection first = database();
      var second = java.sql.DriverManager.getConnection(first.getMetaData().getURL())
    ) {
      first.setTransactionIsolation(java.sql.Connection.TRANSACTION_READ_COMMITTED);
      second.setTransactionIsolation(java.sql.Connection.TRANSACTION_READ_COMMITTED);
      first.setAutoCommit(false);
      change(first, 1, -5);
      assert balance(second, 1) == 100;
      first.commit();
      assert balance(second, 1) == 95;
    }
  }
}
