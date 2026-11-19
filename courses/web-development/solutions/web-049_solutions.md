# web-049: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-049.md`.

## Exercise 1: Explain why a hidden form field alone does not prevent CSRF.

**Expected answer:** The server must verify an unpredictable session-bound value, not merely the presence of a field.

**Why:** A field's presence proves nothing; the server must compare an unpredictable value bound to the user's session.

## Exercise 2: Add wrong-type and missing-token rejection.

**Expected evidence:** Array, null and absent values cannot reach a successful comparison.

**Why:** Rejecting arrays, null and empty strings first prevents type errors and accidental matches.

## Exercise 3: Build a state-change decision that checks method, token and authorization.

**Expected evidence:** Only a deliberate allowed POST with matching token can reach the mutation branch.

**Why:** A state change needs a deliberate POST, a valid token and authorization; any missing check opens a different attack.

## Exercise 4: Diagnose a token placed in a URL.

**Expected answer:** URLs can leak through logs, history and referrers, so use the appropriate body or header channel.

**Why:** URLs appear in logs, history and Referer headers, so a token in the query string can leak.

## Exercise 5: Test mismatched, empty and matching synthetic tokens.

**Expected evidence:** Only the exact nonempty expected token passes the local comparison contract.

**Why:** hash_equals compares in constant time, and only the exact nonempty expected token should pass.

## Exercise 6: Explain the relationship between CSRF, SameSite and XSS.

**Expected answer:** They are distinct mechanisms; SameSite supports CSRF defenses while same-origin script injection can defeat them.

**Why:** SameSite limits when cookies are sent cross-site and supports CSRF defense, but injected same-origin script can read tokens and send valid requests.

## Reference comparison

Open `courses/web-development/solutions/web-049_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
