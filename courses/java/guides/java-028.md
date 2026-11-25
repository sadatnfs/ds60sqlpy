# java-028: HTTP services and clients

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-027`

## Learning objectives

Serve and call an owned loopback HTTP endpoint and keep status, method and route errors distinct.

The six exercises practice these steps:

- Call an owned loopback endpoint.
- Inspect content metadata.
- Reject an unsupported method.
- Reject a prefix lookalike.
- Keep error status separate from transport success.
- Verify local-only target and closure.

## Purpose and mental model

HTTP is a request/response protocol with method, path, status, headers and body. A successful network exchange can still return an application error such as 404 or 400. A client must inspect status before interpreting the body. Timeouts bound waiting but do not prove that a remote operation did not happen. Response bodies and server exchanges own resources that need closure.

This lesson starts one short-lived server bound only to 127.0.0.1 on an operating-system-selected port, then uses the JDK HttpClient to call it. It does not contact an external service or start a persistent deployment. The handler accepts an exact path and GET method, returns explicit UTF-8 content, and closes every exchange. try-with-resources owns both client and server wrapper in Java 21. The fixture exposes prefix-routing and method-validation mistakes without requiring a web framework.

## Vocabulary and concepts

**HTTP status:** The response code describing protocol/application outcome.

**Loopback binding:** A listener restricted to the local host network interface.

**Request timeout:** A bound on client waiting for a request.

**Exchange lifetime:** Ownership of request/response streams and connection state.

## How to run this lesson

`LocalServer` binds the JDK `HttpServer` to 127.0.0.1 on a port the operating system picks, serves one `/health` handler, and stops in `close`; every request carries a two-second timeout and nothing leaves the machine.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

HttpServer.create binds an InetSocketAddress with port 0, then getAddress reveals the actual port. createContext uses prefix matching, so the handler should validate an exact path when that is the contract. HttpRequest specifies a timeout and method. HttpResponse exposes statusCode, headers and body separately. stop(0) releases the owned listener when the fixture closes.

## Worked example / walkthrough

### Example A: Call an owned loopback endpoint

The request reaches a real localHTTPserver. A a returned String alone would not verify routing, status or resource closure.

```java
import java.util.*;

public class Main {

  static final class LocalServer implements AutoCloseable {

    final com.sun.net.httpserver.HttpServer server;
    boolean closed;

    LocalServer() throws java.io.IOException {
      server = com.sun.net.httpserver.HttpServer.create(
        new java.net.InetSocketAddress("127.0.0.1", 0),
        0
      );
      server.createContext("/health", exchange -> {
        try (exchange) {
          int status;
          String body;
          if (!exchange.getRequestURI().getPath().equals("/health")) {
            status = 404;
            body = "not found";
          } else if (!exchange.getRequestMethod().equals("GET")) {
            status = 405;
            body = "method not allowed";
          } else {
            status = 200;
            body = "ok";
          }
          byte[] bytes = body.getBytes(java.nio.charset.StandardCharsets.UTF_8);
          exchange.getResponseHeaders().set("Content-Type", "text/plain; charset=utf-8");
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
    try (
      LocalServer server = new LocalServer();
      var client = java.net.http.HttpClient.newBuilder()
        .connectTimeout(java.time.Duration.ofSeconds(2))
        .build()
    ) {
      var response = client.send(
        java.net.http.HttpRequest.newBuilder(server.uri("/health"))
          .timeout(java.time.Duration.ofSeconds(2))
          .GET()
          .build(),
        java.net.http.HttpResponse.BodyHandlers.ofString()
      );
      assert response.statusCode() == 200 && response.body().equals("ok");
    }
  }
}
```

**Expected:** status 200 and body ok.

### Example B: Inspect content metadata

The encoding contract belongs in the response metadata as well as the byte-writing code. Clients should not guess a platform default.

```java
import java.util.*;

public class Main {

  static final class LocalServer implements AutoCloseable {

    final com.sun.net.httpserver.HttpServer server;
    boolean closed;

    LocalServer() throws java.io.IOException {
      server = com.sun.net.httpserver.HttpServer.create(
        new java.net.InetSocketAddress("127.0.0.1", 0),
        0
      );
      server.createContext("/health", exchange -> {
        try (exchange) {
          int status;
          String body;
          if (!exchange.getRequestURI().getPath().equals("/health")) {
            status = 404;
            body = "not found";
          } else if (!exchange.getRequestMethod().equals("GET")) {
            status = 405;
            body = "method not allowed";
          } else {
            status = 200;
            body = "ok";
          }
          byte[] bytes = body.getBytes(java.nio.charset.StandardCharsets.UTF_8);
          exchange.getResponseHeaders().set("Content-Type", "text/plain; charset=utf-8");
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
    try (
      LocalServer server = new LocalServer();
      var client = java.net.http.HttpClient.newBuilder()
        .connectTimeout(java.time.Duration.ofSeconds(2))
        .build()
    ) {
      var response = client.send(
        java.net.http.HttpRequest.newBuilder(server.uri("/health"))
          .timeout(java.time.Duration.ofSeconds(2))
          .GET()
          .build(),
        java.net.http.HttpResponse.BodyHandlers.ofString()
      );
      assert response.statusCode() == 200 && response.body().equals("ok");
    }

    try (
      LocalServer server = new LocalServer();
      var client = java.net.http.HttpClient.newHttpClient()
    ) {
      var response = client.send(
        java.net.http.HttpRequest.newBuilder(server.uri("/health"))
          .timeout(java.time.Duration.ofSeconds(2))
          .GET()
          .build(),
        java.net.http.HttpResponse.BodyHandlers.ofString()
      );
      assert response
        .headers()
        .firstValue("Content-Type")
        .orElseThrow()
        .equals("text/plain; charset=utf-8");
    }
  }
}
```

**Expected:** text/plain with UTF-8 charset.

## Prediction before your attempt

Before running Example A, decide what status and body a `GET /health` receives, and what the handler sends for `GET /health!` given that `createContext("/health", ...)` matches by prefix. For Example B, predict the exact `Content-Type` header value, including the charset. Before Exercise 3, decide whether a `POST` to the same path should reach the success branch or be rejected first.

## Exercises

1. **Call an owned loopback endpoint: change one input.** Change `java.net.http.HttpRequest.newBuilder(server.uri("/health"))` to `java.net.http.HttpRequest.newBuilder(server.uri("/health!"))` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `response.statusCode() == 200 && response.body().equals("ok")`.
   **Verify:** Name the value that makes `response.statusCode() == 200 && response.body().equals("ok")` false, then restore the line.

2. **Inspect content metadata: diagnose an edited check.** Example B's new assertion was edited to `.equals("text/plain; charset=utf-9");`. Explain why it fails for unchanged state and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `response.headers().firstValue("Content-Type").orElseThrow().equals("text/plain; charset=utf-8")`; the restored assertion passes.
   **Verify:** Explain why the edited assertion rejects the state that `response.headers().firstValue("Content-Type").orElseThrow().equals("text/plain; charset=utf-8")` accepts.

3. **Reject an unsupported method.** POST to /health under a GET-only contract.
   **Expected:** status 405 and method not allowed body.
   **Verify:** Control: changing `var request = java.net.http.HttpRequest.newBuilder(server.uri("/health"))` to `var request = java.net.http.HttpRequest.newBuilder(server.uri("/health!"))` must fail the assertion on `response.statusCode() == 405 && response.body().equals("method not allowed")`.

4. **Reject a prefix lookalike.** GET/health-extra, which matches the context prefix but not the declared exact path.
   **Expected:** status 404.
   **Verify:** Control: changing `assert response.statusCode() == 404;` to `assert response.statusCode() != 404;` inside the assertion must make it fail.

5. **Keep error status separate from transport success.** GET an unknown path and inspect the completed response.
   **Expected:** HTTP exchange completes with 404 rather than a fabricated 200.
   **Verify:** Control: changing `assert response.statusCode() == 404;` to `assert response.statusCode() != 404;` inside the assertion must make it fail.

6. **Verify local-only target and closure.** Inspect the bound host and positive ephemeral port, then close the wrapper.
   **Expected:** host 127.0.0.1; port positive; closed flag true.
   **Verify:** Name an input that would make `owned.closed` false and the value that changes.

## Common pitfalls and diagnosis

The JDK `HttpClient` does not throw for a 404 or 500: the exchange succeeded, so code that reads the body without checking `statusCode()` parses an error page as data. `HttpServer.createContext` matches by prefix, so `/health-extra` reaches the same handler unless it checks the exact path. A handler that forgets to close the exchange leaks the connection. Binding to 0.0.0.0 exposes a test server to the network, and a request without a timeout can wait forever.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the edit requests `/health!`. Then follow it through the handler: the prefix context accepts it, but the exact path check fails. Finally, predict a 404 with body "not found" instead of 200 with "ok".
- **Exercise 2:** First note that the in-check edit expects `charset=utf-9`. Then read the header the handler actually sets, `text/plain; charset=utf-8`. Finally, explain why the request succeeded and only the metadata comparison fails.
- **Exercise 3:** First build a request to `/health` with `POST(HttpRequest.BodyPublishers.noBody())`. Then send it with a two-second timeout and read the status and body. Finally, assert 405 and "method not allowed", and say why validation must happen before any work.
- **Exercise 4:** First request `/health-extra`, which the prefix context still routes to the handler. Then read the status the exact path check produces. Finally, assert 404 and explain what would happen if the handler trusted the context alone.
- **Exercise 5:** First request an unknown path such as `/missing` on the same server. Then confirm that `client.send` returned normally with no exception. Finally, assert status 404 and explain why the caller, not the transport, decides that the request failed.
- **Exercise 6:** First create a `LocalServer` without try-with-resources. Then read the host and port from `uri("/health")` and assert 127.0.0.1 and a positive port. Finally, call `close()` and assert the `closed` flag.

## Self-check and retrieval

From memory, explain why a completed HTTP exchange can still be a failure, how the handler distinguishes 200, 404 and 405, why the context needs an exact path check, and which two settings keep this fixture local and bounded.

## Next step

Continue with `java-029`: JDBC and transactions. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.httpserver/com/sun/net/httpserver/HttpServer.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-028: HTTP services and clients.
Read courses/java/guides/java-028.md and courses/java/lessons/java-028.java. Direct prerequisites: `java-027`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
