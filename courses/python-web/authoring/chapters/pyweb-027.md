## Starting point and result

FastAPI connects Python type information to HTTP input parsing, validation and documentation. A route is still an ordinary function, but the framework examines its signature before receiving requests. This chapter follows one identifier and one query value from a URL into that function, then compares malformed requests with a successful response.

## Mechanism: declarations become a boundary

A path parameter identifies a resource within the route. A query parameter modifies the requested representation or operation. `Annotated` pairs the Python type with FastAPI metadata such as a numerical lower bound. The annotation does not execute the request itself; the framework builds a validation pipeline from it.

For example, an integer identifier with a lower bound rejects a negative value even though that value is syntactically an integer. A malformed word fails the integer conversion earlier. Both differ from a well-formed identifier that does not exist in storage. Input validation and resource lookup answer different questions and should have separate failure behavior.

A response model also establishes a contract. It describes the fields clients may consume and validates what the application returns. That boundary does not make the underlying function automatically correct. A route can return the wrong resource while still satisfying its schema, so the example checks both status and content.

## Worked case: a valid typed request

Read the complete program before running it. Locate the path declaration, query declaration and response model. Follow the successful request through the converter and the function arguments. The result is a JSON representation whose numeric values remain numbers, rather than arbitrary strings copied from the URL.

The assertion compares the expected response content. This is stronger than checking that the handler ran. It confirms that the values admitted at the boundary reached the intended computation and were serialized through the response contract. The application uses a real TestClient with its context manager, but opens no external port.

Changing a declared limit changes which requests the framework admits. It does not update a database constraint, another service or a previously generated client. In a larger system, those contracts must be reviewed together rather than relying on one decorator as the sole definition of validity.

## Worked case: conversion and range failures

The program submits invalid identifiers and query values. A word where an integer is required fails conversion. A numeric value outside its declared range fails the range rule. The framework returns a structured validation response without running the successful business path.

The distinction matters for debugging. If an endpoint returns validation errors, first inspect the request location, spelling and type. Do not immediately debug the database. Conversely, a valid request followed by a missing-resource response is evidence that the parsing boundary was crossed and lookup semantics now matter.

Framework defaults may allow coercion, such as converting a numeric string into an integer. That behavior is useful for URL text, but may be inappropriate for a strict JSON command. The next chapter treats coercion and partial bodies explicitly instead of assuming every input location should have identical rules.

## Failure diagnosis and discussion

**Why use `Annotated` instead of placing every rule inside the function?** It makes the boundary visible to validation and documentation while leaving business invariants in the function or domain layer. This reduces accidental discrepancies between the advertised input and the admitted input.

**Does a validated response prove correct authorization?** No. Response schemas control representation. Authentication, ownership, tenant isolation and side effects require separate checks. A perfectly shaped response can still disclose another user's data.

If local nested model annotations fail to resolve, inspect annotation evaluation rather than changing assertions. These complete examples keep model classes available when FastAPI examines signatures and remain parseable by the contributor Python version. Continue with partial updates, where omitted and explicit null values have different meanings.
