# Optional local PHP HTTP lab

This is a deliberately separate server exercise for `web-057` and `web-060`.
The classroom's PHP pad executes one CLI file. It does not start this server.
This fixture demonstrates actual requests, session cookies, CSRF checks,
prepared SQLite writes, escaped templates, validation redisplay and durable
local storage. It has **anonymous session ownership, not verified accounts**.
Do not put real personal information in it or expose it to the internet.

## Prepare a learner copy

Use Bash on Linux, macOS or Windows WSL 2. Start your Linux Docker engine.
From the repository root, choose a new ignored learner directory:

```sh
mkdir -p work/web-study
cp -R courses/web-development/fixtures/php-http-lab/. work/web-study/
cd work/web-study
```

If that directory already contains your work, keep it and choose a different
new directory before copying. Do not overwrite a previous learner project.
The commands below assume the project name `ds60-web-study` and loopback port
`18088`. Inspect existing ownership first:

```sh
docker context show
docker compose --project-name ds60-web-study ps --all
```

Stop if the context is a remote engine you did not intend to use, if this
project belongs to another task, or if port 18088 is occupied. Choose a fresh
project name consistently in your learner copy. Changing the published port
also requires updating the explicit Host and Origin allowlists in `index.php`.
Do not disable those checks to resolve a port mismatch.

## Build and open the lab

The first build requires internet access for the pinned PHP base image. The
application itself makes no external request and installs no Composer package.
The image checks that PDO SQLite is available during its build.

```sh
docker compose --project-name ds60-web-study --progress plain build
docker compose --project-name ds60-web-study up --detach --wait
curl --fail http://127.0.0.1:18088/health
```

Open `http://127.0.0.1:18088/` in your browser. Keep that hostname consistent:
`localhost` and `127.0.0.1` have different cookie scopes. The image runs as an
unprivileged user and the Compose port binds only to host loopback. The PHP
built-in server is a development tool, not a production architecture.

## Observe the real boundaries

1. Open the browser network panel and load the page. Inspect the HTML
   `Content-Type`, `Cache-Control`, and session `Set-Cookie` attributes. The
   local HTTP cookie is HttpOnly and SameSite=Lax; it deliberately lacks Secure
   because this fixture is loopback HTTP. A real HTTPS deployment needs Secure
   plus a complete trusted-proxy and session policy.
2. Enter a synthetic note containing `<Ada & Bea>`. Submit with the keyboard.
   Observe a POST to `/notes`, a 303 redirect and a subsequent GET. The visible
   note must be literal text, not an HTML element.
3. Submit an empty or oversized note through a deliberate request inspection.
   The server must reject it, retain the submitted text when safe, and avoid a
   partial write. The contract is 1 to 500 UTF-8 **bytes**, which is not the same
   as 500 user-perceived characters. The full request has a 4 KiB budget.
4. Change or omit the hidden CSRF token in your owned test request. Expect 403
   and no new note. Do not test another person's site.
5. Open a separate private browser session. It should not list the first
   session's notes. This demonstrates anonymous session separation. It does
   not prove a person logged in or that account recovery exists.
6. Inspect keyboard focus, labels, narrow layout and zoom after interaction.
   A successful HTTP request is not an accessibility review.

## Stop, resume and preserve data

```sh
docker compose --project-name ds60-web-study stop
docker compose --project-name ds60-web-study start
```

The `ds60-web-study_notes-data` named volume contains the SQLite file and server
sessions. Container replacement retains it too:

```sh
docker compose --project-name ds60-web-study up --detach --force-recreate --wait
```

Keep the same browser cookie and project name when testing session continuity.
Clearing cookies creates a new anonymous session and does not authenticate you
back into the old one. A volume surviving is different from a verified backup.
For a backup exercise, stop the lab, copy its owned volume to a deliberate
backup location, and restore into a separately named disposable volume. Verify
actual restored notes and session behavior before claiming recovery. Never
copy a live SQLite file casually and assume the copy is transactionally sound.

To remove this lab's container and network while retaining its named volume:

```sh
docker compose --project-name ds60-web-study down
```

A reset that includes `--volumes` deletes this lab's notes and sessions. Do that
only as an explicit decision after retaining any wanted work. Do not use broad
Docker pruning as the normal way to stop a lesson.

## Troubleshooting and production boundary

Use `docker compose --project-name ds60-web-study logs --tail 80 web` for the owned
server logs. A 400 Host error means the browser URL disagrees with the explicit
allowlist. A 403 means the token or origin did not match. A 422 means the note
failed validation. A 500 needs local server diagnosis; public responses do not
include exception details or paths.

This small server has no production login, password reset, distributed session
store, durable migration framework, public TLS termination, internet rate
limiting or multi-instance concurrency qualification. The per-session note cap
is a teaching budget, not a robust abuse-prevention service. Study `web-058`
and `web-059` before designing those capabilities. No source example grants
permission to publish real learner data or run this development server publicly.
