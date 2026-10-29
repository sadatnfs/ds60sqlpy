## Starting point and result

Django REST Framework adds serializers, API views, routers and other tools for HTTP APIs. This chapter uses a serializer and a ViewSet to create and list notes, while making clear which fields are writable and how validation failures differ from successful creation.

## Mechanism: serializer and view responsibilities differ

A serializer validates incoming data and produces a representation. A ViewSet groups related actions such as list and create. A router connects those actions to URL patterns. These abstractions do not automatically provide persistence or authorization; the application still defines those behaviors.

The fixture's serializer marks identifier read-only and validates a bounded title. Its custom validator strips whitespace and rejects content that becomes too short. The ViewSet calls is_valid with raise_exception so the framework produces its standard validation response for invalid input.

The records live in a small in-memory list to keep the serializer/router mechanism self-contained. This is not a durable database or a multi-worker store. ModelSerializer and database-backed generic views can connect these ideas to real models, but they still require explicit field and ownership review.

## Worked case: create through a real router and serializer

The APIClient sends a title with surrounding whitespace and a client-supplied identifier. The serializer ignores the read-only identifier for writing, the server assigns its own identifier and the stored title is normalized. The response has 201 and the exact public representation.

The router exposes the collection route from the registered ViewSet. The program then lists records and checks the expected representation. This verifies that create and list agree on the serializer's public shape rather than returning unrelated dictionaries by accident.

A read-only field is not the same as a strict unknown-field refusal. If an API promises to reject supplied identifiers or undeclared fields, it must implement that policy and test it explicitly. The lesson reports the actual DRF behavior instead of implying an input key was rejected when it was ignored.

## Worked case: validation failure leaves the collection unchanged

A title whose meaningful length is too short receives 400. The later list still contains only the earlier valid record. This checks both the response and the absence of an unintended side effect.

Validation must happen before the application appends or commits the object. A common mistake is to construct and persist a partial object before calling all validators, then catch an error and return a refusal while leaving the object behind.

DRF's validation status differs from FastAPI's default 422 in earlier chapters. That is not inherently a defect. An API should adopt and document a coherent convention and clients should follow its contract. Framework comparison is more useful when it identifies actual semantics instead of declaring one default universally correct.

## Failure diagnosis and discussion

**Does a router create an authorization policy?** No. It maps actions to URLs. Authentication, permissions and scoped querysets remain separate responsibilities.

**Why separate input and output field decisions?** Some values are server-assigned or sensitive. A serializer can expose a value for reading while refusing or ignoring it for writing, according to the documented contract.

If a route is missing, inspect router registration and trailing-slash conventions. If a field disappears, inspect read-only/write-only flags and serializer construction. Continue with authentication, pagination and throttling to examine the additional API boundaries around these actions.
