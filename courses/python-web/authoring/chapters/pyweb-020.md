## Starting point and result

Authentication identifies a caller; authorization decides what that caller may do. A successful login does not grant access to every row in a table. This chapter uses two real Flask-Login client sessions and verifies ownership rules on both a list endpoint and an individual-object endpoint.

## Mechanism: trusted identity scopes every lookup

The user loader restores a known user from the signed session. The list endpoint filters records using `current_user.id`. The object endpoint checks the requested record's owner before returning it. Neither endpoint accepts a client-supplied owner field as authority.

Object-level authorization matters even when IDs are difficult to guess. A client can obtain an ID from logs, links or another user. Authorization therefore belongs at the data-access boundary, not in an assumption that an identifier will remain secret. A database implementation should incorporate the caller's permitted scope in its query where practical.

The fixture returns the same 404 shape for an absent record and a record outside the caller's scope. That is a deliberate policy to limit disclosure. Some products use a different documented policy, but they still need a consistent ownership check and must avoid leaking the protected representation.

## Worked case: authenticated list scope

Alice and Bob use separate client cookie jars. After login, each sees only the record they own. Alice also sends a query parameter asking for Bob's owner value; the endpoint still derives its scope from the authenticated identity and returns Alice's record.

The query parameter is not an authorization mechanism. This fixture ignores it because it is outside the supported filter contract. A larger API may choose to reject unsupported filters explicitly. In either design, a caller must not broaden their authority by adding a field to the request.

Separate clients matter in the test. Reusing one cookie jar while switching user assumptions can accidentally turn both requests into the same authenticated principal and hide an authorization defect.

## Worked case: individual-object refusal

Alice requests Bob's record directly by ID, and Bob requests Alice's. Both receive 404. The program also confirms that an anonymous list request receives 401. These cases test different layers: no authenticated identity, an authenticated identity with a permitted list, and an authenticated identity requesting a forbidden object.

A list endpoint that filters correctly does not automatically protect a separate detail endpoint. Similarly, a protected GET does not automatically secure update or deletion routes. Review every operation that can read or mutate the object, including bulk actions, exports and background-job submission.

## Failure diagnosis

If changing an ID reveals another user's data, inspect the query/lookup predicate rather than trying to hide IDs more carefully. If a list leaks records while detail views are protected, compare their scope logic. If an authorization test passes unexpectedly, verify which client session actually made the request.

Permissions can also change after login. A long-lived token or cached user object may carry stale roles. Decide which checks need current database state and how revocation works. This small ownership fixture does not claim to solve organization-wide identity lifecycle or distributed cache invalidation.

## Interview discussion

**Is a random UUID an authorization control?** It can reduce easy enumeration, but it does not prove the caller is allowed to access the object. The access check remains necessary.

**Where should tenant filtering live?** Keep it explicit and consistently applied at the relevant data/service boundary. Repeated ad hoc filters scattered across handlers are easier to omit; an abstraction still needs tests proving it cannot accidentally broaden scope.

## Next step

Apply similarly explicit ownership to filesystem downloads. A submitted filename must not become authority to read any path the process can access.
