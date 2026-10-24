# js-029: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

The Document Object Model is a live tree of nodes exposed by the browser. HTML source describes an initial tree, but scripts can create, remove and update nodes after parsing. A variable holding an element is a reference to that node, not a query that automatically finds a replacement later. querySelector can return null, so selecting an element and assuming it exists is a contract that should be checked at startup.

Events are dispatched through a path. A click on a nested span can have the span as target while the list holding the listener is currentTarget. Delegation uses this relationship to handle dynamically added children with one ancestor listener. The handler must check that the matched element belongs to the intended component. Bubbling, stopping propagation and preventing a default browser action are separate mechanisms; preventDefault does not stop propagation.

Native controls carry useful keyboard and focus behavior. A button responds to the appropriate keyboard activation without a custom keydown imitation. A disclosure control should expose its expanded state, keep its label understandable and move focus only when the interaction requires it. Adding aria attributes does not automatically implement keyboard behavior. A live status region can announce a concise result, but repeatedly replacing large regions may overwhelm assistive technology.

Listeners also have a lifetime. A component removed from use should release subscriptions it owns. addEventListener can accept an AbortSignal, allowing a group of listeners to be removed together. This is real browser event behavior; a Node computation with a fake document object does not establish it.

**DOM node:** A live object representing part of the document tree.

**Event target:** The object at which an event originated.

**Delegation:** Handling descendant events at an ancestor listener.

**Focus:** The element receiving keyboard interaction.

## Reading the implementation

Select an element after its markup exists, guard its expected type, and attach a named listener. textContent inserts text without parsing HTML. event.target identifies the originating target, while event.currentTarget identifies the listener owner during dispatch. closest can locate an action button from a nested child. A native button has type=button when it should not submit a surrounding form. hidden changes visibility and participation in layout; aria-expanded communicates the control state but does not itself hide content.

## Exercise 1: Use a native button and live result

Task: Open the complete snippet, activate Add twice by pointer and once by keyboard, then inspect the count.

The browser supplies native button activation. The script handles click once rather than separately counting keydown and click, which could double-count keyboard use.

```html
<!doctype html><html lang='en'><meta charset='utf-8'><title>Counter</title>
<button type='button' id='add'>Add one</button>
<p role='status' id='count'>Count: 0</p>
<script>
const button = document.querySelector('#add');
const output = document.querySelector('#count');
if (!(button instanceof HTMLButtonElement) || !(output instanceof HTMLElement)) throw new Error('required controls missing');
let count = 0;
button.addEventListener('click', () => { count += 1; output.textContent = `Count: ${count}`; });
</script></html>
```

**Expected:** count 3; button remains keyboard reachable.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Trace target and currentTarget through delegation

Task: Click the nested word inside the list button in the snippet.

The listener belongs to the list, but the original target can be a child inside the button. Delegation checks both the matching action and its containment in the component.

```html
<!doctype html><html lang='en'><meta charset='utf-8'><title>Delegation</title>
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
</script></html>
```

**Expected:** selected A; target SPAN and currentTarget UL.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Handle a dynamically appended action

Task: Create a new list item with button B after the listener is installed and activate it.

Delegation observes future descendants through the same event path. It avoids installing a second listener for every new row, but its selector and containment checks still define the allowed action surface.

```html
const item = document.createElement('li');
const button = document.createElement('button');
button.type = 'button';
button.dataset.id = 'B';
button.textContent = 'Choose B';
item.append(button);
list.append(item);
```

**Expected:** the existing ancestor listener reports B without a new per-button listener.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Implement an accessible disclosure

Task: Toggle a details region and keep hidden and aria-expanded synchronized.

The visual state and accessibility state describe the same Boolean. A disclosure normally keeps focus on its toggle; moving focus on every open can make repeated keyboard interaction unpredictable.

```html
const expanded = toggle.getAttribute('aria-expanded') === 'true';
toggle.setAttribute('aria-expanded', String(!expanded));
details.hidden = expanded;
```

**Expected:** opening reveals details and sets true; closing hides it and sets false.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Remove listeners through their lifecycle signal

Task: Attach a counter listener with a signal, click once, abort, and click again.

Removing a listener is separate from deleting visible content. The lifecycle signal releases the event subscription so a retired component no longer handles input.

```html
const controller = new AbortController();
button.addEventListener('click', onClick, { signal: controller.signal });
controller.abort();
```

**Expected:** the count stops increasing after abort.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Diagnose a missing required element

Task: Query a deliberately absent id and report the failed startup contract.

A typo or changed HTML structure can invalidate selectors. An explicit startup check gives a useful diagnosis instead of a later cannot-read-property exception.

```html
const missing = document.querySelector('#not-present');
if (missing === null) {
  output.textContent = 'Required element not found';
}
```

**Expected:** null is detected before accessing a property.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
