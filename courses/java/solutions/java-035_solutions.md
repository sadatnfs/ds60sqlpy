# java-035: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A small data service combines domain rules, storage and transport contracts. Its correctness is more than an HTTP 200 status: the response grain, columns, ordering, error semantics and resource lifetime must agree. This capstone serves a read-only grouped summary over three authored records. Storage is an explicit in-memory repository, not a simulated JDBC claim. The earlier JDBC lesson separately exercised a real database.

The service binds only to loopback on an ephemeral port and stops when the owned fixture closes. It accepts one GET route with one group query parameter. The group must be a single uppercase letter; unknown valid groups return 404, malformed queries return 400, and unsupported methods return 405. The domain summary is tested directly and through actual HTTP requests. This is a bounded local service demonstration, not a deployed authenticated application.

**Response grain:** The identity of one row or object in a service result.

**Repository port:** The contract through which domain logic reads stored records.

**HTTP adapter:** Code translating validated requests into domain calls and responses.

**Contract test:** A check of observable behavior across a component boundary.

## Reading the reference

A Repository port exposes an immutable row list. The pure summary function filters by group and returns count and integer total. The HTTP adapter validates exact path, method and query structure before calling the core. Since the admitted group is one uppercase ASCII letter, the fixed JSON encoder cannot be influenced by arbitrary quotes. HttpClient requests use timeouts, and every exchange, response body and server instance is closed.

## Exercise 1: Verify the domain summary

Task: Summarize group A over amounts 10,20 and group B over 5.

The domain result has one object per requested group. It is checked independently of HTTP formatting and status handling.

```java
Repository repository = () ->
  List.of(new Row("a1", "A", 10), new Row("a2", "A", 20), new Row("b1", "B", 5));
assert summarize(repository, "A").equals(new Summary("A", 2, 30));
assert summarize(repository, "B").equals(new Summary("B", 1, 5));
```

**Expected:** A count 2, total 30; B count 1, total 5.

**Verify:** Compare the program values or named exception with A count 2, total 30; B count 1, total 5. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Read a successful HTTPsummary

Task: GET/summary?group=Afromtheownedserver.

The exact body check fixes the public schema and integer representation. The source counts remain independently known.

```java
try (
  DataServer server = new DataServer(repository);
  var client = java.net.http.HttpClient.newHttpClient()
) {
  var response = send(client, server.uri("/summary?group=A"), "GET");
  assert response.statusCode() == 200 &&
  response.body().equals("{\"group\":\"A\",\"count\":2,\"total\":30}");
}
```

**Expected:** status 200 andexactJSONwithcount2,total 30.

**Verify:** Compare the program values or named exception with status 200 andexactJSONwithcount2,total 30. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Report an unknown valid group

Task: GETgroupC,which passes syntax buthasnorecords.

A valid but absent domain identity differs from malformed input. Keeping the status distinction helps clients respond appropriately.

```java
try (
  DataServer server = new DataServer(repository);
  var client = java.net.http.HttpClient.newHttpClient()
) {
  var response = send(client, server.uri("/summary?group=C"), "GET");
  assert response.statusCode() == 404 && response.body().contains("not_found");
}
```

**Expected:** status404 withnot_found error.

**Verify:** Compare the program values or named exception with status404 withnot_found error. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Reject ambiguous or malformed queries

Task: Send duplicate group parameters andalowercasegroup.

The adapter refuses to guess which duplicate value wins. A broader query grammar would need an explicit parser and validation policy.

```java
try (
  DataServer server = new DataServer(repository);
  var client = java.net.http.HttpClient.newHttpClient()
) {
  assert send(client, server.uri("/summary?group=A&group=B"), "GET").statusCode() == 400;
  assert send(client, server.uri("/summary?group=a"), "GET").statusCode() == 400;
}
```

**Expected:** bothstatus400.

**Verify:** Compare the program values or named exception with bothstatus400. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Reject unsupported methods andpathlookalikes

Task: POST to the summary route andGET/summary-extra.

The underlying server uses prefix contexts,so theadaptermustenforceitsownexactpathcontract. No write operation is exposed.

```java
try (
  DataServer server = new DataServer(repository);
  var client = java.net.http.HttpClient.newHttpClient()
) {
  assert send(client, server.uri("/summary?group=A"), "POST").statusCode() == 405;
  assert send(client, server.uri("/summary-extra?group=A"), "GET").statusCode() == 404;
}
```

**Expected:** 405 and404 respectively.

**Verify:** Compare the program values or named exception with 405 and404 respectively. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Preserve storage and close the owned listener

Task: Comparetherepositorybefore/afterrequests and close the server.

The read-onlyservice should not mutate its storage. Thefixture owns the listener and does not leave a background deployment running.

```java
List<Row> before = repository.rows();
DataServer server = new DataServer(repository);
server.close();
assert server.closed && repository.rows().equals(before) && repository.rows().size() == 3;
```

**Expected:** 3 unchanged records; closed flag true.

**Verify:** Compare the program values or named exception with 3 unchanged records; closed flag true. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
