function required(selector, type) {
  const node = document.querySelector(selector);
  if (!(node instanceof type)) throw new Error(`Required ${type.name} missing: ${selector}`);
  return node;
}
const add = required('#add', HTMLButtonElement);
const count = required('#count', HTMLElement);
let value = 0;
add.addEventListener('click', () => { value += 1; count.textContent = `Count: ${value}`; });
const list = required('#list', HTMLUListElement);
const selection = required('#selection', HTMLElement);
list.addEventListener('click', event => {
  if (!(event.target instanceof Element)) return;
  const action = event.target.closest('button[data-id]');
  if (!(action instanceof HTMLButtonElement) || !list.contains(action)) return;
  selection.textContent = `Selected ${action.dataset.id}; target ${event.target.tagName}; currentTarget ${event.currentTarget.tagName}`;
});
required('#append', HTMLButtonElement).addEventListener('click', event => {
  const item = document.createElement('li');
  const action = document.createElement('button');
  action.type = 'button'; action.dataset.id = 'B'; action.textContent = 'Choose B';
  item.append(action); list.append(item); event.currentTarget.disabled = true;
});
const toggle = required('#toggle', HTMLButtonElement);
const details = required('#details', HTMLElement);
toggle.addEventListener('click', () => {
  const expanded = toggle.getAttribute('aria-expanded') === 'true';
  toggle.setAttribute('aria-expanded', String(!expanded));
  details.hidden = expanded;
  toggle.textContent = expanded ? 'Show details' : 'Hide details';
});
const lifecycle = new AbortController();
let tracked = 0;
required('#tracked', HTMLButtonElement).addEventListener('click', () => {
  tracked += 1;
  required('#tracked-count', HTMLElement).textContent = `Tracked: ${tracked}`;
}, { signal: lifecycle.signal });
required('#stop', HTMLButtonElement).addEventListener('click', event => {
  lifecycle.abort(); event.currentTarget.disabled = true;
});
required('#diagnose', HTMLButtonElement).addEventListener('click', () => {
  const missing = document.querySelector('#not-present');
  required('#diagnosis', HTMLElement).textContent = missing === null ? 'Required element not found' : 'Unexpected element exists';
});
