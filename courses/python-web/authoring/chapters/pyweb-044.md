## Starting point and result

The FastAPI branch now combines a typed write schema, identity dependency, SQL storage, response filtering and object-level access. This chapter walks through one complete note creation and read sequence, then proves that rejected writes and cross-user reads do not alter or expose the stored record.

## Mechanism: compose the request into one accountable operation

The request schema permits only a bounded title. A dependency maps a synthetic bearer credential to an identity. The database write assigns that identity as owner on the server and uses parameter binding. The response model exposes identifier and title while excluding the internal owner field.

The read path includes both identifier and owner in its SQL predicate. This makes visibility part of data access rather than a later formatting decision. A row outside the caller's scope appears missing under this fixture's disclosure policy.

The program uses a temporary SQLite database and fixed fixture credentials. It performs real SQL and framework request handling, but it is not a deployed identity provider, PostgreSQL service or network acceptance test. Those layers belong to the owned multi-file workshop and have separate receipts.

## Worked case: create and retrieve an owned note

Alice's credential creates a note and receives 201. The response contains exactly the public fields. A subsequent GET under Alice's identity returns the same representation. The final database query confirms one committed row with the server-assigned owner.

Follow the boundaries in order: validate the command, establish identity, execute the authorized parameterized write, commit, then serialize the allowed representation. An implementation that mutates storage before checking identity would violate this order even if its eventual error response looked correct.

The database stores owner because later authorization needs it, while the API response omits owner because this representation does not require it. Internal persistence shape and external representation are allowed to differ. Keeping them explicit makes future schema changes easier to review.

## Worked case: unauthorized reads and writes have no effect

Bob requests Alice's identifier and receives 404. A write that tries to provide owner is rejected by the strict request schema. An anonymous write receives 401. After all those requests, the database still contains only Alice's original note.

That final effect check is stronger than checking three refusal codes. It detects accidental writes performed before a validation or authentication exception. It also catches an implementation that silently creates a second record while returning an error.

The read predicate is important even when identifiers are difficult to guess. An identifier can leak through logs, links or browser history. Access control must continue to work when an attacker knows the identifier; obscurity is not a substitute for the owner condition.

## Failure diagnosis and discussion

**Which part changes when replacing fixture tokens with verified JWTs?** The authentication dependency changes, while the route should continue consuming a trusted principal. The ownership and transaction rules remain necessary.

**Which part changes when moving to PostgreSQL?** Connection management, migrations and concurrency behavior require review. Parameter binding and explicit ownership remain conceptual invariants, but driver syntax and transaction semantics must be tested in the real database.

If the response is correct but the final row count is wrong, inspect side-effect ordering. If Bob can read Alice's note, inspect SQL scoping rather than the response model. If a restart loses data, inspect where the database lives relative to the container.

The next branch introduces Django's project conventions and integrated components. The shared engineering chapters later compare these frameworks through the same operational questions: who owns a request, which state is durable, how failures are observed and how a service is resumed safely.
