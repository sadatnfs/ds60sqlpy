# java-028: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

HTTP is a request/response protocol with method, path, status, headers and body. A successful network exchange can still return an application error such as 404 or 400. A client must inspect status before interpreting the body. Timeouts bound waiting but do not prove that a remote operation did not happen. Response bodies and server exchanges own resources that need closure.

This lesson starts one short-lived server bound only to 127.0.0.1 on an operating-system-selected port, then uses the JDK HttpClient to call it. It does not contact an external service or start a persistent deployment. The handler accepts an exact path and GET method, returns explicit UTF-8 content, and closes every exchange. try-with-resources owns both client and server wrapper in Java 21. The fixture exposes prefix-routing and method-validation mistakes without requiring a web framework.

**HTTP status:** The response code describing protocol/application outcome.

**Loopback binding:** A listener restricted to the local host network interface.

**Request timeout:** A bound on client waiting for a request.

**Exchange lifetime:** Ownership of request/response streams and connection state.

## Reading the reference

HttpServer.create binds an InetSocketAddress with port 0, then getAddress reveals the actual port. createContext uses prefix matching, so the handler should validate an exact path when that is the contract. HttpRequest specifies a timeout and method. HttpResponse exposes statusCode, headers and body separately. stop(0) releases the owned listener when the fixture closes.

## Exercise 1: Call an owned loopback endpoint: change one input

Task: Copy Example A into a scratch `Main.java` and change `java.net.http.HttpRequest.newBuilder(server.uri("/health"))` to `java.net.http.HttpRequest.newBuilder(server.uri("/health!"))`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.

The request reaches a real localHTTPserver. A a returned String alone would not verify routing, status or resource closure.

The unchanged code is the part that Example A adds:

```java
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
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `response.statusCode() == 200 && response.body().equals("ok")`. Restoring the original line brings back the worked observation: status 200 and body ok.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `response.statusCode() == 200 && response.body().equals("ok")` false. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Inspect content metadata: diagnose an edited check

Task: A careless edit changed the assertion that Example B adds after Example A so that it reads `.equals("text/plain; charset=utf-9");`. Run Example B with that line, explain why the edited assertion now fails for the same program state, and restore it.

The encoding contract belongs in the response metadata as well as the byte-writing code. Clients should not guess a platform default.

The unchanged code is the part that Example B adds:

```java
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
```

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `response.headers().firstValue("Content-Type").orElseThrow().equals("text/plain; charset=utf-8")`; after it the line reads `.equals("text/plain; charset=utf-8");` again and text/plain with UTF-8 charset.

**Verify:** Keep the failing and the repaired runs. Explain why the edited assertion rejects the same program state that `response.headers().firstValue("Content-Type").orElseThrow().equals("text/plain; charset=utf-8")` accepts.

## Exercise 3: Reject an unsupported method

Task: POST to /health under a GET-only contract.

A route existing does not make every method valid. Validation occurs before performing domain work.

```java
try (
  LocalServer server = new LocalServer();
  var client = java.net.http.HttpClient.newHttpClient()
) {
  var request = java.net.http.HttpRequest.newBuilder(server.uri("/health"))
    .timeout(java.time.Duration.ofSeconds(2))
    .POST(java.net.http.HttpRequest.BodyPublishers.noBody())
    .build();
  var response = client.send(request, java.net.http.HttpResponse.BodyHandlers.ofString());
  assert response.statusCode() == 405 && response.body().equals("method not allowed");
}
```

**Expected:** status 405 and method not allowed body.

**Verify:** Keep an assertion equivalent to `response.statusCode() == 405 && response.body().equals("method not allowed")`. As a control, change `var request = java.net.http.HttpRequest.newBuilder(server.uri("/health"))` to `var request = java.net.http.HttpRequest.newBuilder(server.uri("/health!"))`: the run must fail with an `AssertionError` from the assertion on `response.statusCode() == 405 && response.body().equals("method not allowed")`. Restore the line before continuing.

## Exercise 4: Reject a prefix lookalike

Task: GET/health-extra, which matches the context prefix but not the declared exact path.

HttpServer context matching is prefix-based. An exact application route needs its own path check to avoid accidentally accepting lookalikes.

```java
try (
  LocalServer server = new LocalServer();
  var client = java.net.http.HttpClient.newHttpClient()
) {
  var response = client.send(
    java.net.http.HttpRequest.newBuilder(server.uri("/health-extra"))
      .timeout(java.time.Duration.ofSeconds(2))
      .GET()
      .build(),
    java.net.http.HttpResponse.BodyHandlers.ofString()
  );
  assert response.statusCode() == 404;
}
```

**Expected:** status 404.

**Verify:** Keep an assertion equivalent to `response.statusCode() == 404`. As a control, change `assert response.statusCode() == 404;` to `assert response.statusCode() != 404;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## Exercise 5: Keep error status separate from transport success

Task: GET an unknown path and inspect the completed response.

A transport-level success does not mean the domain operation succeeded. Client logic should branch on status before parsing a success schema.

```java
try (
  LocalServer server = new LocalServer();
  var client = java.net.http.HttpClient.newHttpClient()
) {
  var response = client.send(
    java.net.http.HttpRequest.newBuilder(server.uri("/missing"))
      .timeout(java.time.Duration.ofSeconds(2))
      .GET()
      .build(),
    java.net.http.HttpResponse.BodyHandlers.ofString()
  );
  assert response.statusCode() == 404;
}
```

**Expected:** HTTP exchange completes with 404 rather than a fabricated 200.

**Verify:** Keep an assertion equivalent to `response.statusCode() == 404`. As a control, change `assert response.statusCode() == 404;` to `assert response.statusCode() != 404;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## Exercise 6: Verify local-only target and closure

Task: Inspect the bound host and positive ephemeral port, then close the wrapper.

The fixture owns and stops its listener. It does not change a shared server or leave a deployment running after the lesson.

```java
LocalServer owned = new LocalServer();
assert owned.uri("/health").getHost().equals("127.0.0.1") && owned.uri("/health").getPort() > 0;
owned.close();
assert owned.closed;
```

**Expected:** host 127.0.0.1; port positive; closed flag true.

**Verify:** Keep an assertion equivalent to `owned.closed` and confirm that `java -ea Main` completes. Then name an input that would make it fail and explain which value changes.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
