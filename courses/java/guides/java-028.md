# java-028: HTTP services and clients

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-027`

## Learning objectives

Serve and call an owned loopback HTTP endpoint and keep status, method and route errors distinct. Along the way, explain http status, loopback binding, request timeout, exchange lifetime using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: POST to /health under a GET-only contract. The final exercise transfers the mechanism to verify local-only target and closure.

## Purpose and mental model

HTTP is a request/response protocol with method, path, status, headers and body. A successful network exchange can still return an application error such as 404 or 400. A client must inspect status before interpreting the body. Timeouts bound waiting but do not prove that a remote operation did not happen. Response bodies and server exchanges own resources that need closure.

This lesson starts one short-lived server bound only to 127.0.0.1 on an operating-system-selected port, then uses the JDK HttpClient to call it. It does not contact an external service or start a persistent deployment. The handler accepts an exact path and GET method, returns explicit UTF-8 content, and closes every exchange. try-with-resources owns both client and server wrapper in Java 21. The fixture exposes prefix-routing and method-validation mistakes without requiring a web framework.

## Vocabulary and concepts

**HTTP status:** The response code describing protocol/application outcome.

**Loopback binding:** A listener restricted to the local host network interface.

**Request timeout:** A bound on client waiting for a request.

**Exchange lifetime:** Ownership of request/response streams and connection state.

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-028/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



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

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Call an owned loopback endpoint: change one input.** Copy Example A into a scratch `Main.java` and change `java.net.http.HttpRequest.newBuilder(server.uri("/health"))` to `java.net.http.HttpRequest.newBuilder(server.uri("/health!"))`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.
   **Expected:** The changed run fails with an `AssertionError` from the assertion on `response.statusCode() == 200 && response.body().equals("ok")`. Restoring the original line brings back the worked observation: status 200 and body ok.
   **Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `response.statusCode() == 200 && response.body().equals("ok")` false. After restoring the line, the program completes without an `AssertionError` again.

2. **Inspect content metadata: diagnose an edited check.** A careless edit changed the assertion that Example B adds after Example A so that it reads `.equals("text/plain; charset=utf-9");`. Run Example B with that line, explain why the edited assertion now fails for the same program state, and restore it.
   **Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `response.headers().firstValue("Content-Type").orElseThrow().equals("text/plain; charset=utf-8")`; after it the line reads `.equals("text/plain; charset=utf-8");` again and text/plain with UTF-8 charset.
   **Verify:** Keep the failing and the repaired runs. Explain why the edited assertion rejects the same program state that `response.headers().firstValue("Content-Type").orElseThrow().equals("text/plain; charset=utf-8")` accepts.

3. **Reject an unsupported method.** POST to /health under a GET-only contract.
   **Expected:** status 405 and method not allowed body.
   **Verify:** Keep an assertion equivalent to `response.statusCode() == 405 && response.body().equals("method not allowed")`. As a control, change `var request = java.net.http.HttpRequest.newBuilder(server.uri("/health"))` to `var request = java.net.http.HttpRequest.newBuilder(server.uri("/health!"))`: the run must fail with an `AssertionError` from the assertion on `response.statusCode() == 405 && response.body().equals("method not allowed")`. Restore the line before continuing.

4. **Reject a prefix lookalike.** GET/health-extra, which matches the context prefix but not the declared exact path.
   **Expected:** status 404.
   **Verify:** Keep an assertion equivalent to `response.statusCode() == 404`. As a control, change `assert response.statusCode() == 404;` to `assert response.statusCode() != 404;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

5. **Keep error status separate from transport success.** GET an unknown path and inspect the completed response.
   **Expected:** HTTP exchange completes with 404 rather than a fabricated 200.
   **Verify:** Keep an assertion equivalent to `response.statusCode() == 404`. As a control, change `assert response.statusCode() == 404;` to `assert response.statusCode() != 404;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

6. **Verify local-only target and closure.** Inspect the bound host and positive ephemeral port, then close the wrapper.
   **Expected:** host 127.0.0.1; port positive; closed flag true.
   **Verify:** Keep an assertion equivalent to `owned.closed` and confirm that `java -ea Main` completes. Then name an input that would make it fail and explain which value changes.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

- **Exercise 1:** First restate the expected observation: status 200 and body ok. Then list the values read by `response.statusCode() == 200 && response.body().equals("ok")` and trace each one from its declaration. Finally, compute the asserted value with `java.net.http.HttpRequest.newBuilder(server.uri("/health!"))` in place before running.
- **Exercise 2:** First restate the expected observation: text/plain with UTF-8 charset. Then list the values read by `response.headers().firstValue("Content-Type").orElseThrow().equals("text/plain; charset=utf-8")` and trace each one from its declaration. Finally, compare `.equals("text/plain; charset=utf-9");` with the same line in Example B and state the claim each version makes.
- **Exercise 3:** First restate the expected observation: status 405 and method not allowed body. Then list the values read by `response.statusCode() == 405 && response.body().equals("method not allowed")` and trace each one from its declaration. Finally, predict the effect of changing `var request = java.net.http.HttpRequest.newBuilder(server.uri("/health"))` to `var request = java.net.http.HttpRequest.newBuilder(server.uri("/health!"))` before running anything.
- **Exercise 4:** First restate the expected observation: status 404. Then list the values read by `response.statusCode() == 404` and trace each one from its declaration. Finally, name one input that would make `response.statusCode() == 404` false.
- **Exercise 5:** First restate the expected observation: HTTP exchange completes with 404 rather than a fabricated 200. Then list the values read by `response.statusCode() == 404` and trace each one from its declaration. Finally, name one input that would make `response.statusCode() == 404` false.
- **Exercise 6:** First restate the expected observation: host 127.0.0.1; port positive; closed flag true. Then list the values read by `owned.closed` and trace each one from its declaration. Finally, name one input that would make `owned.closed` false.

## Self-check and retrieval

Close the solution and explain HTTP status, Loopback binding, Request timeout in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.httpserver/com/sun/net/httpserver/HttpServer.html), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

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
