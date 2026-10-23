from render import add, ex

add(29,
'''The Document Object Model is a live tree of nodes exposed by the browser. HTML source describes an initial tree, but scripts can create, remove and update nodes after parsing. A variable holding an element is a reference to that node, not a query that automatically finds a replacement later. querySelector can return null, so selecting an element and assuming it exists is a contract that should be checked at startup.

Events are dispatched through a path. A click on a nested span can have the span as target while the list holding the listener is currentTarget. Delegation uses this relationship to handle dynamically added children with one ancestor listener. The handler must check that the matched element belongs to the intended component. Bubbling, stopping propagation and preventing a default browser action are separate mechanisms; preventDefault does not stop propagation.

Native controls carry useful keyboard and focus behavior. A button responds to the appropriate keyboard activation without a custom keydown imitation. A disclosure control should expose its expanded state, keep its label understandable and move focus only when the interaction requires it. Adding aria attributes does not automatically implement keyboard behavior. A live status region can announce a concise result, but repeatedly replacing large regions may overwhelm assistive technology.

Listeners also have a lifetime. A component removed from use should release subscriptions it owns. addEventListener can accept an AbortSignal, allowing a group of listeners to be removed together. This is real browser event behavior; a Node computation with a fake document object does not establish it.''',
'''Select an element after its markup exists, guard its expected type, and attach a named listener. textContent inserts text without parsing HTML. event.target identifies the originating target, while event.currentTarget identifies the listener owner during dispatch. closest can locate an action button from a nested child. A native button has type=button when it should not submit a surrounding form. hidden changes visibility and participation in layout; aria-expanded communicates the control state but does not itself hide content.''',
[('DOM node','A live object representing part of the document tree.'),('Event target','The object at which an event originated.'),('Delegation','Handling descendant events at an ancestor listener.'),('Focus','The element receiving keyboard interaction.')],[
ex('Use a native button and live result','Open the complete snippet, activate Add twice by pointer and once by keyboard, then inspect the count.','count 3; button remains keyboard reachable.',r'''<!doctype html><html lang='en'><meta charset='utf-8'><title>Counter</title>
<button type='button' id='add'>Add one</button>
<p role='status' id='count'>Count: 0</p>
<script>
const button = document.querySelector('#add');
const output = document.querySelector('#count');
if (!(button instanceof HTMLButtonElement) || !(output instanceof HTMLElement)) throw new Error('required controls missing');
let count = 0;
button.addEventListener('click', () => { count += 1; output.textContent = `Count: ${count}`; });
</script></html>''','The browser supplies native button activation. The script handles click once rather than separately counting keydown and click, which could double-count keyboard use.'),
ex('Trace target and currentTarget through delegation','Click the nested word inside the list button in the snippet.','selected A; target SPAN and currentTarget UL.',r'''<!doctype html><html lang='en'><meta charset='utf-8'><title>Delegation</title>
<ul id='list'><li><button type='button' data-id='A'><span>Choose A</span></button></li></ul>
<p id='result' role='status'>No selection</p>
<script>
const list = document.querySelector('#list');
const output = document.querySelector('#result');
if (!(list instanceof HTMLUListElement) || !(output instanceof HTMLElement)) throw new Error('required nodes missing');
list.addEventListener('click', event => {
  if (!(event.target instanceof Element)) return;
  const button = event.target.closest('button[data-id]');
  if (!(button instanceof HTMLButtonElement) || !list.contains(button)) return;
  output.textContent = `Selected ${button.dataset.id}; target ${event.target.tagName}; currentTarget ${event.currentTarget.tagName}`;
});
</script></html>''','The listener belongs to the list, but the original target can be a child inside the button. Delegation checks both the matching action and its containment in the component.'),
ex('Handle a dynamically appended action','Create a new list item with button B after the listener is installed and activate it.','the existing ancestor listener reports B without a new per-button listener.',r'''const item = document.createElement('li');
const button = document.createElement('button');
button.type = 'button';
button.dataset.id = 'B';
button.textContent = 'Choose B';
item.append(button);
list.append(item);''','Delegation observes future descendants through the same event path. It avoids installing a second listener for every new row, but its selector and containment checks still define the allowed action surface.'),
ex('Implement an accessible disclosure','Toggle a details region and keep hidden and aria-expanded synchronized.','opening reveals details and sets true; closing hides it and sets false.',r'''const expanded = toggle.getAttribute('aria-expanded') === 'true';
toggle.setAttribute('aria-expanded', String(!expanded));
details.hidden = expanded;''','The visual state and accessibility state describe the same Boolean. A disclosure normally keeps focus on its toggle; moving focus on every open can make repeated keyboard interaction unpredictable.'),
ex('Remove listeners through their lifecycle signal','Attach a counter listener with a signal, click once, abort, and click again.','the count stops increasing after abort.',r'''const controller = new AbortController();
button.addEventListener('click', onClick, { signal: controller.signal });
controller.abort();''','Removing a listener is separate from deleting visible content. The lifecycle signal releases the event subscription so a retired component no longer handles input.'),
ex('Diagnose a missing required element','Query a deliberately absent id and report the failed startup contract.','null is detected before accessing a property.',r'''const missing = document.querySelector('#not-present');
if (missing === null) {
  output.textContent = 'Required element not found';
}''','A typo or changed HTML structure can invalidate selectors. An explicit startup check gives a useful diagnosis instead of a later cannot-read-property exception.')],source='https://dom.spec.whatwg.org/',notes='''### Browser fixture and evidence

Copy the starter folder `courses/javascript-typescript/fixtures/js-029/` into your own ignored `.learning/expansion/js-029/` directory. Implement its TODO handlers from the six tasks. The separate completed browser reference is `courses/javascript-typescript/solutions/browser/js-029/`; reveal it after an attempt. Each folder has a README with loopback serving and interaction steps. The worked snippets above can also be saved as separate HTML files.

Record pointer and keyboard outcomes separately. Observe target/currentTarget text, disclosure state, focus retention and the stopped listener. Reading mode means the classroom does not execute this HTML through its Node worker. A source check or a completed reference file does not by itself establish browser interaction or assistive-technology behavior. A screen-reader claim requires an actual screen-reader session in addition to DOM attribute inspection.''')

add(30,
'''A form is a structured input interface, not merely a collection of text boxes. Labels connect descriptions to controls, native constraints support immediate feedback, and submit represents the user's request to process the whole form. Input values arrive as strings. Number conversion, whitespace handling, required fields and numeric bounds are explicit domain decisions. Client validation improves interaction but cannot replace validation at a server or other trust boundary.

Separate the current application state from its visual rendering and its stored representation. A successful validation produces a new state; rendering then reflects it. localStorage stores strings scoped by origin and persists across page reloads subject to browser policy. JSON.stringify and JSON.parse provide serialization syntax, not a schema or migration strategy. A version field helps recognize whether stored data matches the code's current contract.

Storage access can fail because of browser policy, quota, origin restrictions or malformed prior data. Catch these failures at the persistence boundary and report that the in-memory result was not saved. Do not claim persistence merely because the interface updated. file URLs can have implementation-dependent storage behavior, so the reproducible fixture uses an explicit loopback HTTP origin. It stores only a tiny non-sensitive draft under a lesson-specific key and never calls localStorage.clear.

Two tabs share the same localStorage area when their origins match, but the storage event is delivered to other documents, not the document performing the write. Automatically replacing a user's unsaved form on such an event can lose edits. This fixture reports an external change and asks the learner to reload stored state explicitly. Conflict policy matters even in a small local application.''',
'''Listen for submit on the form and preventDefault only because this local fixture handles the request itself. FormData reads named controls; disabled controls and unnamed controls have different submission behavior. Trim text under a stated policy, parse numeric input and check safe integer bounds. Persist an object containing version and validated fields. Loading requires parse and schema checks before rendering. Use removeItem with the owned key for reset, never clear unrelated browser storage.''',
[('Form submission','Processing the complete set of named controls under a declared action.'),('Application state','The accepted data from which the interface is rendered.'),('Persistence','Saving state beyond the current page lifetime.'),('Origin','The scheme, host and port boundary governing browser storage.')],[
ex('Validate one local form submission','Save the snippet as HTML and submit name Ada and quantity 2, then try an invalid quantity.','valid output Ada: 2; invalid input produces no accepted state.',r'''<!doctype html><html lang='en'><meta charset='utf-8'><title>Local form</title>
<form id='form'><label>Name <input name='name' required maxlength='40'></label>
<label>Quantity <input name='quantity' type='number' min='1' max='20' step='1' required></label>
<button>Apply</button></form><p role='status' id='status'>No accepted state</p>
<script>
const form = document.querySelector('#form');
const status = document.querySelector('#status');
form.addEventListener('submit', event => {
  event.preventDefault();
  const fields = new FormData(form);
  const name = String(fields.get('name') ?? '').trim();
  const quantity = Number(fields.get('quantity'));
  if (!name || !Number.isInteger(quantity) || quantity < 1 || quantity > 20) return;
  status.textContent = `${name}: ${quantity}`;
});
</script></html>''','Native constraints stop many invalid user submissions before the submit handler. The explicit domain check still defines the accepted state and protects alternate invocation paths.'),
ex('Handle storage success and failure explicitly','Run this standalone snippet on a loopback HTTP origin and activate Save.','either Saved or a visible Storage unavailable message, never an invented success.',r'''<!doctype html><html lang='en'><meta charset='utf-8'><title>Storage boundary</title>
<button id='save' type='button'>Save tiny draft</button><p id='status' role='status'>Not saved</p>
<script>
const key = 'ds60-js030-demo';
document.querySelector('#save').addEventListener('click', () => {
  try {
    localStorage.setItem(key, JSON.stringify({ version: 1, name: 'Ada', quantity: 2 }));
    document.querySelector('#status').textContent = 'Saved';
  } catch {
    document.querySelector('#status').textContent = 'Storage unavailable; draft is not persisted';
  }
});
</script></html>''','A successful state update and a successful storage operation are separate observations. The interface reports the actual persistence outcome without hiding failure behind a local display update.'),
ex('Load only a recognized stored schema','Reject malformed JSON or a stored version other than 1 before rendering.','invalid saved state is diagnosed and does not become accepted application state.',r'''const value = JSON.parse(text);
if (value === null || value.version !== 1 || typeof value.name !== 'string'
    || !Number.isInteger(value.quantity) || value.quantity < 1 || value.quantity > 20) {
  throw new Error('Unsupported saved draft');
}''','Stored data is another external boundary. A version label makes incompatibility explicit, while field checks prevent syntax-valid but invalid data from entering the UI.'),
ex('Distinguish current state from persisted state','Change a form value after saving without submitting again, then reload the page.','the last saved value returns; the unsaved edit is not falsely described as persisted.',r'''// Compare the visible form draft before submission with the last saved JSON.
// Only a successful save operation changes the persistence receipt.''','An editable control is a draft, not automatically committed application state. Keeping that distinction visible prevents misleading autosave expectations.'),
ex('Observe a change from another tab','Open the same loopback URL in two tabs, save in one, and observe the other.','the other tab reports an external change; the writing tab does not receive its own storage event.',r'''window.addEventListener('storage', event => {
  if (event.key === key) status.textContent = 'Saved draft changed in another tab; reload when ready';
});''','The event notifies other same-origin documents. It does not resolve concurrent editing or choose which draft should win; this fixture avoids overwriting an unsaved form automatically.'),
ex('Reset only this lesson\'s key','Remove the owned draft and verify an unrelated storage key remains.','owned key absent; unrelated key unchanged.',r'''localStorage.removeItem(key);
// Do not use localStorage.clear(), which removes unrelated keys for the origin.''','A lesson owns its namespaced state, not the entire origin storage area. Scoped removal respects other lessons and applications sharing that origin.')],source='https://html.spec.whatwg.org/multipage/webstorage.html',notes='''### Browser fixture and persistence scope

Use the starter folder `courses/javascript-typescript/fixtures/js-030/` in a saved learner copy. The separate completed reference is `courses/javascript-typescript/solutions/browser/js-030/`. Serve the selected copy on loopback using its README. Keep the exact scheme, host and port stable when testing persistence; changing localhost to 127.0.0.1 or changing the port creates a different origin.

Use only the authored fake names and quantities. The reference stores one tiny lesson draft. Its reset removes that key only. Two-tab evidence requires two actual browser documents; dispatching a fabricated Event in Node does not establish browser storage behavior. A deliberate malformed-draft button in the reference writes only the lesson key so the recovery path can be inspected without editing unrelated storage.''')

add(31,
'''Rendering untrusted text is a data-versus-code boundary. textContent inserts characters as text. innerHTML parses a string as markup and can create active elements or unsafe attributes. A report title containing angle brackets should usually remain a title, not become a document fragment. Escaping for one context does not automatically make a value safe in another context: HTML text, URL attributes, CSS and JavaScript each have different parsing rules.

URLs need semantic validation after parsing. A link that begins with javascript: is not an ordinary navigation to a document. A relative URL can resolve against the current page, while an absolute URL can point to another origin. The fixture accepts only http/https links to the same origin and rejects embedded credentials. That is a deliberately narrow local-navigation policy, not a universal URL sanitizer. It compares parsed origins rather than unsafe string prefixes.

Content Security Policy restricts allowed resource loads and execution. It provides an additional layer; it does not replace correct DOM construction, input validation or authorization. The complete fixture uses a meta policy with default-src none, script-src self, style-src self, object-src none, base-uri none and form-action none. Its script and stylesheet are separate local files, so inline script and inline event handlers are unnecessary. Some directives require HTTP headers and are not enforced through meta; the lesson does not claim meta establishes frame-ancestors protection.

The same-origin policy is a browser boundary based on scheme, host and port. CORS can selectively permit reading cross-origin responses, but it is not authentication and does not mean a server may skip authorization. This lesson makes no external requests. The checks inspect local text, URL decisions, DOM structure and CSP console behavior. A production service needs its own server-side controls and deployment evidence.''',
'''Create elements with document.createElement, set textContent for untrusted visible text, and assign a URL only after a parsed policy check. new URL(candidate, location.href) resolves relative values before inspecting protocol, username, password and origin. Do not compare raw prefixes such as startsWith('https://trusted.example'), which can match an attacker-controlled suffix. A meta CSP must appear before the resources it governs, and the external script uses addEventListener rather than inline onclick attributes.''',
[('Injection boundary','A point where data could be interpreted as executable syntax.'),('Safe text insertion','Creating a text value without parsing it as markup.'),('URL policy','A semantic allowlist applied to a parsed URL.'),('Content Security Policy','A browser-enforced resource and execution restriction.')],[
ex('Render a markup-looking title as literal text','Save the snippet and inspect the resulting DOM and visible title.','the angle-bracket text is visible; no img element is created.',r'''<!doctype html><html lang='en'><meta charset='utf-8'><title>Literal text</title>
<p id='title'></p><p id='status' role='status'></p>
<script>
const input = '<img src=x onerror=alert(1)>';
const title = document.querySelector('#title');
title.textContent = input;
document.querySelector('#status').textContent = `Image elements: ${title.querySelectorAll('img').length}`;
</script></html>''','The suspicious-looking string is a local inert test value. textContent preserves it as characters, so the browser does not create the image or interpret its event attribute.'),
ex('Validate a URL before creating a link','Use a same-origin relative link and reject a javascript URL under the shown policy.','local help is accepted; javascript: is rejected.',r'''<!doctype html><html lang='en'><meta charset='utf-8'><title>URL policy</title><pre id='result'></pre>
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
</script></html>''','The policy acts on parsed components rather than textual resemblance. Serve this example over loopback HTTP; a file origin does not satisfy its HTTP navigation contract.'),
ex('Install the complete fixture CSP','Inspect the reference HTML and load its external script and stylesheet under the meta policy.','local resources load; no inline handlers or eval are needed.',r'''<meta http-equiv='Content-Security-Policy' content="default-src 'none'; script-src 'self'; style-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'">
<link rel='stylesheet' href='style.css'>
<script src='app.js' defer></script>''','The policy permits only the local resource categories the fixture requires. It is a second layer around correct DOM code, not a substitute for that code.'),
ex('Reject origin and credential tricks','Try a different port, an external origin, a data URL and embedded credentials.','every candidate is rejected by the local-link policy.',r'''const credentialed = new URL(location.href);
credentialed.username = 'public-demo';
credentialed.password = 'not-a-secret';
for (const candidate of ['http://127.0.0.1:1/', 'https://example.invalid/', 'data:text/html,hello', credentialed.href]) {
  // Call the policy and record its rejection; do not navigate to these values.
}''','Changing the port changes origin. Credentials and non-HTTP schemes are rejected independently. The task inspects decisions without sending requests to the candidate destinations.'),
ex('Inspect dynamic text without changing policy','Enter strong-tag-looking text, render it, then inspect child element count.','text remains literal and child element count stays zero.',r'''output.textContent = userText;
const count = output.childElementCount;
// Expected count: 0, even when userText contains angle brackets.''','An allowlisted script can still be unsafe if it uses an injection sink. Correct text insertion remains necessary even with a restrictive CSP.'),
ex('Explain the actual policy boundary','Record what the meta policy proves and what needs headers or server authorization.','no claim that CSP authenticates callers, CORS authorizes actions, or meta implements frame-ancestors.',r'''// Inspect browser console policy messages and the loaded resource list.
// Keep document-policy observations separate from server authentication claims.''','Browser restrictions and server decisions solve different problems. An accurate security explanation names which component enforces each claim and avoids inferring deployment protection from a local fixture.')],source='https://www.w3.org/TR/CSP3/',notes='''### Complete CSP fixture

Use `courses/javascript-typescript/fixtures/js-031/` as the starter and `courses/javascript-typescript/solutions/browser/js-031/` for the separate completed reference. Serve a saved copy over loopback HTTP as described in its README. The complete reference uses external app.js and style.css under a restrictive meta CSP. The first two standalone teaching snippets intentionally show the DOM and URL mechanisms before adding that policy; their inline scripts are not examples of the final policy configuration.

Use browser developer tools to inspect actual elements, resources and policy diagnostics. Do not disable CSP to make an unsafe implementation pass. No exercise needs to execute injected script, navigate to external candidates or request a remote service. Keep actual browser evidence separate from a source scan or a Node parser check.''')
