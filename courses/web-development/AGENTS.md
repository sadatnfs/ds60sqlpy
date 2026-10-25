# Web development authoring and teaching

Read the root guidance and `.agents/skills/add-learning-path/SKILL.md`. The
integrated subject has stable IDs `web-001` through `web-060`. HTML supplies
structure, CSS presentation, JavaScript browser behavior and PHP server-side
logic. Keep these responsibilities explicit. A subject is not a runtime.

The durable prose and metadata source is `authoring/chapters.json`. Durable
executable starters and references are `authoring/templates/`. Edit those
sources, then run `python courses/web-development/authoring/build.py`. The
published guides, lesson sources, solutions and manifests are generated.
Format both templates and published code with the repository toolchain, then
run the generator's `--check` mode. Do not normalize source by deleting
whitespace or claim lexical resemblance proves behavior.

Every guide includes two worked examples, six distinct progressive exercises,
mechanism explanations, common mistakes, explicit boundaries and a specific
tutor prompt. Preserve answer-free starters. Keep source output and explanatory
solutions separate. The reader is not an HTML execution host: syntax examples
must render escaped and highlighted, while the explicit HTML preview runs the
learner's complete document in its isolated frame.

`html-browser` accepts a single complete HTML document with embedded CSS and
bounded inline JavaScript. Preserve native parsing, classic lexical scope and real document lifecycle events. External imports and navigation metadata are rejected. Reference documents have no CDN, external script,
network data, cookies or required remote fonts. Ordinary forms do not submit
from that preview. Do not weaken the sandbox to make an external example work.
`php-cli` stages `main.php`; prepared PHP and PDO SQLite support deterministic
CLI examples. A PHP string containing HTML is text output, not an automatically
rendered page. No reference assumes Composer, arbitrary files, mail, external
services or a persistent HTTP process.

Server lessons that model requests, sessions and CSRF must say they are models.
The separate maintained fixture in `fixtures/php-http-lab/` provides a real
loopback-only HTTP exercise under a deliberately owned Compose project. It has
anonymous session ownership, not verified user accounts. Do not describe it as
a production login system or expose PHP's development server publicly. Its
Docker commands require the learner's explicit setup action; reading a lesson
must not execute them. Preserve named volumes and browser-session state.

Teach validation and contextual escaping separately. Bound untrusted input,
check scalar shape before string functions, use prepared SQL values and
allowlisted query structure, and enforce ownership server-side. Keep fake
credentials and tokens visibly synthetic. A local hash test does not qualify
authentication; an in-memory database does not qualify PostgreSQL concurrency;
a browser success marker does not qualify accessibility or mastery.

Test structural relationships, real settled browser behavior, keyboard focus,
resizing, script failures, saved pads and receipt isolation. Run all PHP
references in the prepared worker and include invalid inputs. The reference
inventory describes expected observations, never an invented runtime receipt.
Link to JavaScript/D3, SQL and Docker paths where they add depth instead of
repeating those subjects shallowly. Do not use em dashes.

## Live preview state contract

Live HTML and browser JavaScript/D3 rendering is explicitly enabled for the
current workspace in the current page session. It debounces source edits and
guards against stale frames and callbacks. It must never write immutable
browser-run receipts automatically. Existing draft saving is independent.
Manual Run leaves live mode and preserves its exact submitted source; explicit
Save observation captures the current preview and pauses automatic updates.
Navigation, source-context changes, Stop and historical-result selection cancel
pending refreshes. Reload does not restore execution opt-in. Viewport and
fullscreen changes alter presentation without restarting source. Preserve
editor focus while an automatically refreshed page initializes.

Run the permanent live acceptance script against disposable learning state:

```sh
python courses/web-development/authoring/check_live_preview.py --url http://127.0.0.1:PORT --confirm-disposable --report work/web-live-report.json
```

Never point it at a learner's real saved classroom. It intentionally edits
test pads and creates only the explicitly requested observation records.
