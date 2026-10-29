## Starting point and result

HTTP methods communicate the intended semantics of an operation. GET retrieves a representation, PUT replaces a target representation, and DELETE removes a target resource under its documented contract. This chapter compares repeated PUT and DELETE requests and separates idempotence from identical response bytes.

## Mechanism: method semantics describe effects

A safe method is intended to be read-only from the client's perspective. Servers may still record access logs or metrics. An idempotent method has the same intended effect after multiple identical requests as after one. Safety and idempotence are related but different properties: deletion changes state, yet repeated deletion can leave the same final absence.

The sample PUT handler validates a complete representation containing a title. It stores that representation under the ID supplied in the URL. It returns 201 when the resource was newly created and 200 when an existing resource was replaced. The DELETE handler returns 204 after removal and 404 when no resource exists.

These choices form this application's explicit contract. Method names do not enforce it automatically. A handler registered under GET could incorrectly mutate important state, and a handler registered under PUT could append duplicate records. Correct semantics require both design and implementation.

## Worked case: repeated replacement preserves one resource

The client sends the same PUT request twice to `/items/1`. The first creates the resource and returns 201. The second replaces it with the same representation and returns 200. There is still exactly one stored item with the same title.

This is an idempotent effect despite the different status codes. Comparing only response equality would misclassify the operation. Conversely, returning the same status code for two requests would not prove idempotence if the handler secretly created another record each time.

The in-memory dictionary makes the example easy to inspect. It is a temporary fixture, not durable storage or a multi-worker consistency mechanism. A real database implementation must combine its identity/uniqueness rules with transaction behavior, especially when requests arrive concurrently.

## Worked case: repeated deletion leaves absence

The first DELETE removes item one and returns 204 with an empty body. The second DELETE returns 404 because the item is already absent. After either sequence, the resource is absent. The program checks both the state and the empty 204 body.

Some APIs choose to return 204 for an already absent target as well. That can be a valid documented contract. The important point is that a retry does not create a new destructive side effect or operate on an unrelated resource. Authorization must be checked for each request regardless of whether the method is idempotent.

## Failure diagnosis

A repeated request that creates duplicate database rows suggests a mismatch between the declared method and identity handling. An unexpected body on a 204 response can confuse clients that correctly expect no content. A client automatically retrying every POST after a timeout can create duplicate operations; later chapters introduce explicit idempotency keys for suitable workflows.

Timeouts also create uncertainty. A client may lose the response after the server already committed an operation. The client cannot conclude that the operation failed merely because it did not observe success. This is why retry policy must follow method and application semantics, not only exception types.

## Interview discussion

**Must idempotent requests return identical responses?** No. The property concerns intended effects. A second DELETE can observe that the first already removed the resource.

**Does PUT mean partial update?** PUT represents replacement under the target's contract. Partial-update formats and semantics usually belong to a deliberately defined PATCH operation. Neither method automatically provides concurrency control.

## Next step

Inspect body encodings and media types. A correct method and status still need a representation that the receiving client can interpret.
