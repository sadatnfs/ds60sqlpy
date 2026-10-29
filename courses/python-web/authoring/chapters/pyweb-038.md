## Starting point and result

Authentication establishes who is calling. Authorization determines what that caller may do to a particular resource. This chapter separates permission scopes from tenant and owner predicates, demonstrating why a broadly capable token must not grant access to another tenant's object.

## Mechanism: combine operation and resource checks

A scope expresses permission for a class of operation, such as writing notes. A role often groups permissions for an organizational function. A tenant boundary separates customer or workspace data. Ownership identifies the principal responsible for a particular object. These dimensions can overlap, but none should be assumed to imply all the others.

FastAPI's SecurityScopes carries the scopes required by the endpoint into a dependency. The dependency verifies that the synthetic credential includes those scopes. The route then looks up the object within the verified tenant and owner context. That second check is necessary even when the scope is correct.

The example uses fixed opaque fixture tokens to focus on authorization. They are not JWTs, and the tokenUrl declaration does not create an OAuth server. Cryptographic authentication was tested in the preceding chapter. Keeping that boundary explicit prevents a short teaching fixture from being mistaken for a production identity implementation.

## Worked case: the owner with the required scope

The owner has a credential containing both read and write scopes. The dependency admits the write operation. The route finds the note, checks its tenant and owner against the verified identity, then updates the title. The program asserts the successful response and the final stored title.

The identity comes from the credential mapping, not a request field named owner or tenant. A client may choose which resource to request, but it cannot choose the authority under which the server performs that request. Real database queries should include the authorized scope in their predicates rather than fetching a globally visible row and hoping later code remembers to filter it.

For batch operations, apply the same rule to every affected row. Checking the first object and assuming the rest share its owner is a common source of partial unauthorized writes.

## Worked case: distinguish three refusals

An unknown credential receives 401 because identity is not established. The owner's read-only credential receives 403 because its operation scope is insufficient. Another tenant's writer receives 404 because the requested note is outside that caller's visible resource scope.

The 404 policy avoids revealing whether another tenant's identifier exists. Some APIs use 403 under a different disclosure policy; the choice must be consistent and documented. What matters here is that the operation has no unauthorized side effect and that the tests exercise all three boundaries.

A numerical identifier is not an authorization secret. Sequential or guessable IDs can be perfectly acceptable when every access is scoped correctly. Replacing them with random IDs can reduce enumeration convenience, but it does not repair a missing ownership predicate.

## Failure diagnosis and discussion

**Why does a write scope not authorize every write?** The scope names a capability class. Resource ownership, tenant membership and business state further restrict where that capability applies.

**Should authorization live only in the UI?** No. The server must enforce it for every entrypoint, including direct HTTP calls, background jobs and administrative paths that share the same domain operation.

If one tenant can see another's data, inspect query scoping and cached-result keys. A cache keyed only by resource ID can bypass otherwise correct per-request filtering. Continue with files and streaming, where filesystem identity and response lifetime create additional resource boundaries.
