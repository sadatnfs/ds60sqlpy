# java-035: Build a tested local data service

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-034`

## Learning objectives

Explain response grain, repository port, http adapter, contract test using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Summarize group A over amounts 10,20 and group B over 5. The final exercise transfers the mechanism to preserve storage and close the owned listener.

## Purpose and mental model

A small data service combines domain rules, storage and transport contracts. Its correctness is more than an HTTP 200 status: the response grain, columns, ordering, error semantics and resource lifetime must agree. This capstone serves a read-only grouped summary over three authored records. Storage is an explicit in-memory repository, not a simulated JDBC claim. The earlier JDBC lesson separately exercised a real database.

The service binds only to loopback on an ephemeral port and stops when the owned fixture closes. It accepts one GET route with one group query parameter. The group must be a single uppercase letter; unknown valid groups return 404, malformed queries return 400, and unsupported methods return 405. The domain summary is tested directly and through actual HTTP requests. This is a bounded local service demonstration, not a deployed authenticated application.

## Vocabulary and concepts

**Response grain:** The identity of one row or object in a service result.

**Repository port:** The contract through which domain logic reads stored records.

**HTTP adapter:** Code translating validated requests into domain calls and responses.

**Contract test:** A check of observable behavior across a component boundary.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-035/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

A Repository port exposes an immutable row list. The pure summary function filters by group and returns count and integer total. The HTTP adapter validates exact path, method and query structure before calling the core. Since the admitted group is one uppercase ASCII letter, the fixed JSON encoder cannot be influenced by arbitrary quotes. HttpClient requests use timeouts, and every exchange, response body and server instance is closed.

## Worked example / walkthrough

### Example A: Verify the domain summary

The domain result has one object per requested group. It is checked independently of HTTP formatting and status handling.

```java
import java.util.*;

public class Main {

  record Row(String id, String group, int amount) {}

  record Summary(String group, int count, int total) {}

  interface Repository {
    List<Row> rows();
  }

  static Summary summarize(Repository repository, String group) {
    var rows = repository
      .rows()
      .stream()
      .filter(row -> row.group().equals(group))
      .toList();
    if (rows.isEmpty()) throw new NoSuchElementException("not found");
    return new Summary(group, rows.size(), rows.stream().mapToInt(Row::amount).sum());
  }

  static java.net.http.HttpResponse<String> send(
    java.net.http.HttpClient client,
    java.net.URI uri,
    String method
  ) throws Exception {
    var builder = java.net.http.HttpRequest.newBuilder(uri).timeout(
      java.time.Duration.ofSeconds(2)
    );
    if (method.equals("GET")) builder.GET();
    else builder.method(method, java.net.http.HttpRequest.BodyPublishers.noBody());
    return client.send(builder.build(), java.net.http.HttpResponse.BodyHandlers.ofString());
  }

  static final class DataServer implements AutoCloseable {

    final com.sun.net.httpserver.HttpServer server;
    boolean closed;

    DataServer(Repository repository) throws java.io.IOException {
      server = com.sun.net.httpserver.HttpServer.create(
        new java.net.InetSocketAddress("127.0.0.1", 0),
        0
      );
      server.createContext("/summary", exchange -> {
        try (exchange) {
          int status;
          String body;
          String query = exchange.getRequestURI().getRawQuery();
          if (!exchange.getRequestURI().getPath().equals("/summary")) {
            status = 404;
            body = "{\"error\":\"not_found\"}";
          } else if (!exchange.getRequestMethod().equals("GET")) {
            status = 405;
            body = "{\"error\":\"method_not_allowed\"}";
          } else if (query == null || !query.matches("group=[A-Z]")) {
            status = 400;
            body = "{\"error\":\"invalid_query\"}";
          } else {
            try {
              Summary result = summarize(repository, query.substring(6));
              status = 200;
              body =
                "{\"group\":\"" +
                result.group() +
                "\",\"count\":" +
                result.count() +
                ",\"total\":" +
                result.total() +
                "}";
            } catch (NoSuchElementException missing) {
              status = 404;
              body = "{\"error\":\"not_found\"}";
            }
          }
          byte[] bytes = body.getBytes(java.nio.charset.StandardCharsets.UTF_8);
          exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
          exchange.sendResponseHeaders(status, bytes.length);
          try (var output = exchange.getResponseBody()) {
            output.write(bytes);
          }
        }
      });
      server.start();
    }

    java.net.URI uri(String path) {
      return java.net.URI.create("http://127.0.0.1:" + server.getAddress().getPort() + path);
    }

    public void close() {
      server.stop(0);
      closed = true;
    }
  }

  public static void main(String[] args) throws Exception {
    Repository repository = () ->
      List.of(new Row("a1", "A", 10), new Row("a2", "A", 20), new Row("b1", "B", 5));
    assert summarize(repository, "A").equals(new Summary("A", 2, 30));
    assert summarize(repository, "B").equals(new Summary("B", 1, 5));
  }
}
```

**Expected:** A count 2, total 30; B count 1, total 5.

### Example B: Read a successful HTTPsummary

The exact body check fixes the public schema and integer representation. The source counts remain independently known.

```java
import java.util.*;

public class Main {

  record Row(String id, String group, int amount) {}

  record Summary(String group, int count, int total) {}

  interface Repository {
    List<Row> rows();
  }

  static Summary summarize(Repository repository, String group) {
    var rows = repository
      .rows()
      .stream()
      .filter(row -> row.group().equals(group))
      .toList();
    if (rows.isEmpty()) throw new NoSuchElementException("not found");
    return new Summary(group, rows.size(), rows.stream().mapToInt(Row::amount).sum());
  }

  static java.net.http.HttpResponse<String> send(
    java.net.http.HttpClient client,
    java.net.URI uri,
    String method
  ) throws Exception {
    var builder = java.net.http.HttpRequest.newBuilder(uri).timeout(
      java.time.Duration.ofSeconds(2)
    );
    if (method.equals("GET")) builder.GET();
    else builder.method(method, java.net.http.HttpRequest.BodyPublishers.noBody());
    return client.send(builder.build(), java.net.http.HttpResponse.BodyHandlers.ofString());
  }

  static final class DataServer implements AutoCloseable {

    final com.sun.net.httpserver.HttpServer server;
    boolean closed;

    DataServer(Repository repository) throws java.io.IOException {
      server = com.sun.net.httpserver.HttpServer.create(
        new java.net.InetSocketAddress("127.0.0.1", 0),
        0
      );
      server.createContext("/summary", exchange -> {
        try (exchange) {
          int status;
          String body;
          String query = exchange.getRequestURI().getRawQuery();
          if (!exchange.getRequestURI().getPath().equals("/summary")) {
            status = 404;
            body = "{\"error\":\"not_found\"}";
          } else if (!exchange.getRequestMethod().equals("GET")) {
            status = 405;
            body = "{\"error\":\"method_not_allowed\"}";
          } else if (query == null || !query.matches("group=[A-Z]")) {
            status = 400;
            body = "{\"error\":\"invalid_query\"}";
          } else {
            try {
              Summary result = summarize(repository, query.substring(6));
              status = 200;
              body =
                "{\"group\":\"" +
                result.group() +
                "\",\"count\":" +
                result.count() +
                ",\"total\":" +
                result.total() +
                "}";
            } catch (NoSuchElementException missing) {
              status = 404;
              body = "{\"error\":\"not_found\"}";
            }
          }
          byte[] bytes = body.getBytes(java.nio.charset.StandardCharsets.UTF_8);
          exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
          exchange.sendResponseHeaders(status, bytes.length);
          try (var output = exchange.getResponseBody()) {
            output.write(bytes);
          }
        }
      });
      server.start();
    }

    java.net.URI uri(String path) {
      return java.net.URI.create("http://127.0.0.1:" + server.getAddress().getPort() + path);
    }

    public void close() {
      server.stop(0);
      closed = true;
    }
  }

  public static void main(String[] args) throws Exception {
    Repository repository = () ->
      List.of(new Row("a1", "A", 10), new Row("a2", "A", 20), new Row("b1", "B", 5));
    assert summarize(repository, "A").equals(new Summary("A", 2, 30));
    assert summarize(repository, "B").equals(new Summary("B", 1, 5));

    try (
      DataServer server = new DataServer(repository);
      var client = java.net.http.HttpClient.newHttpClient()
    ) {
      var response = send(client, server.uri("/summary?group=A"), "GET");
      assert response.statusCode() == 200 &&
      response.body().equals("{\"group\":\"A\",\"count\":2,\"total\":30}");
    }
  }
}
```

**Expected:** status 200 andexactJSONwithcount2,total 30.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Verify the domain summary.** Summarize group A over amounts 10,20 and group B over 5.
   **Expected:** A count 2, total 30; B count 1, total 5.
   **Verify:** Compare your assertion values or captured diagnostic with A count 2, total 30; B count 1, total 5.

2. **Read a successful HTTPsummary.** GET/summary?group=Afromtheownedserver.
   **Expected:** status 200 andexactJSONwithcount2,total 30.
   **Verify:** Compare your assertion values or captured diagnostic with status 200 andexactJSONwithcount2,total 30.

3. **Report an unknown valid group.** GETgroupC,which passes syntax buthasnorecords.
   **Expected:** status404 withnot_found error.
   **Verify:** Compare your assertion values or captured diagnostic with status404 withnot_found error.

4. **Reject ambiguous or malformed queries.** Send duplicate group parameters andalowercasegroup.
   **Expected:** bothstatus400.
   **Verify:** Compare your assertion values or captured diagnostic with bothstatus400.

5. **Reject unsupported methods andpathlookalikes.** POST to the summary route andGET/summary-extra.
   **Expected:** 405 and404 respectively.
   **Verify:** Compare your assertion values or captured diagnostic with 405 and404 respectively.

6. **Preserve storage and close the owned listener.** Comparetherepositorybefore/afterrequests and close the server.
   **Expected:** 3 unchanged records; closed flag true.
   **Verify:** Compare your assertion values or captured diagnostic with 3 unchanged records; closed flag true.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Response grain, Repository port, HTTP adapter in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.httpserver/com/sun/net/httpserver/HttpServer.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-035: Build a tested local data service.
Read courses/java/guides/java-035.md and courses/java/lessons/java-035.java. Direct prerequisites: `java-034`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
