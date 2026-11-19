// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Call an owned loopback endpoint: change one input
    // Copy Example A into a scratch `Main.java` and change
    // `java.net.http.HttpRequest.newBuilder(server.uri("/health"))` to
    // `java.net.http.HttpRequest.newBuilder(server.uri("/health!"))`. Before running it with
    // `java -ea Main`, predict which assertion fails and which value it now sees; then run it
    // and restore the original line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `response.statusCode() == 200 && response.body().equals("ok")`. Restoring the original
    // line brings back the worked observation: status 200 and body ok.

    // Exercise 2: Inspect content metadata: diagnose an edited check
    // A careless edit changed the assertion that Example B adds after Example A so that it reads
    // `.equals("text/plain; charset=utf-9");`. Run Example B with that line, explain why the
    // edited assertion now fails for the same program state, and restore it.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `response.headers().firstValue("Content-Type").orElseThrow().equals("text/plain;
    // charset=utf-8")`; after it the line reads `.equals("text/plain; charset=utf-8");` again
    // and text/plain with UTF-8 charset.

    // Exercise 3: Reject an unsupported method
    // POST to /health under a GET-only contract.
    // Expected: status 405 and method not allowed body.

    // Exercise 4: Reject a prefix lookalike
    // GET/health-extra, which matches the context prefix but not the declared exact path.
    // Expected: status 404.

    // Exercise 5: Keep error status separate from transport success
    // GET an unknown path and inspect the completed response.
    // Expected: HTTP exchange completes with 404 rather than a fabricated 200.

    // Exercise 6: Verify local-only target and closure
    // Inspect the bound host and positive ephemeral port, then close the wrapper.
    // Expected: host 127.0.0.1; port positive; closed flag true.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
