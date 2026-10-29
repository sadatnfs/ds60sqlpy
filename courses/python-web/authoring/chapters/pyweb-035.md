## Starting point and result

Clients need stable error semantics, but an exception's internal text is rarely an appropriate public contract. This chapter defines a small problem-response shape for invalid input, a known resource conflict and an unexpected server failure. It verifies both HTTP status and response content using real FastAPI exception handlers.

## Mechanism: classify failures before serializing them

A problem response contains a type identifier, human-readable title, status and instance. The type identifies a class of problem rather than a particular stack trace. Additional fields can describe safe validation locations or machine-readable codes. The response uses `application/problem+json` so callers can recognize the representation.

The fixture uses original URN identifiers for its small example. A real API should document stable types and avoid changing their meaning casually. Human wording can improve over time, while a programmatic client should branch on stable fields rather than substring matches inside an exception message.

Expected domain failures and unexpected defects deserve different treatment. A capacity conflict can return 409 with a clear public explanation. An invalid request can return 422 with safe field locations. An unhandled internal exception should produce a generic 500 response while detailed diagnostics remain available through controlled internal logging.

## Worked case: classify a valid command and an expected conflict

The reserve endpoint accepts a bounded positive amount. An amount within the fixture's capacity returns a successful reservation. A larger valid amount reaches domain logic and raises the named Conflict exception. Its handler returns the conflict problem type and status 409.

This separates input validity from business availability. The number can be a valid positive integer while the requested operation cannot currently be fulfilled. Collapsing both situations into a generic validation response would hide the distinction from clients deciding whether to correct input or retry later.

The test examines the response media type, status and problem fields. A JSON body saying status 409 with an actual HTTP 200 would be an inconsistent contract, so both layers are asserted. The response does not need to expose the Python exception class to communicate the domain condition.

## Worked case: invalid input and an internal defect

An amount below the schema's lower bound fails request validation. The custom handler extracts safe location and error-code information instead of echoing arbitrary submitted content. A separate endpoint raises an exception containing a private diagnostic phrase; the public 500 response must not include that phrase.

TestClient is configured to observe error responses rather than reraising server exceptions. This is intentional for the public-contract case. Developer tests can also retain the default reraising mode when they need the original traceback. Choosing one observation mode does not make the other behavior disappear.

Validation errors can contain sensitive inputs, especially for passwords, tokens or uploaded metadata. A generic dump of the framework exception may disclose them. Build the public error representation from an explicit allowlist and keep diagnostic collection proportionate to the operational need.

## Failure diagnosis and discussion

**Should every exception be converted to a 409?** No. That would label programming errors and infrastructure failures as expected conflicts and could trigger inappropriate client behavior. Handle only conditions whose semantics are understood.

**Why include an instance field?** It helps connect the problem to the attempted resource or operation. It should avoid sensitive query values or credentials and need not reveal internal file paths.

If a handler produces the right body but the wrong status, inspect the Response construction rather than only the serialized dictionary. If sensitive text appears, inspect error extraction and logging independently. Continue with bearer authentication, where signature checks and claim validation become another explicit boundary before domain code runs.
