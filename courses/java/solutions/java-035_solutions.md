# java-035: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

A small data service combines domain rules, storage and transport contracts. Its correctness is more than an HTTP 200 status: the response grain, columns, ordering, error semantics and resource lifetime must agree. This capstone serves a read-only grouped summary over three authored records. Storage is an explicit in-memory repository, not a simulated JDBC claim. The earlier JDBC lesson separately exercised a real database.

The service binds only to loopback on an ephemeral port and stops when the owned fixture closes. It accepts one GET route with one group query parameter. The group must be a single uppercase letter; unknown valid groups return 404, malformed queries return 400, and unsupported methods return 405. The domain summary is tested directly and through actual HTTP requests. This is a bounded local service demonstration, not a deployed authenticated application.

**Response grain:** The identity of one row or object in a service result.

**Repository port:** The contract through which domain logic reads stored records.

**HTTP adapter:** Code translating validated requests into domain calls and responses.

**Contract test:** A check of observable behavior across a component boundary.

## Reading the reference

A Repository port exposes an immutable row list. The pure summary function filters by group and returns count and integer total. The HTTP adapter validates exact path, method and query structure before calling the core. Since the admitted group is one uppercase ASCII letter, the fixed JSON encoder cannot be influenced by arbitrary quotes. HttpClient requests use timeouts, and every exchange, response body and server instance is closed.

## Exercise 1: Verify the domain summary: change one input

Task: Change `List.of(new Row("a1", "A", 10), new Row("a2", "A", 20), new Row("b1", "B", 5));` to `List.of(new Row("a1", "A", 10), new Row("a2", "A", 20), new Row("b1", "B", 6));` in Example A and predict which assertion fails and why.

The domain result has one object per requested group. It is checked independently of HTTP formatting and status handling.

The unchanged code is the part that Example A adds:

```java
Repository repository = () ->
  List.of(new Row("a1", "A", 10), new Row("a2", "A", 20), new Row("b1", "B", 5));
assert summarize(repository, "A").equals(new Summary("A", 2, 30));
assert summarize(repository, "B").equals(new Summary("B", 1, 5));
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `summarize(repository, "B").equals(new Summary("B", 1, 5))`.

**Verify:** Name the value that makes `summarize(repository, "B").equals(new Summary("B", 1, 5))` false, then restore the line.

## Exercise 2: Read a successful HTTP summary: diagnose an edited check

Task: Example B's new assertion was edited to `\"count\":3`. Explain why it fails for unchanged state and restore it.

The exact body check fixes the public schema and integer representation. The source counts remain independently known.

The unchanged code is the part that Example B adds:

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

**Expected:** The edited run fails with an `AssertionError` from the assertion on `response.statusCode() == 200 && response.body().equals("{\"group\":\"A\",\"count\":2,\"total\":30}")`; the restored assertion passes.

**Verify:** Explain why the edited assertion rejects the state that `response.statusCode() == 200 && response.body().equals("{\"group\":\"A\",\"count\":2,\"total\":30}")` accepts.

## Exercise 3: Report an unknown valid group

Task: GET group C, which passes syntax but has no records.

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

**Expected:** status 404 with not_found error.

**Verify:** Control: changing `var response = send(client, server.uri("/summary?group=C"), "GET");` to `var response = send(client, server.uri("/summary?group=C!"), "GET");` must fail the assertion on `response.statusCode() == 404 && response.body().contains("not_found")`.

## Exercise 4: Reject ambiguous or malformed queries

Task: Send duplicate group parameters and a lowercase group.

The adapter refuses to guess which duplicate value wins. A broader query grammar would need an explicit parser and validation policy.

```java
try (
  DataServer server = new DataServer(repository);
  var client = java.net.http.HttpClient.newHttpClient()
) {
  int duplicate = send(client, server.uri("/summary?group=A&group=B"), "GET").statusCode();
  int lowercase = send(client, server.uri("/summary?group=a"), "GET").statusCode();
  assert duplicate == 400 && lowercase == 400;
}
```

**Expected:** both status 400.

**Verify:** Control: changing `int duplicate = send(client, server.uri("/summary?group=A&group=B"), "GET").statusCode();` to `int duplicate = send(client, server.uri("/summary?group=A&group=B"), "GET!").statusCode();` must fail the assertion on `duplicate == 400 && lowercase == 400`.

## Exercise 5: Reject unsupported methods and path lookalikes

Task: POST to the summary route and GET /summary-extra.

The underlying server uses prefix contexts, so the adapter must enforce its own exact path contract. No write operation is exposed.

```java
try (
  DataServer server = new DataServer(repository);
  var client = java.net.http.HttpClient.newHttpClient()
) {
  int post = send(client, server.uri("/summary?group=A"), "POST").statusCode();
  int lookalike = send(client, server.uri("/summary-extra?group=A"), "GET").statusCode();
  assert post == 405 && lookalike == 404;
}
```

**Expected:** 405 and 404 respectively.

**Verify:** Control: changing `assert post == 405 && lookalike == 404;` to `assert post != 405 && lookalike == 404;` inside the assertion must make it fail.

## Exercise 6: Preserve storage and close the owned listener

Task: Compare the repository before/after requests and close the server.

The read-only service should not mutate its storage. The fixture owns the listener and does not leave a background deployment running.

```java
List<Row> before = repository.rows();
DataServer server = new DataServer(repository);
server.close();
assert server.closed && repository.rows().equals(before) && repository.rows().size() == 3;
```

**Expected:** 3 unchanged records; closed flag true.

**Verify:** Control: changing `assert server.closed && repository.rows().equals(before) && repository.rows().size() == 3;` to `assert server.closed && repository.rows().equals(before) && repository.rows().size() != 3;` inside the assertion must make it fail.

## After comparing the answer

Add a `GET /groups` route to your copy that returns the sorted distinct group names as a JSON array, and write one exact-body check and one 405 check for it.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
