# java-028: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

HTTP is a request/response protocol with method,path,status,headers and body. A successful network exchange can still return an application error such as404 or400. Aclient must inspect status before interpreting the body. Timeouts bound waiting but do not prove that a remote operation didnot happen. Response bodies and server exchanges own resources that need closure.

This lesson starts one short-lived server bound only to127.0.0.1 on an operating-system-selected port,then uses the JDK HttpClient to call it. It does not contact an external service or start a persistent deployment. Thehandler accepts an exact path and GET method,returns explicitUTF-8content,and closes every exchange. try-with-resources owns both client and server wrapper in Java 21. Thefixture exposes prefix-routing andmethod-validation mistakes without requiring a web framework.

**HTTP status:** The response code describing protocol/application outcome.

**Loopback binding:** A listener restricted to the local host network interface.

**Request timeout:** A bound on client waiting for a request.

**Exchange lifetime:** Ownership of request/response streams and connection state.

## Reading the reference

HttpServer.create binds an InetSocketAddress withport0,thengetAddress reveals the actual port. createContext uses prefix matching,so the handler should validate an exact path when that is the contract. HttpRequest specifies a timeout and method. HttpResponse exposes statusCode,headers and body separately. stop(0) releases the owned listener when the fixture closes.

## Exercise 1: Call an owned loopback endpoint

Task: Start the fixture and request `GET /health`.

The request reaches a real localHTTPserver. A a returned String alone would not verify routing,status or resource closure.

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

**Expected:** status 200 and body ok.

**Verify:** Compare the program values or named exception with status 200 and body ok. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Inspect content metadata

Task: ReadContent-Type on the successful response.

Theencoding contract belongs in the response metadata as well as thebyte-writing code. Clients should not guess a platform default.

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

**Expected:** text/plain with UTF-8 charset.

**Verify:** Compare the program values or named exception with text/plain with UTF-8 charset. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Reject an unsupported method

Task: POSTto/health underaGET-onlycontract.

A routeexistingdoesnotmakeeverymethodvalid. Validation occursbeforeperformingdomainwork.

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

**Expected:** status405 and method not allowed body.

**Verify:** Compare the program values or named exception with status405 and method not allowed body. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Reject a prefix lookalike

Task: GET/health-extra,which matches the context prefix but not the declared exact path.

HttpServercontextmatchingisprefix-based. An exact application route needs its own path check toavoidaccidentallyacceptinglookalikes.

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

**Expected:** status404.

**Verify:** Compare the program values or named exception with status404. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Keep error status separate from transport success

Task: GETanunknownpathandinspectthecompletedresponse.

Atransport-levelsuccessdoesnotmean the domain operation succeeded. Clientlogicshouldbranchonstatusbeforeparsingasuccessschema.

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

**Expected:** HTTP exchange completes with404 rather than a fabricated200.

**Verify:** Compare the program values or named exception with HTTP exchange completes with404 rather than a fabricated200. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Verify local-only target and closure

Task: Inspect the bound host and positive ephemeral port,then close the wrapper.

Thefixtureownsandstopsitslistener. It does not change a shared server orleaveadeploymentrunningafterthelesson.

```java
LocalServer owned = new LocalServer();
assert owned.uri("/health").getHost().equals("127.0.0.1") && owned.uri("/health").getPort() > 0;
owned.close();
assert owned.closed;
```

**Expected:** host 127.0.0.1;port positive; closed flag true.

**Verify:** Compare the program values or named exception with host 127.0.0.1;port positive; closed flag true. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
