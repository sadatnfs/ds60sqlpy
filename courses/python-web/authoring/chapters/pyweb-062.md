## Starting point and result

The Django branch culminates in a small authenticated notes flow using real models, ModelForms, sessions and CSRF middleware. The program tests successful creation, owner-scoped listing and refused writes, then inspects the actual row count. It keeps password verification and deployment acceptance as separately identified evidence.

## Mechanism: use trusted identity throughout the write

The model stores a title and a foreign key to the user. The ModelForm exposes only title. The view requires an authenticated user, rejects unexpected POST keys, validates the form, constructs the object with commit=False and assigns request.user as owner before saving.

The list path filters by the same authenticated owner. This keeps collection visibility aligned with creation semantics. A real application also needs equivalent detail/update/delete scoping and a transaction design for operations involving several models.

Clients use enforce_csrf_checks so the test does not bypass the middleware. They use force_login to establish known principals because password verification has its own complete chapter. These choices make the claim precise: this test qualifies composed authorization, CSRF and persistence behavior under established identities.

## Worked case: create a note and list it as the owner

Alice's client obtains a real CSRF token and posts a valid title. The view saves one row owned by Alice and returns 201. Alice's subsequent list contains that row, while Bob's list is empty.

The database relationship is real, and the model table is prepared inside an explicitly disposable fixture. The program also runs the framework migrations needed by authentication and sessions. It does not pretend that the compact schema setup for the teaching model is a reviewed production migration history.

The successful sequence demonstrates that the token, cookie session, request.user and database owner agree. Testing those pieces only in isolation could miss an integration mistake such as using an anonymous identity after session setup or assigning owner from the submitted form.

## Worked case: missing CSRF and attempted owner assignment

A POST without the token is refused with 403 before mutation. Another POST includes owner as an unexpected field and is refused with 400. The final database count remains one, so neither refused request created a hidden row.

The explicit unknown-key check complements ModelForm's writable-field list. ModelForms normally ignore undeclared keys; this endpoint chooses a stricter API-like policy and tests it. The title field remains validated by the form rather than by a separate inconsistent string check.

Bob's empty list also illustrates collection authorization. A detail route that checks ownership is insufficient if the collection endpoint returns all rows. Authorization must be consistent across each way of reading or modifying the resource.

## Failure diagnosis and discussion

**Why is there both a fields list and an unexpected-key check?** They express different contracts. The fields list limits what the form can write; the key check makes attempts to supply other fields visibly invalid for this endpoint.

**Why inspect the database after refused requests?** It verifies the absence of unauthorized side effects. Correct response codes alone cannot establish that storage remained unchanged.

If a valid POST fails after login, inspect token freshness and client cookie continuity. If the wrong owner is stored, inspect where request.user is obtained and assigned. If restart loses data, inspect database placement relative to the container rather than changing form code.

Continue with the shared engineering chapters. They address deadlines, retries, outboxes, database contention, observability and deployment across all three frameworks, using the same distinction between a declared contract and its actual runtime evidence.
