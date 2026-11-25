// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Verify the domain summary: change one input
    // Change `List.of(new Row("a1", "A", 10), new Row("a2", "A", 20), new Row("b1", "B", 5));`
    // to `List.of(new Row("a1", "A", 10), new Row("a2", "A", 20), new Row("b1", "B", 6));` in
    // Example A and predict which assertion fails and why.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `summarize(repository, "B").equals(new Summary("B", 1, 5))`.

    // Exercise 2: Read a successful HTTP summary: diagnose an edited check
    // Example B's new assertion was edited to `\"count\":3`. Explain why it fails for unchanged
    // state and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `response.statusCode() == 200 &&
    // response.body().equals("{\"group\":\"A\",\"count\":2,\"total\":30}")`; the restored
    // assertion passes.

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
