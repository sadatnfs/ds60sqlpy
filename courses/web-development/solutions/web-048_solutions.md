# web-048: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-048.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Explain which data is in the browser and which is on the server.

**Expected answer:** The browser normally holds an identifier while server storage holds the associated session state.

**Approach:** Place each item: the browser stores the session identifier cookie, while the server stores the session data that identifier points to.

**Why:** The cookie normally holds only a random session identifier, while the session data stays on the server.

**Plausible wrong approach:** Saying the browser stores the user's role or id fails because that would let the client edit its own permissions.

**How to verify:** Your diagram shows only an identifier crossing the network, with user data kept in server storage. The only cookie the server sets carries a random identifier and no account details.

## Exercise 2: Add a fixed-clock inactivity check.

**Expected evidence:** The test can inspect the exact expiry boundary reproducibly.

**Approach:** Pass `$now` into the check as a fixed integer and compare `$now - $session['last_seen']` with 1800.

**Why:** An injected clock lets a test place last activity exactly at the boundary.

**Plausible wrong approach:** Calling `time()` inside the check fails because the boundary moves every second and the test cannot hit it exactly.

**How to verify:** With `last_seen` at 1000, the check returns false for 2800 and true for 2801.

## Exercise 3: Model session activity and expiry with explicit state transitions.

**Expected evidence:** An expired session is rejected and a valid activity update preserves the declared identity.

**Approach:** Write a function that takes a session array and `$now`, returns rejected when expired, and otherwise returns a copy with an updated `last_seen`.

**Why:** Explicit transitions make expiry and activity updates testable without a real server.

**Plausible wrong approach:** Updating `last_seen` before checking expiry fails because an expired session is refreshed and never rejected.

**How to verify:** An expired input returns rejected and its `last_seen` is unchanged, while a valid one gets the new time.

## Exercise 4: Explain why a client-supplied user id is not a trusted session.

**Expected answer:** A caller can choose that value unless a server-verified credential establishes the identity.

**Approach:** Trace where the user id comes from: request data is client controlled, while server session storage is set only after a verified login.

**Why:** The caller controls every submitted field, so identity must come from a server-verified session.

**Plausible wrong approach:** Signing nothing and trusting `$_COOKIE['user_id']` fails because any client can send `user_id=1` in a request.

**How to verify:** Your explanation shows a forged request and the server check that rejects it.

## Exercise 5: Test activity exactly at and beyond the timeout boundary.

**Expected evidence:** The implementation follows its documented inclusive or exclusive timeout rule.

**Approach:** Test the difference exactly at 1800 seconds and at 1801 seconds, and compare with the documented rule.

**Why:** The example uses >, so 1800 seconds is still active and 1801 has expired; the boundary must match the documented rule.

**Plausible wrong approach:** Testing only 0 and 5000 seconds fails because an off by one at the boundary is never exercised.

**How to verify:** At 1800 the session stays valid under the `>` rule, and at 1801 it is rejected. Switching the rule to `>=` flips only the 1800 result, which shows the boundary is real.

## Exercise 6: Describe a real HTTP session acceptance test.

**Expected answer:** Observe Set-Cookie, a subsequent Cookie request, identifier rotation, logout and expiry through an owned server.

**Approach:** Describe a test against a server you own that records Set-Cookie, sends the cookie back, logs in, logs out and waits past expiry.

**Why:** A real test watches Set-Cookie, the next request's Cookie header, identifier rotation after login, logout and expiry.

**Plausible wrong approach:** Citing the CLI state test as proof of session security fails because no cookie or HTTP header was ever sent.

**How to verify:** Your checklist includes identifier rotation after login and a rejected request after logout. The test also confirms that the cookie carries the HttpOnly and Secure attributes.

## Reference comparison

The reference requires activity at 2800 to succeed, 2801 to expire and a backward clock at 999 to be rejected, then states that no HTTP session was created. That catches an off-by-one timeout. It does not set cookies or start a session, so describe the HTTP test that would.

Open `courses/web-development/solutions/web-048_solution.php` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
