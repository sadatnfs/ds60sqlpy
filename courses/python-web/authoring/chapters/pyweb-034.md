## Starting point and result

An internal object often contains more information than an API should expose. A database row might include an owner key, private annotation or password hash. This chapter uses a response model to define the public representation, then deliberately returns an invalid value to show that output validation can reveal an application defect.

## Mechanism: output is a separate contract

Request validation protects the input boundary. Response validation protects the representation produced by the application. They are independent: valid input does not guarantee valid output, and a correctly shaped response does not prove that the underlying operation was authorized.

FastAPI uses the declared response model to serialize and validate the returned object. Fields outside the public model are excluded from the representation. This is a useful final boundary, but sensitive data should still be handled carefully before serialization. Debug logs, exception messages and other code paths can expose values that the response model would have removed.

An invalid response is a server defect, not an ordinary client validation mistake. Returning a client-error code for a broken internal representation would mislead callers into changing a request that may already be valid. Tests should make that distinction visible and retain a safe diagnostic path for maintainers.

## Worked case: expose only the declared representation

The successful route returns an internal mapping that contains both public and private fields. Its declared response model includes only the intended public fields. The TestClient response is checked against the exact allowed key set and values.

Checking only that a private field is absent is weaker than checking the whole public contract. An unrelated accidental field could still appear. An exact representation assertion is appropriate for a small stable fixture, while a larger API may use schema compatibility tests to allow documented additive changes.

The public model can also transform values into their serialized representation. That transformation must remain deliberate. A model that silently coerces an unexpected internal value can hide a defect, so choose strictness and validators according to the contract's purpose rather than treating defaults as universally correct.

## Worked case: an invalid return reveals a server error

The second route returns data that cannot satisfy its response model. With the default TestClient behavior, the framework raises a response-validation exception to the test. With server exceptions converted into HTTP responses, the same defect appears as an internal server error.

These are two observation surfaces for one application failure. The exception form is useful while developing because it retains a precise diagnostic. The HTTP form resembles what a remote caller receives and should avoid exposing internal data. Neither should be mistaken for successful execution merely because the handler function returned something.

A production error handler should record a request correlation identifier and safe error classification. It should not copy the entire invalid response or private model into public JSON. The next chapter builds explicit problem responses for expected and unexpected failures.

## Failure diagnosis and discussion

**Why not return ORM objects directly without a response model?** It makes the public contract depend on internal shape and serialization behavior. An explicit output model gives reviewers a concrete boundary and helps catch accidental disclosure.

**Can a response model replace ownership checks?** No. A correctly filtered object can still belong to another user. Authorization chooses which object may be returned; serialization chooses which part of that object is public.

When an endpoint begins returning 500 after a schema change, inspect the actual returned value and the response model together. Do not remove output validation just to make the test pass. Continue with structured errors so clients can distinguish validation, conflict and unexpected failures reliably.
