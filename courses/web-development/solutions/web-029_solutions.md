# web-029: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-029.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Compare origins for the same host on two different ports.

**Expected answer:** Different ports form different origins even when the host matches.

**Approach:** Compare the scheme, host and port of both URLs; an origin is the exact triple, so any difference makes them distinct.

**Why:** An origin is the triple of scheme, host and port, so a different port is a different origin.

**Plausible wrong approach:** Treating `localhost:3000` and `localhost:8000` as one origin fails because the port is part of the origin.

**How to verify:** `new URL('http://localhost:3000').origin` and the 8000 version print different strings in the console.

## Exercise 2: Render an angle-bracket string safely as visible text.

**Expected evidence:** No extra element or event handler is created.

**Approach:** Assign the untrusted string with `textContent` and inspect the output element to confirm it holds a single text node.

**Why:** textContent creates a text node, so the angle brackets display as characters and no img element or handler is created.

**Plausible wrong approach:** Escaping only `<` with a replace call fails because other contexts such as attributes and URLs need different handling.

**How to verify:** The output shows the angle brackets literally, and the Elements panel shows no `img` child.

## Exercise 3: Build a small rendering demo that separates text handling from URL policy.

**Expected evidence:** Plain text remains data and navigation candidates pass an explicit scheme decision.

**Approach:** Render free text with `textContent`, and parse candidate links with `new URL` before allowing only the `https:` scheme.

**Why:** Text needs safe insertion, while URLs need an explicit allowlist of schemes before they become navigation targets.

**Plausible wrong approach:** Checking `startsWith('http')` fails because strings such as `httpx:` or mixed case schemes can confuse the check.

**How to verify:** Submitting `javascript:alert(1)` produces a rejected link, while `https://example.invalid/` is accepted without any fetch.

## Exercise 4: Explain why CORS is not authorization.

**Expected answer:** Non-browser clients can still send requests, and the server must enforce permissions.

**Approach:** Separate what the browser enforces for its own scripts from what the server must check for every request it receives.

**Why:** CORS only controls which browser pages may read responses; it does not stop requests, so the server must check permissions.

**Plausible wrong approach:** Saying a restrictive CORS policy blocks attackers fails because curl and other clients ignore CORS and still reach the endpoint.

**How to verify:** A command line request reaches the endpoint even when a browser script on another origin is blocked from reading its reply.

## Exercise 5: Inspect the preview without relying on cookies or parent-window access.

**Expected evidence:** The lesson remains functional within its isolated local contract.

**Approach:** Run the demo inside the classroom preview and confirm it never reads cookies, `localStorage` or `window.parent` properties.

**Why:** The sandboxed preview has no cookies or parent access, so a correct lesson works without them.

**Plausible wrong approach:** Loosening the iframe sandbox to make storage work fails because it removes the isolation the lesson is meant to describe.

**How to verify:** The demo works in the preview, and the console shows no SecurityError from storage or parent access.

## Exercise 6: Explain the separate roles of escaping, validation, CSP and sandboxing.

**Expected answer:** They address contextual interpretation, accepted values, document capabilities and isolation respectively.

**Approach:** Write one line for each control: escaping by context, validation of accepted values, CSP limits on loaded code, and sandboxing for isolation.

**Why:** Escaping stops data from being interpreted as code in one context, validation limits accepted values, CSP limits what the page may load or run, and sandboxing isolates a document's capabilities.

**Plausible wrong approach:** Relying on CSP alone fails because a policy that allows inline script would still run injected handlers.

**How to verify:** Your table names a separate failure each control prevents, with no control repeated for two rows.

## Reference comparison

The reference requires the untrusted pre to have no child elements and the document to contain no img elements, so it catches the string being parsed as markup. It does not test the URL policy text, CSP headers or sandbox limits, so read your URL decision and explain which schemes it rejects.

Open `courses/web-development/solutions/web-029_solution.html` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).
