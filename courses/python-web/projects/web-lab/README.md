# Python web service lab

Run three real applications against an owned PostgreSQL database: Flask through
Gunicorn, FastAPI through Uvicorn, and Django through Gunicorn. Their note stores
and sessions are separate. A fourth Python service owns durable FastAPI jobs.
The lab is for local synthetic data and binds every published port to loopback.
It is not a public multi-tenant hosting platform.

## Prepare once

Use Linux Docker on Linux/macOS, or a Linux Docker engine with WSL 2 on Windows.
No host Python, PostgreSQL or framework installation is required. Work in your
own clone or copy of this complete project directory. Keep `.workshop/` private.

First prepare the classroom's `python-web` image from the repository root:

```sh
./classroom build --profile python-web --local-build
```

The ordinary profile includes the separately locked framework dependencies.
This project builds a small source/static-assets layer on top of that image.
Its build runs Django `collectstatic`; it never downloads assets when you open
a page. The PostgreSQL17 image must also be present locally. If it is not:

```sh
docker pull mirror.gcr.io/library/postgres:17
```

That explicit preparation download is separate from startup and resume. An
already prepared equivalent PostgreSQL17 image can be selected through
`WORKSHOP_POSTGRES_IMAGE` before initial preparation.

```sh
cd courses/python-web/projects/web-lab
./workshop prepare
./workshop start
```

Preparation uses the current documented local worker image by default. Set
`WORKSHOP_BASE_IMAGE` to an already prepared compatible `python-web` image when
using another qualification build. The launcher saves the initial project,
image and port selection. Subsequent actions use the saved values and never
silently follow a changed caller environment.

Default pages are:

- Flask: <http://127.0.0.1:18761>
- FastAPI: <http://127.0.0.1:18762>
- Django: <http://127.0.0.1:18763>

Before first preparation, `WORKSHOP_PROJECT`, `WORKSHOP_FLASK_PORT`,
`WORKSHOP_FASTAPI_PORT` and `WORKSHOP_DJANGO_PORT` can select a distinct owned
project and three unused ports. Use the exact displayed `127.0.0.1` URLs so
Origin/Host checks agree. Do not expose these ports on an external interface.

## Follow one complete request

Sign in as `alice` with password `classroom-demo`. Create a note and refresh the
page. Sign in as `bob`; Alice's note is not in Bob's collection. Every note detail
lookup applies the same owner boundary. A client cannot assign an owner through
the write schema. These are deliberately public synthetic classroom credentials,
not instructions for selecting production passwords.

Flask and FastAPI use the original small PostgreSQL session implementation in
`store.py`. Tokens are stored as SHA256 digests, expire after two hours and have
separate framework namespaces. State-changing requests require the exact local
Origin and a session-bound CSRF token. Django uses its own authentication,
session and CSRF framework with actual migrations and ORM models. The different
implementations intentionally expose comparable user-visible behavior.

The local HTTP fixture declares HttpOnly and SameSite cookies but does not set
Secure, because it does not establish TLS. Public deployment requires a reviewed
HTTPS edge, secure-cookie settings, account policy, abuse controls, secrets
management and operational acceptance. The finite lessons explain those
boundaries without pretending this localhost lab deploys them.

The Django admin is available at `/admin/`. Its synthetic local operator is
`operator` with password `local-admin-demo`. It has privileged access across the
teaching users. Treat this as an explicit administrative role, not an end-user
interface. Django's collected admin assets are served locally through WhiteNoise.

## Observe durable work and actual streaming

On the FastAPI page, create a held job. The separate worker changes its state from
queued to running. The SSE connection shows those events before you press
Release. Release allows the worker to calculate the bounded sum and commit the
result and finished event together. The job remains stored if the browser or its
SSE connection disconnects.

The worker reports healthy only after its live process completes a database job
poll. A private atomic heartbeat expires after 15 seconds without another
successful poll. Startup waits for this check as well as database TCP readiness
and each framework's HTTP readiness. A process that merely exists, or an old
heartbeat left by a killed worker, is insufficient. A failed database transaction
exits the worker instead of renewing its heartbeat.

The browser stores only the selected job identity in its origin's localStorage.
Session/CSRF tokens are not put there. Reloading as the same authorized user can
reconnect to the stored job. Event IDs allow the HTTP client to resume after an
acknowledged event. Cursors from another job or an unknown future event are
refused. The stream is bounded to 30 seconds per connection; EventSource reconnects
while the user has not explicitly disconnected it.

The WebSocket button performs one actual authenticated local echo and closes.
It is a finite protocol demonstration, not a collaborative application or a
persistent background job system. The server bounds message size and waiting.

## Offline API documentation

FastAPI `/docs` serves an original local OpenAPI explorer. It reads local
`/openapi.json`, shows every operation and component schema, and offers explicit
fixed GET/read/create-note calls. It is intentionally smaller than Swagger UI.
Default Swagger/ReDoc pages are disabled, so there are no hidden CDN bundles,
remote validators, fonts or analytics. All UI text is inserted as text, and
request controls cannot choose a remote URL. The HTML/CSS/JavaScript is original
repository source; Django/WhiteNoise assets retain their installed package
licenses. The browser acceptance must separately confirm actual requests remain
local; a source search alone does not prove browser delivery.

## Stop, resume and retain data

```sh
./workshop stop
./workshop resume
```

Resume starts the exact five existing containers. It does not build, pull, rerun
migrations or choose another project. Start can create missing containers from
the saved local images and runs the reviewed idempotent migration/fixture step.
Replace deliberately recreates application/worker containers from the saved
image while keeping the PostgreSQL container and data:

```sh
./workshop replace
```

PostgreSQL data lives in the project-owned named volume ending in
`_postgres-data`. Settings, signing material and acceptance receipts live in
`.workshop/`. Neither is an image layer. Keep both when moving or backing up the
lab; a Git clone alone does not contain your database. No launcher action deletes
volumes, prunes images or removes unrelated containers. Do not use `down -v` or
volume pruning if you want to retain this data.

The worker commits state transitions and event rows in PostgreSQL transactions.
A stopped worker can resume a running, released job from the ledger. There is no
claim of exactly-once arbitrary external effects: this job's effect is its
transactional database result. The separate outbox chapter explains the wider
boundary.

## Actual acceptance and saved readback

```sh
./workshop check
./workshop stop
./workshop resume
./workshop verify
./workshop replace
./workshop verify
```

Check makes real HTTP calls among the owned containers, creates uniquely named
synthetic notes, checks anonymous/owner/CSRF/origin/host refusals, fetches local
assets and OpenAPI, performs an actual WebSocket exchange, and verifies SSE bytes
arrive before the test releases the held job. It disconnects and resumes the
stream using its event identity, then checks the committed result. It saves a
source-hash-bound receipt at `.workshop/acceptance.json`.

Verify reads the exact note/job identities from that receipt. It does not create
replacement notes or jobs and cannot make lost state appear preserved by rerunning
the original workflow. It does establish a fresh session to read the retained
records. Container identity, service acceptance, browser observations and
post-replacement readback are distinct evidence and should be recorded separately.

PostgreSQL readiness checks its TCP listener at `127.0.0.1`. The official image
uses a temporary Unix-socket-only server during first initialization, so a socket
probe alone can report healthy before another container can connect for migrations.
The TCP check waits for the final application-facing server.

Failed project checks embed bounded, redacted tails from allowlisted phase and
service logs in the top-level report before and after cleanup. This retains useful
startup evidence in CI without uploading the private `.workshop/` directory,
password file, signing key, session cookies or authorization headers.

Use `./workshop status` and `./workshop logs` to inspect this project. If startup
fails, retain the error and inspect readiness/database state. Do not switch to a
new project name to conceal a defect. A clean configuration or prepared image is
not a completed acceptance run.

## Maintained native CI/contributor gate

Contributors with an already prepared Python and Playwright/Chromium environment
can run the complete disposable qualification. This is separate from the ordinary
Docker-only learner entrypoint:

```sh
python courses/python-web/projects/web-lab/check_project.py \
  --workspace work/python-web-ci-workspace \
  --image ds60sqlpy-worker-python-web:1.1.0 \
  --browser-python /absolute/path/to/prepared/browser-python \
  --report work/python-web-project-receipts.json \
  --confirm-disposable
```

Use a fresh workspace path and new report path. The checker refuses reused
resources, requires the prepared base and PostgreSQL images to match the native
Linux engine, verifies the shipped public-source hashes and runs the real service,
worker interruption, browser, exact resume and replacement checks. It exports
receipts before removing only its newly owned containers/network. Its synthetic
database volume and workspace evidence remain available for inspection. It never
prunes images or removes learner volumes. Browser downloads belong to explicit
preparation, not to the checker or classroom runtime.
