# java-029: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

JDBC is Java's database-access API. A Connection represents a database session,PreparedStatement separates SQL structure from bound values,and ResultSet exposes rows returned by a query. A connection normally starts in auto-commit mode,where each completed statement is committed independently. A multi-statement business operation needs an explicit transaction when its changes must succeed or fail together. Commit makes the transaction durable under the database contract;rollback discards its uncommitted changes.

This lesson uses a real embedded H2 database in memory through the preparedH2JDBCdriver. Every exercise creates its own named in-memory database and closes all connections. It does not connect to PostgreSQL,Oracle,a shared service ora file-backed database. The tiny account table has a nonnegative-balance constraint. Actual prepared queries,commit,rollback,constraint failure andREAD_COMMITTED visibility are tested. H2 behavior on this fixture is not presented as universal behavior of every database engine.

**Connection:** A database session carrying transaction and statement state.

**Prepared statement:** SQL structure with separately bound parameter values.

**Transaction:** A group of changes committed or rolled back as one declared unit.

**Isolation:** Rules governing which concurrent transaction changes are visible.

## Reading the reference

DriverManager.getConnection selects a loaded driver for thejdbc:h2:mem URL. Bind values withsetInt orsetString rather than concatenating them into SQL. Use setAutoCommit(false),commit and rollback for transaction control. Close ResultSet,PreparedStatement and Connection withtry-with-resources. Check executeUpdate row counts so an unknown account is not silently treated as a successful transfer. SetupDDL occurs before the tested transactions becauseDDL transaction behavior is engine-specific.

## Exercise 1: Verify a real local database

Task: Open the fixture,inspect product metadata and count the two account rows.

Metadata and query execution establish actualJDBCbehavior. A map pretending to be a database would not exercise driver loading,SQL parsing or transaction state.

```java
try(java.sql.Connection connection=database()) {
    assert connection.getMetaData().getDatabaseProductName().equals("H2") && connection.getAutoCommit();
    try(var statement=connection.prepareStatement("SELECT COUNT(*) FROM accounts");var rows=statement.executeQuery()){assert rows.next() && rows.getInt(1)==2;}
}
```

**Expected:** database product H2; 2 rows; auto-commit initially true.

**Verify:** Compare the program values or named exception with database product H2; 2 rows; auto-commit initially true. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Bind an injection-shaped value as data

Task: Query byname usingAlice andthenAlicequoteOR1=1-shaped text through the same prepared statement.

The driver receives the value separately from the query structure. The test uses a valid normal lookup as well as the adversarial-looking value so blanket rejection is not mistaken for correct binding.

```java
try(java.sql.Connection connection=database();var statement=connection.prepareStatement("SELECT COUNT(*) FROM accounts WHERE name = ?")) {
    statement.setString(1,"Alice");try(var rows=statement.executeQuery()){assert rows.next() && rows.getInt(1)==1;}
    statement.setString(1,"Alice' OR '1'='1");try(var rows=statement.executeQuery()){assert rows.next() && rows.getInt(1)==0;}
}
```

**Expected:** Alice matches 1 row;the injection-shaped value matches0.

**Verify:** Compare the program values or named exception with Alice matches 1 row;the injection-shaped value matches0. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Roll back a transfer

Task: Disableauto-commit,move20cents fromaccount1to2,inspect intermediate balances,and rollback.

Both changes belong to the same transaction. The intermediate state is visible to its own connection,but rollback restores the original fixture.

```java
try(java.sql.Connection connection=database()) {
    connection.setAutoCommit(false);change(connection,1,-20);change(connection,2,20);
    assert balance(connection,1)==80 && balance(connection,2)==70;connection.rollback();
    assert balance(connection,1)==100 && balance(connection,2)==50;
}
```

**Expected:** inside80,70;afterrollback100,50.

**Verify:** Compare the program values or named exception with inside80,70;afterrollback100,50. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Commit and read from a second session

Task: Transfer10cents,commit,and open another connection to the same owned memory database.

The first connection remains open while the second reads,keeping this in-memory database alive. No global database name or ambient connection profile is used.

```java
try(java.sql.Connection connection=database()) {
    connection.setAutoCommit(false);change(connection,1,-10);change(connection,2,10);connection.commit();
    try(var second=java.sql.DriverManager.getConnection(connection.getMetaData().getURL())){assert balance(second,1)==90 && balance(second,2)==60 && balance(second,1)+balance(second,2)==150;}
}
```

**Expected:** second connection sees90,60 andtotal150.

**Verify:** Compare the program values or named exception with second connection sees90,60 andtotal150. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Handle a constraint failure and rollback

Task: Attempt tosubtract200frombalance100,catch the SQL integrity error,and rollback.

The database enforces its own invariant even if application validation is missing. The transaction must be resolved explicitly after the failure rather than reused in an unknown state.

```java
try(java.sql.Connection connection=database()) {
    connection.setAutoCommit(false);boolean constraint=false;
    try{change(connection,1,-200);}catch(java.sql.SQLException expected){constraint=expected.getSQLState()!=null && expected.getSQLState().startsWith("23");connection.rollback();}
    assert constraint && balance(connection,1)==100;
}
```

**Expected:** SQLState class23;balance remains100 after rollback.

**Verify:** Compare the program values or named exception with SQLState class23;balance remains100 after rollback. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Observe committed visibility under the declared isolation

Task: Use twoH2connections atREAD_COMMITTED;updateaccount1 without commit,read from the other,then commit and read again.

This is an actual two-session observation for the preparedH2engine. Other engines or isolation levels can have different snapshot and locking behavior,so retain the database/version context.

```java
try(java.sql.Connection first=database();var second=java.sql.DriverManager.getConnection(first.getMetaData().getURL())) {
    first.setTransactionIsolation(java.sql.Connection.TRANSACTION_READ_COMMITTED);second.setTransactionIsolation(java.sql.Connection.TRANSACTION_READ_COMMITTED);first.setAutoCommit(false);
    change(first,1,-5);assert balance(second,1)==100;first.commit();assert balance(second,1)==95;
}
```

**Expected:** second session sees 100 before commit and 95 after commit.

**Verify:** Compare the program values or named exception with second session sees 100 before commit and 95 after commit. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
