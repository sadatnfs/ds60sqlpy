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

## Exercise 1: Verify the domain summary: change one input

Task: Copy Example A into a scratch `Main.java` and change `List.of(new Row("a1", "A", 10), new Row("a2", "A", 20), new Row("b1", "B", 5));` to `List.of(new Row("a1", "A", 10), new Row("a2", "A", 20), new Row("b1", "B", 6));`. Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; then run it and restore the original line.

The domain result has one object per requested group. It is checked independently of HTTP formatting and status handling.

The unchanged code is the part that Example A adds:

```java
Repository repository = () ->
  List.of(new Row("a1", "A", 10), new Row("a2", "A", 20), new Row("b1", "B", 5));
assert summarize(repository, "A").equals(new Summary("A", 2, 30));
assert summarize(repository, "B").equals(new Summary("B", 1, 5));
```

**Expected:** The changed run fails with an `AssertionError` from the assertion on `summarize(repository, "B").equals(new Summary("B", 1, 5))`. Restoring the original line brings back the worked observation: A count 2, total 30; B count 1, total 5.

**Verify:** Compare your written prediction with the reported `AssertionError` and its stack-trace line, and name the value that made `summarize(repository, "B").equals(new Summary("B", 1, 5))` false. After restoring the line, the program completes without an `AssertionError` again.

## Exercise 2: Read a successful HTTP summary: diagnose an edited check

Task: A careless edit changed the assertion that Example B adds after Example A so that it reads `\"count\":3`. Run Example B with that line, explain why the edited assertion now fails for the same program state, and restore it.

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

**Expected:** Before the repair the run fails with an `AssertionError` from the assertion on `response.statusCode() == 200 && response.body().equals("{\"group\":\"A\",\"count\":2,\"total\":30}")`; after it the line reads `\"count\":2` again and status 200 and exact JSON with count 2, total 30.

**Verify:** Keep the failing and the repaired runs. Explain why the edited assertion rejects the same program state that `response.statusCode() == 200 && response.body().equals("{\"group\":\"A\",\"count\":2,\"total\":30}")` accepts.

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

**Verify:** Keep an assertion equivalent to `response.statusCode() == 404 && response.body().contains("not_found")`. As a control, change `var response = send(client, server.uri("/summary?group=C"), "GET");` to `var response = send(client, server.uri("/summary?group=C!"), "GET");`: the run must fail with an `AssertionError` from the assertion on `response.statusCode() == 404 && response.body().contains("not_found")`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `duplicate == 400 && lowercase == 400`. As a control, change `int duplicate = send(client, server.uri("/summary?group=A&group=B"), "GET").statusCode();` to `int duplicate = send(client, server.uri("/summary?group=A&group=B"), "GET!").statusCode();`: the run must fail with an `AssertionError` from the assertion on `duplicate == 400 && lowercase == 400`. Restore the line before continuing.

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

**Verify:** Keep an assertion equivalent to `post == 405 && lookalike == 404`. As a control, change `assert post == 405 && lookalike == 404;` to `assert post != 405 && lookalike == 404;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

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

**Verify:** Keep an assertion equivalent to `server.closed && repository.rows().equals(before) && repository.rows().size() == 3`. As a control, change `assert server.closed && repository.rows().equals(before) && repository.rows().size() == 3;` to `assert server.closed && repository.rows().equals(before) && repository.rows().size() != 3;` inside it: the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
