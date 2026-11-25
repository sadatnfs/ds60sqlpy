# java-035: Build a tested local data service

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-034`

## Learning objectives

Build and test a small local HTTP data service that validates queries strictly and leaves its storage unchanged.

The six exercises practice these steps:

- Verify the domain summary.
- Read a successful HTTP summary.
- Report an unknown valid group.
- Reject ambiguous or malformed queries.
- Reject unsupported methods and path lookalikes.
- Preserve storage and close the owned listener.

## Purpose and mental model

A small data service combines domain rules, storage and transport contracts. Its correctness is more than an HTTP 200 status: the response grain, columns, ordering, error semantics and resource lifetime must agree. This capstone serves a read-only grouped summary over three authored records. Storage is an explicit in-memory repository, not a simulated JDBC claim. The earlier JDBC lesson separately exercised a real database.

The service binds only to loopback on an ephemeral port and stops when the owned fixture closes. It accepts one GET route with one group query parameter. The group must be a single uppercase letter; unknown valid groups return 404, malformed queries return 400, and unsupported methods return 405. The domain summary is tested directly and through actual HTTP requests. This is a bounded local service demonstration, not a deployed authenticated application.

## Vocabulary and concepts

**Response grain:** The identity of one row or object in a service result.

**Repository port:** The contract through which domain logic reads stored records.

**HTTP adapter:** Code translating validated requests into domain calls and responses.

**Contract test:** A check of observable behavior across a component boundary.

## How to run this lesson

`DataServer` binds the JDK HTTP server to 127.0.0.1 on an ephemeral port, serves one read-only `/summary` route over three in-memory rows, and stops in `close`; each client request has a two-second timeout.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



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

### Example B: Read a successful HTTP summary

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

**Expected:** status 200 and exact JSON with count 2, total 30.

## Prediction before your attempt

Before running Example A, compute the count and total for groups A and B from the three rows. For Example B, write the exact JSON body that `GET /summary?group=A` returns, including key order and integer formatting. Before Exercise 4, decide which status a query with two `group` parameters receives, and which check in the handler catches it.

## Exercises

1. **Verify the domain summary: change one input.** Change `List.of(new Row("a1", "A", 10), new Row("a2", "A", 20), new Row("b1", "B", 5));` to `List.of(new Row("a1", "A", 10), new Row("a2", "A", 20), new Row("b1", "B", 6));` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `summarize(repository, "B").equals(new Summary("B", 1, 5))`.
   **Verify:** Name the value that makes `summarize(repository, "B").equals(new Summary("B", 1, 5))` false, then restore the line.

2. **Read a successful HTTP summary: diagnose an edited check.** Example B's new assertion was edited to `\"count\":3`. Explain why it fails for unchanged state and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `response.statusCode() == 200 && response.body().equals("{\"group\":\"A\",\"count\":2,\"total\":30}")`; the restored assertion passes.
   **Verify:** Explain why the edited assertion rejects the state that `response.statusCode() == 200 && response.body().equals("{\"group\":\"A\",\"count\":2,\"total\":30}")` accepts.

3. **Report an unknown valid group.** GET group C, which passes syntax but has no records.
   **Expected:** status 404 with not_found error.
   **Verify:** Control: changing `var response = send(client, server.uri("/summary?group=C"), "GET");` to `var response = send(client, server.uri("/summary?group=C!"), "GET");` must fail the assertion on `response.statusCode() == 404 && response.body().contains("not_found")`.

4. **Reject ambiguous or malformed queries.** Send duplicate group parameters and a lowercase group.
   **Expected:** both status 400.
   **Verify:** Control: changing `int duplicate = send(client, server.uri("/summary?group=A&group=B"), "GET").statusCode();` to `int duplicate = send(client, server.uri("/summary?group=A&group=B"), "GET!").statusCode();` must fail the assertion on `duplicate == 400 && lowercase == 400`.

5. **Reject unsupported methods and path lookalikes.** POST to the summary route and GET /summary-extra.
   **Expected:** 405 and 404 respectively.
   **Verify:** Control: changing `assert post == 405 && lookalike == 404;` to `assert post != 405 && lookalike == 404;` inside the assertion must make it fail.

6. **Preserve storage and close the owned listener.** Compare the repository before/after requests and close the server.
   **Expected:** 3 unchanged records; closed flag true.
   **Verify:** Control: changing `assert server.closed && repository.rows().equals(before) && repository.rows().size() == 3;` to `assert server.closed && repository.rows().equals(before) && repository.rows().size() != 3;` inside the assertion must make it fail.

## Common pitfalls and diagnosis

Asserting only a 200 status misses a wrong schema, an extra field or a string where a number belongs, so compare the exact body. Returning 404 for malformed input or 400 for a missing group blurs two different client mistakes. Picking the first of duplicate parameters silently guesses what the caller meant. The prefix context accepts `/summary-extra` unless the handler checks the path. And forgetting to stop the server leaves a listener running after the tests.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the edit changes row `b1` to an amount of 6. Then recompute the summary for group B, which becomes a count of 1 and a total of 6. Finally, explain why group A still matches and only the B comparison fails.
- **Exercise 2:** First note that the in-check edit expects `"count":3` in the body. Then count the rows in group A, which is 2. Finally, explain why the status and the rest of the JSON were correct and only the expected text was wrong.
- **Exercise 3:** First request `/summary?group=C`, which matches the one-uppercase-letter rule. Then follow it to `summarize`, which finds no rows and throws `NoSuchElementException`. Finally, assert 404 with `not_found` and contrast it with the 400 for a malformed group.
- **Exercise 4:** First request `/summary?group=A&group=B` and read the status. Then request `/summary?group=a` with a lowercase letter. Finally, assert 400 for both and explain why the raw query must match `group=[A-Z]` exactly.
- **Exercise 5:** First send a `POST` to `/summary` and read the status. Then send a `GET` to `/summary-extra`, which the prefix context still routes to the handler. Finally, assert 405 and 404 and say which check produced each one.
- **Exercise 6:** First save `repository.rows()` and start a `DataServer` on that repository. Then close the server without try-with-resources. Finally, assert the `closed` flag, three rows and a list equal to the saved one, proving the service never wrote to storage.

## Self-check and retrieval

Without notes, list the order of checks in the `/summary` handler and the status each one returns. Explain why the domain summary is tested before the HTTP layer, why duplicate parameters are rejected, and what Exercise 6 proves about storage and the listener.

## Next step

Continue with `java-036`: Package, diagnose and maintain a release. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.httpserver/com/sun/net/httpserver/HttpServer.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-035: Build a tested local data service.
Read courses/java/guides/java-035.md and courses/java/lessons/java-035.java. Direct prerequisites: `java-034`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
