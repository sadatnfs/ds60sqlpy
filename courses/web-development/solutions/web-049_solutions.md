# web-049: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

Cross-site request forgery exploits a browser's ability to send credentials with a request that the user did not intend. A state-changing endpoint must distinguish an authorized user's deliberate action from a request induced by another site. A synchronizer-token design stores an unpredictable token in the user's server session and requires the same token in the submitted form or appropriate request header.

The token must be generated with a cryptographically secure source, kept out of URLs and checked before changing state. SameSite cookies and origin checks can add protection but do not eliminate the need to understand the application's request paths. XSS can undermine CSRF defenses because malicious script running in the application's own origin may access tokens or perform actions.

Generate token bytes with random_bytes and encode them for transport. Compare a validated submitted string with the known session token using hash_equals. Reject absent, wrong-type and empty values before a state change. The deterministic CLI fixture uses a clearly fake fixed token to test comparison logic; it is not a production token generator or proof of a browser defense.

## Exercise 1: Explain why a hidden form field alone does not prevent CSRF.

The server must verify an unpredictable session-bound value, not merely the presence of a field.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add wrong-type and missing-token rejection.

Array, null and absent values cannot reach a successful comparison.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a state-change decision that checks method, token and authorization.

Only a deliberate allowed POST with matching token can reach the mutation branch.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a token placed in a URL.

URLs can leak through logs, history and referrers, so use the appropriate body or header channel.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test mismatched, empty and matching synthetic tokens.

Only the exact nonempty expected token passes the local comparison contract.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain the relationship between CSRF, SameSite and XSS.

They are distinct mechanisms; SameSite supports CSRF defenses while same-origin script injection can defeat them.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
