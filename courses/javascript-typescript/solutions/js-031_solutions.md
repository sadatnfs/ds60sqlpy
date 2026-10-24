# js-031: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

Rendering untrusted text is a data-versus-code boundary. textContent inserts characters as text. innerHTML parses a string as markup and can create active elements or unsafe attributes. A report title containing angle brackets should usually remain a title, not become a document fragment. Escaping for one context does not automatically make a value safe in another context: HTML text, URL attributes, CSS and JavaScript each have different parsing rules.

URLs need semantic validation after parsing. A link that begins with javascript: is not an ordinary navigation to a document. A relative URL can resolve against the current page, while an absolute URL can point to another origin. The fixture accepts only http/https links to the same origin and rejects embedded credentials. That is a deliberately narrow local-navigation policy, not a universal URL sanitizer. It compares parsed origins rather than unsafe string prefixes.

Content Security Policy restricts allowed resource loads and execution. It provides an additional layer; it does not replace correct DOM construction, input validation or authorization. The complete fixture uses a meta policy with default-src none, script-src self, style-src self, object-src none, base-uri none and form-action none. Its script and stylesheet are separate local files, so inline script and inline event handlers are unnecessary. Some directives require HTTP headers and are not enforced through meta; the lesson does not claim meta establishes frame-ancestors protection.

The same-origin policy is a browser boundary based on scheme, host and port. CORS can selectively permit reading cross-origin responses, but it is not authentication and does not mean a server may skip authorization. This lesson makes no external requests. The checks inspect local text, URL decisions, DOM structure and CSP console behavior. A production service needs its own server-side controls and deployment evidence.

**Injection boundary:** A point where data could be interpreted as executable syntax.

**Safe text insertion:** Creating a text value without parsing it as markup.

**URL policy:** A semantic allowlist applied to a parsed URL.

**Content Security Policy:** A browser-enforced resource and execution restriction.

## Reading the implementation

Create elements with document.createElement, set textContent for untrusted visible text, and assign a URL only after a parsed policy check. new URL(candidate, location.href) resolves relative values before inspecting protocol, username, password and origin. Do not compare raw prefixes such as startsWith('https://trusted.example'), which can match an attacker-controlled suffix. A meta CSP must appear before the resources it governs, and the external script uses addEventListener rather than inline onclick attributes.

## Exercise 1: Render a markup-looking title as literal text

Task: Save the snippet and inspect the resulting DOM and visible title.

The suspicious-looking string is a local inert test value. textContent preserves it as characters, so the browser does not create the image or interpret its event attribute.

```html
<!doctype html><html lang='en'><meta charset='utf-8'><title>Literal text</title>
<p id='title'></p><p id='status' role='status'></p>
<script>
const input = '<img src=x onerror=alert(1)>';
const title = document.querySelector('#title');
title.textContent = input;
document.querySelector('#status').textContent = `Image elements: ${title.querySelectorAll('img').length}`;
</script></html>
```

**Expected:** the angle-bracket text is visible; no img element is created.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Validate a URL before creating a link

Task: Use a same-origin relative link and reject a javascript URL under the shown policy.

The policy acts on parsed components rather than textual resemblance. Serve this example over loopback HTTP; a file origin does not satisfy its HTTP navigation contract.

```html
<!doctype html><html lang='en'><meta charset='utf-8'><title>URL policy</title><pre id='result'></pre>
<script>
function localLink(text) {
  const url = new URL(text, location.href);
  if (!['http:', 'https:'].includes(url.protocol) || url.origin !== location.origin || url.username || url.password) throw new Error('Local HTTP link required');
  return url;
}
const result = document.querySelector('#result');
try { result.textContent = `Accepted: ${localLink('./help.html').pathname}`; }
catch (error) { result.textContent = error.message; }
try { localLink('javascript:alert(1)'); }
catch { result.textContent += '\nRejected javascript URL'; }
</script></html>
```

**Expected:** local help is accepted; javascript: is rejected.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Install the complete fixture CSP

Task: Inspect the reference HTML and load its external script and stylesheet under the meta policy.

The policy permits only the local resource categories the fixture requires. It is a second layer around correct DOM code, not a substitute for that code.

```html
<meta http-equiv='Content-Security-Policy' content="default-src 'none'; script-src 'self'; style-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'">
<link rel='stylesheet' href='style.css'>
<script src='app.js' defer></script>
```

**Expected:** local resources load; no inline handlers or eval are needed.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Reject origin and credential tricks

Task: Try a different port, an external origin, a data URL and embedded credentials.

Changing the port changes origin. Credentials and non-HTTP schemes are rejected independently. The task inspects decisions without sending requests to the candidate destinations.

```html
const credentialed = new URL(location.href);
credentialed.username = 'public-demo';
credentialed.password = 'not-a-secret';
for (const candidate of ['http://127.0.0.1:1/', 'https://example.invalid/', 'data:text/html,hello', credentialed.href]) {
  // Call the policy and record its rejection; do not navigate to these values.
}
```

**Expected:** every candidate is rejected by the local-link policy.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Inspect dynamic text without changing policy

Task: Enter strong-tag-looking text, render it, then inspect child element count.

An allowlisted script can still be unsafe if it uses an injection sink. Correct text insertion remains necessary even with a restrictive CSP.

```html
output.textContent = userText;
const count = output.childElementCount;
// Expected count: 0, even when userText contains angle brackets.
```

**Expected:** text remains literal and child element count stays zero.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Explain the actual policy boundary

Task: Record what the meta policy proves and what needs headers or server authorization.

Browser restrictions and server decisions solve different problems. An accurate security explanation names which component enforces each claim and avoids inferring deployment protection from a local fixture.

```html
// Inspect browser console policy messages and the loaded resource list.
// Keep document-policy observations separate from server authentication claims.
```

**Expected:** no claim that CSP authenticates callers, CORS authorizes actions, or meta implements frame-ancestors.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
