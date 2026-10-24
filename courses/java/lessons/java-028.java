// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Call an owned loopback endpoint
    // Start the fixture andGET/health.
    // Expected: status200 andbodyok.

    // Exercise 2: Inspect content metadata
    // ReadContent-Type on the successfulresponse.
    // Expected: text/plain withUTF-8 charset.

    // Exercise 3: Reject an unsupported method
    // POSTto/health underaGET-onlycontract.
    // Expected: status405 andmethod not allowed body.

    // Exercise 4: Reject a prefix lookalike
    // GET/health-extra,whichmatchesthecontextprefixbutnot thedeclaredexactpath.
    // Expected: status404.

    // Exercise 5: Keep error status separate from transport success
    // GETanunknownpathandinspectthecompletedresponse.
    // Expected: HTTPexchangecompletes with404 ratherthan a fabricated200.

    // Exercise 6: Verify local-only target and closure
    // Inspecttheboundhostandpositiveephemeralport,thenclose thewrapper.
    // Expected: host127.0.0.1;portpositive;closedflagtrue.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
