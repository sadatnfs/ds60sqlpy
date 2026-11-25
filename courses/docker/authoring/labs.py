"""Per-lesson Docker teaching that replaces the old shared scaffolds.

Each entry holds:
  lab     the optional host experiment for this chapter, with its own cleanup;
  trap    one further misconception, how it shows up and how to correct it;
  ask     a transfer case posed in the guide;
  answer  the worked answer to that case, kept in the solutions file.
Shared operating rules live in courses/docker/STUDY-GUIDE.md.
"""


def t(text):
    return " ".join(text.split())


LABS = {
    "docker-001": dict(
        lab=t("""
Build the fixture image once from your copy of `compose-lab`, run worked example 1, then
repeat the arithmetic run without `--rm`:
`docker run --pull never ds60-docker-study:local python -c "print('kept')"`.
Now `docker ps -a --filter ancestor=ds60-docker-study:local` lists one Exited container with a
generated name, while the `--rm` run left nothing behind. Remove only that container by its ID
with `docker rm`, then confirm with `docker image ls ds60-docker-study` that the image is still
there. You have watched three separate lifetimes: the process ended when `print` returned, the
container stayed until you removed it, and the image outlives both. Nothing here publishes a
port or creates a volume, so the only object left is the local image, which later lessons
reuse.
"""),
        trap=t("""
A related misconception is that every container boots its own small operating system. If that
were true, `uname -r` inside the fixture would report a Debian kernel. Run
`docker run --rm --pull never ds60-docker-study:local uname -r` and compare it with
`docker info --format '{{.KernelVersion}}'`: the two match, because the container's system
calls go to the engine's Linux kernel. What the `python:3.12-slim` base provides is a Debian
userland, meaning files such as libraries, a shell and package metadata. So "this image is
Debian" describes its files, never its kernel, and a kernel feature the engine lacks cannot be
added by choosing a different base image.
"""),
        ask=t("""
A teammate runs `docker run --pull never ds60-docker-study:local python -c
"open('/tmp/n','w').write('1')"` twice without `--rm`. How many containers, images and copies
of `/tmp/n` exist afterwards, and what happens if they now try `docker image rm
ds60-docker-study:local`?
"""),
        answer=t("""
There are two stopped containers, one image and two separate copies of `/tmp/n`, each in its own
container's writable layer. The image is unchanged because writes never flow back into it. The
removal fails with a conflict that names a container still using the image, because stopped
containers keep a reference to the image they were created from. Remove the two containers
first, by ID, and the image removal then succeeds. If `docker ps -a --filter
ancestor=ds60-docker-study:local` showed only one container, or a fresh container from the image
could read `/tmp/n`, this explanation would be wrong.
"""),
    ),
    "docker-002": dict(
        lab=t("""
Run worked example 1 on the host before any other lab and copy four facts into the worksheet:
the context name, the `Endpoint` value from `docker context inspect`, the OSType and the Compose
version. Then check the environment with `env | grep '^DOCKER_'`, which should print nothing on
a plain local setup. If your engine is a local one you control, quit it briefly and run worked
example 2 again: `docker --version` still prints, while `docker info` fails with a connection
error and shows no Server section. Start the engine again and wait for `docker info` to succeed
before continuing. On Windows, do all of this in the Ubuntu terminal under WSL 2, where `command
-v docker` should resolve to a Linux path. This lesson creates no containers or volumes, so
there is nothing to clean up; the recorded endpoint is the evidence that later labs build on.
"""),
        trap=t("""
Another trap is trusting `docker context show` while an environment variable redirects the
client. An exported `DOCKER_HOST` or `DOCKER_CONTEXT` takes precedence over the context saved
with `docker context use`, so the selected context can look local while commands go elsewhere.
The symptom is containers or images you do not recognize, or a different `Name` and kernel in
`docker info`. Read `env | grep '^DOCKER_'`, compare the `Server` section of `docker version`
with the endpoint you recorded, and unset the variable in this shell instead of running
destructive commands to find out what the other engine holds.
"""),
        ask=t("""
On Windows, a learner runs `docker info` successfully in PowerShell, then pastes the fixture
README's guard block (`if [ -e .learning/docker-study ]; then ...`) into the same window and gets
a parse error. Which shell should they use, and does the successful `docker info` change the
answer?
"""),
        answer=t("""
They should switch to the Ubuntu terminal under WSL 2 before running any lab command. The guard
is Bash syntax, and the labs assume Linux paths and Bash quoting. The successful `docker info`
only proves the Windows client reached some engine; it says nothing about whether the shell can
run the lab commands. In Ubuntu, the expected result is that `docker info --format
'{{.OSType}}'` prints `linux` and the guard runs. If `docker context show` inside Ubuntu names a
different endpoint from the one recorded earlier, that observation disproves the assumption that
both shells talk to the same engine, and it must be reconciled first.
"""),
    ),
    "docker-003": dict(
        lab=t("""
Use a named throwaway container to see the writable layer directly:
`docker run --name ds60-layer-demo --pull never ds60-docker-study:local python -c
"open('/tmp/w.txt','w').write('1')"`. Then `docker diff ds60-layer-demo` lists `A /tmp/w.txt`,
an addition recorded only in that container's layer. Remove it with `docker rm ds60-layer-demo`
and the change is gone while the image is untouched. Next, start the fixture project and run
`docker compose -p ds60-docker-study exec app sh -c 'echo note > /tmp/note; touch /app/x'`. The
`/tmp` write succeeds because Compose mounts a tmpfs there, and `touch` fails because the root
filesystem is read-only. After `docker compose -p ds60-docker-study restart app` the note is
gone, since a tmpfs lives in memory and is cleared when the container stops, while `/counter`
still reports the value kept in the `/data` volume.
"""),
        trap=t("""
A tempting rescue after losing a file is `docker commit`, which turns a container's writable
layer into a new image. It does preserve the file, but it also bakes in whatever else the layer
holds: scratch output, caches, perhaps a credential typed during debugging. The result has no
Dockerfile recipe, so nobody can rebuild or review it, and data in volumes is not included at
all. The correction is to separate the two kinds of change: application code changes go into
the Dockerfile and a rebuild, while data that must survive recreation goes into a named volume
mounted at a known path.
"""),
        ask=t("""
A service writes uploads to `/app/uploads` with no volume and no `read_only`. Yesterday the
uploads survived `docker compose restart`. Today, after editing an environment value and running
`docker compose up -d`, they are gone. Explain both observations and propose one change.
"""),
        answer=t("""
`restart` stops and starts the same container, so its writable layer, including `/app/uploads`,
survives. Editing the service configuration makes `up -d` recreate the service: a new container
ID with a fresh, empty writable layer on top of the image, so the uploads are not there.
The fix is a named volume mounted at `/app/uploads`, ideally with a read-only root and a tmpfs
for scratch. Record `docker compose ps -q app` before and after `up`; different IDs confirm
recreation. Seeing the same ID with the files missing would disprove this explanation and point
at the application deleting them.
"""),
    ),
    "docker-004": dict(
        lab=t("""
Start the fixture project, then time the stop in worked example 2:
`time docker compose -p ds60-docker-study stop --timeout 10 app`. The fixture already does three
things right. Its `CMD` is exec form, `init: true` places a small init as PID 1 that forwards
signals, and `server.py` installs a SIGTERM handler that shuts the HTTP server down cleanly. So
the stop should take well under ten seconds, and `docker compose -p ds60-docker-study ps -a`
should report `Exited (0)` rather than 137. Run `docker compose -p ds60-docker-study exec app ps
-o pid,args` before stopping if `ps` is available in your image; otherwise read
`/proc/1/cmdline`. Write the PID 1 command, the stop duration and the exit code in the worksheet.
Start the service again with `up -d --wait` when you are done.
"""),
        trap=t("""
A subtler problem is a startup script that ends without `exec`. A `start.sh` that sets
variables and then runs `python server.py` leaves the shell as the parent, so SIGTERM reaches the
shell, which does not forward it, and Python never runs its handler. The engine waits for the
timeout and then sends SIGKILL, which you see as a stop that always takes the full grace period
and an exit code of 137. The fix is one word: end the script with `exec python server.py`, so
Python replaces the shell and receives signals directly. An init process helps reap children but
does not repair a script that swallows the signal.
"""),
        ask=t("""
A worker container always takes exactly 30 seconds to stop and then shows exit code 137. Its
Compose file sets `stop_grace_period: 30s` and its command is `sh -c "python worker.py"`. What is
happening, and what would you change first?
"""),
        answer=t("""
The shell started by `sh -c` is PID 1 and receives SIGTERM, but the worker never gets it, so the
engine waits the full 30-second grace period and then kills everything with SIGKILL, which is
the 137. Change the command to exec form, `["python", "worker.py"]`, or end the shell command
with `exec`, and make sure the worker handles SIGTERM by finishing its current item. The expected
result is a stop in a few seconds with exit code 0. If the stop still took exactly 30 seconds
after that change, the worker itself would be ignoring SIGTERM, which disproves the shell
explanation.
"""),
    ),
    "docker-005": dict(
        lab=t("""
In a scratch directory, write the five-line Dockerfile from worked example 1 next to a copy of
`server.py`, then build it with a distinct tag such as `ds60-docker-minimal:local` and
`--progress=plain`. Read the log and match each numbered step to an instruction: FROM resolves a
base, COPY transfers one file from the context, and CMD appears only as metadata because nothing
runs at build time. Then run `docker image inspect ds60-docker-minimal:local --format
'{{json .Config.Cmd}} {{json .Config.ExposedPorts}}'` to see the recorded command and the
documented port, and `docker ps` to confirm that nothing is running yet. Start it with `docker
run --rm -p 127.0.0.1:18081:8080 ds60-docker-minimal:local` and open the root URL. Stop it with
Ctrl+C and remove the extra tag with `docker image rm` when you finish.
"""),
        trap=t("""
Learners also expect `docker build` to fail when the program is broken. A build only executes
RUN steps; it never starts the program named by CMD. A `server.py` with a syntax error copies
and builds perfectly, and the failure appears only when a container starts. If you want the
build to reject broken source, add a deliberate RUN check such as
`RUN python -m py_compile /app/server.py`, which runs at build time and fails the build on a
syntax error. Keep in mind that this proves the file parses, not that the server answers
requests, so runtime acceptance still needs its own check.
"""),
        ask=t("""
You add `RUN python -c "print('built')"` and `CMD ["python", "-c", "print('started')"]` to a
Dockerfile, build it, and run one container. Which line appears in the build log, which appears
in the container output, and how many times will each appear if you run three containers?
"""),
        answer=t("""
`built` appears once in the build log, because RUN executes during the build and its result is
stored in a layer; a cached rebuild may not print it again at all. `started` appears in the
output of each container, because CMD is the default command of every new container, so three
runs print it three times and the build log never shows it. The observation that would disprove
this is `started` in the build output, which would mean the command was placed in a RUN step
rather than CMD.
"""),
    ),
    "docker-006": dict(
        lab=t("""
Make a scratch copy of the fixture and add three decoys: `.env` containing a fake value, a
nested `notes/debug.log`, and `cache/__pycache__/x.pyc`. Move the fixture's `.dockerignore`
aside, build once, and read the transferred context size in the plain log. Put the ignore file
back and build again; the context shrinks. To prove exclusion rather than guess it, write a
two-line `ctx.Dockerfile` containing `FROM ds60-docker-study:local` and `COPY . /ctx`, build it
with `-f ctx.Dockerfile -t ds60-ctx-check .`, and list the result with `docker run --rm
ds60-ctx-check find /ctx`. Only the files you meant to send should appear. Remove the decoys,
`ctx.Dockerfile` and the `ds60-ctx-check` image when you finish, and never put a real secret in
a decoy.
"""),
        trap=t("""
Another misconception is that a build argument is a safe way to pass a token, as in `ARG
NPM_TOKEN` followed by a RUN step that uses it. Build arguments are recorded in the image
history, and `docker history --no-trunc` can show the value in the RUN line that consumed it.
The correction is a BuildKit secret mount, `RUN --mount=type=secret,id=npm_token ...`, which
exposes the value as a file only during that one step and keeps it out of every layer and the
history. Rotating a credential that has already been built into a pushed image is still
necessary, because removing it later does not recall copies already pulled.
"""),
        ask=t("""
A project's `.dockerignore` contains `node_modules` and `*.key`. The build still copies
`config/tls/server.key` into the image. Explain why, write the corrected rule, and say how you
would prove the fix worked without trusting the build's success message.
"""),
        answer=t("""
`*.key` in `.dockerignore` matches only at the root of the build context, unlike `.gitignore`,
so a nested `config/tls/server.key` is still sent and copied. The corrected rule is `**/*.key`.
To prove the fix, build a throwaway stage that copies the whole context and list it with `find`,
or check that a `COPY config/tls/server.key` step now fails because the file is absent. The key
must also be rotated, since earlier images already contain it. Seeing `server.key` in the listing
after the change would show that the rule or the context path is still wrong.
"""),
    ),
    "docker-007": dict(
        lab=t("""
Run worked example 1 twice and note which numbered steps say `CACHED` the second time. Then
change one comment in `server.py` and build again: the base and WORKDIR steps stay cached, and
the `COPY server.py` step and everything after it rerun. Next, add a harmless `RUN echo
dependencies` line above the COPY and build twice more; it caches after its first run, and an
edit to `server.py` no longer invalidates it. That ordering is the whole trick of dependency
layers. Finish with worked example 2 and compare its total time with the cached build. Record
each step label and its cache status rather than wall-clock durations, which vary with the
engine. Delete the extra RUN line afterwards so your copy matches the fixture again.
"""),
        trap=t("""
A further trap is believing that `docker build --pull` and `--no-cache` are the same refresh.
`--pull` asks the engine to check the registry for a newer base image before building, while
`--no-cache` reruns every instruction against whatever base is already local. A security fix in
the base image therefore needs `--pull`, and a stale download inside a RUN step needs either a
changed instruction or `--no-cache`. When you need both, use both, and record the resolved base
digest from the build log so you can show which base the new image actually used.
"""),
        ask=t("""
A Dockerfile copies `requirements.txt`, runs `pip install`, and then copies the source tree.
You edit only `app/views.py`. Then, separately, you add a new package to `requirements.txt`.
Which steps rerun in each case, and why?
"""),
        answer=t("""
Editing `app/views.py` changes only the input to the final source COPY, so the base, the
requirements COPY and the `pip install` step are all served from cache and only the source copy
and later steps rerun. Adding a package changes the bytes of `requirements.txt`, which
invalidates that COPY, the install that follows it, and every later step, including the source
copy. In plain logs the first build shows `CACHED` on the install step and the second does not.
If the install step reran after a source-only edit, the source must be copied before the
requirements, which is the ordering this lesson warns against.
"""),
    ),
    "docker-008": dict(
        lab=t("""
Start the fixture project and request the root URL to read the default message. Then create
`compose.override.yaml` in your copy with worked example 1 and run `docker compose -p
ds60-docker-study config` to see the merged value before anything starts. Run `docker compose -p
ds60-docker-study restart app` and request the root URL again: the old message remains, because
restart reuses the existing container configuration. Now run `up -d --wait` and request it once
more; the new message appears and `ps -q app` shows a new container ID. Finally, change worked
example 2 to pass `-e APP_MESSAGE=42` and print `type(os.environ['APP_MESSAGE'])`: the result
is `<class 'str'>`, because every environment value arrives as text. Delete the override file afterwards so later lessons start from the
fixture defaults.
"""),
        trap=t("""
Compose interpolation catches people in a second way: a literal dollar sign in a value is
treated as a variable reference while the file is rendered. A message such as `cost $AMOUNT`
becomes `cost ` followed by nothing, with a warning that the `AMOUNT` variable is not set, before
the container ever sees it. Escape it as `$$AMOUNT`, which Compose renders as a single dollar sign,
and confirm with `docker compose config`, which prints the rendered value. That same command is
the quickest way to see whether a value came from the shell, an `.env` file or the YAML itself.
"""),
        ask=t("""
An image has `ENTRYPOINT ["python", "server.py"]` and `CMD ["--port", "8080"]`. A learner runs
`docker run IMAGE --port 9090` and later `docker run --entrypoint python IMAGE -V`. What
command line does each container start?
"""),
        answer=t("""
In the first run, arguments after the image name replace CMD, so the container runs `python
server.py --port 9090`; the entrypoint stays. In the second, `--entrypoint python` replaces the
entrypoint, and setting the entrypoint also resets the default CMD, so the container runs
`python -V` and prints a version instead of starting the server. `docker inspect` on each
container shows the effective `Path` and `Args`. If the second container started the server, the
entrypoint override was not applied, perhaps because it was placed after the image name, where it
becomes an argument instead.
"""),
    ),
    "docker-009": dict(
        lab=t("""
With the project running, request `http://127.0.0.1:18080/` from the host and then run `docker
compose -p ds60-docker-study port app 8080`, which should print `127.0.0.1:18080`. Next, try the
same URL from inside the app container: `docker compose -p ds60-docker-study exec app python -c
"import urllib.request; urllib.request.urlopen('http://127.0.0.1:18080/', timeout=2)"`. It fails,
because inside the container 127.0.0.1 is the container's own loopback, where nothing listens on
18080. Change the URL to port 8080 and it succeeds. Then run the tools-profile client from the
fixture README, which reaches `app:8080` by name. Three requests, three scopes. Nothing new is
created except the short-lived client container, which `--rm` removes.
"""),
        trap=t("""
Learners on Linux sometimes assume a host firewall such as `ufw` protects a published port. The
engine installs its own packet-filtering rules for published ports, and depending on the setup
those rules can take effect before the host firewall's own chains, so `ports: - "8080:8080"` can
be reachable from the network even when the firewall appears to deny 8080. The reliable control
is the bind address in the mapping: publish to `127.0.0.1` when only the host needs access, as
the fixture does, and check with `docker compose port` or `ss -ltn` on the host which address is
actually listening.
"""),
        ask=t("""
A second service in the same project needs to call the app, and a teammate configures it with
`http://localhost:18080/`. It fails. Give the URL it should use, and explain why the host's URL
does not work from there.
"""),
        answer=t("""
It should use `http://app:8080/`. Inside the second container, `localhost` is that container's own
loopback interface, and port 18080 exists only as a mapping on the host, so nothing listens there.
Compose puts both services on a project network where the service name `app` resolves to the
app container, and the app listens on its container port 8080. The expected result is the same
JSON the browser receives. If `app:8080` also failed while the host URL worked, the services
would likely be on different networks, which `docker network inspect` would show.
"""),
    ),
    "docker-010": dict(
        lab=t("""
Run worked example 2, then repeat each program without `--rm` and with names such as
`ds60-ok` and `ds60-fail`. `docker ps -a --filter name=ds60-` shows `Exited (0)` and `Exited
(1)`, and `docker logs ds60-fail` replays the traceback, because logs belong to the container,
not the process. Separate the streams on the host with `docker logs ds60-fail 2>/dev/null`, which
prints nothing because the traceback went to stderr. Next, start the project, request an unknown
route such as `/missing`, and read `docker compose -p ds60-docker-study logs --tail 5 app`: the
404 appears as a request line while the container stays Up. Save each exit code and log line in
the worksheet, then remove the two named containers with `docker rm ds60-ok ds60-fail`.
"""),
        trap=t("""
A further trap is reading `docker logs` on a service that writes to a log file instead of the
standard streams. The command then shows only startup lines, and the learner concludes that no
requests arrived. The engine's logging driver captures only stdout and stderr of the main
process, so a file such as `/var/log/app.log` is invisible to it and also disappears with the
writable layer. Configure the application to log to stdout or stderr, as the fixture's HTTP
server does, and keep any log file you truly need on a volume with its own retention plan.
"""),
        ask=t("""
After a deployment, `docker compose ps` shows the app as `Up 3 minutes`, but users report
errors. A teammate proposes `docker compose restart app` immediately. What should be captured
first, and why is the restart weak evidence of a fix?
"""),
        answer=t("""
Capture the image identity, `docker compose ps -a` state, a bounded `logs --tail` sample and the
status code from one failing request, with timestamps. `Up` only says the main process exists, so
the evidence has to come from the application's own responses. A restart may make the errors
stop for a while, but it changes the conditions without explaining them, and the logs from the
failing period become harder to find. If the same request still failed after a restart, that
observation would rule out transient in-memory state as the cause.
"""),
    ),
    "docker-011": dict(
        lab=t("""
Follow worked example 1 and 2 from your fixture copy, then inventory what the project owns:
`docker compose -p ds60-docker-study ps`, `docker network ls --filter
label=com.docker.compose.project=ds60-docker-study` and the same label filter on `docker volume
ls`. You should find one app container, one default network and one named volume, each with a
project label. Now run `docker compose ps` in the same directory without `-p`: it lists
nothing, because the fixture sets no top-level `name:`, so the project name defaults to the
directory name, `docker-study`, and that project owns no containers. Then run
`docker compose -p ds60-docker-study down` and repeat the inventory; the container and network
are gone and the volume remains. That volume is your counter, so keep it unless a later lesson
asks for a fresh one.
"""),
        trap=t("""
Learners also expect `docker compose up` to notice that the Dockerfile or `server.py` changed.
For a service with a `build:` section, `up` builds the image only when it does not exist yet; an
existing `ds60-docker-study:local` tag is reused even if the source is newer. The visible symptom
is an edited message that never appears. Run `docker compose build` explicitly, or `up --build`,
and confirm with `docker image inspect` that the image creation time changed before you look for
a bug in the code.
"""),
        ask=t("""
Two learners share one laptop and both run the fixture from directories named `docker-study`,
each with `-p ds60-docker-study`. The second `up` reports a port conflict and the first learner's
counter changes. What went wrong, and how should the second copy be configured?
"""),
        answer=t("""
Both copies used the same project name, so Compose treated them as one project. The second `up`
reconciled the first learner's containers, and both copies shared the same named volume, which is
why the counter changed. The second copy needs a distinct project name such as
`ds60-docker-study-b` and a distinct loopback port such as 18081, used consistently in every
command. After that, `docker compose ls` shows two projects and each label filter finds its own
volume. One volume appearing under both project names would show the rename was incomplete.
"""),
    ),
    "docker-012": dict(
        lab=t("""
Start the project and watch the health state change with `docker compose -p ds60-docker-study
ps` during the first few seconds; it moves from `starting` to `healthy`. Read the recorded probe
results with `docker inspect --format '{{json .State.Health}}'` on the app container ID from
`ps -q app`. Then run the tools-profile client from the fixture README, whose `depends_on`
condition waits for that healthy state before it starts. Finally, compare the internal and host
paths by running the health command yourself through `exec` and requesting `/healthz` from the
host on port 18080. Both succeed here; write down which network namespace each one used, since
the exercises ask what happens when only one of them works.
"""),
        trap=t("""
Another mistake is a health check that is too eager in a slow-starting service. If a database
takes forty seconds to initialize and the check allows five retries at five-second intervals
with no start period, the container is marked unhealthy before it ever had a chance, and
anything waiting on `service_healthy` gives up. The fix is to set `start_period` to cover normal
initialization, during which failed probes do not count against the retry limit, and to keep
the probe itself cheap and local so that it measures the service rather than the network.
"""),
        ask=t("""
A web service depends on a database with `condition: service_healthy`. Startup works, but an
hour later the database restarts and the web service returns errors for a minute. A teammate
suggests adding a second `depends_on` condition. What is the actual fix?
"""),
        answer=t("""
`depends_on` only orders startup; it does not watch the dependency afterwards, so no extra
condition can cover a restart an hour later. The web service itself must handle a temporarily
unavailable database, with bounded retries, timeouts and clear error responses while the
database is down, and its own health check should report that state if traffic should stop. The
expected result is a short period of controlled errors followed by recovery without a restart of
the web container. Needing to restart the web service after every database restart would show
that its reconnect logic is still missing.
"""),
    ),
    "docker-013": dict(
        lab=t("""
Create a scratch volume with `docker volume create ds60-vol-demo` and write into it from one
throwaway container: `docker run --rm --pull never -v ds60-vol-demo:/data
ds60-docker-study:local python -c "open('/data/n.txt','w').write('kept')"`. Read the file back
from a second, separate container with `cat /data/n.txt`. The two containers never ran at the
same time, yet they shared one file, because the data lives in the volume. Next, mount the same
volume at `/app` in a third run and list it with `ls /app`: only `n.txt` appears, and the
packaged `server.py` is hidden for that container. Finish with `docker volume rm
ds60-vol-demo`, a deliberate deletion of a scratch volume you created yourself, and leave the
project's `study-data` volume and its counter untouched.
"""),
        trap=t("""
A quieter surprise comes from how an empty named volume is initialized. The first time an empty
named volume is mounted over a path that already holds files in the image, the engine copies
those files and their ownership into the volume. That is why the fixture's `/data`, owned by UID
10001 in the image, is writable in a brand new volume. After that first mount the volume is no
longer empty, so a later image that ships new or changed files at the same path does not update
it, and the container keeps showing the old copies. Bind mounts never perform this copy. Keep
image defaults out of data paths, or let the application create missing defaults at startup.
"""),
        ask=t("""
Two services in one project mount `study-data`, the app at `/data` and a reporting service at
`/source:ro`. A learner removes the app container and recreates it. Does the reporting service
still see `counter.json`, and what would make the file disappear for both?
"""),
        answer=t("""
Yes. The volume belongs to neither container, so removing and recreating the app does not touch
it, and the reporting service keeps reading the same `counter.json` through its read-only mount.
The file disappears for both only when the volume itself changes: `docker compose down -v`, an
explicit `docker volume rm`, or a project name change that makes Compose create and mount a new,
empty volume. If the reporting service saw no file after the recreation, compare the `Mounts`
section of `docker inspect` for both containers; two different volume names would disprove the
shared-volume assumption.
"""),
    ),
    "docker-014": dict(
        lab=t("""
Rehearse the capstone handoff on a second copy so your main counter stays intact. Copy the
fixture to `.learning/docker-study-rehearsal` with the same guard used for the first copy, change
only the host side of the port to `127.0.0.1:18081`, and use `-p ds60-docker-study-rehearsal` in
every command. Run validation, build, `up -d --wait`, one root request on port 18081 and two
increments, then a forced recreation and a second counter read. Read the rehearsal as a beginner
would and mark each step where you relied on something not written down. When the rehearsal is
finished, `docker compose -p ds60-docker-study-rehearsal down -v` removes its container, network
and volume. That reset is deliberate because the volume belongs to a scratch project; the main
project and its volume are untouched.
"""),
        trap=t("""
A capstone trap is evidence that cannot fail. If the counter reads 0 before a recreation and 0
after it, the record is consistent with persistence and equally consistent with a fresh empty
volume, so it proves nothing. Make the test able to fail: increment to a distinctive value such
as 3 before replacing the container, and write down the exact JSON. The same rule applies to the
message check. Change the message to a phrase that could not appear by accident, such as one
containing today's date, so a stale container returning the default text is caught instead of
being read as success.
"""),
        ask=t("""
A beginner follows your handoff, runs `docker compose -p ds60-docker-study up -d` without
`--wait`, immediately requests `http://127.0.0.1:18080/`, and reports `connection refused`. What
do you check first, and what result would point to a real fault?
"""),
        answer=t("""
Check the project state with `docker compose -p ds60-docker-study ps`. Without `--wait`, `up -d`
returns once the container has started, which can be before the server is listening, so the
health column may still say `starting`. Retry after it reports `healthy`; the expected result is
the configured JSON. A real fault is indicated if the service is healthy and the request is still
refused: then `docker compose port app 8080` shows whether the beginner is using a different
host port, for example from a rehearsal copy on 18081.
"""),
    ),
    "docker-015": dict(
        lab=t("""
In a scratch directory, write a Dockerfile with `FROM python:3.12-slim`, which is already local
from the fixture build, followed by the secret step from worked example 2. Build it once without
`--secret` and read the failure; the step refuses to run because the mount is required. Put a
synthetic value such as `not-a-real-secret` in `demo.txt`, then build with `--secret
id=demo,src=demo.txt -t ds60-secret-demo`. Check two places for leaks: `docker history
--no-trunc ds60-secret-demo` shows the RUN line but not the value, and `docker save
ds60-secret-demo | grep -a -c not-a-real-secret` should print 0. Delete `demo.txt` and remove the
image when you finish. Never rehearse this with a real token, even though nothing is printed.
"""),
        trap=t("""
Another trap is expecting a new secret value to trigger a rebuild. The contents of a secret are
deliberately not part of the cache key, so if you rotate a token and rebuild, an unchanged RUN
step that used the secret is served from cache, and its output still reflects whatever the old
token fetched. That is usually what you want for speed, but it means a rotated credential does
not prove that dependencies were downloaded again. When the step must run with the new secret,
force it explicitly with `--no-cache-filter` for that stage or `--no-cache`, and confirm in the
plain log that the step ran.
"""),
        ask=t("""
A Dockerfile switches to `USER 10001` and then runs `RUN
--mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt`. Every build
downloads everything again. Explain why the cache mount is not helping and how to fix it.
"""),
        answer=t("""
The step runs as UID 10001, so pip does not use `/root/.cache/pip`; it looks for a cache under
that user's home, which is not the mounted path, and it may not be writable either, so pip works
without a cache. Mount the cache where the running user's pip looks, or set `PIP_CACHE_DIR` to
the mount target, and give the mount `uid=10001` so that user can write to it. The expected
result is that the second build logs reused downloads. If downloads still repeat with the paths
aligned, check whether `--no-cache` or a builder prune is clearing the cache between builds.
"""),
    ),
    "docker-016": dict(
        lab=t("""
Save worked example 1 as a Dockerfile in a scratch directory and build it twice: once normally
as `ds60-stage-final` and once with `--target build` as `ds60-stage-build`. Run both with `ls
/out /app`. The build-stage image has `/out/message.txt` and no `/app/message.txt`; the final
image has the reverse, which shows that only the named file crossed the stage boundary. Then run
the final image with no command override and confirm that it prints `prepared`. Compare `docker
image ls ds60-stage-*`: the sizes are close because both stages start from the same base, a
useful reminder that multi-stage builds shrink images only when the build stage carries tools
the final stage leaves out. Remove both tags when you finish.
"""),
        trap=t("""
A maintenance trap is naming stages by number. `COPY --from=0` refers to the first stage in the
file, so when someone later inserts a new stage at the top, for example to fetch test data, the
same line silently copies from a different stage. Sometimes the build fails because the path is
missing, and sometimes it succeeds with the wrong file. Name every stage with `AS` and copy by
name, as in `COPY --from=build`, so reordering cannot change which filesystem is read. Name
external images explicitly too, rather than relying on a stage that happens to start from them.
"""),
        ask=t("""
A program is compiled in a `golang` build stage and copied into a `scratch` final image. Running
the final image fails with `no such file or directory` for the program, even though `docker
export` shows the file is present. What is missing?
"""),
        answer=t("""
The binary is almost certainly dynamically linked, and the message refers to its program
interpreter, the C library loader, which does not exist in a `scratch` image. The file is
present, but the kernel cannot start it without the loader. Build a static binary, for example
with `CGO_ENABLED=0`, or use a final base that provides the C library, then run the final image
again. Running `file` on the binary in the build stage should say `statically linked` after the
fix. If it already said that, the cause lies elsewhere, such as a wrong path in the entrypoint.
"""),
    ),
    "docker-017": dict(
        lab=t("""
Record three platform facts before building anything: `uname -m` on the host, `docker info
--format '{{.Architecture}}'` for the engine, and `docker image inspect ds60-docker-study:local
--format '{{.Os}}/{{.Architecture}}'` for the fixture image. On most machines all three agree.
If you have emulation available, build worked example 1 for the other architecture under its own
tag and run `docker run --rm --pull never --platform linux/arm64 ds60-docker-study:arm64 python
-c "import platform; print(platform.machine())"`, adjusting the platform to the one your host is
not. The program reports the foreign machine type while the host stays unchanged. Without
emulation the same run fails with `exec format error`. Remove the extra tag afterwards with
`docker image rm`.
"""),
        trap=t("""
A practical trap is reusing the native tag for a foreign build. If `docker buildx build
--platform linux/arm64 --load -t ds60-docker-study:local .` runs on an amd64 host, the arm64
image replaces the native one under the same name. The next `docker compose up` then starts the
foreign image under emulation, which may work but runs slowly, or fails with an exec format
error when no emulator is installed. The cause looks like an application fault because nothing
in the Compose file changed. Give each platform build its own tag, as worked example 1 does, and
inspect the platform of the image a service actually uses.
"""),
        ask=t("""
CI on amd64 publishes an image only for `linux/amd64`, and it includes a Python package with
native wheels. A teammate on an arm64 laptop pulls it. Describe what happens with and without
emulation, and what the publishing team should change.
"""),
        answer=t("""
The image has no arm64 entry, so the engine pulls the amd64 image. With emulation installed it
starts and warns that the image platform does not match the host; it then runs translated,
slower, and native extensions may behave differently. Without emulation it fails with `exec
format error`. The publishing team should build and push an index with both `linux/amd64` and
`linux/arm64`, then test each platform separately. If inspection on the laptop showed
`linux/arm64` and the run still failed, the problem would be in the image contents, not
platform selection.
"""),
    ),
    "docker-018": dict(
        lab=t("""
With the project running, resolve the service name from inside the app container:
`docker compose -p ds60-docker-study exec app python -c "import socket;
print(socket.gethostbyname('app'))"`. Compare the address with the container entry in `docker
network inspect ds60-docker-study_default`; they match. Now connect to a port nothing listens on,
replacing the lookup with `socket.create_connection(('app', 9999), timeout=2)`: the name
resolves but the connection is refused, which separates naming from listening. Finally, force a
recreation with `up -d --force-recreate --wait app` and repeat the lookup. The address may
change, and the name still works. Print `/etc/resolv.conf` from the same container with Python and note the nameserver
`127.0.0.11`: that is the engine's embedded resolver, present only on user-defined networks.
Write the before and after addresses in the worksheet; nothing
new needs cleaning up.
"""),
        trap=t("""
A misleading experiment is testing service names with two plain `docker run` containers. Without
`--network`, both join the engine's default bridge network, which does not provide name
resolution between containers, so one cannot resolve the other by name and the learner concludes
that container DNS is broken. Compose creates a user-defined network for each project, and
user-defined networks do include the embedded DNS service. To reproduce Compose behavior by
hand, create a network with `docker network create`, attach both containers with `--network`,
and give the target a `--name` or `--network-alias` to resolve.
"""),
        ask=t("""
A second Compose project for monitoring runs a probe that must request `app:8080` in the study
project. Both projects are up, and the probe fails with a name resolution error. Explain why and
propose the smallest model change.
"""),
        answer=t("""
Each project gets its own default network, and service names resolve only to containers on a
network the caller shares. The probe sits on the monitoring network, so `app` is unknown there.
The smallest change is to declare the study network in the monitoring project as an external
network named `ds60-docker-study_default` and attach only the probe to it. The expected result is
that the probe receives the app's JSON. If the name still failed, `docker network inspect` on
that network should list the probe container; its absence would show the attachment did not
apply.
"""),
    ),
    "docker-019": dict(
        lab=t("""
Create a scratch internal network with `docker network create --internal ds60-internal-demo`.
Run `docker run --rm --pull never --network ds60-internal-demo ds60-docker-study:local cat
/proc/net/route` and compare it with `docker compose -p ds60-docker-study exec app cat
/proc/net/route` from the running project. The project container has a row whose destination is
`00000000`, its default route through the network gateway; the internal network gives a subnet
route and no default route, so traffic for any other address has nowhere to go. Then run worked
example 2 and add `cat /proc/net/dev` to see that `--network none` leaves only the loopback
interface. No request leaves the machine during this lab. Remove the scratch network with
`docker network rm ds60-internal-demo`.
"""),
        trap=t("""
Network isolation limits sockets, not every data path. A worker started with `--network none`
can still read and change any volume or bind mount it receives, and whatever it writes to stdout
is kept in the container log for anyone who can run `docker logs`. So an offline job that mounts
a broad host directory is not contained just because it cannot open connections. When you review
an isolated service, list its mounts, its output destinations and its environment alongside its
networks, and give it only the paths its task needs, read-only where it only reads.
"""),
        ask=t("""
A worker must call an API on the internal `backend` network and must never reach the internet.
A teammate attaches it to both `backend` and the non-internal `frontend` network so it starts
faster. Evaluate the change and state an acceptance check.
"""),
        answer=t("""
Reject it. Joining `frontend`, which is not internal, gives the worker a default route through
that network's gateway and therefore outbound access, which is exactly what the policy forbids;
attachment does not make anything faster. Attach the worker only to `backend`. Acceptance is a
pair: the API request over `backend` succeeds, and the worker's route table shows no default
route, so outbound connections cannot leave. If the API request failed after removing
`frontend`, the API itself is probably not attached to `backend`, which `docker network inspect
backend` would show.
"""),
    ),
    "docker-020": dict(
        lab=t("""
Run worked example 2, then override the identity at run time: `docker run --rm --pull never
--user 0:0 ds60-docker-study:local python -c "import os; print(os.getuid())"` prints 0. `USER`
in a Dockerfile is a default, and any `docker run` caller can change it. Next, make a scratch
host folder with `mkdir hostdata`, record `ls -ldn hostdata`, and try to write into it from the
fixture image with `-v "$PWD/hostdata:/data"`. On a native Linux engine the write is denied
because UID 10001 does not own the folder; Docker Desktop's file sharing may translate ownership
and allow it. Record which you saw. Repeat with `--user "$(id -u):$(id -g)"`, which matches
the folder owner without widening permissions. Remove `hostdata` when you finish.
"""),
        trap=t("""
A related surprise is that `COPY` ignores the current `USER`. Files copied into an image are
owned by root unless the instruction says `--chown`, so a Dockerfile that switches to `USER
10001` and then copies a config file leaves the app unable to rewrite that file at runtime. In
the fixture this behavior is intended: `/app/server.py` stays root owned and read-only to the
app. Use `COPY --chown=10001:10001` only for a path the process must change, and prefer keeping
such state under `/data`, where ownership was set on purpose.
"""),
        ask=t("""
A service used to run as root and now runs as UID 10001. Its existing named volume at `/data`
was filled during the root era. After the change, writes fail with `PermissionError` on
`counter.next`. Why did the Dockerfile's `chown` not help, and what is the repair?
"""),
        answer=t("""
The image's `chown` only affects the image's own `/data` directory and the copy into a brand new,
empty volume. This volume already held root-owned files, so it was mounted as is. Repair it
deliberately with a one-off container that runs as root, mounts only that volume, and changes
ownership of `/data` to 10001, after taking a backup; or restore the data into a fresh volume.
Expect `ls -ln /data` to show 10001 and the increment to succeed. If ownership already showed
10001, look instead for a read-only mount of `/data`.
"""),
    ),
    "docker-021": dict(
        lab=t("""
Follow the export and restore sections of the fixture README: stop the app, export
`counter-backup.json` with noclobber, then restore it into the new `ds60-docker-study-restore`
volume and run the read-only verification. Add one more check that uses the application's own
validation rather than a copy of it: `docker run --rm --pull never --network none --read-only -v
ds60-docker-study-restore:/data:ro ds60-docker-study:local python -c "import server;
print(server.read_counter())"`. `read_counter` rejects a wrong schema version or a negative
counter, so a printed number means the app would accept the file. Start the original project
again with `up -d --wait` and confirm that its counter did not change. Keep the backup file and
remove the restore volume only after you record both values.
"""),
        trap=t("""
Another weak backup is one stored next to the data it protects. A JSON export written into the
same named volume, or a volume archive kept only inside the Docker Desktop virtual disk, shares
every failure of the original: `docker compose down -v`, a reset of the engine's virtual machine
or a disk failure removes both at once. A backup also needs a recorded location and owner outside
the engine. The fixture README writes `counter-backup.json` to the host folder, which is the
minimum; a real service would also copy it off the machine and test a restore from that copy.
"""),
        ask=t("""
A nightly job exports the counter volume while the app is still serving `POST /increment`. The
exported JSON always parses. Using the fixture's write pattern, is each export consistent, and
what does it still fail to guarantee?
"""),
        answer=t("""
For this single file, yes. `increment` writes `counter.next` and then atomically replaces
`counter.json`, so a reader sees either the old complete file or the new one, never a half
write. The export can still miss increments that land after the copy, which is the recovery
point objective, and the guarantee does not extend to a database whose state spans several files
written at different moments; that needs a stopped writer or the database's own export. A parse
failure or a truncated export would disprove the atomic replacement assumption.
"""),
    ),
    "docker-022": dict(
        lab=t("""
Compare two CPU limits with the same small workload: run `docker run --rm --pull never --cpus 1
ds60-docker-study:local python -c "import time; t=time.time(); sum(range(30_000_000));
print(round(time.time()-t,2))"` three times, then three times with `--cpus 0.25`, and record all
six numbers. The limited runs take longer, but the ratio is rarely exactly four. Add `print(open('/sys/fs/cgroup/cpu.stat').read())` to one limited run on a cgroup v2 engine and look for a nonzero `nr_throttled`. Next, start a named container with `--memory 64m` that allocates `bytearray(200_000_000)`, then read `docker inspect --format '{{.State.OOMKilled}} {{.State.ExitCode}}'` on it. Expect `true 137`. Remove the named container when you finish.
"""),
        trap=t("""
A common misreading is that exit code 137 always means the container ran out of memory. The code
only says the main process was ended by SIGKILL, and that signal also arrives when a stop
exceeds its grace period, when someone runs `docker kill`, or when the host kernel kills a
process for its own reasons. Before raising a memory limit, read `.State.OOMKilled` in `docker
inspect`, which is set when the container's memory limit was the cause, and compare the time of
death with the logs of any stop or deploy command that ran then.
"""),
        ask=t("""
A worker has `pids_limit: 64` and starts one thread per job. Under load it fails with `can't
start new thread` while memory and CPU look normal in `docker stats`. Explain the failure and how
you would confirm it.
"""),
        answer=t("""
The PID limit counts tasks in the container's cgroup, and every thread is a task, so 64 threads
across all processes exhausts it even though each thread needs little memory or CPU. Confirm by
reading `/sys/fs/cgroup/pids.current` and `pids.max` inside the container during load, or the
PIDS column of `docker stats`, which should sit at the limit. The fix is a bounded worker pool,
or a deliberately raised limit with a stated reason. If the count stayed well below 64 during
the failures, the limit is not the cause and memory mapping limits deserve a look.
"""),
    ),
    "docker-023": dict(
        lab=t("""
Read the effective security state of the running app rather than the YAML:
`docker compose -p ds60-docker-study exec app grep -E 'CapEff|NoNewPrivs' /proc/self/status`
should show `CapEff` as all zeros and `NoNewPrivs` as 1. For comparison, run a throwaway
container as root without the fixture settings, `docker run --rm --pull never --user 0
ds60-docker-study:local grep CapEff /proc/self/status`, and note the nonzero default set. Then
add `--cap-drop ALL` and try `python -c "import os; os.chown('/app/server.py', 1, 1)"`: even
root is refused, because changing ownership needs `CAP_CHOWN`. Finish with `docker inspect` on
the app container and read `HostConfig.CapDrop`, `ReadonlyRootfs` and `SecurityOpt`. Nothing
here changes the project.
"""),
        trap=t("""
A review trap is checking hardening only in the Compose file. The file describes what Compose
asks for, but the running container is what matters, and run-time flags can change it: a
`docker run` of the same image with `--user 0` or `--cap-add`, or a later override file, can
undo a setting the reviewed YAML still shows. Verify the live container with `docker inspect`,
reading `HostConfig.CapDrop`, `HostConfig.ReadonlyRootfs` and `HostConfig.SecurityOpt`, and
confirm from inside with `/proc/self/status`, so the evidence describes the process you are
actually trusting.
"""),
        ask=t("""
A vendor image's documentation says it needs `CAP_NET_ADMIN` for networking. Your deployment only
serves HTTP on 8080 behind a published port. How do you decide whether to grant the capability,
and what evidence do you collect?
"""),
        answer=t("""
Start from `cap_drop: [ALL]` and run the service's real acceptance check: start up, answer HTTP
on 8080, and persist its data. If that passes, the capability is not needed for this deployment
and stays denied. If startup fails, read the exact operation that was refused, often interface
or firewall changes at boot, and prefer turning that feature off or doing it outside the
container. Grant the capability only for a named, required operation, and record why. A passing
acceptance run without it is the observation that disproves the vendor's claim for your use.
"""),
    ),
    "docker-024": dict(
        lab=t("""
This lab only reads. Run `docker info --format '{{json .SecurityOptions}}'` and look for
`name=rootless` or `name=userns`; on a default engine neither appears. Then compare how
identities map: `docker run --rm --pull never ds60-docker-study:local cat /proc/self/uid_map`
prints `0 0 4294967295` when container IDs equal host IDs, and a shifted range such as `0 100000
65536` under a user namespace. On Linux, run `id -nG` to see whether your account is in the
`docker` group, and `ls -l /var/run/docker.sock` to see who owns the socket. Record each result
next to a sentence saying who could control the engine. Nothing is created, so there is nothing
to clean up.
"""),
        trap=t("""
A tempting compromise is mounting the engine socket read-only, as in
`/var/run/docker.sock:/var/run/docker.sock:ro`. The `:ro` flag only stops the container from
modifying the socket file in the filesystem; it does nothing to the API requests sent through
that socket, so the container can still create a privileged container with the host's root
directory mounted. A truly limited view needs a different mechanism, such as a filtering proxy
that allows only specific read endpoints, and even that deserves review as a trust decision
rather than a convenience setting.
"""),
        ask=t("""
A CI job proposes running its image builds inside a container with the host engine socket
mounted, arguing that it is only CI. What authority does the job gain, and which alternatives
would you weigh?
"""),
        answer=t("""
The job gains full control of the host engine, which in practice means root on that host: it can
start a privileged container that mounts `/`, read other jobs' containers and volumes, and
change images that later deployments use. Alternatives include a rootless BuildKit builder, a
remote buildx builder dedicated to CI, or a disposable virtual machine per job. Acceptance should
show the job can build and push its image yet cannot list unrelated containers. If the job could
not list containers through the socket, the socket would not be the real engine endpoint.
"""),
    ),
    "docker-025": dict(
        lab=t("""
Stop the study project with `docker compose -p ds60-docker-study down` so no container holds the
image, then record its identity with `docker image inspect --format '{{.Id}}'
ds60-docker-study:local`. Save it outside your fixture copy with `docker image save -o
../study-image.tar ds60-docker-study:local` and record `shasum -a 256 ../study-image.tar`
(`sha256sum` on Linux). Remove the name with `docker image rm ds60-docker-study:local`, then try
the offline run from worked example 2: it fails at once with a no-such-image error, and nothing
is downloaded. Load the archive with `docker image load -i ../study-image.tar`; the engine
prints `Loaded image: ds60-docker-study:local`. Inspect the ID again, compare it with your first
note, and rerun the offline command to see `offline ready`. Delete `../study-image.tar` when you
finish. The volume was never touched, so `up -d --wait` brings the app back with its counter.
"""),
        trap=t("""
Saving by image ID instead of by name looks equivalent, because the layers are the same. It is
not: `docker image save -o handoff.tar <image-id>` writes an archive whose manifest carries no
repository or tag, so on the receiving engine `docker image load` reports `Loaded image ID:`
followed by a digest rather than `Loaded image: ds60-docker-study:local`, and `docker image ls`
shows the image without a name. Every command that names `ds60-docker-study:local` with `--pull
never` then fails as if the transfer never happened. Save by reference so the name travels with
the bytes, or, on the receiving side, attach the name deliberately with `docker image tag
<loaded-id> ds60-docker-study:local` after checking that the loaded ID matches your handoff
record.
"""),
        ask=t("""
A colleague on an Apple silicon laptop loads your archive, which you built on an amd64 Linux
host, and the offline run prints a platform warning or fails with `exec format error`. What
happened, and which handoff field would have prevented the surprise?
"""),
        answer=t("""
The archive carries the image for the platform it was built on, linux/amd64. On an arm64 engine
the run either goes through emulation, with a warning that the requested platform does not match
the host, or fails with `exec format error` where no emulator is installed. `docker image inspect
--format '{{.Os}}/{{.Architecture}}' ds60-docker-study:local` shows the mismatch. The handoff
record needs a platform field, and a build for linux/arm64 when that is the target. If inspect
already reports arm64 and the run still fails, the cause lies elsewhere.
"""),
    ),
    "docker-026": dict(
        lab=t("""
Work in a scratch copy of the fixture so the committed files stay unchanged. Create
`compose.study.yaml` holding only `services:`, `app:`, `environment:` and `APP_MESSAGE: override
from study file`, then render `docker compose -p ds60-docker-study -f compose.yaml -f
compose.study.yaml config` and find the new message under `app`. Add a `ports:` entry of
`"127.0.0.1:18081:8080"` to the same override and render again: the effective list now holds
both 18080 and 18081, one after the other. Next compare `docker compose -p ds60-docker-study
config --services`, which prints only `app`, with the same command after `--profile tools`,
which prints `app` and `client`; `config --profiles` prints `tools`. None of these commands
creates a container, network or volume, so deleting the scratch copy is the whole cleanup, and
the rendered output is the record you keep.
"""),
        trap=t("""
Naming your override `compose.override.yaml` feels tidy, but Compose loads a file with exactly
that name automatically whenever a command runs without `-f`. Every plain `docker compose up` in
that directory then carries your study message and extra port, and the project you reviewed with
explicit files is no longer the one people launch by habit. The symptom is a setting nobody
passed on the command line. List `compose*.yaml` in the directory and render `docker compose
config` with no flags to see what a bare command really uses. Keep study overrides under a name
Compose does not pick up, such as `compose.study.yaml`, and pass them with `-f` so the choice is
visible in every command you record.
"""),
        ask=t("""
A teammate adds `ports: []` to an override, expecting the app to run with no published port for
a private test. What does the rendered model show, and how would you actually remove the
mapping?
"""),
        answer=t("""
An empty list merges into the inherited one and adds nothing, so `config` still shows
`127.0.0.1:18080` and the port stays published. Compose provides the `!reset` YAML tag for this
case: `ports: !reset []` in the override clears the inherited list, and the rendered `app`
service then has no `ports` key at all. Accept the change only when `config` shows that and,
after `up`, `docker compose port app 8080` reports no mapping. If `config` still lists 18080, the
override was not included or your Compose release predates `!reset`.
"""),
    ),
    "docker-027": dict(
        lab=t("""
Rehearse the full recovery path once, writing one line per transition with the observation that
let you move on. Start with `up -d --wait`, then request `/counter` from the host and run the
`tools` client, so both paths are confirmed before you touch data. Perform one increment through
`exec` as the README shows, stop the writer, export with the README's `run --rm --no-deps`
command into `counter-backup.json`, and check that the file's counter equals the value you just
saw. Create and fill the separate `ds60-docker-study-restore` volume with the README's three
commands, ending with the read-only verify, then start the app again and read `/counter` from
the source. Both numbers should match the backup. Finish by removing only the restore volume and
the backup file, and note in your record that `study-data` was never a restore target.
"""),
        trap=t("""
A healthcheck looks like self-healing, yet plain Docker and Compose only report health. When
`/healthz` starts failing, `docker compose ps` shows the app as `unhealthy`, but no restart
follows: the fixture sets no restart policy, and even a policy reacts to the process exiting,
not to a failed probe. The `depends_on` condition `service_healthy` is likewise a check Compose
makes when it starts the client; it does not watch the app afterward or repair it. Treat
`unhealthy` as a signal someone must act on. Read `docker inspect --format '{{json
.State.Health}}'` on the app container for the recent probe output, then decide between a
targeted fix and a recreate.
"""),
        ask=t("""
After the rehearsal, `/counter` on the source shows 5 while the read-only verify of
`ds60-docker-study-restore` shows 4. Is the restore broken, and which observation decides?
"""),
        answer=t("""
Not necessarily. The restore volume holds the snapshot taken at export time, while the source
keeps accepting increments, so a later increment through `exec` or the browser explains a higher
source value. Compare the restored value with the counter in `counter-backup.json`: if both say
4, export and restore are correct and the source simply moved on, which `docker compose logs app`
confirms with a later `POST /increment` line. If the backup says 5 and the restore says 4, the
restore step wrote something other than the export.
"""),
    ),
    "docker-028": dict(
        lab=t("""
Give the existing image a second name without contacting any registry: `docker image tag
ds60-docker-study:local localhost:5000/ds60-study:rehearsal`. Run `docker image ls --format
'{{.Repository}}:{{.Tag}} {{.ID}}'` and find both names beside one ID, because tagging only adds
a reference. Read the new reference from left to right: `localhost:5000` is the registry, since a
first component holding a port, a dot or the word `localhost` names a host; `ds60-study` is the
repository; `rehearsal` is the tag. Compare `python:3.12-slim`, which expands to
`docker.io/library/python:3.12-slim`, and the README's mirror reference, whose registry is
`mirror.gcr.io`. Do not push. Remove the extra name with `docker image rm
localhost:5000/ds60-study:rehearsal`; the engine prints `Untagged:` and keeps the image, which
`docker image ls ds60-docker-study` confirms. Nothing else was created.
"""),
        trap=t("""
A reference can carry a tag and a digest at once, such as `ds60-study:1.0@sha256:` followed by
the hash, and it reads as if the engine checks both. It does not: when a digest is present, the
pull resolves by digest alone and the tag plays no part in resolution, so a stale tag beside a
correct digest still pulls the right bytes, and a familiar tag beside a wrong digest pulls
whatever that digest names or fails. Reviewers who glance at the tag can approve an artifact
they never meant to ship. In release records and deployment files, treat the digest as the
identity and the tag as a label for people, and check the digest character by character against
the release record, since nothing else in the reference is enforced.
"""),
        ask=t("""
`ds60-docker-study:local` and `registry.example.com/team/ds60-study:1.0` show the same image ID.
If you remove the first name, does the second still run, and what would pushing the second
create?
"""),
        answer=t("""
Removing the first name only untags it; the image stays because the second reference still
points at it, so `docker run --pull never registry.example.com/team/ds60-study:1.0` keeps
working. A push would upload the image's layers and manifest to `registry.example.com` under
`team/ds60-study`, creating a remote copy whose visibility depends on that registry's settings,
and the push prints the digest that becomes the release identity. If `docker image rm` had
printed `Deleted:` lines rather than only `Untagged:`, no other reference shared the image.
"""),
    ),
    "docker-029": dict(
        lab=t("""
From your fixture copy, run worked example 1 to export the build result with its SBOM into
`../ds60-sbom-out`. If the engine answers that the current builder driver cannot produce
attestations, record that message as your finding and stop there; switching builders is a
separate decision. Otherwise open the file with `python3 -c "import json;
d=json.load(open('../ds60-sbom-out/sbom.spdx.json')); doc=d.get('predicate', d);
print(doc['spdxVersion'], len(doc['packages']))"`. The wrapper is an in-toto statement whose
`predicate` holds the SPDX document. Search the package names for `python` and for a Debian
library whose name starts with `libssl`, then note which ones your Dockerfile never mentions:
they arrived with `python:3.12-slim`. Delete `../ds60-sbom-out` afterward, since it also holds a
full copy of the image filesystem.
"""),
        trap=t("""
A clean SBOM for the shipped image says nothing about tools used only while building it.
BuildKit scans the final stage by default, so in a multi-stage Dockerfile a compiler, a package
manager cache or a downloaded binary used in an earlier stage never appears, even though it
shaped the output. The fixture is single-stage, which hides the issue here, but a project that
later adds a `builder` stage will see its SBOM stay just as short. When build stages matter to
the review, set the build argument `BUILDKIT_SBOM_SCAN_STAGE=true`, globally or in the stages
concerned, so they are scanned too, and state in the review which stages each inventory covers.
"""),
        ask=t("""
An auditor asks whether `server.py` appears in the SBOM you exported. Predict the answer,
explain it, and say where the application's own identity should be recorded instead.
"""),
        answer=t("""
Most likely it does not appear as a package. The scanner finds packages through metadata such
as the Debian package database and Python `dist-info` directories, and a loose file copied by
`COPY server.py` has none. Its identity belongs in the source revision and build inputs that
provenance records, tied to the same image digest. Searching the exported file for `server.py`
settles it: if a file entry shows up, this scanner also catalogs plain files, and the review
should note that coverage rather than assume it.
"""),
    ),
    "docker-030": dict(
        lab=t("""
With the app running, try the patch-in-place habit and watch the fixture refuse it: `docker
compose -p ds60-docker-study exec app python -c "open('/app/patched', 'w')"` fails with a
read-only file system error, because the service sets `read_only`, and even a writable root
would stop UID 10001 from writing into root-owned `/app`. Now take the inventory a finding would
be matched against: `docker compose -p ds60-docker-study exec app python -c "import platform,
ssl; print(platform.python_version(), ssl.OPENSSL_VERSION); print(open('/etc/os-release').read())"`.
Write the Python version, the OpenSSL version and the Debian release next to the output of
`docker image inspect --format '{{.Id}}' ds60-docker-study:local`. That pair, inventory plus
identity, is what a patch decision cites. Nothing was changed, so there is no cleanup.
"""),
        trap=t("""
Running `docker compose build` again feels like patching, but with an unchanged Dockerfile and
context every step is served from cache and the base comes from the local copy of the Python
image, so the new image has the same ID as the old one and the same vulnerable packages. The
build output gives it away with `CACHED` beside each step after `FROM`. A deliberate update
refreshes the base, for example `docker compose -p ds60-docker-study build --pull app` where
network access is allowed, or a new pinned base digest in the Dockerfile, and then compares
image IDs: an unchanged ID means nothing was patched, whatever the command was called.
"""),
        ask=t("""
A scanner reports a finding in the base image's OpenSSL, but the fixture serves plain HTTP on
loopback and never opens TLS itself. Do you patch now, defer, or accept the risk, and what goes
in the record?
"""),
        answer=t("""
Presence is established; reachability is weak, because `server.py` opens no TLS and the
healthcheck uses HTTP. Since a base refresh is cheap and reversible here, a reasonable decision
is to rebuild from a refreshed base, rerun the health, peer and counter checks, and record the
old and new image IDs with the version printed by `ssl.OPENSSL_VERSION`. The record states the
residual risk if no fixed version exists yet. If the rebuilt image still prints the old OpenSSL
version, the refresh did not take effect and the finding stays open.
"""),
    ),
    "docker-031": dict(
        lab=t("""
Build a small receipt by hand. In your fixture copy run `shasum -a 256 Dockerfile server.py
compose.yaml` and `docker image inspect --format '{{.Id}}' ds60-docker-study:local`, then
perform one named check, such as the host request to `/healthz`, and write the hashes, the ID,
the check and its result to `../ds60-receipt.json`. Now add a comment line to `server.py` and
run `docker compose -p ds60-docker-study build app`: the source hash changes, the `COPY
server.py` step rebuilds and the image ID differs, so the receipt no longer describes what you
would ship. Remove the comment and build again; the original ID usually returns because the
earlier layers are still cached, and the hashes match the receipt once more. Delete
`../ds60-receipt.json` when you are done.
"""),
        trap=t("""
Teams often add a `test` stage to the Dockerfile and assume every build runs it. BuildKit builds
only the stages the requested target depends on, so `docker build .` producing the final stage
silently skips a `test` stage that nothing copies from, and the build log simply never mentions
it. A green build then proves only that packaging succeeded. Either build the test stage
explicitly with `--target test` as its own pipeline step, or make the final stage depend on it,
for example by copying a small marker file the tests write, and look in the build log for the
test command's own output rather than trusting the stage's presence in the file.
"""),
        ask=t("""
Your pipeline builds on amd64 runners and the receipt passes, but production nodes are arm64 and
pull a multi-platform index under the same tag. Which part of the receipt still applies to them?
"""),
        answer=t("""
Only the source hashes. The receipt's image identity names the amd64 image, while arm64 nodes
resolve the index to a different platform manifest with its own digest, which no recorded check
ran against. Either run the same named checks on an arm64 runner and record that digest, or
state in the receipt that it covers linux/amd64 only. `docker buildx imagetools inspect` on the
published reference lists each platform's digest; if it shows only linux/amd64, the arm64 nodes
cannot pull a native image at all.
"""),
    ),
    "docker-032": dict(
        lab=t("""
Collect the three views without installing anything. From the host, run `curl -s
http://127.0.0.1:18080/healthz`. From a peer, run the `tools` client, which reaches `app:8080`
by service name. From inside, use the fixture's own Python as worked example 1 shows. Then try
`docker compose -p ds60-docker-study exec app curl -s http://127.0.0.1:8080/healthz`: the slim
image ships no `curl`, so the engine reports that the executable was not found, which describes
the image, not the app. For process evidence, `docker compose -p ds60-docker-study top app`
reads the process list from the host side, and because the service sets `init: true` it shows a
small init process with `python server.py` as its child. Record each result under its vantage
point. There is nothing to clean up.
"""),
        trap=t("""
The address `127.0.0.1` means a different machine depending on where a command runs, and
debugging sessions mix these up constantly. Inside the app container it is the app's own
loopback, where port 8080 answers. Inside a separate helper container on the project network it
is the helper itself, so a request to `127.0.0.1:8080` there is refused even though nothing is
wrong, while `app:8080` works. A helper started with `--network container:` and the app's
container name shares the app's network namespace, and then its loopback is the app's again. On
the host it is the host, where only the published 18080 answers. Before reading a refused
connection as a fault, write down which network namespace the command ran in.
"""),
        ask=t("""
The host request to `127.0.0.1:18080` times out, yet the peer client and the in-container health
request both succeed. Which layer is at fault, and what would you check first?
"""),
        answer=t("""
The app, its listener and the project network work, so the fault sits on the published path
between the host and the container. Start with `docker compose -p ds60-docker-study port app
8080`, which should print `127.0.0.1:18080`; then check whether another host process holds
18080, and on Docker Desktop whether its port forwarding is running. A repair is confirmed when
the host request returns the health JSON. If `port` reports no mapping at all, the container was
created without its `ports` entry, which points back to the effective Compose model.
"""),
    ),
    "docker-033": dict(
        lab=t("""
Watch a bounded failure loop in a scratch container: `docker run -d --name ds60-restart-demo
--restart on-failure:3 --pull never ds60-docker-study:local python -c "import sys;
print('starting'); sys.exit(3)"`. Wait about ten seconds, then read `docker inspect --format
'{{.RestartCount}} {{.State.Status}} {{.State.ExitCode}}' ds60-restart-demo`: three restarts,
status `exited`, exit code 3. `docker logs ds60-restart-demo` shows `starting` four times, once
per attempt, and nothing about the cause, because restarting never addressed it. The attempts come quickly at first and
then slow down, because the engine doubles its delay before each restart, starting at 100
milliseconds; a longer loop backs off much further, so a quiet container may still be waiting.
Remove it with
`docker rm ds60-restart-demo`. Then check the fixture's own startup: note `/counter`, run
`docker compose -p ds60-docker-study restart app`, and read `/counter` again. The value is
unchanged, since `main()` only creates the data directory if needed and validates the stored
file; nothing is written until a `POST /increment` arrives.
"""),
        trap=t("""
The policies `restart: always` and `restart: unless-stopped` behave alike until the engine
itself restarts. A container you stopped by hand with `docker stop` stays stopped under both
while the engine runs, but after an engine or Docker Desktop restart, `always` starts it again
and `unless-stopped` leaves it alone. Learners who stop a misbehaving lab service and then reboot
are surprised to find it running and writing again. Choose `unless-stopped` when an operator's
manual stop should stick, keep the fixture's default of no policy for teaching runs, and after
any engine restart check `docker ps` before assuming that what you stopped is still stopped.
"""),
        ask=t("""
A client's `POST /increment` timed out, the client retried, and the counter rose by two. Was the
retry wrong, and how would you tell what the server actually did?
"""),
        answer=t("""
The first request probably committed before the client gave up, because the fixture replaces
the file and only then responds, and `/increment` is not idempotent, so the retry added a second
increment. `docker compose -p ds60-docker-study logs app` shows one line per handled request;
two `POST /increment` lines with status 200 confirm it. A safer client reads `/counter` before
retrying, or the protocol carries an idempotency key the server records. If the log shows a
single POST, the extra increment came from another caller.
"""),
    ),
    "docker-034": dict(
        lab=t("""
Practice reading the version marker without changing live data. After at least one increment,
print the stored record with `docker compose -p ds60-docker-study exec app python -c
"print(open('/data/counter.json').read())"`; it shows `{"schema_version": 1, "counter": N}`.
Then rehearse a v1-to-v2 conversion on a copy only: take the README export into
`counter-backup.json`, and on the host run `python3 -c "import json;
v=json.load(open('counter-backup.json')); assert v['schema_version'] == 1;
print(json.dumps({'schema_version': 2, 'counter': v['counter'], 'unit': 'increments'}))"`. The
fixture's `read_counter()` accepts only `schema_version` 1, so it would refuse this v2 record
with its invalid-state error, which is exactly what a rolled-back v1 reader does when it meets
migrated data. Nothing here wrote to `study-data`; delete `counter-backup.json` afterward.
"""),
        trap=t("""
A migration that runs automatically when a container starts looks convenient: every new image
upgrades whatever it finds. With more than one container able to start against the same volume,
two migrators can read v1 at once and both write, and a crashed half-migration is retried on
every restart with nobody watching. It also ties an irreversible data step to an image rollout
that people expect to be cheap to undo. Run the migration as a separate, explicit one-off job,
for example a `run --rm --no-deps` command while the service is stopped and after the backup is
verified, and let the application at startup only check that the version it finds is one it
supports.
"""),
        ask=t("""
A v2 release migrated the counter file, then a bug forced a rollback to the v1 image, which now
exits at startup. What are your options, and which one keeps every write?
"""),
        answer=t("""
The v1 reader rejects the v2 record, so restarting it will keep failing. Options are rolling
forward with a fixed v2 image, running a tested v2-to-v1 conversion as a one-off job, or
restoring the pre-migration backup and accepting the loss of later increments. Rolling forward
keeps every write; the conversion does too if it is lossless; the backup does not. Whichever you
choose, `/counter` returning the expected value confirms it. If v1 still exits after a correct
downgrade, the record holds another incompatibility you have not found.
"""),
    ),
    "docker-035": dict(
        lab=t("""
Measure before optimizing. Read the local size with worked example 1, then run `docker image
history ds60-docker-study:local` and compare the fixture's own steps, the `COPY server.py` and
the `RUN mkdir` layers, with the base layers below them: nearly all of the bytes come from the
base, so trimming `server.py` could never matter. Next time readiness. Stop the app with `docker
compose -p ds60-docker-study stop app`, then run `time docker compose -p ds60-docker-study up -d
--wait app`, and repeat the stop and start three times. Note the spread. The healthcheck runs its
first probe about one 5-second interval after the container starts, so `--wait` cannot finish
sooner than that; the healthcheck settings, not the image, set the floor of this number. Leave
the app running, since nothing was removed.
"""),
        trap=t("""
Sizes in `docker image ls` look additive, so five images at 150 MB each seem to cost 750 MB.
Images built on the same base share those layers on disk and in transfer; the column reports
each image's full size, not its unique share. Judging an optimization by the sum leads people
to flatten or squash images, which destroys sharing: a squashed image can be smaller on its own
yet cost more total disk and download than two images that reuse one base. Use `docker system
df -v` to see shared and unique sizes per image, and judge a size change by what a target host
would really have to transfer given the layers it already holds.
"""),
        ask=t("""
Someone proposes switching the fixture to an Alpine-based Python image to cut its size. Before
agreeing, what would you measure, and which correctness checks would you rerun?
"""),
        answer=t("""
Measure the transfer a target host would actually need, given which base layers it already
holds, and readiness with the same `--wait` method, since a new base shares nothing cached.
Alpine uses musl rather than glibc, so rerun the health, host and peer requests, an increment,
and the export and restore commands, and check that any later HTTPS client still finds a CA
bundle. Accept only a measured gain with identical behavior. If readiness time does not move,
the healthcheck interval, not image size, was the limit.
"""),
    ),
    "docker-036": dict(
        lab=t("""
Walk the failure domains with commands you already trust. Kill the app's process with `docker
compose -p ds60-docker-study kill -s SIGKILL app` and note that it stays exited, since the
service sets no restart policy. Recreate it with `up -d --wait` and read `/counter`: the value
survived because `study-data` outlives containers. Then run `docker volume inspect
ds60-docker-study_study-data --format '{{.Mountpoint}}'` and note that the path lives on this
one engine's disk; on Docker Desktop it sits inside the Linux virtual machine, which is the same
single failure domain. A lost host takes the only copy with it unless an export exists
elsewhere. Write one row per domain, process, container, engine and host, naming the mechanism
that covered it or writing none, and keep that table for the questions below.
"""),
        trap=t("""
A Compose file that starts the client only after the app is healthy leads people to expect the
same ordering on a cluster. Kubernetes has no cross-workload start ordering: Pods for the client
and the app start independently, and a client that runs before the app is ready simply fails
its request. Translating `depends_on` therefore produces nothing, and a migrated client that
never retries turns into intermittent failures after every rollout. The cluster equivalent is a
readiness probe on the app, which keeps its Service from routing traffic until the probe passes,
plus a client that retries with a bounded backoff until the Service has ready endpoints.
"""),
        ask=t("""
Your manager asks whether the study app should move to Kubernetes now that two classes use it.
Give a recommendation and the evidence that would change it.
"""),
        answer=t("""
For a single-host teaching fixture used by two classes, Compose remains the better fit: the
workload is one process with one small volume, nobody needs failover, and learners benefit from
seeing every resource. The recommendation changes if the app must survive host loss, serve many
concurrent users, or be run by a team already operating a cluster; then the work is a storage,
recovery and traffic design, not a file conversion. A measured outage or a load that one host
cannot carry would be the evidence against the current choice.
"""),
    ),
    "docker-037": dict(
        lab=t("""
Read what the fixture tells clients about itself, then sketch the TLS hop it lacks. Run `curl
-sv http://127.0.0.1:18080/ 2>&1 | grep '^< '` and read the response headers: `Cache-Control:
no-store`, a JSON content type, and a `Server` header naming Python's built-in HTTP server.
There is no TLS, no authentication and no forwarded-header handling, which is why the fixture
publishes only on loopback. Next run `curl -sv https://127.0.0.1:18080/` and read the failure:
the client opens a TLS handshake that a plain HTTP listener cannot answer, an SSL protocol error
rather than a certificate problem. Draw the design real exposure would need, browser to a proxy
holding a certificate for a DNS name, proxy to `app:8080` on a private network, and label each
hop with its identity and timeout.
"""),
        trap=t("""
A proxy in front of an app often keeps its default upstream timeout, and the resulting symptom
is misread as an app bug. When the app is slow, the proxy gives up first and returns `504`,
while the app finishes the request and, for a `POST /increment`, commits it. The client sees a
failure, retries, and the counter moves twice. When the proxy cannot reach the app at all,
because of a refused connection or a failed name lookup, it returns `502` instead. Set upstream
timeouts deliberately against the app's own limits, log the upstream status beside the proxy
status, and treat a proxy `504` on a non-idempotent route as an unknown outcome to reconcile.
"""),
        ask=t("""
Users see a browser warning that the certificate is not valid for the site name, and someone
suggests changing the app's container port from 8080 to 443. What is wrong with that plan, and
what fixes the warning?
"""),
        answer=t("""
The warning comes from the TLS identity check between the browser and the proxy: the
certificate the proxy presents does not list the DNS name users typed. The container port sits
behind the proxy and plays no part in that check, so changing it fixes nothing and may break the
upstream route. The fix is a certificate whose subject alternative names include that DNS name,
installed on the proxy. `openssl s_client -connect` with `-servername` set to that name should
show it; if the warning persists, users are reaching a different endpoint.
"""),
    ),
    "docker-038": dict(
        lab=t("""
Assemble an evidence packet before any cleanup. Run `docker system df` and copy its table, then
`docker system df -v` for per-volume sizes and the number of containers using each image. List
the project's resources with `docker compose -p ds60-docker-study ps -a` and the label filter
from worked example 1, and capture recent logs with `docker compose -p ds60-docker-study logs
--since 10m app > ../incident-logs.txt`. Add the time, the symptom and one sentence on what you
will remove and what you will keep. Then run worked example 2 and confirm with `docker volume ls
--filter label=com.docker.compose.project=ds60-docker-study` that `study-data` is still listed.
Start the app again with `up -d --wait`, check that `/counter` kept its value, and only then
delete `../incident-logs.txt`. The packet, not the deletion, is what this lab produces.
"""),
        trap=t("""
Container logs are a disk-pressure source that `docker system df` does not report at all. Its
container size column measures writable layers, while each container's log file sits beside
them in the engine's data directory, and with the `json-file` driver and no rotation options it
grows without limit. A chatty service can fill the disk while images and volumes look modest.
Check the logging settings with `docker inspect --format '{{json .HostConfig.LogConfig}}'` on
the container, and when logs are the cause, set `max-size` and `max-file` for that service, or
engine-wide in the daemon configuration, rather than deleting files under the engine's
directories by hand.
"""),
        ask=t("""
During an incident on a shared host the disk is 95 percent full, and `docker system df` shows
several gigabytes of reclaimable build cache. Is clearing it in scope, and how do you limit the
effect on others?
"""),
        answer=t("""
Build cache is regenerable, so clearing it costs rebuild time rather than data, which makes it a
reasonable target once the evidence packet exists. On a shared host it also slows other people's
builds, so prefer a bounded command such as `docker builder prune --filter until=24h`, announce
it, and record what was freed. Rerun `docker system df` to confirm the reclaimed space and check
that the app is still healthy. If disk use barely drops, the pressure lies elsewhere, often in
logs or volumes.
"""),
    ),
    "docker-039": dict(
        lab=t("""
Read the isolation from inside without changing anything. Run worked example 1 and note that the
process sees itself as PID 1, while `docker compose -p ds60-docker-study top app` on the same
engine lists the app's processes with host-side PIDs. Then compare kernels: `uname -r` on a
Linux host, and `docker run --rm --pull never ds60-docker-study:local python -c "import
platform; print(platform.release())"` inside. On Linux both print the same release, because
containers share the host kernel; on Docker Desktop the container reports the virtual machine's
kernel, which differs from macOS or Windows. Finally run the same image with `--network none`
and `python -c "import socket; print(socket.if_nameindex())"` to see a network namespace holding
only loopback. Every container used `--rm`, so nothing persists.
"""),
        trap=t("""
Inside the app container, `python -c "import os; print(os.cpu_count())"` prints the engine's
full CPU count rather than the half CPU the service is allowed, and `/proc/meminfo` shows the
machine's memory rather than 128 MB. Neither source is namespaced; the limits live in the cgroup.
Programs that size worker pools or heaps from those numbers start more threads or allocate more
memory than the cgroup permits, and the kernel's out-of-memory killer then ends the process,
which Docker reports as exit code 137. Read the real limits from `/sys/fs/cgroup/memory.max` and
`/sys/fs/cgroup/cpu.max` on cgroup v2, and set worker counts explicitly rather than trusting
detected hardware.
"""),
        ask=t("""
A colleague says containers are lightweight virtual machines, so a kernel exploit inside one
cannot touch the others. Correct the claim using what this lesson's observations showed.
"""),
        answer=t("""
On Linux the kernel release printed inside the container matched the host's, so every container
shares that kernel; namespaces only limit what each process can see, and cgroups only meter what
it can use. A kernel vulnerability reachable from inside one container can therefore affect the
host and its neighbors. Mitigations are a patched kernel, dropped capabilities, the default
seccomp profile and no-new-privileges as the fixture uses, or a stronger boundary such as a VM
per tenant. A differing release on a Linux host would mean a VM-based runtime.
"""),
    ),
    "docker-040": dict(
        lab=t("""
Rehearse a file secret in a scratch copy of the fixture. Write a throwaway value with `printf
'study-only-value' > demo-secret.txt`, and put the top-level `secrets:` block and the service
grant from worked example 1 in a `compose.secret.yaml` override. Render `docker compose -p
ds60-docker-study -f compose.yaml -f compose.secret.yaml config` and confirm that `app` lists
`demo`. Start the app with both files and `up -d --wait`, then run `docker compose -p
ds60-docker-study exec app python -c "from pathlib import Path;
print(len(Path('/run/secrets/demo').read_text().strip()) > 0)"`, which prints `True` without
revealing the value. Search `docker inspect` output for the app container for `study-only-value`:
it is absent. Finish with a plain `up -d --wait` from the original file to recreate the app
without the grant, then delete the override and the secret file.
"""),
        trap=t("""
Tightening the secret file with `chmod 600` feels like the responsible step, and on a Linux host
it breaks the service. Without Swarm, Compose bind-mounts a file secret into `/run/secrets` with
its host owner and mode, so a file readable only by your account is unreadable for UID 10001 in
the container. The validator then fails with `PermissionError`, which looks like a missing
secret. Docker Desktop's file sharing can mask the problem, so a setup that works on a laptop
fails on a server. Grant read access to the container's identity instead, for example group
10001 with mode 640, and run the validator to prove the service can read it.
"""),
        ask=t("""
A teammate wants to bake a database password into the image with `ENV` so deployments need no
extra files. What does that expose, and what would you propose instead?
"""),
        answer=t("""
`ENV` values become part of the image configuration, so anyone who can pull or inspect the image
reads the password with `docker image inspect`, it travels to every registry and archive the
image reaches, and rotating it requires a rebuild. Propose a runtime secret file granted only to
the service, read from `/run/secrets` and validated without printing it. Acceptance is that
`docker image inspect` and `docker inspect` show no password while the app connects. If the
value still appears in either output, it enters through image or environment configuration.
"""),
    ),
    "docker-041": dict(
        lab=t("""
Ask Compose for a second replica and read why it refuses: `docker compose -p ds60-docker-study
up -d --scale app=2`. The second container is created but cannot start, and the error names the
`127.0.0.1:18080` binding already held by the first, because a fixed host port can be bound by
only one container. Run `docker compose -p ds60-docker-study ps -a` to see one running and one
created container, then return to one replica with `docker compose -p ds60-docker-study up -d
--scale app=1 --wait`, which removes the extra. Both would have mounted the same `study-data`
volume, so trace on paper what two working replicas would do: each holds its own `LOCK`, each
reads the same file, and each writes its own increment, which is the lost update from worked
example 1.
"""),
        trap=t("""
Even the fixture's careful write path hides a single-writer assumption: every writer stages its
data in the same file name, `counter.next`, before `replace()` moves it into place. Two processes
in separate containers sharing the volume can both write `counter.next`, after which the first
`replace()` moves the other writer's bytes into place and the second fails with
`FileNotFoundError` because the staging file is already gone. Its client sees the connection
close without a response, alongside the lost updates. Atomic replacement is only as good as the
uniqueness of its staging name and the exclusivity of its writer, so a scaled design needs
unique temporary names and, more importantly, one owner or a transactional store.
"""),
        ask=t("""
A product owner wants three replicas of the study app behind a load balancer for a workshop of
two hundred learners. What must change before that is safe, and what is the simplest correct
alternative?
"""),
        answer=t("""
Three replicas need a routing layer instead of the fixed host port, and the counter needs a
shared store with transactions, such as a database that increments in one statement, because
file replacement and an in-process lock cannot serialize writers in different containers. The
simplest correct alternative is one replica with an explicit single writer, measured first: a
standard-library server answering small JSON requests may well carry two hundred learners. A
load test showing that one replica saturates is the evidence that would justify the larger
design.
"""),
    ),
    "docker-042": dict(
        lab=t("""
Run the final rehearsal as a prediction exercise. Before any command, write the expected result
for the normal path, meaning the host request, the peer request and one increment; for one
controlled failure, such as the client pointed at `app:9090` in a scratch copy; for container
replacement with `up -d --force-recreate --wait app`, which should keep the counter; and for the
README's export and separate restore. Then run each step, mark every prediction as matched or
not, and for a mismatch write the first observation that differed before changing anything.
Close by removing only what you created, the scratch copy, `counter-backup.json` and the restore
volume, and copy `docker compose -p ds60-docker-study ps -a` and the project's volume list into
the packet as proof of the final state.
"""),
        trap=t("""
A handoff that lists every command reads as complete, yet a new operator follows commands in
order and cannot tell a normal pause from a failure. Without the expected observation beside
each step, `--wait` taking twenty seconds, an empty `docker compose ps` after `down`, or a 404
from an unknown route can each be mistaken for breakage, and a real failure can be accepted as
normal. Put the expected output, or its shape, next to every command, mark which steps change
state and which only read, and test the handoff by having someone else follow it on a clean
engine while you watch silently and note where they hesitate.
"""),
        ask=t("""
While preparing the release packet you change `APP_MESSAGE` in `compose.yaml`. Do you rebuild
the image or recreate the container, and which observation proves you picked correctly?
"""),
        answer=t("""
Recreate. `APP_MESSAGE` is runtime environment that Compose sets, not something copied into the
image, so `docker compose -p ds60-docker-study up -d --wait app` recreates the container with
the new value and the image ID in the packet stays valid. A host request to `/` returning the
new message, with `docker image inspect --format '{{.Id}}'` unchanged, proves it. Had you edited
`server.py`, a rebuild would be required and the packet's image identity would change. If `/`
still shows the old message, the container was not recreated.
"""),
    ),
}
