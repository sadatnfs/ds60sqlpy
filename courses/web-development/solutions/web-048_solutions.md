# web-048: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A cookie is a small value the browser stores and sends according to its scope and attributes. A common session design stores an unpredictable session identifier in a cookie and keeps application state on the server. The identifier is a bearer credential: possession may allow the server to associate a request with that session. Do not put sensitive application state into an unsigned client value and treat it as trusted.

Session lifetime involves creation, authentication transitions, inactivity, absolute expiry and logout. Regenerating the identifier after privilege changes helps address fixation, but safe concurrency and invalidation policies still matter. HttpOnly limits script access to a cookie, Secure restricts transport to HTTPS, and SameSite controls some cross-site sending behavior. These attributes support different defenses and do not replace authorization.

Configure session behavior before session_start and before output. Prefer cookie-only identifiers and strict session handling. Real session storage can lock during a request, so write-close when the required state update is complete in applications that support concurrent requests. The CLI reference uses a pure state transition to demonstrate expiry; it does not claim to create or test a browser session.

## Exercise 1: Explain which data is in the browser and which is on the server.

The browser normally holds an identifier while server storage holds the associated session state.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a fixed-clock inactivity check.

The test can inspect the exact expiry boundary reproducibly.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Model session activity and expiry with explicit state transitions.

An expired session is rejected and a valid activity update preserves the declared identity.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Explain why a client-supplied user id is not a trusted session.

A caller can choose that value unless a server-verified credential establishes the identity.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test activity exactly at and beyond the timeout boundary.

The implementation follows its documented inclusive or exclusive timeout rule.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Describe a real HTTP session acceptance test.

Observe Set-Cookie, a subsequent Cookie request, identifier rotation, logout and expiry through an owned server.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
