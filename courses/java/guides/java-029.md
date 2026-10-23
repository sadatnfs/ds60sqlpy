# java-029: JDBC and transactions

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-028`

## Learning objectives

Explain connection, prepared statement, transaction, isolation using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Open the fixture,inspect product metadata andcount the two account rows. The final exercise transfers the mechanism to observe committed visibility under the declared isolation.

## Purpose and mental model

JDBC is Java's database-access API. AConnection represents a database session,PreparedStatement separates SQL structure from bound values,andResultSet exposes rows returned by a query. A connection normally starts in auto-commit mode,where each completed statement is committed independently. A multi-statement business operation needs an explicit transaction when its changes must succeed orfail together. Commit makes the transaction durable under the database contract;rollback discards its uncommitted changes.

This lesson uses a real embedded H2 database in memory through the preparedH2JDBCdriver. Every exercise creates its own named in-memory database andcloses all connections. It doesnot connect toPostgreSQL,Oracle,a shared service ora file-backed database. The tiny account table has a nonnegative-balance constraint. Actual prepared queries,commit,rollback,constraint failure andREAD_COMMITTED visibility are tested. H2 behavior onthisfixture isnot presented as universal behavior ofevery database engine.

## Vocabulary and concepts

**Connection:** A database session carrying transaction andstatement state.

**Prepared statement:** SQL structure with separately bound parameter values.

**Transaction:** A group of changes committed orrolled back as one declared unit.

**Isolation:** Rules governing which concurrent transaction changes are visible.

## How to run this lesson

Open the Docker classroom, choose the prepared Java21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-029/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.

## Required prepared JDBC dependency

The classroom Java21 image includes the pinned H2 driver at `/opt/course-libs/h2-2.5.252.jar` and adds it to the fixed runtime classpath. This lesson needs that real driver;it doesnot simulateJDBC when the driver is missing. The database URL is always an owned `jdbc:h2:mem:` fixture. No external database setup orreset is performed.

For an already prepared nativeJDK andH2JAR,compile with `javac --release 21 Main.java`. Run onPOSIX with `java -ea -cp ".:/path/to/h2-2.5.252.jar" Main`;onWindows use the classpath separatorsemicolon: `java -ea -cp ".;C:\course-libs\h2-2.5.252.jar" Main`. Substitute the actual prepared JAR path. Do not download orinstall a driver from inside the lesson.


## Syntax anatomy and execution trace

DriverManager.getConnection selects a loaded driver for thejdbc:h2:mem URL. Bind values withsetInt orsetString rather than concatenating them into SQL. Use setAutoCommit(false),commit androllback for transaction control. Close ResultSet,PreparedStatement andConnection withtry-with-resources. Check executeUpdate row counts so an unknown account isnot silently treated as a successful transfer. SetupDDL occurs before the tested transactions becauseDDL transaction behavior is engine-specific.

## Worked example / walkthrough

### Example A: Verify a real local database

Metadata andquery execution establish actualJDBCbehavior. A map pretending to be a database would not exercise driver loading,SQL parsing ortransaction state.

```java
import java.util.*;

public class Main {
    static final java.util.concurrent.atomic.AtomicInteger DATABASE_IDS=new java.util.concurrent.atomic.AtomicInteger();
    static java.sql.Connection database() throws java.sql.SQLException {
        java.sql.Connection connection;
        try{connection=java.sql.DriverManager.getConnection("jdbc:h2:mem:ds60_java29_"+DATABASE_IDS.incrementAndGet());}
        catch(java.sql.SQLException error){throw new java.sql.SQLException("Prepared H2 2.5.252 JDBC driver required on the classpath",error);}
        try(var statement=connection.createStatement()){
            statement.execute("CREATE TABLE accounts(id INTEGER PRIMARY KEY,name VARCHAR(40) NOT NULL,balance INTEGER NOT NULL CHECK(balance>=0))");
            statement.executeUpdate("INSERT INTO accounts VALUES(1,'Alice',100),(2,'Bob',50)");
        }catch(java.sql.SQLException error){connection.close();throw error;}
        return connection;
    }
    static int balance(java.sql.Connection connection,int id) throws java.sql.SQLException {
        try(var statement=connection.prepareStatement("SELECT balance FROM accounts WHERE id=?")){statement.setInt(1,id);try(var rows=statement.executeQuery()){if(!rows.next())throw new java.sql.SQLException("unknown account");return rows.getInt(1);}}
    }
    static void change(java.sql.Connection connection,int id,int delta) throws java.sql.SQLException {
        try(var statement=connection.prepareStatement("UPDATE accounts SET balance=balance+? WHERE id=?")){statement.setInt(1,delta);statement.setInt(2,id);if(statement.executeUpdate()!=1)throw new java.sql.SQLException("expected one account update");}
    }
    public static void main(String[] args) throws Exception {
        try(java.sql.Connection connection=database()) {
            assert connection.getMetaData().getDatabaseProductName().equals("H2") && connection.getAutoCommit();
            try(var statement=connection.prepareStatement("SELECT COUNT(*) FROM accounts");var rows=statement.executeQuery()){assert rows.next() && rows.getInt(1)==2;}
        }
    }
}

```

**Expected:** database productH2;2 rows;auto-commit initiallytrue.

### Example B: Bind an injection-shaped value as data

The driver receives the value separately from the query structure. The test uses a valid normal lookup as well as the adversarial-looking value so blanket rejection isnot mistaken forcorrect binding.

```java
import java.util.*;

public class Main {
    static final java.util.concurrent.atomic.AtomicInteger DATABASE_IDS=new java.util.concurrent.atomic.AtomicInteger();
    static java.sql.Connection database() throws java.sql.SQLException {
        java.sql.Connection connection;
        try{connection=java.sql.DriverManager.getConnection("jdbc:h2:mem:ds60_java29_"+DATABASE_IDS.incrementAndGet());}
        catch(java.sql.SQLException error){throw new java.sql.SQLException("Prepared H2 2.5.252 JDBC driver required on the classpath",error);}
        try(var statement=connection.createStatement()){
            statement.execute("CREATE TABLE accounts(id INTEGER PRIMARY KEY,name VARCHAR(40) NOT NULL,balance INTEGER NOT NULL CHECK(balance>=0))");
            statement.executeUpdate("INSERT INTO accounts VALUES(1,'Alice',100),(2,'Bob',50)");
        }catch(java.sql.SQLException error){connection.close();throw error;}
        return connection;
    }
    static int balance(java.sql.Connection connection,int id) throws java.sql.SQLException {
        try(var statement=connection.prepareStatement("SELECT balance FROM accounts WHERE id=?")){statement.setInt(1,id);try(var rows=statement.executeQuery()){if(!rows.next())throw new java.sql.SQLException("unknown account");return rows.getInt(1);}}
    }
    static void change(java.sql.Connection connection,int id,int delta) throws java.sql.SQLException {
        try(var statement=connection.prepareStatement("UPDATE accounts SET balance=balance+? WHERE id=?")){statement.setInt(1,delta);statement.setInt(2,id);if(statement.executeUpdate()!=1)throw new java.sql.SQLException("expected one account update");}
    }
    public static void main(String[] args) throws Exception {
        try(java.sql.Connection connection=database()) {
            assert connection.getMetaData().getDatabaseProductName().equals("H2") && connection.getAutoCommit();
            try(var statement=connection.prepareStatement("SELECT COUNT(*) FROM accounts");var rows=statement.executeQuery()){assert rows.next() && rows.getInt(1)==2;}
        }

        try(java.sql.Connection connection=database();var statement=connection.prepareStatement("SELECT COUNT(*) FROM accounts WHERE name = ?")) {
            statement.setString(1,"Alice");try(var rows=statement.executeQuery()){assert rows.next() && rows.getInt(1)==1;}
            statement.setString(1,"Alice' OR '1'='1");try(var rows=statement.executeQuery()){assert rows.next() && rows.getInt(1)==0;}
        }
    }
}

```

**Expected:** Alice matches1row;the injection-shaped value matches0.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Verify a real local database.** Open the fixture,inspect product metadata andcount the two account rows.
   **Expected:** database productH2;2 rows;auto-commit initiallytrue.
   **Verify:** Compare your assertion values or captured diagnostic with database productH2;2 rows;auto-commit initiallytrue.

2. **Bind an injection-shaped value as data.** Query byname usingAlice andthenAlicequoteOR1=1-shaped text through the same prepared statement.
   **Expected:** Alice matches1row;the injection-shaped value matches0.
   **Verify:** Compare your assertion values or captured diagnostic with Alice matches1row;the injection-shaped value matches0.

3. **Roll back a transfer.** Disableauto-commit,move20cents fromaccount1to2,inspect intermediate balances,androllback.
   **Expected:** inside80,70;afterrollback100,50.
   **Verify:** Compare your assertion values or captured diagnostic with inside80,70;afterrollback100,50.

4. **Commit andread from a second session.** Transfer10cents,commit,andopen another connection to the same owned memory database.
   **Expected:** second connection sees90,60 andtotal150.
   **Verify:** Compare your assertion values or captured diagnostic with second connection sees90,60 andtotal150.

5. **Handle a constraint failure androllback.** Attempt tosubtract200frombalance100,catch theSQL integrity error,androllback.
   **Expected:** SQLState class23;balance remains100 afterrollback.
   **Verify:** Compare your assertion values or captured diagnostic with SQLState class23;balance remains100 afterrollback.

6. **Observe committed visibility under the declared isolation.** Use twoH2connections atREAD_COMMITTED;updateaccount1 withoutcommit,read fromtheother,thencommit andreadagain.
   **Expected:** second session sees100beforecommit and95aftercommit.
   **Verify:** Compare your assertion values or captured diagnostic with second session sees100beforecommit and95aftercommit.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Connection, Prepared statement, Transaction in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.sql/java/sql/Connection.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Consult `docs/implementation/java-content-status.md` for the actual compile/run receipts. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning for java-029: JDBC and transactions.
Read courses/java/guides/java-029.md and courses/java/lessons/java-029.java. Direct prerequisites: `java-028`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
