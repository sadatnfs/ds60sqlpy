# ruff: noqa: E501
"""Per-exercise solution reasoning for the Docker lessons.

REASONING maps each lesson title (the same keys as KEY_TERMS) to six tuples,
one per exercise, of (approach, why it is correct, a plausible wrong approach
and why it fails, how to verify). build.py validates and renders them into the
explanatory solutions.
"""

REASONING = {}

REASONING["Containers, images and the process model"] = (
    (
        "Separate the two objects that the run touched: the image tagged ds60-docker-study:local and the container that the --rm flag created for one python -c call.",
        "The build wrote the image once; the run only borrowed it. When print(2 + 3) returns, the container's only process ends and --rm deletes that container, leaving the tag untouched.",
        "Assuming --rm cleans up everything the run used leads learners to rebuild before every run. The flag never reaches the image store, so the rebuild is wasted work.",
        "After the run, docker image ls ds60-docker-study still lists the local tag, while docker ps -a --filter ancestor=ds60-docker-study:local returns no rows.",
    ),
    (
        "Draw one box for the image's read-only layers, then two separate boxes on top, each holding its own process tree and its own thin writable layer.",
        "Each docker run creates a new container with a fresh writable layer and a new PID namespace. Only the read-only image layers are referenced by both.",
        "Drawing a single python process with two names suggests that a variable set in one container is visible in the other. Separate namespaces and writable layers make that impossible.",
        "Start two short runs that each print os.getpid(); both can report PID 1, which is only possible because each container has its own PID namespace.",
    ),
    (
        "Write each object with the event that creates it and the command that removes it: edit server.py, docker build, docker run or compose up, and docker volume create.",
        "server.py lives on the host, ds60-docker-study:local is an image reference, each run produces a container, and study-data is a named volume declared in compose.yaml.",
        "Treating the tag as the container leads to docker rm ds60-docker-study:local, which fails because rm expects a container name or ID, not an image reference.",
        "List each object with its own inventory command: ls for source, docker image ls, docker ps -a and docker volume ls. Each object appears in exactly one listing.",
    ),
    (
        "Reason from the main process lifecycle: when it ends, the engine records an exit code and keeps the container object unless --rm or docker rm removes it.",
        "docker ps -a shows all containers, including those in the exited state. The stopped record holds the exit code, logs and writable layer for later inspection.",
        "Concluding that the process is still running because the name is listed confuses docker ps -a with docker ps. Only the default listing filters to running containers.",
        "Run a container without --rm, then compare docker ps and docker ps -a; the STATUS column for the second shows Exited with the recorded code.",
    ),
    (
        "Compare what each program calls underneath: the containerized python binary is a Linux ELF executable that makes Linux system calls inside the engine's virtual machine.",
        "On macOS, Docker Desktop runs a Linux kernel in a lightweight VM. Containers share that kernel, not the macOS one, so macOS APIs are unavailable inside them.",
        "Expecting an image built for linux/arm64 to run any macOS arm64 binary fails, because matching CPU architecture is not enough when the operating system interface differs.",
        "Run uname -s through docker run against the local image; it reports Linux, while the same command in a macOS terminal reports Darwin.",
    ),
    (
        "Stack three claims in order: the image exists, the container's main process is running, and a request to the published endpoint returns the expected body.",
        "Only the last layer tests behavior. The fixture's GET / should return JSON with the APP_MESSAGE text, which no image or process listing can show.",
        "Treating a running status from docker ps as proof skips the request. A server bound to the wrong interface or crashing per request still shows a running container.",
        "From the host, send curl --max-time 3 http://127.0.0.1:18080/ and confirm a 200 response whose message field matches the compose environment value.",
    ),
)

REASONING["The Linux engine, WSL 2 and your first inspection"] = (
    (
        "Ask which component answers the command. docker --version is printed by the client binary from its own build metadata.",
        "The client does not contact the daemon for that flag, so the line appears even when the engine is stopped, missing or unreachable.",
        "Treating a printed version as a green light leads to confusing errors at the first docker build, when the client finally tries to reach the daemon socket.",
        "Stop the engine and run docker --version and docker info. The first still prints; the second reports that it cannot connect to the daemon.",
    ),
    (
        "Run docker context show for the name, then inspect that context and read its endpoint host field, rather than trusting the context label.",
        "Context names are arbitrary strings. The endpoint value, such as a local Unix socket path versus an ssh:// or tcp:// address, decides which engine receives commands.",
        "Accepting a context called local at face value fails if someone pointed it at a remote host. The name stays reassuring while commands mutate a shared engine.",
        "In the docker context inspect output, the Docker endpoint Host is a local socket path such as unix:///var/run/docker.sock or a Desktop-managed socket, not a network address.",
    ),
    (
        "List only what the lessons call from the host: a Bash shell, a running local Linux-container engine, the Compose plugin, and CPU, memory and disk allocated to it.",
        "Every program in the fixture runs inside `python:3.12-slim`, so the host never needs Python. The engine and Compose are what docker build and docker compose require.",
        "Installing Python, Node and compilers on the host first adds work and leaves docker info failing if the engine was never started.",
        "Tick each item with a command: echo $BASH_VERSION, docker info returning OSType linux, and docker compose version printing a version line.",
    ),
    (
        "Split the failure into three independent questions: is the engine process running, does the context point to it, and does this user have permission on its socket?",
        "A successful client line plus a connection error means the request never reached a daemon, so nothing about the Dockerfile has been evaluated yet.",
        "Editing the Dockerfile or reinstalling the image in response wastes effort, because the same docker info error appears before any build input is read.",
        "Fix one layer at a time and rerun docker info after each change; success is the first time it prints server details instead of a connection error.",
    ),
    (
        "Open the Ubuntu distribution installed under WSL 2 and run every lesson command in its Bash terminal, with the project stored in the Linux filesystem.",
        "The commands use $(...) substitution, double-quoted Go templates and backslash continuations, which Bash interprets as written. WSL 2 integration exposes the Linux engine there.",
        "Pasting the same lines into PowerShell fails in subtle ways, since PowerShell uses a backtick for continuation and its own quoting rules for the {{.OSType}} template.",
        "In the WSL terminal, uname -s prints Linux and docker info --format with the OSType template prints linux, showing both shell and engine match the lessons.",
    ),
    (
        "Pause before any create, stop or remove command, record the context name and endpoint, then switch to or create a context whose endpoint is your own local engine.",
        "The lesson authorizes changes to a disposable local project only. A remote endpoint belongs to someone else, whose containers and volumes the cleanup commands could delete.",
        "Running docker compose down to test whether the remote is harmless fails as a safety check, because it already mutates the very engine you have not been authorized to use.",
        "After switching, docker context show names the local context and its inspected endpoint is a local socket, checked before running any fixture command.",
    ),
)

REASONING["The filesystem, writable layers and container lifetime"] = (
    (
        "Trace /app/server.py to the Dockerfile line COPY server.py /app/server.py, which places it in a read-only image layer below every container's writable layer.",
        "Because the file comes from a build instruction, every container started from the tag sees it, and only a rebuild with a changed source can alter it.",
        "Calling it a runtime file created by the server fails here, since server.py never writes into /app; it only writes counter files under /data.",
        "Worked example 1 prints True for Path('/app/server.py').is_file() even with --rm and no mounts, which only image content can explain.",
    ),
    (
        "Picture each container's writable layer as private copy-on-write storage over the shared image layers, then check whether any mount links the two containers.",
        "Without a shared volume or bind mount, a file written by one container exists only in that container's upper layer, so the sibling's view of the path is unchanged.",
        "Assuming the shared tag means a shared filesystem fails, because the tag only names the read-only lower layers that both containers began from.",
        "Write a marker file in /tmp of one long-running container, then list the same path in a second container from the same image; the marker is absent.",
    ),
    (
        "Build a table with rows for the writable layer, the study-data volume and the /tmp tmpfs, and columns for restart, recreate and image rebuild.",
        "Restart keeps the container ID and its writable layer; recreate discards both. The volume survives both because compose.yaml mounts it by name; tmpfs is empty after either.",
        "A single blanket rule such as data survives restarts misses that the fixture's /tmp is tmpfs, which is wiped on every restart even though the container persists.",
        "Increment the counter, restart the app service, read /counter, then recreate and read again; the value persists both times because counter.json lives in /data.",
    ),
    (
        "Compare the container ID before and after compose up, then ask where the missing file was written: the writable layer, /tmp, or the /data volume.",
        "Compose recreates a service when its configuration or image changes. The new container starts with a fresh writable layer, so files outside volumes disappear.",
        "Restoring the image or reinstalling Compose fails to recover the file, because the image never held it and the old writable layer was removed with the old container.",
        "docker compose -p ds60-docker-study ps -q app prints a different ID after recreation, and a file written to /data before it is still present afterward.",
    ),
    (
        "Look at each mount separately: compose.yaml sets read_only: true for the root filesystem and adds a tmpfs at /tmp with `rw,noexec,nosuid` and `size=16m`.",
        "The read-only flag applies to the root mount. The tmpfs is its own mount with its own options, so writes under /tmp succeed while writes under /app fail.",
        "Removing read_only to silence an application write error fails the lesson goal, because it makes /app and every other path writable to a compromised process.",
        "With the stack running, a python -c write to /tmp/x succeeds through docker compose exec, while the same write to /app/x raises a read-only filesystem error.",
    ),
    (
        "Classify each kind of data by whether a learner would lose work if it vanished, and then pick a volume, tmpfs or writable layer to match.",
        "Progress such as counter.json must survive container replacement, which only the study-data volume guarantees. Scratch files gain from tmpfs, which is bounded and cleared automatically.",
        "Putting everything into the volume keeps stale scratch files forever and widens what a backup or privacy review must cover, while the writable layer loses progress on recreate.",
        "Recreate the app service and check that /data/counter.json still exists and /tmp is empty, matching the retention rule you wrote for each.",
    ),
)

REASONING["Processes, PID 1, signals and graceful shutdown"] = (
    (
        'Identify the main process from CMD ["python", "server.py"] and follow what happens when serve_forever returns and main() finishes.',
        "The container's lifetime is tied to its main process. When that python process exits, the engine marks the container exited and records the exit code.",
        "Expecting a background thread to keep the container up fails, because threads belong to the main process and end with it.",
        "Stop the app with docker compose stop and read docker compose ps -a; the app row shows an exited state with the code the process returned.",
    ),
    (
        'Write both forms side by side: CMD ["python", "server.py"] versus CMD python server.py, and note which program becomes PID 1 or the direct child of init.',
        "The exec form runs python directly, so SIGTERM reaches the handler registered in server.py. The shell form starts /bin/sh -c, which may not forward the signal.",
        "Declaring the shell form always broken is wrong; a shell that uses exec python server.py hands control to python and keeps signals working.",
        "docker compose exec app ps is unavailable in slim images, so inspect the configured command with docker image inspect and confirm Cmd is a two-item array.",
    ),
    (
        "Map each step to server.py: the SIGTERM handler calls server.shutdown, serve_forever stops accepting, the finally block runs server_close, and main returns.",
        "stop_grace_period: 10s bounds the drain, and the atomic counter.next to counter.json replace means no reader ever sees a half-written record during shutdown.",
        "Closing the socket in the signal handler itself can raise errors in the serving thread, which is why the fixture starts shutdown on a separate daemon thread.",
        "Time docker compose -p ds60-docker-study stop app; it returns well before 10 seconds, and the logs show no traceback on exit.",
    ),
    (
        "Ask what PID 1 actually is: if a command such as sleep infinity runs while the server starts in the background, the container tracks sleep, not the server.",
        "Container status reflects only the main process. A crashed background server leaves sleep running, so the status looks healthy while requests fail.",
        "Adding a second sleep or longer timeout to hide the crash makes the false signal stronger and delays the moment anyone notices the outage.",
        "Use the healthcheck instead: the fixture's /healthz probe turns unhealthy when the server stops answering, regardless of which process holds PID 1.",
    ),
    (
        "Read 137 as 128 plus signal 9, SIGKILL, and then list who could have sent it: the kernel OOM killer, the engine after a stop timeout, or a user.",
        "The code records how the process ended, not why. docker inspect reports State.OOMKilled separately, and engine events show whether a stop or kill was issued.",
        "Doubling mem_limit from 128m on every 137 can hide a stop timeout bug, because a process that ignores SIGTERM is killed after the grace period with the same code.",
        "Check docker inspect for State.OOMKilled and the event stream around the exit time; true OOM shows OOMKilled true, a timeout kill shows false.",
    ),
    (
        "Write three checks in order: stop within the grace period, inspect the record on disk, then start again and read it through the API.",
        "server.py writes counter.next and then renames it, so an interrupted write leaves the old counter.json intact. read_counter validates schema on startup.",
        "Checking only for exit code 0 passes even if the counter file was truncated, because the process can exit cleanly after a bad write.",
        "After stop and start, GET /counter returns the last acknowledged value with schema_version 1, and the app logs show no invalid counter state error.",
    ),
)

REASONING["Dockerfile instructions and the first reproducible image"] = (
    (
        "Label each instruction with when it executes: RUN mkdir -p /data runs during docker build, while CMD only stores the default command in image configuration.",
        "The builder executes RUN in a temporary container and snapshots the filesystem. CMD changes metadata and runs only later, when a container starts.",
        "Writing RUN python server.py to start the app blocks the build forever, because serve_forever never returns and no layer is committed.",
        "docker image inspect shows Config.Cmd as python server.py, while the build log lists the RUN step and its completion, not the server starting.",
    ),
    (
        "Read the trailing dot in docker build -t ds60-docker-study:local . as the context path, the directory whose files the builder may read.",
        "COPY server.py resolves against that context, so the command must run from the fixture copy where server.py and the Dockerfile sit side by side.",
        "Running the same command from the repository root sends a much larger context and fails to find the Dockerfile, which is only in the fixture directory.",
        "Run the build from the fixture copy and check that the build log reports a small context transfer and that the COPY step succeeds.",
    ),
    (
        "Choose a base with Python, set WORKDIR /app, copy only server.py, and set an exec-form CMD that runs it in the foreground.",
        "Those four instructions match worked example 1 and need nothing from the host except the file. The server uses only the standard library, so no install step is required.",
        "Adding RUN pip install of unrelated packages makes the image larger and the build dependent on a package index without changing what server.py can do.",
        "Build the image, then run python -c to check that /app/server.py exists and that Config.Cmd and WorkingDir match the recipe.",
    ),
    (
        "Read the error as a context boundary problem: COPY ../shared/config.txt names a path outside the context directory sent to the builder.",
        "The builder only receives the context; relative paths cannot climb out of it. Either move the needed file into the project or choose a narrower, deliberate context.",
        "Running docker build from / so the parent is inside the context ships every file on the host to the builder, including private material.",
        "After the layout change, the build log shows a context of the expected size and the COPY step completes without a not found error.",
    ),
    (
        "Separate image metadata from runtime wiring. EXPOSE 8080 records intent; the compose port mapping 127.0.0.1:18080:8080 actually forwards host traffic.",
        "server.py binds 0.0.0.0:8080 inside the container, and only a -p or ports entry creates the host side. Without it, nothing on the host listens.",
        "Requesting `localhost:8080` after docker run without -p fails, and adding a second EXPOSE line cannot help because metadata never opens a socket.",
        "docker compose port app 8080 prints 127.0.0.1:18080, and a request to that address returns the JSON greeting.",
    ),
    (
        "Write two lists: build acceptance covers the tag existing with the intended Cmd and User; runtime acceptance covers the endpoint, the user and /data writes.",
        "The image declares USER 10001:10001 and a /data owned by that user, so the runtime check must confirm a counter increment succeeds under those settings.",
        "Stopping at a green build misses errors that appear only at runtime, such as a permission failure when the non-root user writes to a mounted volume.",
        "After compose up, POST /increment returns a counter of 1 on a fresh volume, and GET /healthz returns status ready.",
    ),
)

REASONING["Build context, .dockerignore and accidental data exposure"] = (
    (
        "Compare the two rule files by their consumers: Git reads .gitignore, while the Docker builder reads only .dockerignore in the context root.",
        "The builder never looks at .gitignore, so an untracked .env next to the Dockerfile is still sent unless .dockerignore excludes it.",
        "Relying on .gitignore because the file is not committed fails exactly when it matters, since local secrets are usually ignored by Git yet present on disk.",
        "Place a harmless test file covered only by .gitignore, build with COPY . /probe, and list /probe; the file is present until .dockerignore names it.",
    ),
    (
        "Evaluate *.pyc against the full path from the context root, app/__pycache__/server.cpython-312.pyc, remembering that a single star stops at a slash.",
        "The root-only pattern cannot match a nested path, while the fixture's **/*.pyc and **/__pycache__ entries cover any depth.",
        "Copying the habit from .gitignore, where a slash-free pattern matches anywhere, leaves nested bytecode in the context.",
        "Add a nested .pyc file in a scratch copy, build with a broad COPY, and confirm the file is present with *.pyc and absent with **/*.pyc.",
    ),
    (
        "List the files the Dockerfile reads: the Dockerfile itself, .dockerignore and server.py, and nothing more, given that the only COPY names server.py.",
        "That short inventory makes review possible and matches the fixture's .dockerignore, which also excludes .git, .learning, .env files, logs, tar archives and JSON.",
        "Writing COPY . /app to be safe copies README.md, compose.yaml and any stray local file, so the inventory stops being something a reviewer can check.",
        "Compare the inventory to the image by running python -c to list /app; only server.py appears there.",
    ),
    (
        "Picture the layer stack: COPY secret.txt creates one layer, and RUN rm secret.txt adds a later layer with a whiteout entry hiding that path.",
        "Each layer is stored and distributed separately. Hiding a path in the merged view leaves the bytes in the earlier layer, recoverable by anyone holding the image.",
        "Adding the rm in the same Dockerfile and calling the image clean fails, because docker save or a registry pull still exposes the earlier layer.",
        "docker history shows both steps with sizes, and the secret-bearing layer is still listed; the fix is to keep the file out of the context entirely.",
    ),
    (
        "Exclude server.py in a scratch .dockerignore and predict which instruction fails and with what kind of error.",
        "The context no longer contains server.py, so COPY server.py /app/server.py stops the build with a not-found error instead of using a stale or host copy.",
        "Removing the ignore rule for all Python files to fix it widens the context to nested .pyc and other files when only server.py needed restoring.",
        "The build log names the failing COPY step; after restoring the precise rule, the build passes and the image lists only /app/server.py.",
    ),
    (
        "Check three places in order: .dockerignore excludes private inputs, the Dockerfile copies named files only, and the finished image holds only the intended files.",
        "Each check catches a different leak: the context check stops transfer, explicit COPY limits layering, and image inspection catches anything that slipped through.",
        "Trusting a single scan of the final image misses secrets that were copied and later deleted, since a merged-view listing cannot show hidden earlier layers.",
        "Record the .dockerignore entries, the COPY lines and a listing of /app and /data from the built image, and confirm each matches the public inventory.",
    ),
)

REASONING["Layers, cache invalidation and efficient rebuilds"] = (
    (
        "Walk the fixture Dockerfile top to bottom and find the first instruction whose input includes server.py: COPY server.py /app/server.py.",
        "FROM and WORKDIR keep their cache keys, so they reuse. COPY's checksum changes, and every later step, including RUN mkdir and the metadata steps, rebuilds after it.",
        "Expecting only the COPY step to rebuild fails, because the builder reuses a later step only when its parent layer is unchanged.",
        "Edit a comment in server.py, rebuild with --progress=plain, and confirm the log shows CACHED up to WORKDIR and executed steps from COPY onward.",
    ),
    (
        "Capture the plain progress output of the second identical build and look for the CACHED marker beside specific step numbers.",
        "A CACHED label is the builder's own record that it reused a layer, which ties the evidence to the decision rather than to timing noise.",
        "Using a shorter wall-clock time as proof fails, because a warm disk or a quiet network can make an uncached build faster too.",
        "Save both logs and point to the step lines for COPY and RUN mkdir labeled CACHED in the second log.",
    ),
    (
        "Place a COPY of dependency metadata such as requirements.txt and its RUN install before the COPY of application source.",
        "Editing source then leaves the metadata checksum unchanged, so the expensive install layer is reused and only the source copy reruns.",
        "Copying source before installing dependencies reruns the install on every code edit, and copying too few files can make the install fail.",
        "Edit only application source and rebuild; the install step should show CACHED while the source COPY runs. Then edit the lockfile and see the install run again.",
    ),
    (
        "Note that a RUN that fetches a file by URL has a cache key built from the command text, not from the bytes at that URL.",
        "If the server publishes a new file under the same URL, the builder still reuses the old layer, so two machines can hold different contents.",
        "Running --no-cache on every build to stay fresh discards all reuse and still does not pin anything, so builds stay unrepeatable.",
        "Pin the download by version and checksum and verify it in the RUN; changing either value changes the command text and forces a rebuild.",
    ),
    (
        "Name the two controls: --no-cache ignores existing build cache, and --pull asks the builder to resolve and fetch the FROM image again.",
        "The fixture builds FROM a `python:3.12-slim` tag; --no-cache can rerun every step on the same local base, while --pull may get a newer image.",
        "Using --no-cache to pick up a base security fix fails if the local base is stale, because no new base is fetched.",
        "Compare the base image ID before and after each option with docker image inspect; only a pull can change it, while --no-cache changes step execution.",
    ),
    (
        "Fix the engine, context and base, make one controlled edit, and record the step log and timing for a cold build and a warm rebuild.",
        "Holding everything else constant makes the CACHED and executed steps attributable to the single edit, so the slow step is identified by evidence.",
        "Changing the base tag, Dockerfile order and source at once leaves no way to tell which change caused the speedup or slowdown.",
        "Present a table of step number, cached or executed, and duration for each run, and name the slowest executed step as the optimization target.",
    ),
)

REASONING["Environment variables, command arguments and configuration"] = (
    (
        "Ask who reads each value: Compose substitutes ${VAR} while rendering compose.yaml on the host, while the environment: block becomes input to the python process.",
        "Interpolation finishes before any container exists, so a ${HOST_PORT} used in ports never reaches server.py, and the literal APP_MESSAGE needs no host variable.",
        "Exporting APP_MESSAGE in the host shell and expecting server.py to see it fails unless the model forwards it, because the container does not inherit the host shell.",
        "docker compose config prints the rendered model with substitutions applied, and the GET / response shows the APP_MESSAGE string the process actually received.",
    ),
    (
        'Follow the value into server.py, which reads os.environ.get("APP_MESSAGE") and places it straight into the JSON response.',
        "The process environment is a list of byte strings. Setting APP_MESSAGE to 42 still delivers the characters 4 and 2, and the JSON message field is a string.",
        "Expecting a YAML integer such as APP_MESSAGE: 42 to arrive as a number fails, because Compose converts the value to text before starting the process.",
        "Run worked example 2 with -e APP_MESSAGE=42 and print type(os.environ['APP_MESSAGE']); python reports str.",
    ),
    (
        "Define REQUEST_TIMEOUT_SECONDS with a documented default, parse it as a number at startup, and reject values that are not finite or fall outside a stated range.",
        "Validating once at startup makes a bad deployment fail immediately with a clear message, before any request depends on a zero, negative or huge timeout.",
        "Passing the raw string to a socket timeout fails late and unclearly: an empty value raises inside a request, and 99999 silently turns a stuck call into a hang.",
        "Start the container with a missing, valid, nonnumeric and oversized value in turn; only the default and the valid value reach a ready /healthz.",
    ),
    (
        'Read the exec array ["python", "server.py", "--port", "$PORT"] literally: each element goes to the program as written, with no shell in between.',
        "Only a shell expands $PORT. In exec form the program receives the five characters $PORT, so it must read os.environ itself.",
        "Switching to the shell form just to expand one variable makes /bin/sh the parent process and can block SIGTERM from reaching python.",
        "Print sys.argv inside the container for the exec form; the last element is the literal $PORT, confirming that no expansion happened.",
    ),
    (
        "Separate the edited YAML from the container's stored configuration: docker compose restart restarts the existing container with the environment it was created with.",
        "Environment is fixed at container creation. docker compose up -d compares the model with the running container and recreates the service when they differ.",
        "Running restart repeatedly and concluding the app ignores configuration fails, because the new value never reached a container.",
        "After docker compose up -d, ps -q app prints a new container ID and GET / returns the edited message.",
    ),
    (
        "Record the variable name, a synthetic value, where it was set (compose.yaml, an override file or -e), the container ID and the response body.",
        "Those fields link the configured source to the observed application output, and a public greeting can be logged without exposing anything private.",
        "Pasting a real API token as the sample value proves precedence just as well but copies a secret into notes, screenshots and shell history.",
        "Someone else can repeat the record: change the value at the stated source, recreate, and see the same message in the JSON response.",
    ),
)

REASONING["Ports, loopback and the first browser request"] = (
    (
        'Split "127.0.0.1:18080:8080" at its colons from left to right: host IP, host port, then container port.',
        "The fixture's server binds port 8080 inside the container, and the host side is fixed to loopback on 18080, so a browser on the same machine is the only intended client.",
        'Writing "127.0.0.1:8080:18080" still opens a host listener but forwards traffic to container port 18080, where nothing listens.',
        "docker compose port app 8080 prints 127.0.0.1:18080, and a request to that host address returns the fixture JSON.",
    ),
    (
        "Locate the caller: a command run through docker compose exec app has its own network namespace and its own loopback interface.",
        "Inside app, 127.0.0.1 is the container itself, where only port 8080 listens. Port 18080 exists only on the host side of the mapping.",
        "Copying the browser URL into a health probe or a sibling client produces connection refused and looks like a broken server.",
        "From inside app, a python urllib request to 127.0.0.1:8080/healthz succeeds while 127.0.0.1:18080 is refused.",
    ),
    (
        "Draw four hops: the browser connects to 127.0.0.1:18080, the engine forwards it to the container, and server.py's listener on 0.0.0.0:8080 handles it.",
        "Port translation happens once, at the published mapping. After that the request reaches the container interface and the Handler class chooses the response.",
        "Drawing the browser connecting straight to container port 8080 hides the mapping, so a missing ports: entry would be impossible to locate on the diagram.",
        "Annotate each hop with its check: the port listing, container state, the app logs showing the request line, and the JSON body.",
    ),
    (
        "Compare the listener address with the mapping target: a server that binds 127.0.0.1:8080 inside the container listens only on the container's loopback.",
        "Published traffic arrives on the container's network interface, not on its loopback. The fixture avoids this by binding 0.0.0.0 in LocalServer.",
        "Changing 18080 to another host port cannot help, because every mapping delivers traffic to the same interface where the app is absent.",
        "A probe from inside the container to 127.0.0.1:8080 works while the host request fails; after binding 0.0.0.0, both succeed.",
    ),
    (
        "Ask whether an HTTP response came back at all. A refused connection fails at TCP; a 404 is a complete response from the server.",
        'The fixture returns {"error": "unknown route"} with status 404 for unknown paths, which proves the mapping and listener worked.',
        "Rewriting URL handlers after connection refused changes code the request never reached, while the real fault is a missing mapping or listener.",
        "curl -i http://127.0.0.1:18080/nope prints an HTTP/1.0 404 status line, while a request to an unmapped port reports connection refused.",
    ),
    (
        "Publish only the user-facing web service on loopback and let the internal service talk over the project network by its service name.",
        "Compose DNS resolves service names on the project network, as the client service does with `http://app:8080/`, so internal traffic needs no host port.",
        "Publishing the database on 0.0.0.0 to make debugging easy exposes it to anyone who can reach the host on that port.",
        "docker compose ps shows a port column only for the web service, and the web service still reaches the internal one by name.",
    ),
)

REASONING["Logs, exit status and observation before repair"] = (
    (
        "Match each program to its stream: print('ok') writes to stdout, and an uncaught ValueError makes python write a traceback to stderr.",
        "Python prints uncaught exceptions on stderr and exits with status 1. Docker keeps both streams, so you can split them on the host.",
        "Assuming all container output is one undivided log fails when a script captures only stdout, which loses the traceback.",
        "Rerun worked example 2 with 2>/dev/null: ok still appears, the traceback disappears, and echo $? prints a nonzero status.",
    ),
    (
        "Name the project, the service and a line limit: docker compose -p ds60-docker-study logs --tail 30 app.",
        "The project and service filters keep the sample to the fixture's own container, and --tail caps the volume before anything is copied into notes.",
        "Running docker logs on every container and grepping afterward shows output from unrelated workloads and may expose their data.",
        "The output prefix names only the app service, and the line count is at most 30.",
    ),
    (
        "Collect four items with timestamps: the image ID behind ds60-docker-study:local, docker compose ps -a state, a bounded log sample and one failing request with its status.",
        "Each item answers a different question: what was packaged, whether it ran, what it reported and how it behaved, all fixed to the time of failure.",
        "Collecting only a screenshot of the browser error leaves no way to tell whether a stale image, stopped container or app bug caused it.",
        "A second reader can rebuild the timeline from the packet alone and name the layer where the failure first appears.",
    ),
    (
        "Accept that the engine reports a running process and move on to the application: send requests and read the status codes and bodies.",
        "Container state only tracks the main process. If counter.json fails validation in read_counter, the fixture stays running while GET /counter raises inside the handler and the client gets no valid response.",
        "Restarting until the status says Up treats process lifecycle as correctness and can repeat the same failing request forever.",
        "GET /counter failing while ps shows the container running, plus a ValueError traceback in the app logs, confirms an application-layer fault.",
    ),
    (
        "Separate mitigation from diagnosis: a restart may restore service, but it also replaces the evidence that explained the failure.",
        "After restart, the old process's memory state is gone. Only logs and exit records captured beforehand can still point to a cause.",
        "Writing fixed by restart in an incident note claims a root cause that nobody observed, so the same fault returns unexplained.",
        "Check that the incident note records the pre-restart logs and states plainly that the cause is unknown if it has not been reproduced.",
    ),
    (
        "Log the method, path, status and duration for each request, and leave out headers, query strings and bodies that may carry tokens or personal data.",
        "Logs are copied into terminals, reports and screenshots. A fixed small schema keeps debugging value while keeping secrets out of those copies.",
        "Logging full request headers for convenience copies Authorization values into every place the log travels.",
        "Send a request with a dummy Authorization header and confirm the log line shows method, path and status but not the header value.",
    ),
)

REASONING["Compose services, projects and a complete application"] = (
    (
        "Read the names from their sources: -p ds60-docker-study sets the project, and the services: key in compose.yaml defines app and client.",
        "The project prefixes resource names such as the network and volume, the service is the role, and each container has its own ID.",
        "Treating the container ID as the stable name fails after recreation, because the ID changes while the project and service stay the same.",
        "docker compose -p ds60-docker-study ps lists app under the project, and ps -q app shows the current container ID.",
    ),
    (
        "Predict the effect from what the command reads: config --quiet parses compose.yaml, applies interpolation and checks the schema.",
        "It exits zero for a valid file and creates nothing, so it is safe to run before any build or start.",
        "Treating a clean config result as proof the stack works fails, because port 18080 may be busy or the volume may reject writes.",
        "After config --quiet, docker compose -p ds60-docker-study ps -a lists no containers for the project if none existed before.",
    ),
    (
        "Order the commands as worked examples 1 and 2 do: config --quiet, build, up -d --wait, ps, then down, each with -p ds60-docker-study.",
        "Each command adds one kind of evidence, from a valid model through a healthy service, and the fixed project flag keeps every command on the same resources.",
        "Omitting -p means Compose derives the project from the directory name, so a renamed copy silently creates a second project.",
        "Every ps listing during the session shows the same project name, and down reports removing only that project's container and network.",
    ),
    (
        "Before changing anything, list resources by project label and check what already holds host port 18080.",
        "A collision means another stack is using the same project name or port. Only after identifying the owner is it safe to rename or stop.",
        "Running docker rm -f on whatever holds the port may remove another learner's or tool's container that this lesson never created.",
        "docker ps --filter label=com.docker.compose.project=ds60-docker-study lists only owned containers; anything else on 18080 belongs to someone else.",
    ),
    (
        "Compare what down removes by default (containers and the project network) with what it removes only when asked (volumes, with -v).",
        "The study-data volume holds counter.json, which is learner progress. Keeping it by default means routine stops do not erase work.",
        "Adding -v to every down for a tidy machine deletes the counter each time and makes the persistence lessons impossible to observe.",
        "After down, docker volume ls still lists the project's study-data volume, and the next up returns the previous counter value.",
    ),
    (
        "Give each copy its own -p project name and its own host port on the ports line, while leaving service names and container ports unchanged.",
        "Each project gets its own network and volume, so app resolves within each copy. Host ports share one namespace and must differ.",
        "Changing only the project name leaves both copies trying to bind 127.0.0.1:18080, so the second up fails to publish.",
        "Both projects appear in docker compose ls, and each loopback port returns its own copy's response.",
    ),
)

REASONING["Health checks, startup order and real readiness"] = (
    (
        "Contrast the two states by their source: running comes from the process lifecycle, healthy from the healthcheck command passing on its interval.",
        "The fixture marks app healthy only after a python urllib request to /healthz succeeds, which requires the server to be listening.",
        "Reporting running as ready fails during startup, because the container is running from the first instant, before the socket is bound.",
        "Watch docker compose ps right after up without --wait: the status shows starting first and then healthy.",
    ),
    (
        "Find where the check command runs: CMD in the healthcheck executes inside the app container, so 127.0.0.1 is that container's loopback.",
        "The probe targets 127.0.0.1:8080 directly, never the host mapping on 18080, so a healthy result says nothing about host publication.",
        "Changing the probe to port 18080 makes the check fail permanently, since that port exists only on the host.",
        "Health stays healthy while the host request is tested separately with curl to 127.0.0.1:18080.",
    ),
    (
        "Check what the counter app needs to serve: a listener, and readable /data state. Probe both without writing anything.",
        "A GET that calls read_counter proves the volume is mounted and valid; it changes nothing and needs no internet.",
        "Using POST /increment as the probe proves writes work but adds 1 to the learner's counter every five seconds.",
        "Over a minute of healthy status, GET /counter returns an unchanged value, showing the probe is non-destructive.",
    ),
    (
        "Trace both paths: the healthcheck runs inside the container, while the browser goes through the host port mapping.",
        "A wrong or missing ports: entry breaks only the host path, so healthy and unreachable can be true at once.",
        "Removing or loosening the healthcheck because the browser fails throws away a correct signal and leaves the mapping broken.",
        "docker compose port app 8080 shows the wrong or missing mapping while health stays healthy; fixing the ports line restores the browser.",
    ),
    (
        "Separate startup from runtime: condition: service_healthy gates only when client starts, not what happens to app afterward.",
        "Once client is running, Compose does not stop it if app later fails. The client's own timeout=3 call is what bounds a failure.",
        "Expecting depends_on to restart or pause client when app crashes leaves no error handling for the real failure.",
        "Stop app while a long-lived client is running; the client sees connection errors that only its own retry or timeout logic can handle.",
    ),
    (
        "Write two lists: the health assertion checks /healthz returns ready quickly, and acceptance checks GET / text, POST /increment and persistence across recreation.",
        "Health runs every 5s with a 3s timeout, so it must stay cheap. Acceptance runs once per change and can cover more behavior.",
        "Putting the full acceptance flow into the healthcheck makes it slow and write-heavy, and may mark a working app unhealthy.",
        "Acceptance passes only when the message, the counter increment and the post-recreation value all match their contracts.",
    ),
)

REASONING["Named volumes, bind mounts and persistence experiments"] = (
    (
        "Look for the volume line study-data:/data and check that the recreated container mounts the same named volume.",
        "Recreation replaces the container and its writable layer, but study-data is a separate object, so counter.json survives.",
        "Assuming any recreate keeps data fails when the project name changes, because Compose then creates a new prefixed volume.",
        "Read GET /counter before and after worked example 2; the value is unchanged and the container ID differs.",
    ),
    (
        "Compare where the bytes live: a named volume is managed by the engine, and a bind mount is a host path you choose.",
        "A bind mount exposes the exact host directory and its permissions to the container, while a named volume avoids depending on host layout.",
        "Bind-mounting a home directory to share a single file gives the container write access to everything else in it.",
        "docker volume inspect shows an engine-managed Mountpoint for study-data, while a bind mount's Source in docker inspect is the host path you chose.",
    ),
    (
        "Record the counter before, the old container ID, the volume name, the new container ID and the counter after.",
        "Matching counter values alone could be coincidence; adding both IDs and the volume name ties persistence to the replacement.",
        "Recording only the after value of 3 cannot exclude a fresh volume seeded or incremented to the same number.",
        "The table shows two different container IDs, one unchanged volume name and a counter that continues from its previous value.",
    ),
    (
        "Notice that mounting any source at /app places a different filesystem over the image directory holding server.py.",
        "A bind mount hides image content at the mount point; it does not merge or copy files, so python finds no server.py.",
        "Rebuilding the image to restore the file fails, because the mount still hides whatever the image places at /app.",
        "Remove the mount or point it elsewhere, then python -c printing Path('/app/server.py').is_file() reports True again.",
    ),
    (
        "Check volume names: Compose prefixes study-data with the project name, so a new -p value refers to a different volume.",
        "The old volume and counter still exist under the old name. The new project simply started with an empty volume.",
        "Deleting volumes that look unused in a panic can destroy the real progress that was never lost.",
        "docker volume ls lists both prefixed volumes; switching back to the original project shows the old counter again.",
    ),
    (
        "Use down without -v for routine stops, and require an explicit reset step with a backup before docker volume rm.",
        "Learner progress outlives containers. Separating stop from reset ensures that only a deliberate action deletes it.",
        "Putting docker compose down -v into a convenience script turns every stop into an irreversible reset.",
        "After a routine stop and start, GET /counter returns the earlier value; only the documented reset path sets it to 0.",
    ),
)

REASONING["First capstone: build, serve, replace and explain"] = (
    (
        "Read compose.yaml for each object it implies: the image ds60-docker-study:local, an app container, a default project network and the study-data volume.",
        "The client service has profiles: [tools], so a plain up does not create it. The other four objects come from the model.",
        "Listing the client container among the resources fails, because profile-gated services start only with --profile tools or an explicit run.",
        "After up, docker compose ps -a shows only app, while docker network ls and docker volume ls show the project's network and volume.",
    ),
    (
        "Edit APP_MESSAGE in your copy of compose.yaml, run up -d --wait, and leave server.py and the image untouched.",
        "server.py reads the variable at request time, and Compose recreates the container for the new environment, so the response changes without a rebuild.",
        "Editing the default string inside server.py also changes the output, but it mixes a code change into what should test configuration.",
        "The image ID is the same before and after, while GET / returns the new message.",
    ),
    (
        "Assemble the build log, config --quiet exit status, the health state from ps, and the exact JSON body from GET /.",
        "Each piece covers a stage: model, packaging, process readiness and application output. Together they rule out a stale image or browser cache.",
        "Submitting only a browser screenshot cannot show whether the build ran or whether the page came from cache.",
        "Every item carries a timestamp from the same session, and the JSON message matches the value in compose.yaml.",
    ),
    (
        'Change only the container port in a scratch copy, for example "127.0.0.1:18080:8081", predict the failing hop, then restore it.',
        "The host listener still exists, but traffic goes to container port 8081, where nothing listens, so health stays green while host requests fail.",
        "Changing the host port, the listener and the healthcheck together leaves no clear cause and no clean regression case.",
        "The broken copy fails at the host request while health passes; restoring the original line makes the request return the JSON again.",
    ),
    (
        "Increment the counter, note the value and container ID, run up --force-recreate --wait app, then note both again.",
        "The invariant requires a new container ID, the same study-data volume and an unchanged counter. All three are needed.",
        "Rebuilding the image or refreshing the browser does not replace the container, so the test passes without testing persistence.",
        "ps -q app prints different IDs and GET /counter returns the value recorded before the recreate.",
    ),
    (
        "Write a fresh-copy procedure: prerequisites, copying the fixture, the commands from worked examples 1 and 2, expected observations, and the down step.",
        "The `python:3.12-slim` base is the only download, and pull_policy: never shows that the local tag must be built first.",
        "Writing up -d without the build step works on the author's laptop only because the tag already exists there.",
        "Follow the procedure on a machine or engine without the local tag; it completes and ends with down leaving only the volume.",
    ),
)

REASONING["BuildKit, cache mounts and build secrets"] = (
    (
        "Compare the two RUN --mount types from the worked examples: type=cache at /root/.cache/pip and type=secret with id=demo at /run/secrets/demo.",
        "The cache directory persists between builds to save downloads, while the secret file exists only during its RUN step. Neither becomes part of an image layer.",
        "Using a cache mount to hold a token because it also stays out of layers fails, since the cache persists and later builds can read it.",
        "docker history lists no layer holding /root/.cache/pip or /run/secrets/demo, and a later unrelated RUN cannot list /run/secrets.",
    ),
    (
        "Read required=true on the secret mount and predict that BuildKit stops at that RUN when no secret with id demo is supplied.",
        "The test -s check never runs without the file, so the build fails loudly instead of continuing with an empty or borrowed credential.",
        "Dropping required=true so the build passes everywhere makes a missing secret look like success, and a later fetch fails with a misleading error.",
        "Build without `--secret id=demo` and note the failure at that step; rebuild with `--secret id=demo,src=` pointing at a synthetic file and the step passes.",
    ),
    (
        "Run the build with --no-cache, and also with the cache mount emptied, while keeping requirements.lock and its hashes unchanged.",
        "--require-hashes forces pip to fetch the exact locked wheels again, so a cold build proves the lock alone describes every dependency.",
        "Testing only warm rebuilds can hide a wheel that exists only in the local cache and is no longer published.",
        "The cold build log shows pip downloading every locked package and completing, and the image matches the warm build's package list.",
    ),
    (
        "Read the RUN command itself: a line such as cat /run/secrets/demo > /app/token writes the secret into the step's filesystem snapshot.",
        "The mount keeps the secret file out of the layer, but anything the command copies or prints is captured as normal output.",
        "Concluding that type=secret guarantees secrecy, and skipping review, leaves the leaked copy in the layer and possibly in the build log.",
        "List the image's files and search the build log for the synthetic secret value; the leak appears in /app/token until the command is fixed.",
    ),
    (
        "Trace where an ARG value goes: it is available to RUN steps and can be recorded in image history and build provenance.",
        "docker history can display commands that used ARG values, so a password passed with --build-arg can be read back from the image.",
        "Passing the password as ARG and unsetting it in a later RUN still leaves the earlier history and metadata intact.",
        "Build with a synthetic --build-arg value and check docker history; then switch to a secret mount and confirm the value no longer appears.",
    ),
    (
        "Write a policy that names the lockfile, the package index, when network access is allowed, and which credentials, if any, a build may use.",
        "Hash-locked inputs make a fetch verifiable, and stating when the network is used lets a learner tell first acquisition from an offline rebuild.",
        "Letting builds inherit whatever registry login exists on the host makes results depend on who ran them.",
        "Run the documented acquisition once, then rebuild with networking disabled for RUN steps and the cache warm; it succeeds without new fetches.",
    ),
)

REASONING["Multi-stage builds and runtime dependency boundaries"] = (
    (
        "Follow --from=build back to the stage declared `FROM python:3.12-slim AS build`, and its file /out/message.txt written by the RUN.",
        "COPY --from reads from that stage's finished filesystem, not from the host, so the final stage needs nothing from the developer's directory.",
        "Creating out/message.txt on the host first to help the copy changes nothing, because COPY --from never looks at the context.",
        "Build the example and run the final image; it prints prepared, which can only come from the build stage.",
    ),
    (
        "Ask what the final executable needs to start: its dynamic loader and every shared library it links, all present in the final stage.",
        "Builder tests run in the builder filesystem, where those libraries exist. The final stage holds only what COPY --from placed there.",
        "Trusting the builder's passing tests and shipping fails at container start with a missing library error before main runs.",
        "Run the final image directly; a missing library shows up at once, and running ldd in a debug copy of the final stage lists what is absent.",
    ),
    (
        "List each artifact the final stage needs by path: the executable or package, certificates if it makes TLS calls, and config defaults it reads.",
        "An explicit list keeps the final stage reviewable and makes each COPY --from line match one runtime requirement.",
        "Copying the whole /out or the builder's /usr tree ships compilers and test files.",
        "The final image's file listing matches the artifact list, and the acceptance request passes with nothing more added.",
    ),
    (
        "Check which target the release build selected with --target, and inspect the resulting image's files and command.",
        "Without --target the last stage is built; with --target debug a debug stage is built. Either way the content shows what shipped.",
        "Reading the Dockerfile and assuming the release stage was used fails when a CI script still passes --target debug.",
        "The CI command line names the intended target, and the image lacks debug tools when listed.",
    ),
    (
        "Separate the size metric from the risks that matter: which binaries can run, what user runs them, and whether dependencies receive patches.",
        "A small image running as root with an unpatched library is smaller but no safer. Size cuts attack surface only when removed parts were risky.",
        "Choosing the smallest base regardless of its update cadence can leave known vulnerabilities in place longer.",
        "Compare candidates on size, configured user, and scanner findings for the same date, and record all three.",
    ),
    (
        "Run the exact final image with the user, read-only root, mounts and network it will have in use, then send the acceptance request.",
        "Final-stage problems such as missing files, wrong ownership or a missing library show up only in that configuration.",
        "Accepting the release because the builder stage tests passed checks a filesystem that will never ship.",
        "Record the image ID used in the acceptance run and deploy that same ID, not a rebuilt tag.",
    ),
)

REASONING["CPU architectures, image indexes and cross-platform builds"] = (
    (
        "Read a platform string as two parts: linux/amd64 and linux/arm64 share an OS but differ in instruction set.",
        "Worked example 1 builds the same Dockerfile for linux/arm64, and inspection reports Os linux and Architecture arm64 on any host.",
        "Writing runs on Linux in a release note leaves arm64 users to discover that only amd64 was built.",
        "The image inspect template in worked example 1 prints both fields; a release note should name both.",
    ),
    (
        "Classify by what runs where: a cross-compiler is a native program that outputs target code, and emulation such as QEMU runs target code on another CPU.",
        "Cross-compiling never executes the output, while emulation does, but slowly and with emulator quirks.",
        "Calling an emulated run on amd64 native arm64 qualification ignores timing and behavior differences.",
        "Label each matrix cell with built, emulated or native, and keep native arm64 performance claims for an arm64 host.",
    ),
    (
        "Make a table with rows for linux/amd64 and linux/arm64 and columns for built, executed and acceptance passed.",
        "The index in worked example 2 lists one image per platform, so each row needs its own build and run evidence.",
        "Marking arm64 as executed because the index contains an arm64 entry confuses publishing with running.",
        "Each filled cell names the host and the command used; any cell without evidence stays blank and labeled unqualified.",
    ),
    (
        "Check the architecture first with docker image inspect and compare it to the host's uname -m before reading application code.",
        "exec format error comes from the kernel refusing a binary built for another architecture, before the program's first line.",
        "Raising mem_limit or editing server.py has no effect, because the process never started.",
        "Rebuild for the host's platform or enable emulation; the same command then reaches the application.",
    ),
    (
        "Look at the build driver and image store: --load imports one image into the local store, and older stores may not hold a multi-platform index.",
        "A multi-platform result is an index pointing to several images, which needs an exporter and store that can represent it.",
        "Expecting --platform linux/amd64,linux/arm64 --load to work on every engine fails on stores that keep only one platform per tag.",
        "docker buildx ls shows the driver; push to a registry or use a store that supports indexes, then inspect the index entries.",
    ),
    (
        "State the tested platform, the host used, and the acceptance result, then list other platforms as built but unqualified.",
        "The fixture uses only the standard library, so it likely ports, but native dependencies elsewhere can break per architecture.",
        "Writing works everywhere from one amd64 run makes a claim nobody has observed.",
        "Each platform named as supported has a matching row of execution evidence.",
    ),
)

REASONING["Bridge networks, service DNS and container-to-container traffic"] = (
    (
        "Read the client's command in compose.yaml: it requests `http://app:8080/` using the service name.",
        "Compose registers app on the project network's DNS, which resolves to whatever container serves app now.",
        "Hardcoding the IP from docker inspect works until the container is recreated and receives a new address.",
        "Worked example 1 prints the app's greeting from inside client without any IP in the model.",
    ),
    (
        "Ask whose loopback 127.0.0.1 means: for the client container, it is the client's own namespace.",
        "Nothing listens on 18080 or 8080 inside client, so a request to its loopback fails even with app healthy.",
        "Pointing client at http://127.0.0.1:18080/ because it works in the browser produces connection refused.",
        "Run the client command with the loopback URL and observe refusal, then with `app:8080` and observe the greeting.",
    ),
    (
        "Draw four steps: resolve app via project DNS, open TCP to that address on 8080, send GET /, read the JSON body.",
        "Each step fails differently: name not found, connection refused or timeout, HTTP error, or a wrong body.",
        "Lumping every failure into network broken skips the step-specific check that would shorten diagnosis.",
        "Inside a peer, python socket.gethostbyname('app') returns an address, and the request then returns the body.",
    ),
    (
        "Separate the two facts: a resolved name proves DNS works; refused means nothing accepted on that address and port.",
        "Likely causes are app stopped, app listening on loopback only, or the wrong port. DNS settings are not among them.",
        "Editing DNS settings or adding hosts entries changes the part that already succeeded.",
        "Check docker compose ps for app, then the listener address, then the port in the client URL; one shows the mismatch.",
    ),
    (
        "Separate new connections from existing ones: after recreation, a fresh lookup of app returns the new container's address.",
        "An established connection pointed at the old container breaks when it is removed; a new connection reaches the replacement.",
        "Retrying every failed request blindly can repeat a non-idempotent POST /increment.",
        "Run client after recreating app; it succeeds without changes because it resolves app again.",
    ),
    (
        "Give the database service no ports entry and have the app connect to it by service name and container port on the shared network.",
        "The app needs only a network path. Leaving out a host mapping removes an exposure without affecting the app.",
        "Publishing the database on the host just in case lets any local process, or a remote one if bound widely, reach it.",
        "docker compose ps shows no published port for the database, and the app's queries still succeed.",
    ),
)

REASONING["Network isolation, gateways and outbound connectivity"] = (
    (
        "Separate two settings in the YAML: networks lists which project networks a service joins; ports maps a host socket to the container.",
        "In worked example 1, database joins only backend and has no ports, so api reaches it while the host cannot.",
        "Adding ports to database so api can connect is unnecessary, since they already share backend, and it opens a host path.",
        "docker compose config shows networks for each service and no ports on database; api can still connect to it.",
    ),
    (
        "Check whether the program needs anything outside the container: sum([2, 4, 6]) uses only the interpreter in the image.",
        "--network none removes all interfaces except loopback, which does not affect arithmetic, so the run prints 12.",
        "Expecting every container to fail without a network confuses connectivity with computation.",
        "Worked example 2 prints 12; a variant that calls urllib.request.urlopen on an internet URL fails under the same flag.",
    ),
    (
        "List each service with the networks it needs: api on frontend and backend, database on backend only, and backend marked internal.",
        "internal: true stops backend from routing outward, so database gets peers but no internet path.",
        "Putting every service on every network makes the diagram simpler but lets the frontend reach the database directly.",
        "From a frontend-only container, resolving database fails, while api resolves it.",
    ),
    (
        "Revert network_mode: host and return to the bridge model, then locate the real fault in address or port.",
        "Host mode removes isolation and port mapping entirely, so things seem to work while the original fault remains.",
        "Keeping host mode exposes every listener on all host interfaces.",
        "With the bridge restored and the ports line corrected, the loopback request works and nothing listens on other interfaces.",
    ),
    (
        "Ask two questions per request: can the caller reach the service, and is this caller allowed to perform this operation?",
        "Network placement answers only the first. Any process on backend could call database, including a compromised api.",
        "Skipping database credentials because only backend can reach it leaves every backend process with full access.",
        "Connect from a backend container without credentials; a properly configured service refuses the operation.",
    ),
    (
        "Prepare inputs in the image or a mounted volume, run the worker with --network none, and compare output to the expected result.",
        "If the run succeeds with no network, everything it used was local. That proves this input path only.",
        "Disconnecting once and declaring the worker offline-ready misses code paths, such as an update check, that the test never exercised.",
        "Record which inputs were tested and that each finished under --network none.",
    ),
)

REASONING["Users, UID ownership and writable data paths"] = (
    (
        "Compare numeric IDs, not names: the fixture runs as 10001:10001, while a host user named app might be 1000.",
        "The kernel checks numeric UIDs against owners and mode bits. Matching names on two systems can map to different numbers.",
        "Creating a host user with the same name and expecting access fails when the numbers differ.",
        "Worked example 2 prints 10001 10001; compare with ls -n on the mount source, which shows numeric owners.",
    ),
    (
        "Assign each path a role: /app holds server.py from COPY and stays read-only; /data is the chown'd directory for state.",
        "server.py writes only to /data, and read_only: true in compose keeps /app and everything else from changing.",
        "Dropping read_only so the app can write anywhere hides a mistake that would write state into the wrong path.",
        "In the running fixture, a write to /data succeeds and a write to /app fails with a read-only error.",
    ),
    (
        "Follow the fixture's order: RUN mkdir -p /data, chown 10001:10001 /data, then USER 10001:10001 before CMD.",
        "Ownership is set once, as root, at build time; the process then starts without needing root.",
        "Running as root and calling chown at every startup needs extra privilege and hides packaging errors.",
        "docker image inspect shows Config.User 10001:10001, and /data is listed as owned by 10001 in the image.",
    ),
    (
        "Record three facts: the mount source on the host, the UID inside the container, and the denied call with its path.",
        "A bind mount keeps the host's numeric owner, so a host directory owned by 1000 refuses writes from UID 10001.",
        "Running sudo chown -R across the checkout fixes this mount but changes ownership of unrelated developer files.",
        "ls -n on the source shows the owner; changing only that directory, or using the named volume, makes the write succeed.",
    ),
    (
        "Ask what 777 proves afterward: that anyone can write, not that UID 10001 was meant to write.",
        "The fixture's contract is that only the app's UID owns /data. Mode 777 lets any process in any container sharing the path modify the counter.",
        "Applying 777 to stop errors fixes the symptom while removing the ownership rule the lesson is testing.",
        "After a targeted fix, ls -n /data shows owner 10001 and mode without world-write.",
    ),
    (
        "Write one positive and one negative check: POST /increment updates /data, and a write to /app as the same user fails.",
        "Both are needed: the first proves the data path works, the second that code is protected.",
        "Checking only that the counter increments passes even if /app were writable.",
        "The increment returns the next value, and python -c writing /app/x reports a permission or read-only error.",
    ),
)

REASONING["Backups, restores and proving data recovery"] = (
    (
        "Separate the two events: making an archive of study-data, and starting a fresh service that reads restored data correctly.",
        "Only the second proves recovery, because it exercises read_counter's schema and type checks on the restored file.",
        "Calling the job done when the archive file exists misses a truncated or wrongly owned counter.json.",
        "Start a reader on the restored volume; GET /counter returns the expected value with schema_version 1.",
    ),
    (
        "Recall that transactional databases keep data across several files and in memory, with their own logging.",
        "A file copy taken mid-write can capture files from different moments, which the database may reject or misread.",
        "Using tar on a live database directory because it worked for counter.json ignores that the fixture writes one file atomically.",
        "Use the database's own dump or backup command, then restore it into a new instance and query it.",
    ),
    (
        "Create a new volume with a distinct name, restore the archive into it, and mount it in a separate container.",
        "The source volume stays intact, so if the restore is bad the original is still the working state.",
        "Restoring over the live study-data volume to test risks destroying the only good copy.",
        "docker volume ls shows both volumes, and the source's counter is unchanged after the test.",
    ),
    (
        "Separate byte integrity from meaning: a matching checksum shows the archive equals the source, not that the source was valid.",
        "If counter.json already held a negative counter, the copy matches and read_counter still raises on start.",
        "Trusting the checksum and skipping startup lets an invalid file pass every backup check.",
        "Start the reader on the restored volume; validation either succeeds or reports the invalid counter state.",
    ),
    (
        "Define RPO as how many increments may be lost (backup interval) and RTO as how long from failure to a working /counter.",
        "With a backup taken after counter 7 and two more increments before failure, the restored value is 7 and two updates are lost.",
        "Quoting a local RTO of seconds as a production guarantee ignores larger data and different storage.",
        "Time the restore from start to a successful GET /counter and record the counter gap together with the workload.",
    ),
    (
        "Record the source volume name, the archive hash, the restore volume name, the counter value read back and the cleanup commands run.",
        "The hash ties the archive to the source; the parsed value proves use; the cleanup entry shows only disposable resources were removed.",
        "Deleting the restore volume before review leaves nothing to check if someone questions the result.",
        "A reviewer can match each field and see that only the restore volume was removed after sign-off.",
    ),
)

REASONING["Resource limits, contention and honest performance experiments"] = (
    (
        "Read cpus: 0.5 as a scheduler quota: the app may use up to half a CPU's worth of time per period, spread across whatever cores run it.",
        "The kernel still shares those cores with other containers and host processes, so the quota caps usage without reserving hardware.",
        "Advertising the fixture as having half a dedicated core promises isolation that the quota never provides.",
        "Run a busy loop under cpus 0.5 next to another busy container; both slow, and docker stats shows the capped share rather than a reserved core.",
    ),
    (
        "Add up the configured limits, such as 128m for app and 64m for client, and compare the total with the memory given to the engine's VM.",
        "A limit is a ceiling the engine enforces inside its own allocation; it cannot create memory the VM was never given.",
        "Raising mem_limit on each service when several containers crash together ignores that the VM itself is exhausted.",
        "Check the VM's memory in the engine settings or docker info; once it covers the sum plus overhead, the shared failures stop.",
    ),
    (
        "Keep the image, input and cache state fixed, change only cpus, and repeat each timed run several times with a timeout.",
        "One changed variable lets a difference in timing be attributed to the limit and not to a cold cache or a new image.",
        "Comparing one run at cpus 0.5 on a laptop with one run at cpus 2 on another machine mixes architecture and host load into the result.",
        "The record lists the image ID, platform, cache state and every repeated timing, so someone else can rerun the same comparison.",
    ),
    (
        "Collect several observations before changing anything: CPU throttling, disk I/O, request rate and memory near the 128m ceiling.",
        "Slowness can come from CPU quota, blocking file writes to /data or extra traffic. Memory is just one candidate among them.",
        "Doubling mem_limit at the first slow request leaves a CPU-bound or I/O-bound cause untouched.",
        "The first observation that departs from normal, such as high throttled time, points to the setting worth changing next.",
    ),
    (
        "Treat the --no-stream output as one snapshot taken at the moment the command ran.",
        "A short spike between snapshots, or a peak an hour ago, does not appear in it, so it cannot describe the whole workload.",
        "Concluding that memory is fine from one quiet sample misses the spike that triggered the reported failure.",
        "Collect a bounded series at a fixed interval during the workload, alongside application timings, and compare peaks with the limits.",
    ),
    (
        "Choose a small fixed workload against a container you own, wrap it in a timeout, and name the condition that ends the test.",
        "The goal is to see one mechanism, such as throttling under the 0.5 quota, which a short bounded load already shows.",
        "Running an unbounded fork bomb to find the limit risks the whole host; pids_limit 64 helps but is not a reason to try.",
        "The test stops at its timeout or named condition, and docker compose ps shows only the owned container affected.",
    ),
)

REASONING["Read-only filesystems, capabilities and least privilege"] = (
    (
        "Match each line to its target: read_only to the root mount, cap_drop to kernel capabilities, no-new-privileges to setuid gains and tmpfs to /tmp scratch space.",
        "Each one blocks a different kind of operation, so knowing the mapping tells you which rule refused a given call.",
        "Treating all four as general hardening and removing them together to fix one error hides which boundary was involved.",
        "Trigger one forbidden action at a time, such as writing /app or changing a file owner, and note which setting the error points to.",
    ),
    (
        "Look at the mount table: the root is read-only, while study-data is a separate named volume mounted read-write at /data.",
        "read_only applies to the container's root filesystem; a volume brings its own mount options, so writes to /data still work.",
        "Expecting read_only: true to protect the counter from changes assumes it covers every mount.",
        "POST /increment succeeds and changes counter.json, while a write to /app as the same process fails.",
    ),
    (
        "Pair a required action, GET /healthz returning ready with the counter persisting, with a forbidden one, writing /app/unexpected.txt.",
        "The pair rules out two different errors: a broken app that refuses everything and an open app that allows everything.",
        "Testing only that /app is not writable passes for a container that cannot serve any request.",
        "Run both checks against the hardened compose file; the first succeeds and the second reports a read-only error.",
    ),
    (
        "Find the exact path from the error, then ask whether the cache must survive restarts, can live in memory, or can be disabled.",
        "A temporary cache fits a small tmpfs like /tmp; a durable one needs a named volume; neither needs the root to become writable.",
        "Setting read_only: false makes the error disappear and also removes protection for /app and every other path.",
        "After adding only the chosen mount, the app starts, and a write to /app still fails.",
    ),
    (
        "List what privileged: true grants, including all capabilities, host devices and relaxed confinement, and compare it with what server.py does.",
        "The server only listens on 8080 and writes /data, so none of those grants serve the fixture.",
        "Using privileged mode to get past a permission error trades a narrow fix for broad host access.",
        "The fixture passes its acceptance pair with cap_drop ALL, which shows no capability is needed.",
    ),
    (
        "Describe the configuration as tested: the four settings above, checks that passed, and the assumption that the code is trusted and local.",
        "The settings reduce what the process can do; they do not make the container a sandbox for hostile code.",
        "Calling the result fully secure invites running untrusted images under a configuration never tested for that.",
        "The review lists each control with its passing check and names the threats left out of scope.",
    ),
)

REASONING["Rootless engines, user namespaces and host trust"] = (
    (
        "Place each setting at its layer: rootless mode is how the daemon runs on the host; USER 10001:10001 is who server.py runs as inside one container.",
        "The Dockerfile cannot change how the engine was installed, and a rootless daemon still runs whatever USER the image sets.",
        "Claiming the fixture is rootless because of its USER line confuses the process identity with the engine's privilege.",
        "docker info lists rootless among its security options only when the daemon runs that way, regardless of image USER.",
    ),
    (
        "Expect differences where rootless engines rely on user-level helpers: binding ports below 1024 and applying cgroup limits like cpus.",
        "Without host root, networking runs through a user-mode helper and cgroup limits depend on delegation set up by the host.",
        "Copying a rootful setup and assuming 127.0.0.1:18080 and mem_limit behave identically skips the check that matters.",
        "Run the fixture on the rootless engine and confirm the port answers and docker stats reflects the limits.",
    ),
    (
        "Draw the chain from the mounted socket to the engine API to any new container the API can start, including one mounting the host root.",
        "The socket accepts API calls; a :ro flag on the socket's mount does not limit those calls.",
        "Approving the socket mount because it is marked read-only gives the container control of the engine.",
        "Confirm compose.yaml has no docker.sock mount; a review search for that path should find nothing.",
    ),
    (
        "Recognize that a browser lesson asking for docker commands would route arbitrary learner code to engine control.",
        "The classroom API runs only declared lesson runtimes; giving lessons the engine would cross that boundary.",
        "Mounting the socket into the lesson runtime to make the exercise work exposes the host to any code a learner types.",
        "Move the steps to a host worksheet the learner runs themselves; the classroom configuration still has no engine path.",
    ),
    (
        "Read the mapping as a shift: container UID 10001 corresponds to a host UID inside a configured subordinate range, not to host UID 10001.",
        "Files the app creates appear on the host under the mapped number, so ownership checks must apply the offset.",
        "Matching a host user named app to the container's app user by name ignores both the name lookup and the range shift.",
        "Create a file from the container and list it with ls -n on the host; the owner is the mapped number.",
    ),
    (
        "Record what actually ran on the new setup: the build, the healthy app, the peer request, a volume write and scoped cleanup.",
        "Rootless limits show up in practice, so passing runs are what support the setup, not the documentation's feature list.",
        "Announcing rootless support because the engine's docs list it skips the networking and storage checks that may fail.",
        "Each claim in the support note links to one observed result on that host and engine version.",
    ),
)

REASONING["Image names, digests and an offline transfer"] = (
    (
        "Treat ds60-docker-study:local as a label that points to an image, and the image ID or digest as the content's identity.",
        "A rebuild can move the label to new content, while a digest always names the same content.",
        "Recording only the tag in test evidence lets a later rebuild silently replace what was tested.",
        "docker image inspect before and after a changed rebuild shows the same tag with a different ID.",
    ),
    (
        "Trace what the build does with the tag: it names the result in the local store and talks to no registry.",
        "Uploading needs a separate docker push to a registry reference, which the course never runs.",
        "Worrying that tagging the fixture published it confuses naming with distribution.",
        "No registry login is needed to build, and the image is listed only in the local docker image ls output.",
    ),
    (
        "Send study-image.tar with its checksum, the image ID, its platform and the exact command the receiver should run.",
        "The checksum confirms the bytes arrived intact; the ID and platform confirm which program and architecture they hold.",
        "Sending only the archive file name leaves the receiver unable to tell an older or wrong-platform archive from the right one.",
        "The receiver recomputes the checksum, loads the archive, and compares the image ID and architecture with the record.",
    ),
    (
        "Read --pull never as a rule: if the image is not already local, the run stops instead of fetching it.",
        "The failure reveals that the load step was skipped or used a different tag, which is the fact the handoff needs.",
        "Removing --pull never to make the run work quietly downloads an image and hides the incomplete preparation.",
        "Load study-image.tar, confirm docker image ls lists ds60-docker-study:local, and rerun to see offline ready.",
    ),
    (
        "Separate two questions: did the bytes change in transit, and who produced them?",
        "A matching hash answers only the first; anyone who swaps the archive can publish a matching hash beside it.",
        "Trusting an archive because its hash matches the one in the same download folder accepts an attacker's pair.",
        "Get the expected hash through a separate trusted channel, or check a signature against a known key.",
    ),
    (
        "Start the loaded image under --network none with the study data and run the app's own checks, not just a print command.",
        "The print command proves the interpreter is present; GET /healthz and GET /counter prove the app starts and reads its data.",
        "Accepting the transfer after offline ready alone says nothing about whether server.py runs without the network.",
        "In the offline container, the health and counter routes respond over loopback with the expected JSON.",
    ),
)

REASONING["Compose overrides, profiles and configuration review"] = (
    (
        "Ask two separate questions: which services run (profiles), and what each service's settings are (the ordered -f files).",
        "The tools profile only adds client to the selection; compose.study.yaml changes fields of services that already exist.",
        "Putting a changed APP_MESSAGE in a profile expecting it to alter app misreads profiles as a way to set fields.",
        "docker compose config with and without --profile tools shows client appearing, while only the override changes app's fields.",
    ),
    (
        "Read profiles: [tools] on client and note that ordinary up does not start profiled services.",
        "Plain up starts app only, so nothing needs to be stopped to remove the client afterward.",
        "Expecting client to start with up and finding it missing does not indicate a broken model.",
        "After up --wait, docker compose ps lists app only; the explicit run in worked example 1 still runs client once.",
    ),
    (
        "Write an override containing only services, app, environment and APP_MESSAGE, and compare the merged config with the base.",
        "With a single changed field, any other difference in the merged output would show a mistake in the override.",
        "Changing the message while also adding a mount and dropping read_only makes it unclear which edit caused a later failure.",
        "The merged config differs from the base in APP_MESSAGE only, and GET / returns the new message.",
    ),
    (
        "Print the full merged ports list from config and compare it with each file's ports, in the order the -f flags were given.",
        "Compose combines some lists, such as ports, rather than replacing them, so a later file can add a mapping.",
        "Assuming the override's ports replaced the base's leads you to remove the wrong line.",
        "The config output shows which file contributed the extra mapping, and removing it restores 127.0.0.1:18080 only.",
    ),
    (
        "Ask who can run docker compose for this project: anyone who can reach the engine can pass --profile tools.",
        "A profile changes default selection for convenience; it checks no identity and grants or denies nothing.",
        "Hiding an admin service behind a profile as protection leaves it one flag away for any engine user.",
        "A different user with engine access runs --profile tools and starts the service with no extra check.",
    ),
    (
        "Write down the project name, the -f files in order, the profiles enabled, and the resolved settings with private values removed.",
        "Order matters because later files override earlier ones; without it, someone else gets a different effective model.",
        "Pasting the full config output, including resolved secrets, into the launch record exposes them.",
        "Another person reruns config with the recorded flags and gets the same output apart from the redacted values.",
    ),
)

REASONING["Intermediate capstone: a recoverable two-tier teaching system"] = (
    (
        "List each resource and ask whether recreating it loses anything: study-data and the backup files hold state, while app, client and the network are rebuilt.",
        "server.py keeps its counter only in /data and the root is read-only, so the writable layer holds nothing worth recovering.",
        "Describing a container restart as preserving data because the container kept its name confuses the container with the volume.",
        "Run down without -v and up again; the counter remains, while the container ID and network ID change.",
    ),
    (
        "In a scratch copy, change only the client's URL from `app:8080` to another port and run the client once.",
        "Nothing listens on the new port, so the request fails within its 3 second timeout while app stays healthy.",
        "Also editing the app's ports and network to see what happens loses track of which change caused the failure.",
        "docker compose ps still shows app healthy, and the client error names the port it tried.",
    ),
    (
        "Export counter.json from study-data, restore it into a new volume, and start a reader on that volume.",
        "Reading GET /counter through server.py runs read_counter's checks, proving the restored data is usable.",
        "Checking only that the restored file exists skips parsing and would pass a truncated or invalid file.",
        "The reader returns the same counter as the export, and the source volume's counter is unchanged.",
    ),
    (
        "Compare the two paths: the host uses `127.0.0.1:18080` through a port mapping, the client uses `app:8080` through project DNS.",
        "Since the host request works, the app is serving; the fault is in the client's name, network or port.",
        "Restarting the app because something is down ignores the passing host request.",
        "Check that client joins the project network, resolves app, and targets 8080; one of these shows the mismatch.",
    ),
    (
        "List what the lab does not cover: other hosts, failover, replicated storage, and consistency for real databases.",
        "One engine with one volume teaches the mechanics without claiming a production-grade guarantee.",
        "Presenting the capstone as a highly available design invites someone to rely on it for production.",
        "The handoff names these limits next to the parts that were tested.",
    ),
    (
        "Write the handoff in operating order: prerequisites, start, health evidence, common failures, backup and restore, and scoped cleanup.",
        "A reader with only the listed prerequisites can follow it, and it names which volumes keep state after cleanup.",
        "Writing steps that rely on your shell history or already-built images fails for the next operator.",
        "Someone new follows the handoff on a clean engine and reaches the same health and restore results.",
    ),
)

REASONING["Registries, tags, digests and deliberate publication"] = (
    (
        "Split a reference into registry host, repository path, optional tag after a colon and optional digest after @sha256.",
        "A short name like ds60-docker-study:local has no registry part, and the client fills in a default when talking to one.",
        "Pushing a short name assuming it goes to your own registry may target the default public registry.",
        "Write out the fully qualified reference before any push and compare it with the intended destination.",
    ),
    (
        "Trace docker tag: it adds another name for the same image ID in the local store.",
        "No network call happens; publishing needs a separate docker push, with credentials, to a registry.",
        "Avoiding tags out of worry about publishing loses a useful way to name a candidate for inspection.",
        "The image inspect command in worked example 1 shows the new name, and the registry has no copy until a push.",
    ),
    (
        "Fill each field from a separate source: the revision from version control, the digest from the registry, the platform from inspect and acceptance from a test receipt.",
        "Linking these fields shows which source produced which image and that this image passed which test.",
        "Recording only a release tag cannot tie evidence to content once the tag moves.",
        "Each field in the JSON record can be checked independently, and placeholder values mark it unqualified.",
    ),
    (
        "Resolve the tag's current digest and compare it with the one recorded at acceptance.",
        "If they differ, the tag now names other content and the earlier test results do not apply to it.",
        "Trusting the tag because the name matches applies evidence to an image that was never tested.",
        "Deploy by the recorded digest; it pulls the accepted content regardless of where the tag points now.",
    ),
    (
        "Keep registry credentials in the client's credential store or a secret mount, never in files under the build context.",
        "Files in the context are sent to the builder and can be copied into layers or printed in logs.",
        "Relying on .dockerignore alone fails if a COPY . line or a renamed file slips past the pattern.",
        "Search the context and the image's files for credential files; none appear, and pushes still authenticate.",
    ),
    (
        "Write the proposal with the full registry destination, visibility, the digest to push and how to revert.",
        "Naming the digest ensures what is published equals what was reviewed, not whatever the tag points to later.",
        "Approving publish the latest build lets a different image ship than the one reviewed.",
        "A reviewer can match the digest in the proposal with the accepted record before any push is approved.",
    ),
)

REASONING["Software bills of materials and image provenance"] = (
    (
        "Ask what each document answers: the SBOM lists the packages inside the image, while provenance describes the inputs and builder that produced it.",
        "The sbom.spdx.json from worked example 1 names Python and OS packages but says nothing about which machine ran the build.",
        "Treating a complete SBOM as proof of a trustworthy build skips the separate question of origin.",
        "Look for builder and source fields in sbom.spdx.json; they are absent, which is why a provenance statement is needed too.",
    ),
    (
        "Compare what the Dockerfile names, `python:3.12-slim` and `server.py`, with what the exported image filesystem actually contains.",
        "The base tag resolves to many OS and Python packages at specific versions that appear nowhere in the source.",
        "Building the inventory by reading the Dockerfile lists two items and misses the inherited packages a scanner needs.",
        "The package list in sbom.spdx.json includes OS packages absent from the source files, as worked example 1 notes.",
    ),
    (
        "Make one row per record, acceptance, SBOM and provenance, with columns for image digest and platform.",
        "If every row names the same digest and platform, the documents describe one artifact; any mismatch shows drift.",
        "Linking records by the tag ds60-docker-study:local lets a rebuild silently change which image each record describes.",
        "Compare the digest column; every row matches, or the mismatched row is flagged before release.",
    ),
    (
        "Treat the unsigned statement as a claim: check who issued it and whether a signature verifies against a key your policy trusts.",
        "Anyone can write JSON with builder and source fields, so the fields alone show only that someone wrote them.",
        "Accepting the provenance because its fields look complete trusts an unknown author.",
        "Run the verification your policy defines; with no signature or unknown issuer, the record stays untrusted.",
    ),
    (
        "Follow where the attestation goes: the local output in worked example 1 writes sbom.spdx.json to a directory, while a docker load or registry route may keep it differently or drop it.",
        "Whether metadata survives depends on the exporter and destination, so the flag alone proves nothing downstream.",
        "Assuming --sbom=true means every copy of the image carries an SBOM fails when a later transfer loses it.",
        "Inspect the actual destination for the attestation after each hop in the route.",
    ),
    (
        "List the fixture's known source files, the resolved base digest, the SBOM file, and the acceptance checks that ran.",
        "Each item is observable, and naming what is unknown, such as the base publisher's build process, keeps the review honest.",
        "Writing that the fixture meets supply-chain requirements claims a review program that never took place.",
        "Each line in the review points to a file or command output, and the unknowns are listed in their own section.",
    ),
)

REASONING["Vulnerability findings, patching and dependency updates"] = (
    (
        "Read the synthetic finding: example-library 1.0 is installed and 1.1 is fixed, which shows a version match, not an attack path.",
        "Exploitability depends on whether the app reaches the flawed code under real inputs, which the record does not show.",
        "Ignoring the finding until someone shows an exploit leaves a known affected version waiting for triage.",
        "The triage note states whether the component is used by server.py, and the status stays requires review until decided.",
    ),
    (
        "Trace what recreation starts from: the image built from the Dockerfile, not the old container's writable layer.",
        "A package installed with docker exec lives in that layer and disappears when Compose recreates the container.",
        "Patching the running container and closing the finding leaves the next deployment unpatched.",
        "Recreate the container and check the package version; it is back to the old one until the Dockerfile changes.",
    ),
    (
        "Change only the resolved base, such as a new digest for `python:3.12-slim` passed through DS60_PYTHON_IMAGE, and rerun acceptance.",
        "With one change, a new failure points to the base and not to unrelated edits.",
        "Bumping the base, server.py and the compose file together makes a regression hard to trace.",
        "The record lists old and new base digests, and acceptance passes on the new image.",
    ),
    (
        "Find which digest the scanner examined, and compare it with what the tag resolves to now.",
        "A mutable tag may have moved since the scan, so the findings may describe other content.",
        "Using the tag's scan to close or open findings on today's image applies results to bytes the scanner never read.",
        "The scan record names a digest and database date; rescan the current digest if they differ.",
    ),
    (
        "List what the scanner checks: known identifiers matched to recognized package versions, as of its database date.",
        "Flaws in server.py, weak compose settings and unpublished vulnerabilities fall outside those rules.",
        "Reporting zero findings as the image is secure claims coverage the tool does not provide.",
        "The report names the tool, its database date and the scope, and lists configuration review as a separate check.",
    ),
    (
        "Record the finding, the affected digest, the action chosen, the tests rerun and any risk remaining.",
        "A reviewer can follow the decision and see that the new image passed the same acceptance.",
        "Writing just patched, all safe hides which image changed and what was left unresolved.",
        "Each field links to the scan output, the rebuild and a test receipt for the new digest.",
    ),
)

REASONING["CI builds, test layers and artifact promotion"] = (
    (
        "Ask where unit tests run: often on the CI host with its own Python, not inside the final image.",
        "A Dockerfile that forgets COPY server.py, or sets the wrong CMD, still passes tests that import the code from the checkout.",
        "Gating release on unit tests alone ships an image that may not start.",
        "Add a step that runs the built image and requests /healthz; it fails when the image is missing a file.",
    ),
    (
        "Separate the source archive, which developers and builders read, from the image, which an engine runs.",
        "The archive's checks cover files and formatting; the image's checks cover startup, user and runtime files.",
        "Treating a clean source ZIP as proof the image works skips the stage where packaging errors show up.",
        "Each artifact has its own receipt: archive hash and checks, image ID and startup results.",
    ),
    (
        "Group tests so that groups share no project name, volume or port, and keep tests that share state in one group.",
        "Independent groups can run together safely; groups that share study-data or port 18080 would interfere.",
        "Running every test in parallel to save time makes counter assertions fail at random.",
        "Each group's resources carry a unique project name, and repeated parallel runs give the same results.",
    ),
    (
        "Compare the image ID that passed acceptance with the one deployed after the rebuild.",
        "Unpinned base images or dependencies can change between builds, so the rebuild may differ from what was tested.",
        "Assuming the same source always gives the same image deploys untested content.",
        "Promote the tested ID directly, or run acceptance again on the rebuilt ID before deploying it.",
    ),
    (
        "After a failure, save logs and the receipt first, then remove only resources labeled with the job's project name.",
        "This keeps the evidence while freeing containers and volumes the job created.",
        "Running a broad prune after each failure deletes the evidence and can remove other projects' resources.",
        "The job's resources are gone, the logs remain in artifacts, and other projects' containers are untouched.",
    ),
    (
        "List each check that ran, the exact image ID it ran on, and the surfaces skipped, such as arm64 or other engines.",
        "Visible skips let readers see what the gate does not cover.",
        "Marking the release fully tested because the config defines many checks conflates defined with executed.",
        "The gate output shows ran, passed or skipped for each check, with the image ID.",
    ),
)

REASONING["Debugging minimal images without changing the contract"] = (
    (
        "Check whether the image provides sh or bash before reading the error as an app failure.",
        "A minimal image may ship without a shell; exec fails at lookup while server.py keeps serving.",
        "Restarting the app or adding a shell to the release image to fix the error changes the image to suit the diagnostic.",
        "The health request still succeeds while the shell exec fails, which shows the two are unrelated.",
    ),
    (
        "Use the Python interpreter that CMD already relies on to send one request with a 2 second timeout, as in worked example 1.",
        "The fixture's base already includes python, so the probe adds nothing and still observes the app's own loopback.",
        "Installing curl in the running container adds a package and fails anyway because the root is read-only.",
        "The command prints the healthz JSON and exits; nothing new appears in the image.",
    ),
    (
        "Fill three rows, host, peer and app, with the address each uses and the result it saw.",
        "Each vantage point has its own address scope, so a pattern such as only peer failing points to DNS or the network.",
        "Changing the host port mapping when only the peer request fails fixes a part that was already working.",
        "The row that differs points to one layer, and fixing that layer makes all three rows agree.",
    ),
    (
        "Write down what the live fix revealed, then make the same change in the Dockerfile or source and rebuild.",
        "Recreation starts from the image, so a live edit is lost; only the rebuilt image carries the fix.",
        "Leaving the hand-fixed container running as the release hides that the image is still broken.",
        "Recreate from the rebuilt image and confirm the symptom stays gone.",
    ),
    (
        "List what the diagnosis needs: logs, the image's files and the study-data volume, all reachable without host mounts.",
        "Mounting the host root or home directory gives the container access unrelated to the app.",
        "Bind-mounting / to look around turns a debugging session into broad host access.",
        "The diagnosis completes using logs, exec probes and the volume only.",
    ),
    (
        "Write the steps in order: save the image ID and logs, inspect state, run bounded prepared probes, then test a source fix.",
        "Saving evidence first keeps the original symptom, and prepared probes work on any learner's machine.",
        "A procedure that begins with installing your favorite tools assumes network access and changes what you inspect.",
        "Another learner follows it on a fresh copy and reaches the same diagnosis.",
    ),
)

REASONING["Restart policies, failure loops and idempotent startup"] = (
    (
        "Ask whether a restart changes the cause: an invalid required value is read again the same way on every start.",
        "Each restart repeats the error, and the first log entry is the most useful one.",
        "Adding an always-restart policy to make the service look up hides a permanent fault behind constant restarts.",
        "docker compose logs show the same error on each attempt, and fixing the value stops the loop.",
    ),
    (
        "Read where each field sits: restart under app is a container policy; restart under depends_on.app controls whether client restarts when app is updated.",
        "Same word, different blocks, different meanings, as in the worked example's YAML.",
        "Setting depends_on restart: true to make app restart after a crash edits the wrong field.",
        "docker compose config shows both fields in their blocks, and the documentation for each describes different triggers.",
    ),
    (
        "Follow read_counter: a missing counter.json means zero, nothing is written at startup, and existing files are validated.",
        "Starting twice writes nothing extra, and an invalid file raises ValueError rather than being replaced.",
        "Writing a fresh counter.json at every start would reset real counts after each restart.",
        "Restart the app several times after increments; GET /counter returns the same value.",
    ),
    (
        "Find the code that adds data at startup and check whether it looks for existing data first.",
        "An unconditional append adds a copy per start, so restarts and duplicates rise together.",
        "Lengthening the restart delay makes duplicates arrive more slowly but still arrive.",
        "After guarding the step, repeated starts leave the record count unchanged, and existing duplicates are removed by a reviewed cleanup.",
    ),
    (
        "Consider a POST /increment whose response is lost: the server may have committed the new counter before the client timed out.",
        "The client cannot tell commit from failure, so blindly retrying may increment twice.",
        "Retrying POST until one response arrives can skip a counter value.",
        "Read GET /counter before retrying, or add an operation ID so the server can recognize a repeat.",
    ),
    (
        "Test both cases: restarts with valid data preserve the counter, and restarts with an invalid counter.json fail visibly.",
        "Both outcomes matter; one shows state survives, the other that corruption is not hidden.",
        "Checking that the container shows Up says nothing about whether the counter is still right.",
        "The valid case keeps its value across restarts; the invalid case logs a ValueError and the file is left unchanged for recovery.",
    ),
)

REASONING["Application migrations and durable state versioning"] = (
    (
        "Separate lifetimes: rolling back changes the image, while study-data keeps whatever format the new code wrote.",
        "The old reader accepts only schema_version 1, so data migrated to version 2 fails to load after rollback.",
        "Planning to fix a bad migration by rolling back the image leaves the volume in a format the old code rejects.",
        "Roll back in a copy after migration and see read_counter raise on the new version.",
    ),
    (
        "Check three things first: the current schema_version, that only the migration will write during the change, and that a restored backup works.",
        "Knowing the format avoids misreading data, single-writer control avoids lost updates, and a tested backup allows recovery.",
        "Assuming every record is version 1 and starting the migration risks corrupting records in some other format.",
        "Each condition has a recorded check: the version read, the writer list, and a restore test.",
    ),
    (
        "Write a function that takes the v1 record, checks it, and returns a v2 record with the same counter and schema_version 2.",
        "Running it on copies first means mistakes affect test data only; rejecting bad input avoids guessing values.",
        "Defaulting a missing counter to 0 hides damaged data as a valid reset.",
        "Feed it the worked example's record and a malformed one; the first keeps counter 7, the second is rejected.",
    ),
    (
        "Read the stored schema_version before restarting the old reader again.",
        "If the stored version is newer than the reader supports, every restart fails the same way.",
        "Restarting repeatedly hoping it is transient repeats the failure without new information.",
        "Restore the pre-migration backup or deploy a reader that accepts both versions, as the plan specifies.",
    ),
    (
        "Read increment's sequence: write counter.next, then replace counter.json, all under a lock in one process.",
        "Replace makes readers see the old or new file whole, and the lock orders writers in that process only.",
        "Assuming atomic replace makes two app containers on the same volume safe ignores that each has its own lock.",
        "The plan states the single-writer, single-host assumption next to the atomic write claim.",
    ),
    (
        "Order the plan as preconditions, backup, migration, validation, a rollback that works with the new data, and cleanup of old compatibility.",
        "Each step can be rehearsed on a copy of study-data before touching the real volume.",
        "Treating a new image tag as the plan leaves no way to recover data.",
        "Rehearse the plan on a restored copy and record each step's result before the real run.",
    ),
)

REASONING["Image size, startup latency and measurement"] = (
    (
        "Separate the size reported by image inspect from the bytes actually downloaded when some layers are already cached.",
        "If the `python:3.12-slim` layers are already local, a new fixture build transfers only its small layers.",
        "Estimating download cost from the full reported size overstates transfer for machines with the base cached.",
        "Record which layers were present before the pull and the bytes transferred.",
    ),
    (
        "Count what a pip install at startup adds: network fetches, dependency resolution and file writes on every run.",
        "Startup now depends on a package index being reachable and serving the same versions.",
        "Installing at startup to keep the image small makes each start slower and can fail offline.",
        "Compare readiness time and offline behavior for an image with the packages built in against one installing at start.",
    ),
    (
        "Time from container create to the first healthy /healthz response, using the same image and cache state, repeated several times.",
        "Readiness is what users wait for; process start alone misses server setup.",
        "Timing only docker run returning measures container creation, not when the app can answer.",
        "The record lists image ID, cache state and each repeated timing.",
    ),
    (
        "Check whether the slimmer image dropped CA certificates or similar files that TLS clients need.",
        "Correct behavior outranks size, so a smaller image that fails HTTPS is a regression.",
        "Disabling certificate checks to make the request work trades a security control for fewer bytes.",
        "Restore the missing file, rerun the HTTPS request in the final image, and look for other reductions.",
    ),
    (
        "Run cold-cache measurements on a separate engine or VM, not after pruning the learner's shared engine.",
        "Pruning removes caches and images other projects rely on, which is damage unrelated to the experiment.",
        "Running docker system prune -a before each timing run costs everyone else their cached images.",
        "The cold run happens in a disposable environment, and the main engine's image list is unchanged.",
    ),
    (
        "Name the measured bottleneck, the one change made, the correctness recheck and the measured gain.",
        "Tying the change to a measured user delay shows why the change was worth it.",
        "Recommending the smallest possible base because smaller is faster skips the measurement.",
        "The recommendation cites before and after timings for the same event and a passing acceptance run.",
    ),
)

REASONING["Compose on one host and the limits of orchestration"] = (
    (
        "Ask what Compose can act on: containers on one engine, not a replacement host when this one fails.",
        "If the host's disk or power fails, study-data and the engine go with it, and no Compose setting brings them back elsewhere.",
        "Counting restart settings as host-loss protection confuses restarting a process with replacing a machine.",
        "The worked example's failure table shows host disk failure needing an external copy that Compose does not make.",
    ),
    (
        "Name what the classroom needs: one learner, one machine, resources the learner can list and remove.",
        "Compose gives a reproducible app with a project name that scopes every container, network and volume.",
        "Adopting a cluster scheduler for a single laptop adds setup without improving the learner's experience.",
        "A learner can see everything the project owns with docker compose ps and docker volume ls filtered by project label.",
    ),
    (
        "Write rows for process, container, engine, host and outside dependencies, with columns for detection, recovery and state kept.",
        "Filling each cell shows which failures the fixture handles, such as container replacement, and which leave blanks.",
        "Listing only failures you already handle produces a reassuring table with no gaps by design.",
        "Blank cells, such as host recovery, are named as remaining work rather than left out.",
    ),
    (
        "Ask where a Kubernetes volume claim gets storage: a storage class and provisioner must exist and meet your durability needs.",
        "A claim requests storage; the cluster decides what backs it, which may be a single node's disk.",
        "Translating study-data to a claim and assuming the data is now durable skips the storage review.",
        "Check the bound volume's storage class and test a pod reschedule that reads the counter back.",
    ),
    (
        "Separate traffic paths from data storage: a load balancer picks a healthy endpoint, but every endpoint may use the same database.",
        "If that database fails, all endpoints fail together, however requests are spread.",
        "Adding a load balancer and calling the data highly available addresses routing only.",
        "Stop the shared data store in a test and observe every endpoint failing behind the balancer.",
    ),
    (
        "Start from the workload's stated needs, availability, scale, who operates it and what learners must learn, and pick the smallest system that meets them.",
        "Each requirement maps to a mechanism, so the choice can be argued from the needs rather than from fashion.",
        "Choosing a platform first and adjusting needs to match it leaves failures and recovery undesigned.",
        "The recommendation lists each requirement with the feature that meets it and the matching failure-table row.",
    ),
)

REASONING["TLS, reverse proxies and publishing responsibly"] = (
    (
        "Separate two checks: TLS confirms the server's name and encrypts the hop; the app decides whether this caller may change the counter.",
        "An encrypted POST /increment from any client reaches the same handler, and server.py checks no identity.",
        "Treating HTTPS as access control publishes a writable counter to anyone who can connect.",
        "Send a request over TLS with no credentials; if it succeeds, authorization is still missing.",
    ),
    (
        "Compare the hostname the browser used with the names in the certificate.",
        "If they differ, the client cannot confirm it reached the intended server, so it stops before sending HTTP.",
        "Turning off verification makes the error vanish and also accepts an impostor with any certificate.",
        "Issue a certificate for the hostname clients use, or use the name on the certificate; verification then passes.",
    ),
    (
        "Draw the client-to-proxy hop and the proxy-to-app hop separately, marking where TLS ends and which component checks headers.",
        "The proxy terminates TLS, so the second hop has its own trust and timeout settings.",
        "Drawing one arrow from browser to app hides that the inner hop may be unencrypted and unauthenticated.",
        "The drawing names the certificate on hop one, the upstream address and timeout on hop two, and the header policy.",
    ),
    (
        "Read the status source: 502 is the proxy saying its upstream failed; 404 with unknown route is server.py answering.",
        "A 404 proves the request reached the handler, while a 502 means it never did or the reply failed.",
        "Republishing the app port on the host to bypass the proxy adds exposure instead of reading proxy logs.",
        "Proxy logs show the upstream error for the 502, and the app log shows the 404 route.",
    ),
    (
        "Treat X-Forwarded-For and similar headers as values a client can set unless the proxy overwrites them.",
        "Only a proxy you control that replaces the header gives the app a value worth using.",
        "Rate limiting or logging by a header the client wrote lets anyone claim another address.",
        "Send a request with a forged header through the proxy; the app sees the proxy's value, not the forged one.",
    ),
    (
        "List what public use would need: authentication, TLS, request limits, monitoring, backups and an operator.",
        "The fixture binds 127.0.0.1:18080 because it has none of these, which is acceptable only locally.",
        "Changing the bind to 0.0.0.0 and calling it published exposes an unauthenticated writable counter.",
        "The publication note marks each item as designed, tested or missing before any exposure.",
    ),
)

REASONING["Incident response, disk pressure and scoped cleanup"] = (
    (
        "Run docker system df and split the total into images, build cache, container writable layers and volumes, then check log sizes.",
        "Each type has its own owner and retention rule, so the safe removals differ per type.",
        "Deleting whatever is largest based on the total risks removing a volume that holds data.",
        "The breakdown names a category and owner for each large item before any removal is chosen.",
    ),
    (
        "Read down without -v: it stops and removes the project's containers and network but leaves named volumes.",
        "study-data survives, so a later up sees the same counter.",
        "Adding -v by habit when stopping deletes the learner's counter with the containers.",
        "After down and up, GET /counter returns the earlier value, and docker volume ls still lists the volume.",
    ),
    (
        "Before changing anything, capture the symptom, the time, the df output, the project's ps -a output and a bounded slice of logs.",
        "This preserves the state that explains the failure, so a later fix can be tied to its cause.",
        "Pruning first and checking afterward makes the disk pressure vanish along with its explanation.",
        "The packet has each item with a timestamp, and the repair note refers to it.",
    ),
    (
        "Read the volume's labels and name to find its project, then ask whether its data is still wanted.",
        "A volume with no container attached may be between runs, as study-data is after down.",
        "Deleting every dangling volume because the tool says unused can remove the only copy of learner data.",
        "The project label points to an owner, who confirms keep or delete before removal.",
    ),
    (
        "Compare the scope of the study task, one project's resources, with what system prune touches, everything on the engine.",
        "Pruning can remove other projects' images, caches and volumes that this task never created.",
        "Running a broad prune because the study app is done reaches beyond what the task may remove.",
        "Cleanup commands filter by the project label, and the engine's other resources remain afterward.",
    ),
    (
        "List each target by name, what data stays, the check that shows recovery, and a final listing of the project's resources.",
        "Naming each destructive step lets someone review it, and the final listing shows exactly what remains.",
        "A plan that says clean up Docker gives no target to review and no way to confirm the result.",
        "After the plan runs, the project-filtered listing matches the plan's expected remaining resources.",
    ),
)

REASONING["Namespaces, cgroups, OCI and the runtime beneath Docker"] = (
    (
        "Map each setting to its mechanism: --network none and the PID view come from namespaces; mem_limit and cpus come from cgroups.",
        "Namespaces decide what a process can see; cgroups count and limit what it uses.",
        "Expecting mem_limit 128m to hide host network interfaces mixes a resource control with a visibility control.",
        "The worked example's output shows a PID and a cgroup path; changing the network flag alters interfaces but not the cgroup.",
    ),
    (
        "Run uname -r inside the container and on the engine host or VM and compare.",
        "Both report the same kernel because containers share it; on a desktop that kernel belongs to the engine's Linux VM.",
        "Believing the fixture has its own kernel leads to wrong guesses about isolation and patching.",
        "The kernel versions match between container and engine environment.",
    ),
    (
        "Draw client, engine API, image unpack and mounts, the OCI runtime, and finally python server.py.",
        "Each error belongs to one stage: cannot connect is the client to engine, unpack errors are the image, and tracebacks are the app.",
        "Reading every failure as an application bug sends a daemon connection error to code review.",
        "Classify three sample errors to their stage, and the matching log source confirms each.",
    ),
    (
        "Check which cgroup version the host uses and how the engine lays it out before matching a path from an example.",
        "Paths differ between cgroup v1 and v2 and between engines; the mechanism is the same.",
        "Changing kernel boot settings to match the example's layout alters the host for a cosmetic difference.",
        "Record the observed path and cgroup version; the limit still appears in the container's cgroup files.",
    ),
    (
        "Separate what OCI standardizes, image and runtime formats, from what it leaves to each platform: architectures, features and host setup.",
        "An OCI image for linux/amd64 still needs a compatible host, and a runtime may not support every option.",
        "Promising the fixture runs anywhere OCI is supported skips architecture and feature checks.",
        "Run acceptance on each claimed engine and platform and record the results.",
    ),
    (
        "Note that every container's syscalls reach the same kernel, so a kernel bug can cross the boundary.",
        "That is why the fixture also drops capabilities, runs as 10001 and needs a patched kernel.",
        "Running untrusted code because it is in a container treats namespaces as a full sandbox.",
        "The trust note lists the fixture's least-privilege settings and kernel patching as required parts.",
    ),
)

REASONING["Runtime secrets, configuration files and controlled disclosure"] = (
    (
        "Separate when each secret is needed: a build secret serves one RUN step; a runtime secret like demo is read while the app runs.",
        "A build-only credential that ends up in the runtime image stays readable for the image's whole life.",
        "Using the same token for build and runtime and copying it into the image to reuse it widens exposure.",
        "The final image lacks the build credential, and the app reads demo from /run/secrets at runtime only.",
    ),
    (
        "Ask where demo-secret.txt lives: in plain form on the host, protected only by host file permissions.",
        "Local Compose delivers the file into the container; it does not encrypt the host copy.",
        "Treating the secrets key as encryption leaves the host file readable by other local users if its mode allows.",
        "ls -l on the host file shows its mode and owner, which set who can read it.",
    ),
    (
        "Read the worked example's check: it reads the file, rejects empty content, and prints only that input is present.",
        "The message proves the secret is configured without writing its bytes to output or logs.",
        "Printing the value to confirm it loaded copies it into logs that others may read.",
        "Run the check with an empty file and a filled file; the first raises and the second prints present, with no value shown.",
    ),
    (
        "Check the service's secrets list in docker compose config: a top-level declaration alone does not mount the file into any service.",
        "Without the grant there is no /run/secrets/demo in that container, so reading it fails.",
        "Changing host file permissions or bind-mounting the folder adds exposure without granting the secret.",
        "After adding demo under the service's secrets, the file exists in that container only.",
    ),
    (
        "Separate delivering a new value from making the old one invalid: the service that issued it must revoke it.",
        "Restarting the container picks up the new file but leaves the old credential usable by anyone holding it.",
        "Calling rotation done after a restart leaves the leaked old value working.",
        "A request using the old credential is rejected by the issuing service after revocation.",
    ),
    (
        "Follow the bytes: where they are created, how the host stores them, which service gets them, how it reads them, what may log them, and how they are rotated and deleted.",
        "Each stage can leak in its own way, which a single compose setting does not cover.",
        "Reviewing only the secrets block misses an error message that prints the value.",
        "Each stage in the review has a named control and the check that confirmed it.",
    ),
)

REASONING["Scaling replicas, shared state and concurrency traps"] = (
    (
        "Step through the worked example: both writers read 7 before either writes, and both compute 8.",
        "Each write is atomic, so the file always holds a whole value, but both writes say 8, leaving one increment lost.",
        "Expecting 9 because each write is atomic confuses complete writes with ordered read-modify-write.",
        "Run two concurrent increments against two replicas sharing study-data; the final count can fall short of the starts.",
    ),
    (
        "Ask where the lock lives: in server.py's memory, shared only by that process's threads.",
        "A second container has its own copy of the lock, so the two never wait on each other.",
        "Assuming the in-process lock protects shared study-data across replicas extends it beyond its scope.",
        "The design note states the single-process assumption, and the concurrent test shows lost updates once it is broken.",
    ),
    (
        "Check routing, shared-state writes, sessions, resource budget and recovery one at a time for a second replica.",
        "Any of these can fail alone; the fixture's counter fails the shared-state item.",
        "Starting a second replica and seeing it healthy as proof of scalability ignores the counter's concurrency gap.",
        "Each item has a check; the counter item fails under the concurrent increment test until redesigned.",
    ),
    (
        "Read the ports line: 127.0.0.1:18080 can be bound by only one container at a time.",
        "A second replica tries the same host socket and fails to start.",
        "Switching to network_mode host to avoid the collision removes isolation and still allows only one listener.",
        "Add a proxy in front, or give each replica its own port for a test; each then starts.",
    ),
    (
        "Separate who receives a request from how shared data is updated.",
        "A balancer spreads requests, but each replica still does its own read-modify-write on the same file.",
        "Adding a balancer to fix wrong counts keeps the same race in every replica.",
        "Run the concurrent test behind the balancer; counts still fall short.",
    ),
    (
        "Choose a store with atomic increments or transactions, or route every write to one owning instance.",
        "Either makes increments ordered, which replicas alone cannot provide.",
        "Raising the replica count to show scalability adds more writers to the race.",
        "Concurrent increments match the request count, and a timed-out request is checked rather than retried blindly.",
    ),
)

REASONING["Advanced capstone: a release, recovery and teaching handoff"] = (
    (
        "Before running, write expected results for normal requests, a chosen failure, container replacement and restore.",
        "With written expectations, each result either matches or does not, and a mismatch cannot be reinterpreted as success.",
        "Running first and describing whatever happened as expected makes any outcome look correct.",
        "Compare each observed result with its prediction and record matches and differences.",
    ),
    (
        "Classify the change: editing server.py needs a rebuild; changing APP_MESSAGE in compose.yaml needs only recreation.",
        "Recreating picks up new container settings; only a rebuild puts new source into the image.",
        "Restarting the container after editing server.py keeps running the old image's code.",
        "After the chosen action, GET / or the changed route shows the new behavior, and the image ID changes only after a rebuild.",
    ),
    (
        "Collect the source revision, image ID, platform, exact commands and their observed outputs for the same run.",
        "Each result is tied to the artifact that produced it, so another learner can repeat it.",
        "Reusing screenshots from an earlier image makes the packet describe something not released.",
        "Every entry shows the same image ID, matching the one deployed.",
    ),
    (
        "Introduce one fault, such as a wrong client port, and collect only the evidence needed to find its layer.",
        "One fault and minimal evidence point to one cause; the repair should restore that check's passing result.",
        "Loosening the acceptance check until it passes hides the fault.",
        "Keep the failing case as a regression test; it fails before the repair and passes after.",
    ),
    (
        "Restore the backup into a new volume, start a reader on it, and request GET /counter.",
        "A response with the expected value proves the data is usable, which a stored archive alone does not.",
        "Restoring over the original volume before the check risks losing the only good copy.",
        "The restored reader shows the expected counter while the original volume still holds its own value.",
    ),
    (
        "Explain the request path from the worked example, then list what the system does not guarantee, such as host loss or replicas.",
        "A beginner can operate the system and knows where its guarantees stop.",
        "Presenting local success as production readiness sends the next learner into unsupported use.",
        "A new reader follows the handoff, gets the same results, and can name two limits it states.",
    ),
)
