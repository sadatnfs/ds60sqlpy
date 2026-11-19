# web-048: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-048.md`.

## Exercise 1: Explain which data is in the browser and which is on the server.

**Expected answer:** The browser normally holds an identifier while server storage holds the associated session state.

**Why:** The cookie normally holds only a random session identifier, while the session data stays on the server.

## Exercise 2: Add a fixed-clock inactivity check.

**Expected evidence:** The test can inspect the exact expiry boundary reproducibly.

**Why:** An injected clock lets a test place last activity exactly at the boundary.

## Exercise 3: Model session activity and expiry with explicit state transitions.

**Expected evidence:** An expired session is rejected and a valid activity update preserves the declared identity.

**Why:** Explicit transitions make expiry and activity updates testable without a real server.

## Exercise 4: Explain why a client-supplied user id is not a trusted session.

**Expected answer:** A caller can choose that value unless a server-verified credential establishes the identity.

**Why:** The caller controls every submitted field, so identity must come from a server-verified session.

## Exercise 5: Test activity exactly at and beyond the timeout boundary.

**Expected evidence:** The implementation follows its documented inclusive or exclusive timeout rule.

**Why:** The example uses >, so 1800 seconds is still active and 1801 has expired; the boundary must match the documented rule.

## Exercise 6: Describe a real HTTP session acceptance test.

**Expected answer:** Observe Set-Cookie, a subsequent Cookie request, identifier rotation, logout and expiry through an owned server.

**Why:** A real test watches Set-Cookie, the next request's Cookie header, identifier rotation after login, logout and expiry.

## Reference comparison

Open `courses/web-development/solutions/web-048_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
