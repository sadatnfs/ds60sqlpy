# js-030: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

A form is a structured input interface, not merely a collection of text boxes. Labels connect descriptions to controls, native constraints support immediate feedback, and submit represents the user's request to process the whole form. Input values arrive as strings. Number conversion, whitespace handling, required fields and numeric bounds are explicit domain decisions. Client validation improves interaction but cannot replace validation at a server or other trust boundary.

Separate the current application state from its visual rendering and its stored representation. A successful validation produces a new state; rendering then reflects it. localStorage stores strings scoped by origin and persists across page reloads subject to browser policy. JSON.stringify and JSON.parse provide serialization syntax, not a schema or migration strategy. A version field helps recognize whether stored data matches the code's current contract.

Storage access can fail because of browser policy, quota, origin restrictions or malformed prior data. Catch these failures at the persistence boundary and report that the in-memory result was not saved. Do not claim persistence merely because the interface updated. file URLs can have implementation-dependent storage behavior, so the reproducible fixture uses an explicit loopback HTTP origin. It stores only a tiny non-sensitive draft under a lesson-specific key and never calls localStorage.clear.

Two tabs share the same localStorage area when their origins match, but the storage event is delivered to other documents, not the document performing the write. Automatically replacing a user's unsaved form on such an event can lose edits. This fixture reports an external change and asks the learner to reload stored state explicitly. Conflict policy matters even in a small local application.

**Form submission:** Processing the complete set of named controls under a declared action.

**Application state:** The accepted data from which the interface is rendered.

**Persistence:** Saving state beyond the current page lifetime.

**Origin:** The scheme, host and port boundary governing browser storage.

## Reading the implementation

Listen for submit on the form and preventDefault only because this local fixture handles the request itself. FormData reads named controls; disabled controls and unnamed controls have different submission behavior. Trim text under a stated policy, parse numeric input and check safe integer bounds. Persist an object containing version and validated fields. Loading requires parse and schema checks before rendering. Use removeItem with the owned key for reset, never clear unrelated browser storage.

## Exercise 1: Validate one local form submission

Task: Save the snippet as HTML and submit name Ada and quantity 2, then try an invalid quantity.

Native constraints stop many invalid user submissions before the submit handler. The explicit domain check still defines the accepted state and protects alternate invocation paths.

```html
<!doctype html>
<html lang='en'
  ><meta charset='utf-8' /><title>Local form</title>
  <form id='form'
    ><label>Name <input name='name' required maxlength='40' /></label>
    <label
      >Quantity <input name='quantity' type='number' min='1' max='20' step='1' required
    /></label>
    <button>Apply</button></form
  ><p role='status' id='status'>No accepted state</p>
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
</script></html
>
```

**Expected:** valid output Ada: 2; invalid input produces no accepted state.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Handle storage success and failure explicitly

Task: Run this standalone snippet on a loopback HTTP origin and activate Save.

A successful state update and a successful storage operation are separate observations. The interface reports the actual persistence outcome without hiding failure behind a local display update.

```html
<!doctype html>
<html lang='en'
  ><meta charset='utf-8' /><title>Storage boundary</title>
  <button id='save' type='button'>Save tiny draft</button
  ><p id='status' role='status'>Not saved</p>
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
</script></html
>
```

**Expected:** either Saved or a visible Storage unavailable message, never an invented success.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Load only a recognized stored schema

Task: Reject malformed JSON or a stored version other than 1 before rendering.

Stored data is another external boundary. A version label makes incompatibility explicit, while field checks prevent syntax-valid but invalid data from entering the UI.

```html
const value = JSON.parse(text);
if (value === null || value.version !== 1 || typeof value.name !== 'string'
    || !Number.isInteger(value.quantity) || value.quantity < 1 || value.quantity > 20) {
  throw new Error('Unsupported saved draft');
}
```

**Expected:** invalid saved state is diagnosed and does not become accepted application state.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Distinguish current state from persisted state

Task: Change a form value after saving without submitting again, then reload the page.

An editable control is a draft, not automatically committed application state. Keeping that distinction visible prevents misleading autosave expectations.

```html
// Compare the visible form draft before submission with the last saved JSON.
// Only a successful save operation changes the persistence receipt.
```

**Expected:** the last saved value returns; the unsaved edit is not falsely described as persisted.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Observe a change from another tab

Task: Open the same loopback URL in two tabs, save in one, and observe the other.

The event notifies other same-origin documents. It does not resolve concurrent editing or choose which draft should win; this fixture avoids overwriting an unsaved form automatically.

```html
window.addEventListener('storage', event => {
  if (event.key === key) status.textContent = 'Saved draft changed in another tab; reload when ready';
});
```

**Expected:** the other tab reports an external change; the writing tab does not receive its own storage event.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Reset only this lesson's key

Task: Remove the owned draft and verify an unrelated storage key remains.

A lesson owns its namespaced state, not the entire origin storage area. Scoped removal respects other lessons and applications sharing that origin.

```html
localStorage.removeItem(key);
// Do not use localStorage.clear(), which removes unrelated keys for the origin.
```

**Expected:** owned key absent; unrelated key unchanged.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
