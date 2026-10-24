from pathlib import Path
import html

ROOT = Path(__file__).resolve().parents[3]
STYLE = """body { font: 18px/1.6 system-ui, sans-serif; max-width: 52rem; margin: 2rem auto; padding: 0 1rem; color: #182232; background: #f6f8fb; }
section { background: white; border: 1px solid #ccd5e0; padding: 1.25rem; margin: 1rem 0; border-radius: .5rem; }
button, input, textarea { font: inherit; margin: .3rem; padding: .4rem .7rem; }
label { display: block; } textarea { width: 90%; min-height: 5rem; }
:focus-visible { outline: 3px solid #1260b5; outline-offset: 3px; }
pre, output { white-space: pre-wrap; overflow-wrap: anywhere; } [hidden] { display: none; }
"""
BODY29 = """<section><h2>1. Native counter</h2><button type='button' id='add'>Add one</button><p id='count' role='status'>Count: 0</p></section>
<section><h2>2 and 3. Delegated list actions</h2><ul id='list'><li><button type='button' data-id='A'><span>Choose A</span></button></li></ul><button id='append' type='button'>Append B</button><p role='status' id='selection'>No selection</p></section>
<section><h2>4. Disclosure</h2><button id='toggle' type='button' aria-expanded='false' aria-controls='details'>Show details</button><div id='details' hidden><p>The disclosure keeps focus on its toggle.</p><a href='#add'>Return to counter</a></div></section>
<section><h2>5. Listener lifecycle</h2><button type='button' id='tracked'>Tracked action</button><button type='button' id='stop'>Stop tracking</button><p id='tracked-count' role='status'>Tracked: 0</p></section>
<section><h2>6. Missing element diagnosis</h2><button type='button' id='diagnose'>Check absent element</button><p id='diagnosis' role='status'>Not checked</p></section>"""
APP29 = r"""function required(selector, type) {
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
"""
BODY30 = """<section><h2>Draft form</h2><form id='form'><label for='name'>Name</label><input id='name' name='name' required maxlength='40' autocomplete='off'><label for='quantity'>Quantity</label><input id='quantity' name='quantity' type='number' min='1' max='20' step='1' required><button type='submit'>Validate and save</button></form><p id='status' role='status'>No accepted state</p><pre id='accepted'>No accepted state</pre></section>
<section><h2>Persistence boundaries</h2><button id='reload' type='button'>Load saved draft</button><button id='corrupt' type='button'>Store malformed lesson draft</button><button id='reset' type='button'>Remove only lesson draft</button><p>This page owns only the ds60-js030-draft-v1 key. It never clears all browser storage.</p><p id='external' role='status'>No external storage notification</p></section>"""
APP30 = r"""const KEY = 'ds60-js030-draft-v1';
const form = document.querySelector('#form');
const status = document.querySelector('#status');
const accepted = document.querySelector('#accepted');
if (!(form instanceof HTMLFormElement) || !(status instanceof HTMLElement) || !(accepted instanceof HTMLElement)) throw new Error('required form nodes missing');
let state = null;
function validate(value) {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) throw new Error('Saved draft must be an object');
  if (Object.keys(value).sort().join(',') !== 'name,quantity,version' || value.version !== 1) throw new Error('Unsupported saved draft version or fields');
  if (typeof value.name !== 'string' || value.name.trim() === '' || value.name.length > 40) throw new Error('Name must contain 1 to 40 characters');
  if (!Number.isInteger(value.quantity) || value.quantity < 1 || value.quantity > 20) throw new Error('Quantity must be an integer from 1 to 20');
  return { version: 1, name: value.name.trim(), quantity: value.quantity };
}
function render(next) {
  state = next;
  accepted.textContent = JSON.stringify(state, null, 2);
}
function load() {
  try {
    const text = localStorage.getItem(KEY);
    if (text === null) { status.textContent = 'No saved lesson draft'; return; }
    const next = validate(JSON.parse(text));
    render(next);
    form.elements.namedItem('name').value = next.name;
    form.elements.namedItem('quantity').value = String(next.quantity);
    status.textContent = 'Loaded validated saved draft';
  } catch (error) { status.textContent = `Cannot load saved draft: ${error.message}`; }
}
form.addEventListener('submit', event => {
  event.preventDefault();
  try {
    const fields = new FormData(form);
    const next = validate({ version: 1, name: String(fields.get('name') ?? ''), quantity: Number(fields.get('quantity')) });
    render(next);
    try { localStorage.setItem(KEY, JSON.stringify(next)); status.textContent = 'Accepted and saved'; }
    catch { status.textContent = 'Accepted in memory; storage unavailable and not saved'; }
  } catch (error) { status.textContent = `Rejected: ${error.message}`; }
});
document.querySelector('#reload').addEventListener('click', load);
document.querySelector('#corrupt').addEventListener('click', () => {
  try { localStorage.setItem(KEY, '{broken'); status.textContent = 'Stored malformed data in lesson key; try loading'; }
  catch { status.textContent = 'Storage unavailable; malformed fixture was not stored'; }
});
document.querySelector('#reset').addEventListener('click', () => {
  try { localStorage.removeItem(KEY); status.textContent = 'Removed only lesson draft'; }
  catch { status.textContent = 'Storage unavailable; removal not confirmed'; }
});
window.addEventListener('storage', event => {
  if (event.key === KEY) document.querySelector('#external').textContent = 'Saved draft changed in another tab; load when ready';
});
load();
"""
BODY31 = """<section><h2>Literal text renderer</h2><label for='text'>Text to render</label><textarea id='text'>&lt;img src=x onerror=alert(1)&gt;</textarea><button id='render' type='button'>Render as text</button><pre id='output'></pre><p id='count' role='status'>Not rendered</p></section>
<section><h2>Local navigation policy</h2><label for='url'>Candidate URL</label><input id='url' value='./help.html'><button id='check' type='button'>Check URL</button><p id='url-status' role='status'>Not checked</p><div id='link'></div></section>
<section><h2>Policy evidence</h2><p>The page uses local app.js and style.css. Inspect the meta CSP and browser resource list. Checking a rejected candidate does not navigate to it.</p><p id='origin'></p></section>"""
APP31 = r"""const output = document.querySelector('#output');
const input = document.querySelector('#text');
const count = document.querySelector('#count');
if (!(output instanceof HTMLElement) || !(input instanceof HTMLTextAreaElement) || !(count instanceof HTMLElement)) throw new Error('renderer nodes missing');
document.querySelector('#render').addEventListener('click', () => {
  output.textContent = input.value;
  count.textContent = `Child elements: ${output.childElementCount}; image elements: ${output.querySelectorAll('img').length}`;
});
function localLink(text) {
  const url = new URL(text, location.href);
  if (!['http:', 'https:'].includes(url.protocol) || url.origin !== location.origin || url.username || url.password) throw new Error('Only same-origin HTTP links without credentials are accepted');
  return url;
}
document.querySelector('#check').addEventListener('click', () => {
  const target = document.querySelector('#link');
  target.replaceChildren();
  try {
    const url = localLink(document.querySelector('#url').value);
    const link = document.createElement('a');
    link.href = url.href; link.textContent = 'Open accepted local page';
    target.append(link);
    document.querySelector('#url-status').textContent = `Accepted: ${url.pathname}`;
  } catch (error) { document.querySelector('#url-status').textContent = `Rejected: ${error.message}`; }
});
document.querySelector('#origin').textContent = `This page origin: ${location.origin}`;
"""
TASKS = {
    29: [
        "Counter supports pointer and keyboard activation without double counting.",
        "Delegation distinguishes target and currentTarget.",
        "Appended B works through the existing list listener.",
        "Disclosure synchronizes hidden and aria-expanded while retaining toggle focus.",
        "Abort removes the tracked action listener.",
        "A missing selector produces an explicit diagnosis.",
    ],
    30: [
        "Validate named form fields before accepting state.",
        "Report actual persistence success or failure.",
        "Validate stored version and fields before loading.",
        "Distinguish unsaved draft from persisted state.",
        "Observe external-tab storage notification without overwriting unsaved input.",
        "Reset only the owned storage key.",
    ],
    31: [
        "Render untrusted-looking text using textContent.",
        "Validate parsed URLs before creating a navigation link.",
        "Keep the supplied restrictive CSP and external resource layout.",
        "Reject alternate origins, protocols and embedded credentials.",
        "Prove markup-looking text creates no child elements.",
        "Explain CSP, same-origin and server-authorization boundaries separately.",
    ],
}


def page(number, body, starter=False):
    policy = ""
    if number == 31:
        q = chr(34)
        policy = f"<meta http-equiv='Content-Security-Policy' content={q}default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'{q}>"
    state = "Learner starter" if starter else "Completed reference"
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>{policy}<title>js-{number:03d}: browser practice</title><link rel='icon' type='image/svg+xml' href='favicon.svg'><link rel='stylesheet' href='style.css'><script src='app.js' defer></script></head><body><main><h1>js-{number:03d}: {state}</h1><p>Use the guide and record actual browser observations. No Node execution is implied.</p>{body}</main></body></html>\n"""


for number, body, app in [(29, BODY29, APP29), (30, BODY30, APP30), (31, BODY31, APP31)]:
    for starter in [True, False]:
        base = (
            ROOT
            / "courses/javascript-typescript"
            / ("fixtures" if starter else "solutions/browser")
            / f"js-{number:03d}"
        )
        base.mkdir(parents=True, exist_ok=True)
        (base / "index.html").write_text(page(number, body, starter))
        (base / "style.css").write_text(STYLE)
        (base / "favicon.svg").write_text(
            "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='#1260b5'/><path d='M9 8h5v12c0 5-7 5-7 1h3c0 2 1 2 1-1V11H9zm10 1h7v3h-4v3h4v8h-8v-3h5v-3h-4z' fill='white'/></svg>\n"
        )
        source = (
            "// Answer-free learner starter. Implement each behavior in your saved copy.\n"
            + "\n".join(f"// Exercise {i}: {task}" for i, task in enumerate(TASKS[number], 1))
            + "\n"
            if starter
            else app
        )
        (base / "app.js").write_text(source)
        (base / "help.html").write_text(
            "<!doctype html><html lang='en'><meta charset='utf-8'><title>Local help</title><h1>Local fixture help</h1><p>This is an offline same-origin page.</p><a href='index.html'>Return to practice</a></html>\n"
        )
        (base / "README.md").write_text(
            f"""# js-{number:03d} browser {"starter" if starter else "reference"}

Copy this whole folder into a new learner-owned ignored directory, for example `.learning/expansion/js-{number:03d}/`. Preserve an existing attempt by choosing a new directory name instead of overwriting it. The starter contains the accessible controls and TODO comments; the separate completed reference contains the handlers. Use the guide before revealing the reference.

## Main route: Docker-only static server

Use Explorer, Finder or your native file-copy tool to make a **new learner-owned copy** of this whole folder under `.learning/expansion/js-{number:03d}-browser/`. Preserve an existing copy by choosing a new name. Open a terminal in that copied folder. Mount only this copy, not the repository, its parent directory or the authenticated classroom files.

The already prepared `ds60sqlpy-lab:0.3.0` image supplies Python inside Docker, so no host Python installation is required. Use a separate origin for each lesson. From the copied directory, POSIX shells use:

```bash
docker run --pull never --rm --name ds60-js-{number:03d}-static --read-only --user 65534:65534 --cap-drop ALL --security-opt no-new-privileges --memory 128m --cpus 1 --pids-limit 64 --publish 127.0.0.1:{8700 + number}:8000 --mount "type=bind,source=$PWD,target=/site,readonly" --entrypoint python ds60sqlpy-lab:0.3.0 -m http.server 8000 --bind 0.0.0.0 --directory /site
```

PowerShell uses its current-directory path explicitly:

```powershell
$browserLessonPath = (Get-Location).Path
docker run --pull never --rm --name ds60-js-{number:03d}-static --read-only --user 65534:65534 --cap-drop ALL --security-opt no-new-privileges --memory 128m --cpus 1 --pids-limit 64 --publish 127.0.0.1:{8700 + number}:8000 --mount "type=bind,source=$browserLessonPath,target=/site,readonly" --entrypoint python ds60sqlpy-lab:0.3.0 -m http.server 8000 --bind 0.0.0.0 --directory /site
```

Open `http://127.0.0.1:{8700 + number}/` in a real browser. The host publish address is loopback only; the 0.0.0.0 bind is inside the container namespace so the published port can reach it. The source mount is read-only and the server only reads this copied fixture. Edit your copy on the host and reload the page. If this specific port is occupied, choose a different unused loopback port and keep it consistent for storage checks. Never reuse the authenticated classroom origin for these scripts.

Stop this foreground server with Ctrl+C. If needed, stop only the named `ds60-js-{number:03d}-static` container from another terminal. The --rm option removes that container after it stops; the learner copy remains. The image must already be prepared through the course Docker setup; this command does not install packages or intentionally acquire external assets.

An optional already-prepared native Python environment can instead run `python -m http.server {8700 + number} --bind 127.0.0.1 --directory .` from the same copy. This alternative is not required for the Docker route.

## Checks

"""
            + "\n".join(f"{i}. {task}" for i, task in enumerate(TASKS[number], 1))
            + """

Record visible results, relevant DOM properties, browser version and any console errors. For keyboard behavior, use actual Tab and activation keys. For storage, keep the same scheme/host/port and use two actual tabs for the cross-document notification. Storage may be unavailable under browser policy; report that outcome honestly. The reference never clears unrelated localStorage keys. For CSP, inspect the actual browser policy and resource behavior; a static source check alone is not execution evidence.

No screen-reader compatibility claim follows solely from ARIA attributes. A separate assistive-technology session is needed for that evidence. No exercise requires external navigation or a paid API.
"""
        )
print("Authored browser starter and reference fixtures for 029-031")
