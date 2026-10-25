# Web development: HTML, CSS and PHP

Build readable, accessible pages and understand the server-side application
behind them. The subject combines HTML and CSS because they shape the same
document, then adds PHP as a distinct programming and request-handling layer.
JavaScript integration connects to the existing JavaScript/TypeScript and D3
path. You can start with no web knowledge and choose a pace that fits you.

## Start in the classroom

From the repository root, start or resume the ordinary classroom:

```sh
./classroom
```

Open the displayed browser URL and choose **Web development: HTML, CSS and
PHP**. HTML/CSS lessons use the isolated browser preview and need no host
compiler. Their complete document, inline styles and scripts share one saved
pad. The preview uses native HTML parsing, including real classic-script ordering, inline modules and DOMContentLoaded/load events. It is deliberately offline and cannot submit real network forms. External scripts/imports and navigation metadata such as base or meta http-equiv are unavailable.

For PHP examples, add the prepared Linux worker when you reach `web-031`:

```sh
./classroom --profile php-cli
```

An explicit profile selection changes the saved launch selection. Existing
unselected workers are not stopped. Repeat your custom `--project` name on each
command if you use one. The launcher prepares missing images as needed; after
preparation, use `./classroom stop` and `./classroom resume` to retain local
images, containers and learner state. Read the root setup guide for engine
installation, Windows WSL 2 and the difference between launcher settings and
Docker learning volumes.

PHP runs as a bounded CLI process with PDO SQLite. Output is text, including
HTML strings. Every default example uses small synthetic inputs and no external
service. The optional HTTP lab in `fixtures/php-http-lab/` is a separately
prepared learning project. It demonstrates real requests and persistence when
you explicitly choose that exercise.

## Explore in the preview studio

HTML/CSS and browser JavaScript/D3 lessons have an optional **Live preview**
switch. Turn it on explicitly to see the current page after a short pause in
typing. The studio places your editor and preview beside each other on a wide
screen and stacks them on a narrow screen. Use **Focus on editor & preview**
to give the experiment more space, then return to the lesson layout when ready.

Choose Fit to space, Desktop, Tablet or Phone to inspect the same page at a
different width. Changing the viewport does not rerun your program. Pause
updates keeps the last rendered version while you edit; Stop preview closes
the frame and cancels pending updates. Console errors remain visible so you can
repair a small example and continue.

Live rendering does not fill your saved-run history. **Run** leaves live mode,
saves the submitted source and keeps its result. **Save observation** retains
the currently rendered source and console output, then pauses automatic updates.
Your ordinary draft saving continues independently. Opening history, changing
lessons or reloading never turns live execution on by itself. PHP uses its
separate CLI worker and has no automatic browser execution.

## Choose a route

| Lessons | What you build and explain |
| --- | --- |
| `web-001` to `web-009` | Document structure, semantic headings, navigation, lists, media, tables and labeled forms |
| `web-010` to `web-024` | Cascade, box sizing, typography, contrast, positioning, Flexbox, Grid, responsive components and an accessible portal |
| `web-025` to `web-030` | DOM behavior, disclosures, validation feedback, data tables, browser trust boundaries and quality evidence |
| `web-031` to `web-044` | PHP syntax, types, arrays, functions, Unicode, streams, exceptions, objects, dependencies, dates and testing |
| `web-045` to `web-056` | Escaped templates, HTTP models, server validation, sessions, CSRF, password APIs, PDO, transactions, ownership, JSON APIs and a planner core |
| `web-057` to `web-060` | Real local HTTP integration, uploads and side-effect design, deployment operations and an integrated capstone |

The PHP branch begins after the basic page and form concepts; it does not
require completing every advanced CSS lesson first. Browser scripting lessons
link to `js-029` for the existing JavaScript DOM route. Continue into `js-043`
and the D3 specialization when adding charts, while retaining semantic tables
and honest units. Use the SQL route for deeper relational modeling and the
Docker route for broader deployment and recovery knowledge.

## How to learn from a chapter

Read the mental model and trace both worked examples. Predict before running,
then change one condition. Each practice unit progresses through prediction,
guided change, independent construction, diagnosis, boundary testing and
transfer. Save your own attempt before revealing the separate reference.
References include checks, but a printed marker is not proof of accessibility,
production readiness or your understanding.

Browser lessons need actual observations after interaction, resizing and zoom.
PHP lessons distinguish pure function tests, disposable SQLite execution and
real HTTP evidence. A session represented by an array is a model. The optional
server fixture makes that distinction visible through real cookies, redirects,
CSRF rejection and saved notes. It uses anonymous session ownership and is not
a verified account or production authentication service.

The classroom saves pads, notes and result history under each lesson. Reading a
past result does not rerun it or replace the current source. A saved progress
marker records your chosen pace; it is not a certification. For companion help,
use the lesson's **Ask an AI tutor about this lesson** prompt and share the
attempt you want reviewed.

## Contribute or extend

Read [AGENTS.md](AGENTS.md) and [the authoring instructions](authoring/README.md).
The metadata and prose generator does not install dependencies, execute learner
code or start Docker. New capabilities need a reviewed runtime contract and
actual evidence, not a new manifest field containing a shell command.
