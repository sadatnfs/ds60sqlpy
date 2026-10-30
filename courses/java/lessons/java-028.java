// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Call an owned loopback endpoint
    // Start the fixture and request `GET /health`.
    // Expected: status 200 and body ok.

    // Exercise 2: Inspect content metadata
    // ReadContent-Type on the successful response.
    // Expected: text/plain with UTF-8 charset.

    // Exercise 3: Reject an unsupported method
    // POSTto/health underaGET-onlycontract.
    // Expected: status405 and method not allowed body.

    // Exercise 4: Reject a prefix lookalike
    // GET/health-extra,which matches the context prefix but not the declared exact path.
    // Expected: status404.

    // Exercise 5: Keep error status separate from transport success
    // GETanunknownpathandinspectthecompletedresponse.
    // Expected: HTTP exchange completes with404 rather than a fabricated200.

    // Exercise 6: Verify local-only target and closure
    // Inspect the bound host and positive ephemeral port,then close the wrapper.
    // Expected: host 127.0.0.1;port positive; closed flag true.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
