// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Verify the domain summary: change one input
    // Copy Example A into a scratch `Main.java` and change `List.of(new Row("a1", "A", 10), new
    // Row("a2", "A", 20), new Row("b1", "B", 5));` to `List.of(new Row("a1", "A", 10), new
    // Row("a2", "A", 20), new Row("b1", "B", 6));`. Before running it with `java -ea Main`,
    // predict which assertion fails and which value it now sees; then run it and restore the
    // original line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `summarize(repository, "B").equals(new Summary("B", 1, 5))`. Restoring the original line
    // brings back the worked observation: A count 2, total 30; B count 1, total 5.

    // Exercise 2: Read a successful HTTP summary: diagnose an edited check
    // A careless edit changed the assertion that Example B adds after Example A so that it reads
    // `\"count\":3`. Run Example B with that line, explain why the edited assertion now fails
    // for the same program state, and restore it.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `response.statusCode() == 200 &&
    // response.body().equals("{\"group\":\"A\",\"count\":2,\"total\":30}")`; after it the line
    // reads `\"count\":2` again and status 200 and exact JSON with count 2, total 30.

    // Exercise 3: Report an unknown valid group
    // GET group C, which passes syntax but has no records.
    // Expected: status 404 with not_found error.

    // Exercise 4: Reject ambiguous or malformed queries
    // Send duplicate group parameters and a lowercase group.
    // Expected: both status 400.

    // Exercise 5: Reject unsupported methods and path lookalikes
    // POST to the summary route and GET /summary-extra.
    // Expected: 405 and 404 respectively.

    // Exercise 6: Preserve storage and close the owned listener
    // Compare the repository before/after requests and close the server.
    // Expected: 3 unchanged records; closed flag true.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
