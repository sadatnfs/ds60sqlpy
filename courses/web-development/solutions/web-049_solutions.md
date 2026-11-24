# web-049: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-049.md`.

## Exercise 1: Explain why a hidden form field alone does not prevent CSRF.

**Expected answer:** The server must verify an unpredictable session-bound value, not merely the presence of a field.

**Approach:** Ask what an attacker's page can include: it can add any hidden field, so only an unpredictable value tied to the session proves intent.

**Why:** A field's presence proves nothing; the server must compare an unpredictable value bound to the user's session.

**Plausible wrong approach:** Checking that a field named `csrf` exists fails because a forged form can include that field with any value.

**How to verify:** A synthetic request with a made up token value is rejected by the comparison.

## Exercise 2: Add wrong-type and missing-token rejection.

**Expected evidence:** Array, null and absent values cannot reach a successful comparison.

**Approach:** Check `is_string($submitted) && $submitted !== ''` before `hash_equals`, and treat anything else as a rejected request.

**Why:** Rejecting arrays, null and empty strings first prevents type errors and accidental matches.

**Plausible wrong approach:** Passing an array straight into `hash_equals` fails because the function throws a TypeError instead of returning a clean rejection.

**How to verify:** Array, null and missing tokens all return rejected without an uncaught error.

## Exercise 3: Build a state-change decision that checks method, token and authorization.

**Expected evidence:** Only a deliberate allowed POST with matching token can reach the mutation branch.

**Approach:** Require POST, then a matching token, then an authorization check, and reach the mutation only when all three pass in that order.

**Why:** A state change needs a deliberate POST, a valid token and authorization; any missing check opens a different attack.

**Plausible wrong approach:** Running the mutation first and rolling it back on a bad token fails because side effects such as emails may already be sent.

**How to verify:** Tracing a GET, a bad token and a missing permission shows each stopped before the mutation branch.

## Exercise 4: Diagnose a token placed in a URL.

**Expected answer:** URLs can leak through logs, history and referrers, so use the appropriate body or header channel.

**Approach:** Move the token from the query string into a hidden POST field or a request header.

**Why:** URLs appear in logs, history and Referer headers, so a token in the query string can leak.

**Plausible wrong approach:** Keeping the token in a URL and making it shorter fails because history, logs and Referer headers still record it.

**How to verify:** Your server access log for the form submission shows a path with no token in it.

## Exercise 5: Test mismatched, empty and matching synthetic tokens.

**Expected evidence:** Only the exact nonempty expected token passes the local comparison contract.

**Approach:** Compare a fixed synthetic token against a different string, an empty string and an identical string, recording each result.

**Why:** hash_equals compares in constant time, and only the exact nonempty expected token should pass.

**Plausible wrong approach:** Testing only the matching case fails because a comparison that always returns true would pass it too.

**How to verify:** Only the identical string returns true, and the other two return false. A token differing only in its last character also returns false.

## Exercise 6: Explain the relationship between CSRF, SameSite and XSS.

**Expected answer:** They are distinct mechanisms; SameSite supports CSRF defenses while same-origin script injection can defeat them.

**Approach:** Describe each mechanism: tokens prove a form came from your page, SameSite limits cookie sending, and XSS runs script inside your origin.

**Why:** SameSite limits when cookies are sent cross-site and supports CSRF defense, but injected same-origin script can read tokens and send valid requests.

**Plausible wrong approach:** Saying SameSite cookies remove the need for tokens fails because some browsers and request types still send them.

**How to verify:** Your answer explains that injected script can read the token, so XSS defeats CSRF defenses.

## Reference comparison

Open `courses/web-development/solutions/web-049_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.
