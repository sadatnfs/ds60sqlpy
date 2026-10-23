# java-028: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

HTTP is a request/response protocol with method,path,status,headers andbody. A successful network exchange can still return an application error such as404 or400. Aclient must inspect status before interpreting thebody. Timeouts bound waiting but do not prove that a remote operation didnot happen. Response bodies andserver exchanges own resources that need closure.

This lesson starts one short-lived server bound only to127.0.0.1 on an operating-system-selected port,then uses theJDKHttpClient tocall it. It doesnot contact anexternal service orstart a persistent deployment. Thehandler accepts anexactpath andGETmethod,returns explicitUTF-8content,andcloses everyexchange. try-with-resources owns both client andserver wrapper inJava21. Thefixture exposes prefix-routing andmethod-validation mistakes without requiring a web framework.

**HTTP status:** The response code describing protocol/application outcome.

**Loopback binding:** A listener restricted to thelocal host network interface.

**Request timeout:** A bound on client waiting for a request.

**Exchange lifetime:** Ownership of request/response streams andconnection state.

## Reading the reference

HttpServer.create binds anInetSocketAddress withport0,thengetAddress reveals the actualport. createContext uses prefixmatching,so thehandler should validate anexactpath when that is thecontract. HttpRequest specifies a timeout andmethod. HttpResponse exposes statusCode,headers andbody separately. stop(0) releases the ownedlistener when thefixture closes.

## Exercise 1: Call an owned loopback endpoint

Task: Start the fixture andGET/health.

The request reaches a real localHTTPserver. A returnedStringalonewouldnotverify routing,status orresourceclosure.

```java
try(LocalServer server=new LocalServer();var client=java.net.http.HttpClient.newBuilder().connectTimeout(java.time.Duration.ofSeconds(2)).build()) {
    var response=client.send(java.net.http.HttpRequest.newBuilder(server.uri("/health")).timeout(java.time.Duration.ofSeconds(2)).GET().build(),java.net.http.HttpResponse.BodyHandlers.ofString());
    assert response.statusCode()==200 && response.body().equals("ok");
}
```

**Expected:** status200 andbodyok.

**Verify:** Compare the program values or named exception with status200 andbodyok. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Inspect content metadata

Task: ReadContent-Type on the successfulresponse.

Theencoding contract belongs in the response metadata as well as thebyte-writing code. Clients should not guess aplatform default.

```java
try(LocalServer server=new LocalServer();var client=java.net.http.HttpClient.newHttpClient()) {
    var response=client.send(java.net.http.HttpRequest.newBuilder(server.uri("/health")).timeout(java.time.Duration.ofSeconds(2)).GET().build(),java.net.http.HttpResponse.BodyHandlers.ofString());
    assert response.headers().firstValue("Content-Type").orElseThrow().equals("text/plain; charset=utf-8");
}
```

**Expected:** text/plain withUTF-8 charset.

**Verify:** Compare the program values or named exception with text/plain withUTF-8 charset. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Reject an unsupported method

Task: POSTto/health underaGET-onlycontract.

A routeexistingdoesnotmakeeverymethodvalid. Validation occursbeforeperformingdomainwork.

```java
try(LocalServer server=new LocalServer();var client=java.net.http.HttpClient.newHttpClient()) {
    var request=java.net.http.HttpRequest.newBuilder(server.uri("/health")).timeout(java.time.Duration.ofSeconds(2)).POST(java.net.http.HttpRequest.BodyPublishers.noBody()).build();
    var response=client.send(request,java.net.http.HttpResponse.BodyHandlers.ofString());assert response.statusCode()==405 && response.body().equals("method not allowed");
}
```

**Expected:** status405 andmethod not allowed body.

**Verify:** Compare the program values or named exception with status405 andmethod not allowed body. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Reject a prefix lookalike

Task: GET/health-extra,whichmatchesthecontextprefixbutnot thedeclaredexactpath.

HttpServercontextmatchingisprefix-based. Anexactapplicationroute needsitsownpathcheck toavoidaccidentallyacceptinglookalikes.

```java
try(LocalServer server=new LocalServer();var client=java.net.http.HttpClient.newHttpClient()) {
    var response=client.send(java.net.http.HttpRequest.newBuilder(server.uri("/health-extra")).timeout(java.time.Duration.ofSeconds(2)).GET().build(),java.net.http.HttpResponse.BodyHandlers.ofString());assert response.statusCode()==404;
}
```

**Expected:** status404.

**Verify:** Compare the program values or named exception with status404. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Keep error status separate from transport success

Task: GETanunknownpathandinspectthecompletedresponse.

Atransport-levelsuccessdoesnotmean thedomainoperation succeeded. Clientlogicshouldbranchonstatusbeforeparsingasuccessschema.

```java
try(LocalServer server=new LocalServer();var client=java.net.http.HttpClient.newHttpClient()) {
    var response=client.send(java.net.http.HttpRequest.newBuilder(server.uri("/missing")).timeout(java.time.Duration.ofSeconds(2)).GET().build(),java.net.http.HttpResponse.BodyHandlers.ofString());assert response.statusCode()==404;
}
```

**Expected:** HTTPexchangecompletes with404 ratherthan a fabricated200.

**Verify:** Compare the program values or named exception with HTTPexchangecompletes with404 ratherthan a fabricated200. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Verify local-only target and closure

Task: Inspecttheboundhostandpositiveephemeralport,thenclose thewrapper.

Thefixtureownsandstopsitslistener. Itdoesnotchangeasharedserver orleaveadeploymentrunningafterthelesson.

```java
LocalServer owned=new LocalServer();assert owned.uri("/health").getHost().equals("127.0.0.1") && owned.uri("/health").getPort()>0;owned.close();assert owned.closed;
```

**Expected:** host127.0.0.1;portpositive;closedflagtrue.

**Verify:** Compare the program values or named exception with host127.0.0.1;portpositive;closedflagtrue. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
