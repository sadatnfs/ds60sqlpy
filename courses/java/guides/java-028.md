# java-028: HTTP services and clients

## Level and prerequisites

Advanced, approximately 120 minutes. Direct prerequisites: `java-027`

## Learning objectives

Explain http status, loopback binding, request timeout, exchange lifetime using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Start the fixture and request `GET /health`. The final exercise transfers the mechanism to verify local-only target and closure.

## Purpose and mental model

HTTP is a request/response protocol with method,path,status,headers and body. A successful network exchange can still return an application error such as404 or400. Aclient must inspect status before interpreting the body. Timeouts bound waiting but do not prove that a remote operation didnot happen. Response bodies and server exchanges own resources that need closure.

This lesson starts one short-lived server bound only to127.0.0.1 on an operating-system-selected port,then uses the JDK HttpClient to call it. It does not contact an external service or start a persistent deployment. Thehandler accepts an exact path and GET method,returns explicitUTF-8content,and closes every exchange. try-with-resources owns both client and server wrapper in Java 21. Thefixture exposes prefix-routing andmethod-validation mistakes without requiring a web framework.

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

HttpServer.create binds an InetSocketAddress withport0,thengetAddress reveals the actual port. createContext uses prefix matching,so the handler should validate an exact path when that is the contract. HttpRequest specifies a timeout and method. HttpResponse exposes statusCode,headers and body separately. stop(0) releases the owned listener when the fixture closes.

## Worked example / walkthrough

### Example A: Call an owned loopback endpoint

The request reaches a real localHTTPserver. A a returned String alone would not verify routing,status or resource closure.

```java
import java.util.*;

public class Main {
    static final class LocalServer implements AutoCloseable {
        final com.sun.net.httpserver.HttpServer server;boolean closed;
        LocalServer() throws java.io.IOException {
            server=com.sun.net.httpserver.HttpServer.create(new java.net.InetSocketAddress("127.0.0.1",0),0);
            server.createContext("/health",exchange -> {try(exchange){int status;String body;if(!exchange.getRequestURI().getPath().equals("/health")){status=404;body="not found";}else if(!exchange.getRequestMethod().equals("GET")){status=405;body="method not allowed";}else{status=200;body="ok";}byte[] bytes=body.getBytes(java.nio.charset.StandardCharsets.UTF_8);exchange.getResponseHeaders().set("Content-Type","text/plain; charset=utf-8");exchange.sendResponseHeaders(status,bytes.length);try(var output=exchange.getResponseBody()){output.write(bytes);}}});server.start();
        }
        java.net.URI uri(String path){return java.net.URI.create("http://127.0.0.1:"+server.getAddress().getPort()+path);}
        public void close(){server.stop(0);closed=true;}
    }
    public static void main(String[] args) throws Exception {
        try(LocalServer server=new LocalServer();var client=java.net.http.HttpClient.newBuilder().connectTimeout(java.time.Duration.ofSeconds(2)).build()) {
            var response=client.send(java.net.http.HttpRequest.newBuilder(server.uri("/health")).timeout(java.time.Duration.ofSeconds(2)).GET().build(),java.net.http.HttpResponse.BodyHandlers.ofString());
            assert response.statusCode()==200 && response.body().equals("ok");
        }
    }
}

```

**Expected:** status 200 and body ok.

### Example B: Inspect content metadata

Theencoding contract belongs in the response metadata as well as thebyte-writing code. Clients should not guess a platform default.

```java
import java.util.*;

public class Main {
    static final class LocalServer implements AutoCloseable {
        final com.sun.net.httpserver.HttpServer server;boolean closed;
        LocalServer() throws java.io.IOException {
            server=com.sun.net.httpserver.HttpServer.create(new java.net.InetSocketAddress("127.0.0.1",0),0);
            server.createContext("/health",exchange -> {try(exchange){int status;String body;if(!exchange.getRequestURI().getPath().equals("/health")){status=404;body="not found";}else if(!exchange.getRequestMethod().equals("GET")){status=405;body="method not allowed";}else{status=200;body="ok";}byte[] bytes=body.getBytes(java.nio.charset.StandardCharsets.UTF_8);exchange.getResponseHeaders().set("Content-Type","text/plain; charset=utf-8");exchange.sendResponseHeaders(status,bytes.length);try(var output=exchange.getResponseBody()){output.write(bytes);}}});server.start();
        }
        java.net.URI uri(String path){return java.net.URI.create("http://127.0.0.1:"+server.getAddress().getPort()+path);}
        public void close(){server.stop(0);closed=true;}
    }
    public static void main(String[] args) throws Exception {
        try(LocalServer server=new LocalServer();var client=java.net.http.HttpClient.newBuilder().connectTimeout(java.time.Duration.ofSeconds(2)).build()) {
            var response=client.send(java.net.http.HttpRequest.newBuilder(server.uri("/health")).timeout(java.time.Duration.ofSeconds(2)).GET().build(),java.net.http.HttpResponse.BodyHandlers.ofString());
            assert response.statusCode()==200 && response.body().equals("ok");
        }

        try(LocalServer server=new LocalServer();var client=java.net.http.HttpClient.newHttpClient()) {
            var response=client.send(java.net.http.HttpRequest.newBuilder(server.uri("/health")).timeout(java.time.Duration.ofSeconds(2)).GET().build(),java.net.http.HttpResponse.BodyHandlers.ofString());
            assert response.headers().firstValue("Content-Type").orElseThrow().equals("text/plain; charset=utf-8");
        }
    }
}

```

**Expected:** text/plain with UTF-8 charset.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Call an owned loopback endpoint.** Start the fixture and request `GET /health`.
   **Expected:** status 200 and body ok.
   **Verify:** Compare your assertion values or captured diagnostic with status 200 and body ok.

2. **Inspect content metadata.** ReadContent-Type on the successful response.
   **Expected:** text/plain with UTF-8 charset.
   **Verify:** Compare your assertion values or captured diagnostic with text/plain with UTF-8 charset.

3. **Reject an unsupported method.** POSTto/health underaGET-onlycontract.
   **Expected:** status405 and method not allowed body.
   **Verify:** Compare your assertion values or captured diagnostic with status405 and method not allowed body.

4. **Reject a prefix lookalike.** GET/health-extra,which matches the context prefix but not the declared exact path.
   **Expected:** status404.
   **Verify:** Compare your assertion values or captured diagnostic with status404.

5. **Keep error status separate from transport success.** GETanunknownpathandinspectthecompletedresponse.
   **Expected:** HTTP exchange completes with404 rather than a fabricated200.
   **Verify:** Compare your assertion values or captured diagnostic with HTTP exchange completes with404 rather than a fabricated200.

6. **Verify local-only target and closure.** Inspect the bound host and positive ephemeral port,then close the wrapper.
   **Expected:** host 127.0.0.1;port positive; closed flag true.
   **Verify:** Compare your assertion values or captured diagnostic with host 127.0.0.1;port positive; closed flag true.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain HTTP status, Loopback binding, Request timeout in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.httpserver/com/sun/net/httpserver/HttpServer.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Consult `docs/implementation/java-content-status.md` for the actual compile/run receipts. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning for java-028: HTTP services and clients.
Read courses/java/guides/java-028.md and courses/java/lessons/java-028.java. Direct prerequisites: `java-027`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
