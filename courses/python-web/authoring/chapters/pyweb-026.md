## Starting point and result

The preceding chapters examined individual mechanisms. This walkthrough combines several in one complete Flask fixture: a login flow, CSRF validation, parameterized SQLite storage and server-assigned ownership. The program uses a temporary database and real client requests, then inspects the final stored rows.

## Mechanism: compose boundaries without weakening them

The application owns its database path and test-only signing key. A CSRF endpoint supplies the framework token. Login verifies a hashed password, clears prior session state and records the authenticated user. The client obtains a fresh token after login because clearing the session changes the token's associated context.

The notes endpoint derives identity from the session. It accepts a bounded title and assigns ownership on the server. SQLite parameters carry both the owner and title as data rather than SQL syntax. A context-managed connection commits a successful insert and closes cleanly.

This fixture has one synthetic account and intentionally small behavior. Its purpose is to verify that the composed mechanisms agree. The owned multi-file workshop adds deployment configuration, persistent service storage, real HTTP and broader lifecycle acceptance.

## Worked case: an authenticated protected write

An anonymous note listing is refused with 401. The client retrieves a CSRF token and submits correct credentials through a protected POST. After login it retrieves a new token, then creates a note with that header. The response is 201, and the subsequent listing returns the intended note.

The program also queries the database after the client context closes. This confirms that the intended owner/title pair was committed to the fixture file. It does not claim that the temporary file will survive the end of the program; its lifecycle is explicitly owned and disposable.

The fresh-token step is meaningful. Tests that bypass CSRF or carry a token from an obsolete session can hide the integration behavior that a browser user will encounter. Here the token is obtained from the real application flow each time its context changes.

## Worked case: missing CSRF and attempted owner assignment

A POST without the CSRF header receives 400 and does not create a note. Another request includes a client-supplied owner field and receives 422 because the write schema accepts only title. The final database still contains only the authorized note.

These checks complement each other. CSRF refusal controls the protected request flow. Schema validation limits writable fields. Authentication provides identity. Server-side ownership assignment scopes stored data. None should be treated as an automatic replacement for the others.

A larger application must also check ownership on individual read/update/delete routes, coordinate concurrent transactions and handle account lifecycle. The prior ownership chapter and the later shared engineering chapters extend those contracts.

## Failure diagnosis

If login succeeds but the next protected POST fails, inspect cookie continuity and whether the session/token context changed. If a rejected request still leaves a row, inspect transaction placement and whether validation occurred before mutation. If user-controlled text changes a query's meaning, inspect parameter binding rather than adding ad hoc string replacements.

Keep test scope explicit. A TestClient run can validate application composition without exercising Gunicorn, network ports, browser assets or TLS. The workshop tests those additional layers and checks persistent state through stop/resume. They should not be inferred from this finite fixture's success.

## Interview discussion

**What does the final database assertion add?** It checks the effect of the request sequence, including that refused writes did not silently mutate storage. Response codes alone can miss incorrect side effects.

**Why clear session state at login?** It provides an intentional transition between anonymous and authenticated context. Any state deliberately carried across that boundary should have a reviewed purpose rather than surviving accidentally.

## Next step

Continue with FastAPI's typed contracts or Django's project conventions. The shared HTTP, authentication and transaction principles remain relevant even when the framework supplies different abstractions.
