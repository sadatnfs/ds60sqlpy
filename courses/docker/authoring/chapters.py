"""Original Docker teaching specifications. Examples do not execute while authoring."""

CHAPTERS = []


def add(title, mental, anatomy, a, b, tasks, *refs):
    assert len(tasks) == 6
    CHAPTERS.append((title, mental, anatomy, [a, b], tasks, refs))


add(
    "Containers, images and the process model",
    """A process is a running program together with its memory, open files and operating-system identity. An image is a packaged filesystem plus startup configuration. A container is a running or stopped instance created from an image, with its own writable layer and isolation settings. Docker is tooling that asks a container runtime to create and manage those instances. These words name different objects with different lifetimes.

An image is not a miniature running computer. Starting two containers from one image starts two sets of processes. They initially see the same image files but acquire distinct writable changes. Stopping a container stops its processes; it does not erase the image or automatically remove named volumes. Removing an image is not a reliable or appropriate way to remove application data.

Linux containers share the engine’s Linux kernel. On macOS and a Windows WSL 2 setup, the engine lives in a Linux environment managed by the desktop product or distribution. The application therefore follows Linux process and path rules even when your browser is on another operating system. A VM isolates a whole guest kernel; a container primarily isolates processes using the host kernel. Neither word alone tells you the strength of a deployment’s security boundary.""",
    """Read `docker run --rm IMAGE COMMAND` from left to right. `run` creates a new container and starts its main process. `--rm` asks Docker to remove that container after it exits. `IMAGE` selects a filesystem and defaults; the remaining arguments replace the default command when the image permits. This is different from `docker start NAME`, which restarts an existing container. A printed line is process output, while the exit status tells you whether that invocation reported success.

Use the maintained fixture image after its explicit build. The examples use `ds60-docker-study:local`, a local tag created by the fixture. They do not require an unknown image to be fetched. An image tag is a convenient name; later chapters explain why it is not an immutable identity.""",
    (
        "Run one short process",
        "From your copy of the compose-lab directory, build the image once, then create a disposable Python process with no published port.",
        "sh",
        'docker build -t ds60-docker-study:local .\ndocker run --rm --pull never ds60-docker-study:local python -c "print(2 + 3)"',
        "The build reports its steps and tags the image; the run prints one line containing 5 and then exits, so no long-running web service is implied.",
    ),
    (
        "Compare image and process inventories",
        "Listing images and listing containers answer different questions.",
        "sh",
        "docker image ls ds60-docker-study\ndocker ps -a --filter ancestor=ds60-docker-study:local",
        "The first lists packaged images; the second lists containers created from that image, including stopped ones, and is empty after the --rm run.",
    ),
    [
        (
            "Predict what remains after the short process exits.",
            "The local image remains; the --rm container is removed.",
            "The removal flag applies to the created container, not to every object derived from its image. An image can be reused by another run without retaining that earlier process or writable layer.",
            "List the objects the run command touched, then ask which one the --rm flag names.",
        ),
        (
            "Draw two containers created from one image.",
            "One shared image description, two process groups and two writable layers.",
            "Do not draw one process shared between the containers. Sharing read-only image layers saves storage; it does not merge memory, process IDs or mutable application state.",
            "Draw the image once, then give each container its own box for processes and changed files.",
        ),
        (
            "Classify source code, image tag, container and volume.",
            "Four objects with separate creation and deletion events.",
            "Source is build input, a tag names an image, a container is an instance, and a volume is separately managed storage. Naming these objects correctly makes later cleanup commands predictable.",
            "For each object, name the command that creates it and the command that deletes it.",
        ),
        (
            "Explain why an exited container can still appear in docker ps -a.",
            "Stopped state is distinct from object removal.",
            "The main process ending changes container state. Unless automatic removal was requested or a later removal occurs, Docker retains its metadata and writable layer so you can inspect the outcome.",
            "Compare what docker ps shows with and without -a, and ask what removes a container.",
        ),
        (
            "Compare a Linux container on macOS with a native macOS process.",
            "The container calls a Linux kernel in the engine environment.",
            "CPU architecture and the kernel environment both matter. A Linux container does not gain macOS application frameworks merely because a macOS browser connects to its published port.",
            "Ask which kernel answers the container's system calls on a Mac.",
        ),
        (
            "Explain what evidence proves a web application is serving.",
            "A running process plus a bounded HTTP request and expected response.",
            "An image existing proves only packaging. Container state adds process evidence. The request adds the actual application behavior at a particular endpoint, which remains a separate claim.",
            "Separate what docker image ls, docker ps and an HTTP request each show.",
        ),
    ],
    "https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/",
    "https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/",
)

add(
    "The Linux engine, WSL 2 and your first inspection",
    """The Docker client is the command you type. The daemon or engine receives its requests and manages containers. A context selects the endpoint to which the client connects. A local-looking terminal can be configured to operate a remote engine, so confirming the endpoint is part of ownership rather than a cosmetic setup step.

WSL 2 provides a Linux environment on Windows. The course uses its Ubuntu shell and an engine configured for Linux containers. It does not teach Windows containers or require each language compiler on Windows. On macOS, a desktop engine generally provides a Linux VM. On Linux, the engine can run on the host. These host arrangements differ, while the application’s container filesystem and runtime stay Linux-based.

The fixture needs a local engine and Compose. Compose is the client-side tool that reads a multi-service application definition. A successful client version print does not prove that the engine is running. Conversely, permission to access an engine grants substantial control over its host environment. Resolve setup through the engine’s documented user configuration rather than making a socket world-writable.""",
    """`docker context show` prints the selected context name. `docker context inspect NAME` shows its endpoint configuration. `docker info` actually contacts the engine and exposes its server operating-system type and resource configuration. `docker compose version` checks the Compose plugin. Treat errors separately: an absent command, an unreachable daemon, an authorization problem and a Windows-container engine are different conditions.

Run these in the same Bash terminal you will use for the fixture. Do not change global contexts as an unexplained repair. If a context is remote, stop and select the intended local setup deliberately outside the lesson. Keep private endpoint paths and machine identifiers out of screenshots shared publicly.""",
    (
        "Inspect the selected endpoint",
        "These reads do not start a classroom or change a context.",
        "sh",
        'docker context show\ndocker context inspect "$(docker context show)"\ndocker info --format "{{.OSType}}"\ndocker compose version',
        "The selected endpoint is your intended local engine, OSType is linux, and Compose reports its version.",
    ),
    (
        "Distinguish client from server availability",
        "These two checks have different evidence strength.",
        "sh",
        "docker --version\ndocker info",
        "The first may succeed even when the engine is stopped; the second requires a working engine connection.",
    ),
    [
        (
            "Predict whether docker --version proves readiness.",
            "No; it only proves the client can run.",
            "The version command can use local client information. It does not need to create a server connection and therefore cannot establish permission, engine mode or available resources.",
            "Note which program prints the version and whether it needed to contact the engine.",
        ),
        (
            "Identify the selected context and endpoint.",
            "A locally recorded context name and an intentionally local endpoint.",
            "Names are user-defined and cannot by themselves prove locality. Inspect the endpoint and understand which engine owns it before any state-changing operation.",
            "Run docker context show, then inspect that context's endpoint.",
        ),
        (
            "Produce a minimal setup checklist.",
            "Bash, local Linux engine, Compose and sufficient allocated resources.",
            "The language compilers come from classroom images. The host prerequisite is the engine environment; adding unrelated native toolchains makes first setup harder without solving a daemon connection problem.",
            "List what a lesson command needs: a shell, a reachable engine, Compose and enough memory.",
        ),
        (
            "Diagnose client success with daemon connection failure.",
            "Investigate engine startup, endpoint and permission separately.",
            "Do not interpret an unavailable server as a broken application Dockerfile. No build has occurred yet, so change the setup layer that actually failed.",
            "Compare the Client and Server sections of docker version.",
        ),
        (
            "Explain where commands run on Windows.",
            "Inside the integrated WSL 2 Ubuntu terminal.",
            "Linux paths and Bash quoting are part of the examples. PowerShell has different expansion and continuation syntax, so relabeling commands without changing syntax would mislead beginners.",
            "Ask which shell has the Linux paths and the engine integration the fixture expects.",
        ),
        (
            "Explain a safe response to discovering a remote context.",
            "Stop before mutations and deliberately configure the owned local engine.",
            "The lesson’s authorization concerns a disposable local lab. An ambient context does not extend that ownership to a shared engine or authorize cleanup of its resources.",
            "Ask whose machine a docker compose down would affect with that context selected.",
        ),
    ],
    "https://docs.docker.com/engine/manage-resources/contexts/",
    "https://docs.docker.com/desktop/features/wsl/",
)

add(
    "The filesystem, writable layers and container lifetime",
    """A filesystem maps paths to objects such as files and directories. An image supplies initial read-only layers. A running container sees a merged view plus its own writable changes. Creating or modifying a file in that writable layer does not alter the underlying image used by other containers.

The layer belongs to that container. A restart of the same container generally retains it. Removing and recreating a container creates a different layer, even when the new process has the same name and image. Persistent application data therefore belongs on an explicit volume or other durable store, not accidentally in a disposable container’s root filesystem.

A path is meaningful inside a filesystem namespace. `/app/server.py` inside a container need not exist at that path on your laptop. A bind mount can deliberately map a host directory into a container; it also creates a path by which container processes can change host files. Later lessons treat that relationship explicitly rather than assuming all paths are interchangeable.""",
    """The fixture Dockerfile sets `WORKDIR /app` and copies `server.py` there. `docker run IMAGE python -c ...` starts in that image’s configured directory unless overridden. `--read-only` makes the container root filesystem read-only, but a separately mounted temporary filesystem or volume can still be writable. This is a property of each mount, not a promise that the process has no state.

For diagnosis, first identify whether a file came from the image, the writable layer, a bind mount, a named volume or a temporary filesystem. Then ask which lifecycle operation affects that storage. Do not test persistence by deleting the learner’s real classroom volume.""",
    (
        "Inspect a packaged file",
        "The fixture image contains the app source at its documented path.",
        "sh",
        "docker run --rm --pull never ds60-docker-study:local python -c \"from pathlib import Path; print(Path('/app/server.py').is_file())\"",
        "True; this says the file is packaged, not that the server is running.",
    ),
    (
        "Try a write on a read-only root",
        "A deliberate failure demonstrates an enforcement boundary.",
        "sh",
        "docker run --rm --pull never --read-only ds60-docker-study:local python -c \"from pathlib import Path; Path('/app/change.txt').write_text('x')\"",
        "A nonzero exit and an operating-system write error; the image is unchanged.",
    ),
    [
        (
            "Classify /app/server.py in the fixture.",
            "An image-provided application file.",
            "The Dockerfile COPY instruction places it into a build layer. Reading it from a container demonstrates that the image content is visible through the container filesystem view.",
            "Find the Dockerfile instruction that put the file there.",
        ),
        (
            "Predict whether a sibling container sees an unmounted new file.",
            "It does not share the first container writable layer.",
            "Both instances start from the image. Changes in one private writable layer are not broadcast into another container simply because both use the same tag.",
            "Ask where the first container wrote the file and whether anything is shared.",
        ),
        (
            "Make a restart-versus-recreate persistence table.",
            "Writable layer survives restart but not removal; volumes follow their own lifetime.",
            "A restart preserves the container object. A recreate replaces it. A mounted volume is independent, so the table must name storage rather than make one blanket persistence claim.",
            "Use three columns: the writable layer, a named volume and tmpfs.",
        ),
        (
            "Diagnose a missing file after compose up recreates a service.",
            "Check whether it was written to the old disposable layer.",
            "The service name can stay the same while the container ID changes. A familiar name is not proof that the underlying writable layer or process is the same object.",
            "Compare the container IDs before and after compose up.",
        ),
        (
            "Explain why read-only plus tmpfs permits temporary writes.",
            "The root mount and tmpfs have different write policies.",
            "Read-only is evaluated for the target mount. A bounded tmpfs intentionally supplies volatile writable storage without making the application directory writable.",
            "List the mounts in the container and the write policy of each.",
        ),
        (
            "Choose storage for user progress and transient scratch data.",
            "A named volume for progress and bounded temporary storage for scratch.",
            "The choice should follow retention and recovery requirements. Keeping every file forever increases cleanup and privacy costs; discarding user progress on replacement violates the product contract.",
            "Ask how long each kind of data must survive and who may delete it.",
        ),
    ],
    "https://docs.docker.com/engine/storage/",
    "https://docs.docker.com/engine/storage/drivers/",
)

add(
    "Processes, PID 1, signals and graceful shutdown",
    """PID is a process identifier within a process namespace. The container’s initial process has PID 1 in that namespace and participates in special Linux signal and child-reaping behavior. Docker normally considers a container alive while its main process remains alive. Starting a server in the background and allowing the main shell to exit therefore does not create a durable service.

A signal is a notification delivered to a process. A graceful termination handler stops accepting new work, lets bounded in-flight work finish, closes resources and exits. An abrupt kill cannot perform application cleanup. Docker stop ordinarily sends the configured stop signal, waits for a grace period and then forces termination if necessary.

The exec form of a Dockerfile command gives the runtime an argument array directly. The shell form starts a shell, whose signal forwarding and child handling can become relevant. An init process can reap adopted children and forward signals, but it does not add application-specific transaction recovery. Good shutdown is a cooperation between the orchestrator, process tree and application.""",
    """Compare `CMD ["python", "server.py"]` with `CMD python server.py`. The JSON array has no shell interpolation; each string is one argument. Compose `init: true` requests a small init where supported. The fixture uses it, sets a stop grace period, and logs to standard streams. Do not add an infinite sleep to hide that the real application exited.

For a shutdown investigation record the main process, signal, elapsed time, exit status and whether data is consistent. Exit 137 often indicates a SIGKILL-style termination, but by itself does not prove an out-of-memory cause. Inspect the engine’s OOMKilled state and events before concluding why a process was killed.""",
    (
        "Read an explicit startup command",
        "This is a Dockerfile fragment, not a command to type into Bash.",
        "dockerfile",
        'WORKDIR /app\nCMD ["python", "server.py"]',
        "Python is the direct image command; the process stays in the foreground.",
    ),
    (
        "Observe a bounded stop",
        "Run only after the disposable fixture project is up.",
        "sh",
        "docker compose -p ds60-docker-study logs --tail 20 app\ndocker compose -p ds60-docker-study stop --timeout 10 app\ndocker compose -p ds60-docker-study ps -a",
        "The owned app stops; logs and exit state provide evidence about its actual termination.",
    ),
    [
        (
            "Predict what happens when the main process exits.",
            "The container enters an exited state.",
            "A container is not a VM with an independent background boot lifecycle. Its main process lifecycle drives the container state even if a script attempted to background work.",
            "Ask what Docker watches to decide whether a container is running.",
        ),
        (
            "Compare exec-form and shell-form startup.",
            "An argument array versus an intervening shell.",
            "The difference affects expansion and process hierarchy. It is not a claim that every shell command is wrong, but shell wrappers must intentionally forward signals and wait for children.",
            "Write the process tree for each form and find PID 1.",
        ),
        (
            "Write a four-step graceful shutdown sequence.",
            "Stop new work, bound draining, close owned resources, exit.",
            "An unbounded drain can prevent shutdown forever. Resource cleanup should be explicit, and data correctness may need a transaction or recovery protocol beyond closing file handles.",
            "Start from the moment the stop signal arrives and end with the exit status.",
        ),
        (
            "Diagnose a service kept alive only by sleep.",
            "The alive container does not prove the application is healthy.",
            "The sleep process can make a status look running while the real server has crashed. Measure the application’s endpoint and actual process rather than adding a liveness placeholder.",
            "Check which process is PID 1 and what the server process is doing.",
        ),
        (
            "Explain why exit 137 is not a complete OOM diagnosis.",
            "It identifies a termination pattern, not its unique cause.",
            "A user or timeout can also send a kill signal. Correlate termination state with OOMKilled and relevant events before recommending memory changes.",
            "Compute 137 minus 128 and list what can send that signal.",
        ),
        (
            "Design a shutdown acceptance check for a writer.",
            "Bounded stop, consistent persisted record and restart recovery.",
            "The important observation is what readers see after recovery. A clean exit code is useful but cannot by itself prove that a partially written application record is valid.",
            "Stop the service in the middle of a write, then check the stored record and a restart.",
        ),
    ],
    "https://docs.docker.com/reference/dockerfile/#entrypoint",
    "https://docs.docker.com/reference/cli/docker/container/stop/",
)

add(
    "Dockerfile instructions and the first reproducible image",
    """A Dockerfile is a build recipe. Its instructions define a sequence of filesystem and configuration transformations. `FROM` selects the base image. `WORKDIR` selects a directory for later operations. `COPY` copies files from the build context. `RUN` executes during the build. `CMD` supplies a default command for a future container. Build-time work and runtime work are different phases.

A successful build means the build instructions completed under the builder’s inputs. It does not prove that the server starts, can write its intended volume or responds correctly. Packaging tests and runtime tests belong together. A beginner should be able to identify every file copied into the image and why it is necessary.

The maintained fixture uses only Python’s standard library, so it can teach build mechanics without a package repository. Its base image is still an external dependency during the first build. Later chapters pin immutable identities and export prepared images for disconnected use. The local tag is intentionally never pushed by a course command.""",
    """The final dot in `docker build -t NAME .` is the context directory, not punctuation to omit. Docker reads the Dockerfile relative to the command’s options and copies only eligible files from that context. The tag names the result locally. `--progress=plain` makes build steps and cache decisions visible in terminal logs.

Order instructions by dependency: runtime base, application directory, source copy, identity and command. Declare an unprivileged user after arranging readable files and writable data paths. `EXPOSE` documents an intended container port but does not publish it to your host.""",
    (
        "Read the complete minimal recipe",
        "The actual fixture adds a data directory and non-root identity.",
        "dockerfile",
        'FROM python:3.12-slim\nWORKDIR /app\nCOPY server.py /app/server.py\nEXPOSE 8080\nCMD ["python", "server.py"]',
        "Build creates an image containing the program; port 8080 is documented but remains unpublished.",
    ),
    (
        "Build from the copied fixture",
        "Run from your own compose-lab copy, after engine inspection.",
        "sh",
        "docker build --progress=plain -t ds60-docker-study:local .",
        "Visible build logs finish successfully and the local tag appears in image inspection; no registry upload occurs.",
    ),
    [
        (
            "Sort RUN and CMD into lifecycle phases.",
            "RUN executes at build time; CMD describes later startup.",
            "Putting a long-running server in RUN can hang a build and does not preserve a running process inside the finished image. An image contains files and configuration, not a saved live server.",
            "Ask which instruction runs during docker build and which is only recorded.",
        ),
        (
            "Explain the final context dot.",
            "It selects the current directory as build input.",
            "COPY paths are evaluated against the context. Running the same command from a different directory can change available files, so record both the Dockerfile and context location.",
            "Ask which directory the builder receives as input.",
        ),
        (
            "Write a minimal Dockerfile for a single file app.",
            "Base, workdir, explicit source copy and foreground command.",
            "The minimal file should have no unrelated tools or hidden host dependencies. Each instruction should have a clear effect you can verify in the resulting image.",
            "Use one instruction each for the base, the working directory, the copy and the start command.",
        ),
        (
            "Diagnose COPY failure when a file is outside context.",
            "Change the owned project layout or explicit context intentionally.",
            "Docker cannot copy arbitrary parent files through a relative escape. Expanding the context carelessly can send private material to the builder, so narrow the project layout instead.",
            "Compare the file's path with the context directory you passed.",
        ),
        (
            "Explain why EXPOSE does not make `localhost:8080` work.",
            "It is metadata; port publishing is a runtime configuration.",
            "The container process must listen on the correct interface and a host mapping must exist. An EXPOSE instruction alone establishes neither of those operational facts.",
            "Compare EXPOSE in the Dockerfile with ports in compose.yaml.",
        ),
        (
            "Define build and runtime acceptance separately.",
            "Build succeeds, then endpoint and writable data behavior pass.",
            "Image creation is one stage. Running the exact image with intended user, mounts and network verifies the conditions a learner or operator will actually use.",
            "Write one check that passes after docker build and one that needs a running container.",
        ),
    ],
    "https://docs.docker.com/reference/dockerfile/",
    "https://docs.docker.com/build/concepts/dockerfile/",
)

add(
    "Build context, .dockerignore and accidental data exposure",
    """The build context is the set of files a builder may use. A `.dockerignore` file removes matching paths from that input. This reduces transfer size and prevents accidental inclusion of caches, learner data, credentials and repository history. It is a packaging boundary, not a substitute for reviewing the Dockerfile and resulting image.

A Dockerfile can accidentally copy too much with `COPY . .`. Even if a later instruction deletes a secret, the earlier image layer may retain it. The safe design is to avoid supplying sensitive data as ordinary layer input at all. Build secrets use a separate mechanism covered later; runtime secrets use another lifecycle again.

The fixture keeps its context tiny: server source, Dockerfile, Compose definition and ignore rules. Learner notes and progress live outside the source image. Different builders can run remotely, so context minimization also makes it easier to know which files leave your machine when building against a selected endpoint.""",
    """Ignore patterns are evaluated relative to the build context root with Go's filepath.Match rules, where `*` never crosses a `/`. A pattern such as `.env` or `*.log` therefore excludes only files at the root; `**/.env` and `**/*.log` match at any depth because `**` spans any number of directories. Negated patterns can include an otherwise ignored path, and ordering can matter. Use a simple allowlist or a short reviewed exclude list for a small teaching project. Do not assume `.gitignore` automatically controls Docker build inputs.

Inspect the actual image after a representative build. A source manifest can assert intended exclusions, while an image file listing demonstrates what was packaged. Avoid printing secret content while verifying absence; inspect names or expected safe inventory instead.""",
    (
        "Define a small ignore boundary",
        "These are illustrative rules for the learner copy.",
        "text",
        ".git\n.learning\n**/.env\n**/*.log\n**/__pycache__\n**/*.pyc",
        "Matching paths at any depth are unavailable to COPY; without the `**/` prefix a pattern such as `*.pyc` matches only at the context root, unlike .gitignore.",
    ),
    (
        "Prefer explicit source copying",
        "Explicit paths make packaging intent visible.",
        "dockerfile",
        "COPY server.py /app/server.py",
        "Only the named app file is copied by this instruction; unrelated project files are not implicitly included.",
    ),
    [
        (
            "Predict whether .gitignore protects Docker context.",
            "No automatic equivalence exists.",
            "The tools use distinct input rules. A file ignored by Git can still be available to a Docker build unless the Docker context rules or explicit copy list exclude it.",
            "Ask which tool reads .gitignore and which file the Docker build client reads.",
        ),
        (
            "Predict whether the pattern `*.pyc` excludes `app/__pycache__/server.cpython-312.pyc`.",
            "It does not; `*.pyc` matches only at the context root, so the nested file needs `**/*.pyc`.",
            "Docker matches each pattern against the path from the context root, and a single `*` never crosses a directory separator. Only `**` spans directories, which is why .gitignore habits mislead here: Git matches a slash-free pattern at any depth.",
            "Ask whether a single `*` can match a `/` in a path.",
        ),
        (
            "Design a context inventory for the fixture.",
            "A short list of necessary public build inputs.",
            "An inventory is easier to inspect than a large directory copied indiscriminately. It also makes a missing dependency visible rather than relying on a developer machine file.",
            "List the files the Dockerfile actually copies or reads.",
        ),
        (
            "Explain why deleting a secret in a later layer is insufficient.",
            "The earlier layer can retain the copied bytes.",
            "Layered filesystems record changes; deleting a path from the merged view does not rewrite earlier layers. Prevention is safer than attempting to erase a secret after packaging it.",
            "Run docker history on an image and treat each line as a separately saved change.",
        ),
        (
            "Check that an ignored required source produces a useful failure.",
            "COPY fails instead of silently borrowing a host file.",
            "A deterministic failure makes the missing build input visible. Repair the intended context rules without widening them to unrelated parent directories.",
            "Ignore server.py in a scratch copy and read the COPY error.",
        ),
        (
            "Describe source and image privacy acceptance.",
            "Review inputs, build recipe and safe final file inventory.",
            "No one check covers every route. Input exclusion prevents accidental transfer; explicit copy rules limit layering; final inspection tests the produced artifact against the intended public inventory.",
            "Check three places: what enters the context, what the Dockerfile copies and what the final image contains.",
        ),
    ],
    "https://docs.docker.com/build/concepts/context/",
    "https://docs.docker.com/reference/dockerfile/#dockerignore-file",
)

add(
    "Layers, cache invalidation and efficient rebuilds",
    """A layer records filesystem changes from a build step. Build cache can reuse a prior result when the builder considers an instruction and its relevant inputs unchanged. Caching is a performance mechanism, not proof that a dependency is current or that a security update has been applied.

Instruction order creates a dependency chain. If a source copy changes before an expensive dependency installation, later steps may need to run again. Separating dependency metadata from frequently edited source can improve iteration. The correct split depends on the package manager and lockfile, not on memorizing one Dockerfile pattern.

A cache hit is visible in build logs. A fast build is not automatically cached, and a cache miss is not automatically a bug. Reproducibility requires identifying inputs, versions and build settings. The same text can still download different bytes if it refers to mutable remote dependencies.""",
    """Compare an unchanged rebuild with a rebuild after changing only a harmless source string in your learner copy. Record which instruction first stops being cached. A build with `--no-cache` intentionally ignores build-step cache, but it does not inherently replace every already available base image. Fetching newer bases is a separate operation.

Cache mounts, covered in the next stage, preserve download caches without baking their contents into the runtime image. Do not put real credentials into cache keys, ARG values or copied files. Build output and dependency recovery are observable concerns, so keep plain logs for your experiments.""",
    (
        "Observe an unchanged rebuild",
        "Use the same copied context and local tag.",
        "sh",
        "docker build --progress=plain -t ds60-docker-study:local .\ndocker build --progress=plain -t ds60-docker-study:local .",
        "The second build commonly reports cached unchanged steps; exact durations depend on the engine.",
    ),
    (
        "Compare an explicit cache bypass",
        "This is an optional rebuild, not a general repair for every error.",
        "sh",
        "docker build --no-cache --progress=plain -t ds60-docker-study:local .",
        "Build steps run again; this does not by itself establish a newer base image or a different application result.",
    ),
    [
        (
            "Predict the first invalidated step after editing server.py.",
            "The COPY using that file and dependent later steps.",
            "The builder tracks relevant inputs. Earlier independent operations can remain reusable while operations based on changed filesystem state require new results.",
            "Find the first instruction whose inputs include server.py.",
        ),
        (
            "Record evidence of a real cache hit.",
            "A specific step labeled cached in plain build logs.",
            "Elapsed time alone is ambiguous because network and CPU vary. A named cached step ties the observation to the builder decision being studied.",
            "Build twice with --progress=plain and compare the step lines.",
        ),
        (
            "Reorder dependency metadata and app source conceptually.",
            "Stable dependency inputs precede rapidly changing source.",
            "This allows source edits to reuse dependencies when lockfiles remain unchanged. It does not justify ignoring a lockfile change or copying too little to perform a correct build.",
            "Ask which files change on most edits and which change rarely.",
        ),
        (
            "Diagnose a cached step that downloads a mutable dependency.",
            "A cache hit can preserve old bytes even with unchanged command text.",
            "The command can have external inputs absent from the visible file hash. Pinning and deliberate update procedures provide a stronger reproducibility story than relying on caching behavior.",
            "Ask what the cache key of a RUN step includes and what it leaves out.",
        ),
        (
            "Explain no-cache versus pulling a base.",
            "Reexecuting build steps and refreshing a base are separate choices.",
            "One option changes cache reuse; another changes the image resolved by the base reference. Conflating them makes debugging rebuilds needlessly expensive and hard to interpret.",
            "Compare what --no-cache and --pull each refresh.",
        ),
        (
            "Design a build-performance experiment.",
            "Same engine and context, one controlled edit, named cache observations.",
            "Record build identity and changed inputs so timing is interpretable. Optimize the expensive invalidated step after confirming it is actually the bottleneck.",
            "Change one input at a time and record which steps rebuild.",
        ),
    ],
    "https://docs.docker.com/build/cache/",
    "https://docs.docker.com/build/cache/invalidation/",
)

add(
    "Environment variables, command arguments and configuration",
    """Configuration changes behavior without rebuilding application logic. Environment variables are string values supplied to a process. Command arguments are an ordered array of strings. Image defaults, Compose interpolation and the container’s environment are related but distinct mechanisms.

A Compose `.env` file commonly supplies values used when Compose renders its model. That does not mean every value is automatically injected into every container. A service’s `environment` or `env_file` configuration controls injection. Host-shell interpolation, Compose interpolation and shell expansion inside a container occur at different times.

Treat configuration as data with validation. A missing value should produce a clear startup error or documented default. A string containing `false` is still a nonempty string in many languages. Numeric ports and timeouts need parsing and bounds. Secrets should not be casually placed in versioned files or printed by a diagnostic command.""",
    """The fixture reads `APP_MESSAGE` and serves it in a JSON field. Compose explicitly sets the value. A source-only message edit changes the image; an environment edit changes runtime configuration and usually requires container recreation to take effect. An image environment value is a default which runtime options can override.

An image's `ENTRYPOINT` names the executable and its `CMD` supplies default arguments, or the whole default command when there is no entrypoint. Arguments after the image name in `docker run IMAGE ARG...` replace `CMD` and are appended to the entrypoint; `--entrypoint` replaces the executable and also clears the image's default `CMD`. The fixture's Dockerfile sets only `CMD ["python", "server.py"]`, so `docker run IMAGE python -c ...` replaces the whole command, while its Compose `client` service sets `entrypoint: ["python", "-c"]` and passes the program text as `command`.

The exec-form command array does not expand `$NAME` like a shell. If the application needs an environment value, have the application read it or use an intentionally reviewed shell wrapper. `docker compose config` is valuable for validation but can display interpolated private values; use synthetic data in this lesson.""",
    (
        "Set a public runtime message",
        "This is a Compose fragment for the copied fixture.",
        "yaml",
        'services:\n  app:\n    environment:\n      APP_MESSAGE: "hello from my configuration"',
        "The app reads this public string after recreation; the image source can remain unchanged.",
    ),
    (
        "Read one explicit variable",
        "The short process reads its own environment.",
        "sh",
        "docker run --rm --pull never -e APP_MESSAGE=sample ds60-docker-study:local python -c \"import os; print(os.environ['APP_MESSAGE'])\"",
        "Exactly sample is printed; no secret value is involved.",
    ),
    [
        (
            "Distinguish Compose interpolation from container environment.",
            "Model rendering versus process input.",
            "A value used to choose a host port need not appear inside the container. Conversely, a container environment entry can be literal and independent of a host variable.",
            "Run docker compose config and compare it with the environment inside the container.",
        ),
        (
            "Predict the type of APP_MESSAGE.",
            "A string, even when its contents look numeric.",
            "Environment values do not carry a native integer or Boolean type. The application must parse and validate domain-specific meanings before using them.",
            "Ask what type every value in a process environment has.",
        ),
        (
            "Design defaults and validation for a timeout variable.",
            "A documented default plus finite positive bounded numeric parsing.",
            "Configuration is external input. Rejecting malformed or excessive values at startup gives a clearer failure than a later hang caused by an unintended timeout.",
            "Decide what happens for a missing, a negative, a huge and a non-numeric value.",
        ),
        (
            "Diagnose an exec array containing literal $PORT.",
            "No shell expansion occurs in an argument array.",
            "The runtime passes the characters directly. Add explicit application parsing rather than introducing a shell merely to conceal that the command contract was misunderstood.",
            "Ask which program would expand $PORT and whether one runs in exec form.",
        ),
        (
            "Explain why restart may not apply changed Compose environment.",
            "Existing container configuration and recreation differ.",
            "Restart starts the same configured object again. Applying a changed service model may require recreation, so confirm the observed environment and container identity.",
            "Compare what docker compose restart and docker compose up do to the container.",
        ),
        (
            "Write a public configuration evidence record.",
            "Name, safe synthetic value, source of override and observed response.",
            "Evidence should prove the intended precedence without leaking secrets. A response demonstrating the public message connects model rendering to actual application behavior.",
            "Record where the value came from and the response that shows it.",
        ),
    ],
    "https://docs.docker.com/compose/how-tos/environment-variables/",
    "https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/",
    "https://docs.docker.com/reference/dockerfile/#entrypoint",
)

add(
    "Ports, loopback and the first browser request",
    """An IP address identifies a network interface or virtual destination within a network. A port identifies a transport endpoint at that address. A server listens on an address and port inside its own network namespace. Publishing maps a host endpoint to a container endpoint; it does not change the application’s listening configuration.

Loopback refers to the local network namespace. `127.0.0.1` inside a container points back to that container, not to your laptop and not to another service. A server bound only to container loopback is normally unreachable through a mapping to its container network interface. The fixture listens on `0.0.0.0:8080` inside the container and publishes only `127.0.0.1:18080` on the host.

The wildcard address `0.0.0.0` is a listening choice, not a browser destination. Binding a published port to host loopback reduces accidental exposure to other machines. The real boundary also depends on the engine, host firewall and platform networking, so do not describe a port mapping as an authentication system.""",
    """Read `127.0.0.1:18080:8080` as host address, host port and container port. A browser on the host requests `http://127.0.0.1:18080/`. A peer container on the same Compose network requests `http://app:8080/` using service discovery. They reach the same application through different paths.

Troubleshoot in layers: application listen address, process state, container port, published mapping, host port conflict, then HTTP path and payload. A connection refused response is different from HTTP 404; the latter means an HTTP server responded but did not serve the requested path.""",
    (
        "Publish only to the learner host",
        "The fixture supplies this mapping.",
        "yaml",
        'ports:\n  - "127.0.0.1:18080:8080"',
        "A host browser uses port 18080; the app still listens on 8080 inside its container.",
    ),
    (
        "Compare two destinations",
        "Use the first in the host browser and the second only from a network peer.",
        "text",
        "Host browser -> 127.0.0.1:18080 -> published mapping -> app:8080\nPeer container -> DNS name app -> container address:8080",
        "Loopback and the service name have different scopes; hardcoding the temporary container IP is unnecessary.",
    ),
    [
        (
            "Label every component of the mapping.",
            "Host loopback, host port 18080 and container port 8080.",
            "The three values occupy different positions. Reversing the ports can create a listening mapping that still points at the wrong internal endpoint.",
            "Read 127.0.0.1:18080:8080 from left to right as host address, host port and container port.",
        ),
        (
            "Predict whether `localhost:18080` inside app reaches the host browser endpoint.",
            "It refers to app container loopback and normally fails.",
            "Loopback is relative to the caller namespace. A hostname that works in the browser does not automatically name the same machine from a container.",
            "Ask whose loopback interface localhost means inside the container.",
        ),
        (
            "Draw a host browser request path.",
            "Browser, host socket mapping, container interface and app listener.",
            "Each hop has a separate observable condition. The drawing should show where port translation happens and which process actually handles the request.",
            "Follow the request from the browser to the published socket to the app's listener.",
        ),
        (
            "Diagnose a server bound to container 127.0.0.1 only.",
            "It may answer locally but not through the published mapping.",
            "The mapping targets the container’s reachable interface. Changing the host port cannot fix an application that does not listen on that interface.",
            "Check the address the server listens on inside the container.",
        ),
        (
            "Distinguish connection refused from HTTP 404.",
            "Transport failure versus application routing result.",
            "A 404 establishes that an HTTP exchange happened. A refused connection occurs earlier, so inspect listeners and mappings before changing application URL handlers.",
            "Ask whether any HTTP response came back at all.",
        ),
        (
            "Choose public and internal endpoints for a two-service app.",
            "Only the user-facing service gets a deliberate published port.",
            "Internal services can use Compose DNS without host publication. Avoiding unnecessary published ports simplifies the network and reduces accidental exposure.",
            "Publish only what a person outside the project must reach.",
        ),
    ],
    "https://docs.docker.com/engine/network/port-publishing/",
    "https://docs.docker.com/engine/network/",
)

add(
    "Logs, exit status and observation before repair",
    """Standard output and standard error are streams a process uses to communicate. Docker’s logging system captures those streams according to its configured driver. Logs are useful observations but are not a database and do not automatically have infinite retention.

An exit status is a small integer returned when a process ends. Zero conventionally means success; a nonzero value reports failure according to the program. A running container has not yet produced its final exit status. Its process can still be unhealthy, waiting indefinitely or returning incorrect responses.

The most effective beginner troubleshooting habit is to preserve evidence before changing state. Record the exact image, container state, recent bounded logs and a minimal failing request. Restarting repeatedly can destroy the first useful symptom, and dumping an entire environment can expose credentials unrelated to the problem.""",
    """`docker compose logs --tail 30 app` asks for a bounded recent stream for the project service. `docker compose ps -a` shows lifecycle state. `docker inspect` provides structured fields for a named container; use format selections when you need just exit status or OOMKilled. `docker events` observes lifecycle events but is not a substitute for application request tracing.

The fixture writes concise HTTP access observations to standard error and JSON response data to the HTTP client. Keep those destinations distinct. If you redirect output to a file during a host experiment, store it in your ignored learner copy rather than committing machine logs to the source repository.""",
    (
        "Read a bounded log sample",
        "Use the copied fixture project and service name.",
        "sh",
        "docker compose -p ds60-docker-study ps -a\ndocker compose -p ds60-docker-study logs --tail 30 app",
        "A small project-specific state and log record, without touching unrelated containers.",
    ),
    (
        "Compare successful and failing short programs",
        "Both process results are useful evidence.",
        "sh",
        "docker run --rm --pull never ds60-docker-study:local python -c \"print('ok')\"\ndocker run --rm --pull never ds60-docker-study:local python -c \"raise ValueError('teaching failure')\"",
        "The first exits zero; the second prints a traceback to stderr and exits nonzero.",
    ),
    [
        (
            "Predict the streams used by the two short programs.",
            "Success line on stdout, failure diagnostic on stderr.",
            "Stream conventions help tools separate normal output from diagnostics. They do not prevent an application from misusing a stream, so inspect its documented behavior.",
            "Ask which stream a print call uses and which a failure diagnostic uses.",
        ),
        (
            "Choose a bounded log command.",
            "Project-scoped service logs with an explicit tail limit.",
            "A bounded sample is easier to review and less likely to leak unrelated data. Scope should be enforced by project and service selection rather than by filtering a huge global dump afterward.",
            "Limit the output by project, service and number of lines.",
        ),
        (
            "Write an incident observation packet.",
            "Image identity, lifecycle state, recent logs and one failing request.",
            "These observations connect source packaging to the process and application layers. Include timestamps so a later healthy state is not confused with the original failure.",
            "Collect the image identity, the state, recent logs and one failing request before changing anything.",
        ),
        (
            "Diagnose a running container that returns errors.",
            "Investigate application behavior rather than declaring success from running.",
            "The engine reports process lifecycle. HTTP responses and domain assertions establish whether that process performs its intended function.",
            "Compare the container state with the HTTP status of a request.",
        ),
        (
            "Explain why a restart-only repair is weak evidence.",
            "It can hide the cause and may not preserve a useful failure record.",
            "A restart can be an operational mitigation while still leaving root cause unknown. State both facts instead of claiming that disappearance proves a permanent fix.",
            "Ask what you learn about the cause if the error disappears after a restart.",
        ),
        (
            "Design log content for a public teaching server.",
            "Useful request metadata without tokens, raw secrets or private payloads.",
            "Logs often persist beyond the request. A small diagnostic schema gives enough context to debug while limiting the information copied into reports or shared screenshots.",
            "List the fields that help diagnose a request and the values that must never be logged.",
        ),
    ],
    "https://docs.docker.com/engine/logging/",
    "https://docs.docker.com/reference/cli/docker/container/inspect/",
)

add(
    "Compose services, projects and a complete application",
    """Compose describes a related set of services, networks and volumes in one application model. A service describes how to create containers with a common role. A project groups their owned resources so commands can target the application rather than every container on the engine.

The YAML model is declarative input, but running Compose is still an operation against a particular engine. Two copies of the same file can create different projects. Conversely, reusing the same project name can act on existing resources from an earlier invocation. Explicit project identity makes a teaching lab safer and its cleanup understandable.

A service name is also a useful DNS name on its Compose network. The default network enables peers to find each other without fixed IPs. Named volumes remain separate storage resources. An application can therefore be recreated while preserving its data, provided the same intended volume remains mounted.""",
    """Use `docker compose -p ds60-docker-study ...` from the copied fixture directory. The explicit `-p` sets the project name consistently for build, up, logs and down. The fixture has `app` and an optional tools-profile `client`; the client uses the same local image but runs a short request command instead of the server.

`config --quiet` validates and renders the model without printing its values or starting services. `up -d --wait` creates or updates services and waits according to readiness behavior. `down` removes the project’s containers and ordinary networks while retaining named volumes unless explicit volume deletion is requested.""",
    (
        "Validate before creating",
        "This checks the copied Compose file only.",
        "sh",
        "docker compose -p ds60-docker-study config --quiet",
        "Exit zero for a valid model; no containers are created by this command.",
    ),
    (
        "Start and inspect the project",
        "The first build downloads its base if necessary; no image is pushed.",
        "sh",
        "docker compose --progress plain -p ds60-docker-study build\ndocker compose -p ds60-docker-study up -d --wait\ndocker compose -p ds60-docker-study ps",
        "The app becomes healthy and its host loopback endpoint is available.",
    ),
    [
        (
            "Identify the project and service names.",
            "Project ds60-docker-study and service app.",
            "The project groups engine resources; the service describes an application role. A container ID is a third identity that can change after recreation.",
            "Find the -p value and the keys under services in compose.yaml.",
        ),
        (
            "Predict what config --quiet changes.",
            "It validates the model without creating runtime resources.",
            "Static model validation is valuable early evidence, but it cannot prove port availability, image execution, volume permissions or endpoint correctness.",
            "Ask whether config creates containers, networks or volumes.",
        ),
        (
            "Write the project lifecycle command sequence.",
            "Validate, build, up with readiness, inspect, then down.",
            "Each step adds evidence and has a defined effect. Keeping the project option on every command prevents a directory-name change from accidentally selecting a different project.",
            "Order the commands from validating the model to removing the project's containers.",
        ),
        (
            "Diagnose an unexpected resource collision.",
            "Inspect project identity and existing owned resources before changes.",
            "A reused project name or host port can collide with another copy. Renaming or deleting blindly may affect work you did not create; establish ownership first.",
            "List the containers, networks and volumes that carry the project's label before changing anything.",
        ),
        (
            "Explain why down preserves user data by default.",
            "Named volume removal is a separate explicit operation.",
            "Containers and networks are generally disposable application infrastructure. Persistent state deserves a deliberate retention policy, so destruction is not an incidental consequence of stopping a lab.",
            "Compare docker compose down with and without -v.",
        ),
        (
            "Design a two-copy experiment without interference.",
            "Distinct project names and distinct published host ports.",
            "Both copies can use the same internal service names because each project has its own network. Host-published ports share a host namespace and must avoid conflicts.",
            "List every name and port the two copies would share.",
        ),
    ],
    "https://docs.docker.com/compose/intro/compose-application-model/",
    "https://docs.docker.com/compose/how-tos/project-name/",
)

add(
    "Health checks, startup order and real readiness",
    """Readiness means the application can perform the work a dependent component needs. Process existence is weaker evidence. A server can be running while it initializes files, connects to a database or rejects requests. A health check periodically executes a small observation and classifies container health according to timing and failure rules.

Compose can wait for a dependency to become healthy before starting a dependent service. This improves startup ordering, but it is not a permanent dependency availability guarantee. The dependency can fail later. Applications still need bounded timeouts, useful error handling and appropriate reconnect behavior.

A useful health endpoint checks enough to represent readiness without performing expensive or destructive work. It should not mutate learner data or require a public internet service to declare a local classroom ready. Its failure should point to the missing capability, not trigger an unbounded retry loop.""",
    """The fixture’s health command uses Python’s standard-library HTTP client to request its own loopback `/healthz` endpoint with a timeout. `interval`, `timeout`, `retries` and `start_period` control repeated observations. The health command runs inside the container, so its loopback is the app’s loopback. An image can also declare a default check with the Dockerfile instruction `HEALTHCHECK --interval=5s --timeout=3s CMD ["python", "-c", "..."]`; a Compose `healthcheck` overrides the image's values for that service.

A dependent service may specify `depends_on: app: condition: service_healthy`. That describes an initial ordering condition. A check that only tests whether a PID exists is usually too weak for a web dependency; a check that queries an unrelated remote service may be unnecessarily strong and fragile.""",
    (
        "Inspect the fixture readiness command",
        "This is an illustrative Compose fragment.",
        "yaml",
        'healthcheck:\n  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen(\'http://127.0.0.1:8080/healthz\', timeout=2).read()"]\n  interval: 5s\n  timeout: 3s\n  retries: 5\n  start_period: 5s',
        "A responding local health endpoint establishes app readiness according to this narrow check.",
    ),
    (
        "Express a dependency condition",
        "The client is a separate short-lived observation role.",
        "yaml",
        "depends_on:\n  app:\n    condition: service_healthy",
        "The dependent service waits for app health at startup; later app failures still require client error handling.",
    ),
    [
        (
            "Compare running and healthy.",
            "A lifecycle state versus a defined repeated behavioral check.",
            "A running process may not be ready. A healthy classification is only as meaningful as its check, so review what the command actually observes.",
            "Compare the State and Health fields in docker inspect.",
        ),
        (
            "Predict which loopback the health command uses.",
            "The app container network namespace.",
            "The command runs inside that container. It does not traverse the published host port, so host-browser acceptance remains a separate observation.",
            "Ask in which container the health command runs.",
        ),
        (
            "Design a readiness endpoint for a file-backed teaching app.",
            "A bounded non-destructive test of required local capability.",
            "Readiness should verify that the app can serve its intended role without creating records or depending on unrelated internet availability.",
            "Check the capability the app needs without changing stored data.",
        ),
        (
            "Diagnose a healthy app with a broken host mapping.",
            "The internal readiness check can pass while browser access fails.",
            "The checks traverse different paths. Inspect the host port mapping and request destination rather than weakening a valid internal readiness check.",
            "Compare where the health check runs with where the browser connects.",
        ),
        (
            "Explain a dependency crash after startup.",
            "depends_on does not replace runtime recovery logic.",
            "An initial condition can become false later. Clients need timeouts and failure handling that match whether retrying the specific operation is safe.",
            "Ask when depends_on is evaluated.",
        ),
        (
            "Write separate health and acceptance assertions.",
            "Health endpoint succeeds; user-facing response and persistence also satisfy their contracts.",
            "The cheap periodic check should remain small. A fuller acceptance check proves features such as content, authentication or saved-state behavior that health may intentionally omit.",
            "Write one assertion for /healthz and one for the user-facing response.",
        ),
    ],
    "https://docs.docker.com/compose/how-tos/startup-order/",
    "https://docs.docker.com/reference/compose-file/services/#healthcheck",
)

add(
    "Named volumes, bind mounts and persistence experiments",
    """A named volume is storage managed by the engine and mounted into containers. A bind mount maps an explicitly chosen host path into a container. A temporary filesystem is volatile storage usually backed by memory. The choice determines ownership, portability, backup and what survives container replacement.

The fixture stores its counter in a named volume mounted at `/data`. Its application code is in the image. This separation lets the app container be replaced without losing the counter. A bind mount is useful for editing a local project, but it gives container processes direct access to the chosen host files with the mount’s permissions.

Mounting a directory over an image path hides the image content at that location while the mount is present. A bind mount hides the packaged directory without copying its files into the host directory. Docker-managed volumes have an important initialization exception: when an empty volume is mounted over existing image content, Docker copies that content into it by default unless volume-nocopy is selected. A nonempty mounted volume hides the packaged content. Distinguish those cases before diagnosing missing or unexpectedly seeded files.""",
    """A Compose service can mount `study-data:/data`, with `study-data` declared in the top-level `volumes` section. Compose assigns a project-scoped volume name unless configured otherwise. The fixture’s app treats an absent counter.json as an initial count of zero and updates that file through an atomic replace under a process-local lock. It does not create an exclusive marker file. The separate restore command uses exclusive file creation to refuse overwriting an existing restore target.

Use POST `/increment` only within the disposable lab to intentionally change the teaching counter; GET `/counter` reads it without mutation. Record a value, recreate only the app container, and verify that the value did not reset. Rebuilding an image is unnecessary for this test, because the question concerns storage lifetime.""",
    (
        "Declare separate application data",
        "The volume is owned by this Compose project.",
        "yaml",
        "services:\n  app:\n    volumes:\n      - study-data:/data\nvolumes:\n  study-data: {}",
        "The mounted data is independent of the app container writable layer.",
    ),
    (
        "Recreate the app while retaining its volume",
        "Record the counter before and after in the browser.",
        "sh",
        "docker compose -p ds60-docker-study up -d --force-recreate --wait app",
        "The container ID changes; the same mounted counter persists and can continue increasing.",
    ),
    [
        (
            "Predict data retention after app recreation.",
            "Named-volume data remains if the same volume is mounted.",
            "The container object changes, but the volume is separate. A changed project name can select a different volume, so identity matters as much as the mount path.",
            "Ask whether the new container mounts the same named volume.",
        ),
        (
            "Compare named volume and bind mount ownership.",
            "Engine-managed storage versus an explicit host directory.",
            "Bind mounts are convenient for editing and exports but can expose private or sensitive host paths. Volumes are easier to keep independent of a host directory layout.",
            "Ask who creates and manages the storage location in each case.",
        ),
        (
            "Build a persistence evidence table.",
            "Before value, old/new container IDs, volume identity and after value.",
            "A value alone can be ambiguous if a seed coincidentally matches. Recording both storage and container identities makes the replacement experiment stronger.",
            "Record the counter, the container ID and the volume name before and after.",
        ),
        (
            "Diagnose missing code after mounting over /app.",
            "The mount hides packaged content at that path.",
            "A mount presents another filesystem view. It does not automatically copy all image files into an arbitrary bind directory, so mount code and data intentionally.",
            "List the mounts and ask what happens to image files under a mount point.",
        ),
        (
            "Explain why changing project names may look like data loss.",
            "The new project can create a different named volume.",
            "The original data may still exist under the original project. Inspect ownership and volume names before declaring corruption or deleting apparently unused storage.",
            "Run docker volume ls and compare the volume names for both projects.",
        ),
        (
            "Choose a safe cleanup policy for progress.",
            "Stop containers routinely; delete data only after an explicit reset decision.",
            "Learner progress has a longer intended lifetime than runtime processes. Cleanup should preserve it and provide a backup/export route before any irreversible deletion.",
            "Separate routine stopping from a deliberate data reset.",
        ),
    ],
    "https://docs.docker.com/engine/storage/volumes/",
    "https://docs.docker.com/engine/storage/bind-mounts/",
)

add(
    "First capstone: build, serve, replace and explain",
    """A capstone combines mechanisms into an observable delivery story. The target here is deliberately small: a local HTTP application with a visible message, a health endpoint and a persistent counter. Completing it requires understanding build inputs, image identity, container state, loopback publishing, readiness and volume lifetime.

The project is successful when a new learner can reproduce the outcome from the copied fixture and explain why each step works. A screenshot of a browser alone is insufficient: it could show an old process or cached content. Combine the visible response with the exact project, image and replacement evidence.

This lab is not a benchmark, production service or shared hosting system. Its fixed host loopback port and synthetic counter keep the exercise inspectable. If the port or project identity conflicts with existing work, choose an unused owned identity before starting rather than stopping another application.""",
    """Copy `courses/docker/fixtures/compose-lab/` into a new directory below `.learning/`. Read its README in full. Validate the model, build with plain progress, start with readiness, request the message and counter, and recreate the app with its volume intact. Preserve commands and observations in the lesson worksheet.

The request chain is host browser to published host loopback port to app listener to JSON handler to the volume-backed counter. A new image is packaging evidence. A new container ID with retained counter is persistence evidence. The distinction is the core of the exercise.""",
    (
        "Create the bounded application",
        "These commands run from your own fixture copy.",
        "sh",
        "docker compose -p ds60-docker-study config --quiet\ndocker compose --progress plain -p ds60-docker-study build\ndocker compose -p ds60-docker-study up -d --wait",
        "The app is healthy and http://127.0.0.1:18080/ returns the configured message.",
    ),
    (
        "Prove replacement and stop cleanly",
        "Record the counter and app container ID around replacement.",
        "sh",
        "docker compose -p ds60-docker-study ps -q app\ndocker compose -p ds60-docker-study up -d --force-recreate --wait app\ndocker compose -p ds60-docker-study ps -q app\ndocker compose -p ds60-docker-study down",
        "The ID changes, data persists, and final down stops only this project while retaining its named volume.",
    ),
    [
        (
            "Predict every resource the project creates.",
            "A local image, app container, project network and named data volume.",
            "The optional client is created only for its explicit run. Listing resource types before execution makes ownership and later cleanup easier to verify.",
            "Read compose.yaml for the image, services, networks and volumes.",
        ),
        (
            "Change the public message in the learner copy.",
            "The observed response matches the deliberate runtime configuration.",
            "Keep the source image unchanged for this experiment. It demonstrates that configuration and application packaging are separable inputs.",
            "Change APP_MESSAGE, recreate the app and request /.",
        ),
        (
            "Produce the complete build-and-request evidence packet.",
            "Build logs, model validation, health state and exact JSON response.",
            "Each item covers a different layer. Together they make it less likely that a stale browser page or old image is mistaken for the new build.",
            "Follow the order build, validate, start, wait for health, then request.",
        ),
        (
            "Introduce and repair one wrong host port in a scratch model.",
            "Explain the first failing network hop and restore the original mapping.",
            "Avoid unrelated changes. A single deliberate configuration fault gives a clean causal explanation and a regression case for the working mapping.",
            "Change only the host side of the mapping and test each hop.",
        ),
        (
            "Verify replacement without resetting the counter.",
            "Different container ID, same intended volume and nonreset counter.",
            "This is the central persistence invariant. An image rebuild or browser refresh alone does not test container replacement, so record the actual object change.",
            "Record the container ID and counter before and after recreation.",
        ),
        (
            "Teach the project to a beginner without using hidden host state.",
            "A fresh-copy procedure with prerequisites, expected outputs and scoped cleanup.",
            "A reproducible explanation should name what must already be installed and which downloads occur. It must not depend on a private image tag or an unmentioned file on the author’s laptop.",
            "Start from a fresh copy and write down every prerequisite you use.",
        ),
    ],
    "https://docs.docker.com/compose/gettingstarted/",
    "https://docs.docker.com/reference/cli/docker/compose/",
)

add(
    "BuildKit, cache mounts and build secrets",
    """BuildKit is the build engine used by modern Docker tooling. It can execute a build graph, reuse cached results and make special mounts available to individual build steps. A cache mount stores reusable downloads; a secret mount provides sensitive input to a step without treating that input as an ordinary copied image file. These mounts have different purposes and lifetimes.

A secret mount reduces accidental persistence but does not make arbitrary build commands safe. A command can still print a secret or copy it into an output. The author must review what the step does. Never put credentials in ARG, ENV, a source file or a command URL simply because the final application does not use them.

Build-time network access is an external dependency. Prefer locked public inputs for the default teaching build. The fixture has no package downloads beyond its base image. This chapter uses a synthetic secret string in a separate scratch build and never needs a real registry credential.""",
    """A Dockerfile RUN mount exists only for that build operation. `type=cache` selects a persistent builder cache directory. `type=secret,id=demo` selects a separately supplied secret. Read a secret only at its declared path, and do not echo its bytes. `required=true` causes a missing input to fail clearly. Supply the value from the host with `docker build --secret id=demo,src=./demo-secret.txt .` or `--secret id=demo,env=DEMO_SECRET`; the step reads it at `/run/secrets/demo`.

Cache entries can improve speed but should not be the only copy of a required source artifact. A cold build must still produce the same intended result from declared dependencies. Treat cache as discardable acceleration, not durable application data.""",
    (
        "Reuse downloads with a cache mount",
        "This pattern is illustrative for a Python project with a hash-locked requirements file.",
        "dockerfile",
        "COPY requirements.lock /tmp/requirements.lock\nRUN --mount=type=cache,target=/root/.cache/pip python -m pip install --require-hashes -r /tmp/requirements.lock",
        "A rebuild after a lock change reuses previously downloaded wheels from the cache mount; the cache directory is not part of any image layer.",
    ),
    (
        "Require a synthetic build secret without printing it",
        "Use only an invented demo value in a separate scratch build.",
        "dockerfile",
        "RUN --mount=type=secret,id=demo,required=true test -s /run/secrets/demo",
        "The build succeeds only when the named nonempty secret is supplied; the command does not reveal its content.",
    ),
    [
        (
            "Compare a cache mount and a secret mount.",
            "Reusable acceleration versus sensitive transient input.",
            "The two mounts solve different problems. A cache may persist across builds; a secret should be available only to the intended step and should never become a normal artifact.",
            "Ask what each mount holds and how long it should live.",
        ),
        (
            "Predict a required secret missing from the build.",
            "The step fails before pretending to authenticate.",
            "Failing explicitly keeps the dependency visible. Silently using another credential would undermine both reproducibility and the learner’s understanding of which identity performed the operation.",
            "Read what required=true does when no --secret is supplied.",
        ),
        (
            "Design a cold-build check.",
            "Remove reliance on cache while preserving declared public inputs.",
            "A cache hit should not supply an otherwise missing source file. A reproducible build can rebuild necessary artifacts from declared dependencies when acceleration state is absent.",
            "Build with the cache removed and compare the result with a warm build.",
        ),
        (
            "Diagnose a secret copied into an output file.",
            "Mount isolation does not prevent the command from leaking bytes.",
            "The build command remains responsible for what it writes and prints. Review outputs and layers rather than treating the mount option as a universal secrecy guarantee.",
            "Ask what the RUN command did with the bytes it read.",
        ),
        (
            "Explain why ARG is unsuitable for a password.",
            "Build metadata and history can expose values.",
            "Arguments are configuration inputs and can appear in provenance or logs. Use the explicit secret channel and restrict the command that reads it.",
            "Check where build arguments appear, such as docker history and provenance.",
        ),
        (
            "Describe a dependency acquisition policy.",
            "Locked inputs, deliberate network access and no default private credentials.",
            "Builds should state what they fetch and how its identity is verified. A learner must be able to distinguish a prepared offline run from the initial network-dependent acquisition.",
            "List what the build downloads, from where and how its identity is checked.",
        ),
    ],
    "https://docs.docker.com/build/buildkit/",
    "https://docs.docker.com/build/building/secrets/",
)

add(
    "Multi-stage builds and runtime dependency boundaries",
    """A multi-stage Dockerfile uses more than one FROM instruction. Each stage has its own filesystem and configuration. A builder stage can contain compilers and tests; a final stage can copy only the artifacts required to run. This reduces unnecessary tooling in the shipped image and makes the build-to-runtime boundary inspectable.

Copying a binary is not proof that it is self-contained. Dynamically linked programs require compatible libraries and an appropriate loader. Language runtimes, certificates, timezone data and user identity can also be necessary. A tiny image that fails at startup is not an improvement over a larger correct one.

Multi-stage design is about an explicit artifact contract. Define what the build produces, what tests validate it, what the final image needs and how the final image is exercised. The runtime test must execute the final stage, because tests in the builder can pass using files or tools absent from the shipped stage.""",
    """Name stages with `AS build`, then use `COPY --from=build /path /destination`. The source path refers to that stage’s filesystem, not the local host. `--target` deliberately stops at a named stage for debugging or testing. Do not accidentally distribute a debug stage containing credentials or development-only files.

The following Python example demonstrates stage selection with a text artifact; compiled-language lessons apply the same pattern to actual build output. It does not claim to reduce Python runtime size. A real optimized build requires measuring the resulting image and testing its runtime assumptions.""",
    (
        "Trace a copied artifact",
        "A complete conceptual two-stage recipe writes a public text artifact.",
        "dockerfile",
        'FROM python:3.12-slim AS build\nRUN mkdir /out && printf "prepared\\n" > /out/message.txt\nFROM python:3.12-slim\nCOPY --from=build /out/message.txt /app/message.txt\nCMD ["python", "-c", "print(open(\'/app/message.txt\').read().strip())"]',
        "The final container prints prepared; the final stage only receives the explicitly copied artifact.",
    ),
    (
        "Distinguish builder and final tests",
        "This is a release evidence outline rather than a shell script.",
        "text",
        "builder: compile -> unit tests -> /out/program\nfinal: copy program + runtime dependencies -> start -> acceptance request",
        "A builder success is followed by an actual final-image execution check.",
    ),
    [
        (
            "Locate the filesystem used by COPY --from.",
            "The named build stage.",
            "It is not a host path. This distinction lets the final stage copy exactly the artifact created by the build without relying on a developer’s local output directory.",
            "Find the FROM line with the matching AS name.",
        ),
        (
            "Predict failure when a shared library is omitted.",
            "The final process fails even if builder tests passed.",
            "The loader and dependencies are part of runtime requirements. A successful compile does not prove the executable can start in a different filesystem.",
            "Ask in which stage the program finally runs.",
        ),
        (
            "Design a builder-to-runtime artifact list.",
            "Executable or package plus explicit required runtime assets.",
            "Include certificates or configuration defaults only when needed. The list should be small enough to review and broad enough to run correctly.",
            "List everything the final process opens when it starts and runs.",
        ),
        (
            "Diagnose an accidentally shipped debug target.",
            "Inspect final stage selection and image contents.",
            "A named target changes what is built. Verify the release command and artifact rather than assuming the last intended stage was selected.",
            "Check which stage the build targeted and list the final image's files.",
        ),
        (
            "Explain why a smaller image is not automatically safer.",
            "Correct dependencies, patching and privileges still matter.",
            "Size is one useful measurement, but security also depends on what executes, what it can access and how its dependencies are maintained.",
            "List security properties that do not depend on size.",
        ),
        (
            "Specify final-image acceptance.",
            "Run the exact final image under intended user, mounts and network.",
            "This exposes missing libraries, permissions and files that builder tests can hide. Preserve the exact tested image identity for delivery.",
            "Run the exact final image with its real user, mounts and network.",
        ),
    ],
    "https://docs.docker.com/build/building/multi-stage/",
)

add(
    "CPU architectures, image indexes and cross-platform builds",
    """An architecture is a machine instruction family such as amd64 or arm64. A Linux image can target one or several architectures. A multi-platform image index points to platform-specific images; it is not one binary that magically runs everywhere. The engine selects a compatible image based on platform metadata.

An Apple Silicon laptop commonly runs arm64 natively while many hosted runners use amd64. Emulation can run some foreign-architecture programs, but it adds cost and does not prove native performance or compatibility. A successful source build on one platform is only evidence for that platform’s produced artifact.

Cross-compilation and emulation are distinct strategies. A compiler may emit target binaries while itself running natively; an emulator executes foreign instructions. Some projects need target-specific libraries or test hosts. A release matrix must name which platforms were actually built and executed.""",
    """BuildKit exposes platform arguments such as BUILDPLATFORM and TARGETPLATFORM. A Dockerfile may choose a native builder stage and pass the target into a compiler. Do not use these names as a substitute for correct compiler flags. A multi-platform build also needs an output strategy compatible with your image store or a deliberate export.

The course does not push images. For an optional local experiment, build one selected platform with `docker buildx build --platform linux/arm64 --load` and inspect the result. When the target differs from the host architecture, every RUN step executes under emulation: Docker Desktop includes QEMU emulation, while a Linux engine needs binfmt handlers installed first. A single-platform `--load` works with the default image store; loading a multi-platform index needs the containerd image store. Do not force a foreign platform on the ordinary classroom just to avoid investigating a missing dependency wheel.""",
    (
        "Build and inspect one target platform",
        "From your fixture copy, build one explicit platform and read the result's platform metadata. The arm64 base image is downloaded if it is not already local.",
        "sh",
        'docker buildx build --platform linux/arm64 --load -t ds60-docker-study:arm64 .\ndocker image inspect ds60-docker-study:arm64 --format "{{.Os}}/{{.Architecture}}"',
        "linux/arm64 whatever the host is; on an amd64 host the RUN steps executed under QEMU emulation, which shows the image was packaged for arm64, not that it performs well natively.",
    ),
    (
        "Read the index model",
        "These are illustrative identities, not real downloadable digests.",
        "text",
        "image index\n  linux/amd64 -> image A -> amd64 program\n  linux/arm64 -> image B -> arm64 program",
        "Each platform entry needs its own build and runtime qualification.",
    ),
    [
        (
            "Predict whether Linux implies amd64.",
            "No; operating system and architecture are separate axes.",
            "Linux supports multiple instruction families. A release statement should name both dimensions rather than collapsing them into a single platform label.",
            "Read the platform string as two separate parts.",
        ),
        (
            "Classify cross-compilation and emulation.",
            "Producing target code versus executing foreign code.",
            "A cross-compiler can be native while its output is foreign. Emulation may permit execution but changes performance and cannot establish all native behavior.",
            "Ask which machine executes the target instructions.",
        ),
        (
            "Design a two-platform evidence matrix.",
            "Separate build and execution columns for amd64 and arm64.",
            "Do not fill an execution cell from an index manifest alone. The matrix should make untested combinations visible.",
            "Give each platform separate build and run results.",
        ),
        (
            "Diagnose exec format error.",
            "Inspect architecture and executable format before app logic.",
            "A program can fail before its entry point because the kernel cannot load its format. Changing business logic or increasing memory will not fix that boundary.",
            "Compare the image's architecture with the host's.",
        ),
        (
            "Explain why multi-platform output is not always one --load result.",
            "Exporter and image-store capabilities constrain output.",
            "Understand the selected build driver and local store rather than assuming every multi-platform result can be loaded identically on every engine.",
            "Ask what the local image store can hold.",
        ),
        (
            "Write an honest portability claim.",
            "Name the tested platform and label other platforms unqualified.",
            "Source portability is valuable but weaker than observed execution. Architecture-specific dependencies and runtime behavior need their own evidence.",
            "Name only the platforms you actually built and ran.",
        ),
    ],
    "https://docs.docker.com/build/building/multi-platform/",
)

add(
    "Bridge networks, service DNS and container-to-container traffic",
    """A bridge network connects container interfaces on one engine. A user-defined bridge provides scoped service discovery and connectivity for attached containers. Compose normally creates such a network for a project. DNS maps a service name to a current reachable address; the name is a better application dependency than a temporary container IP.

The app and client in the fixture communicate using `app:8080`. The client does not need the host’s published port. A container replacement can change its address while the service name remains the intended lookup key. Applications must reconnect and resolve names appropriately rather than retaining a dead connection forever.

Network attachment and authorization are different concerns. Sharing a network can permit connectivity, but an application still needs authentication when serving sensitive operations. Conversely, a private network is not a reason to publish every internal port on the host.""",
    """The optional client uses Python’s HTTP library and a short timeout. `docker compose run --rm client` creates a short-lived container attached to the project’s network. It resolves `app`, connects to 8080 and prints the JSON response. The fixture marks that service with a tools profile so it does not remain as another server during ordinary startup.

A DNS resolution failure, a refused connection and a valid HTTP error are different observations. Diagnose from the caller’s namespace, because the host may resolve different names and use a different route.""",
    (
        "Request from a real peer",
        "Run after the app is healthy in the copied fixture.",
        "sh",
        "docker compose -p ds60-docker-study --profile tools run --rm client",
        "The peer prints the app response using `app:8080` without relying on host port 18080.",
    ),
    (
        "Contrast destination scopes",
        "This diagram names the caller for each address.",
        "text",
        "host browser: 127.0.0.1:18080\npeer client: app:8080\napp healthcheck: 127.0.0.1:8080",
        "The same application is observed through three intentionally different paths.",
    ),
    [
        (
            "Predict the name a peer uses for the app.",
            "The Compose service name app.",
            "The project network’s discovery maps that name to current service endpoints. A hardcoded IP creates unnecessary coupling to a container instance.",
            "Look at the service keys in compose.yaml.",
        ),
        (
            "Explain why a peer should not use host loopback.",
            "Its loopback refers to the peer itself.",
            "Network namespace scope applies consistently. A copied browser URL is not a universal address for every caller.",
            "Ask whose loopback 127.0.0.1 is inside the peer.",
        ),
        (
            "Draw the DNS-to-request sequence.",
            "Resolve app, connect to container port, send HTTP request, inspect body.",
            "Separate name resolution from transport and application processing so each failure has a minimal next observation.",
            "Separate name resolution, the connection and the HTTP exchange.",
        ),
        (
            "Diagnose DNS success with connection refusal.",
            "The destination resolved but no reachable listener accepted that port.",
            "Check app state, listen address and target port. Replacing DNS configuration is not justified by a successful resolution.",
            "Check the port the app listens on inside its container.",
        ),
        (
            "Predict a reconnect after app recreation.",
            "A fresh lookup and connection can reach the new instance.",
            "An established connection can fail when its old backend disappears. Client recovery must match operation safety rather than blindly replay every request.",
            "Ask whether the service name or the IP address stays stable.",
        ),
        (
            "Design an internal-only database connection.",
            "Use service DNS and container port without host publication.",
            "Internal peers need a network path, not necessarily a host socket. Keep publication limited to intended user entrypoints and use application credentials as needed.",
            "Decide whether a person on the host needs to reach the database at all.",
        ),
    ],
    "https://docs.docker.com/engine/network/drivers/bridge/",
    "https://docs.docker.com/compose/how-tos/networking/",
)

add(
    "Network isolation, gateways and outbound connectivity",
    """A gateway forwards traffic beyond a local network. Docker bridge networking commonly uses routing and address translation for outbound traffic. The exact host rules depend on the engine and platform. Container traffic can reach external destinations unless its configuration and surrounding policy restrict it.

An internal network reduces external connectivity for its attached network. A service attached to both an external-facing and internal network can intentionally connect two application tiers, but this is not an automatic application firewall. Review the service’s role, listener ports and credentials.

Network mode none creates a container without ordinary external networking. This is useful for a pure computation that needs no DNS or HTTP. Host networking removes a major layer of network isolation and behaves differently across environments; it is not the beginner default or a repair for a wrong port mapping.""",
    """Compose networks are named model objects. Services explicitly join the networks they require. A database can live only on `backend`, while an API joins `frontend` and `backend`. Marking `backend` internal should be tested from the actual callers and engine because host connectivity and DNS details are operational facts.

The fixture uses a single bridge for its first exercises. Sketch multi-tier designs before editing your copy. No chapter asks you to change host firewall rules, install a packet filter or disable existing security software.""",
    (
        "Separate tiers in a model fragment",
        "This illustrates attachment, not a complete deployable app.",
        "yaml",
        "services:\n  api:\n    networks: [frontend, backend]\n  database:\n    networks: [backend]\nnetworks:\n  frontend: {}\n  backend:\n    internal: true",
        "Only api joins both named networks; database has no declared frontend attachment.",
    ),
    (
        "Run a network-free computation",
        "This deliberately needs no external connectivity.",
        "sh",
        'docker run --rm --pull never --network none ds60-docker-study:local python -c "print(sum([2, 4, 6]))"',
        "12 prints without a network request; the computation does not need DNS or a published port.",
    ),
    [
        (
            "Distinguish attachment from published ports.",
            "Joining a network and exposing a host socket are different operations.",
            "A service can communicate with peers without publishing anything. A published port is an additional host-facing path that deserves separate review.",
            "Compare the networks key with the ports key.",
        ),
        (
            "Predict a pure computation with network none.",
            "It succeeds if its files and runtime are already present.",
            "Network isolation does not prevent local arithmetic or file reads. It reveals undeclared dependencies when a program unexpectedly tries to download input.",
            "Ask whether the computation needs anything outside the container.",
        ),
        (
            "Design a frontend/backend attachment table.",
            "Each service joins only the networks needed by its role.",
            "A small explicit table makes unintended paths easier to notice. Avoid putting every component on every network merely for convenience.",
            "List which services must talk to each other.",
        ),
        (
            "Diagnose host-network mode used to hide a mapping error.",
            "Restore the intended isolation and fix the actual address or port.",
            "Changing the network mode can mask the symptom while broadening access. Test the original topology’s contract instead.",
            "Undo host networking and test the original mapping hop by hop.",
        ),
        (
            "Explain why network isolation is not authentication.",
            "Reachability policy and application identity answer different questions.",
            "An allowed caller may still be unauthorized for an operation. Sensitive services need appropriate request authentication and authorization in addition to network placement.",
            "Ask what a caller on the same network can still do.",
        ),
        (
            "Define outbound acceptance for an offline worker.",
            "Prepared local computation succeeds and no external fetch is required.",
            "Offline qualification is about actual inputs and behavior. Merely disconnecting the network does not prove that all future code paths are prepared.",
            "Run the worker with outbound access removed.",
        ),
    ],
    "https://docs.docker.com/engine/network/drivers/none/",
    "https://docs.docker.com/reference/compose-file/networks/",
)

add(
    "Users, UID ownership and writable data paths",
    """A user ID, or UID, is a numeric operating-system identity used for ownership and permission checks. A username is a label mapped to that number. The same username on the host and in a container can refer to different numbers. File access follows effective identities and mount behavior, not matching display names.

Running an application as a non-root user reduces the privileges of its ordinary process. It does not make a hostile program harmless or replace container isolation. The image must arrange readable application files and an intentionally writable data directory before switching users.

Bind mounts expose host ownership more directly than an image’s files. Broad recursive ownership changes on a host project can break unrelated files. Diagnose the exact UID, path and mount before modifying permissions. A named teaching volume can have a deliberately prepared owner without changing your repository ownership.""",
    """The fixture creates `/data`, assigns it to UID 10001 and uses `USER 10001:10001`. Application code is readable and the root filesystem is read-only at runtime. The named volume is mounted at the intended data path. Check the actual mounted permissions rather than assuming every volume driver behaves identically.

A permission denied error is a useful boundary. Inspect identity and path. Do not respond with `chmod -R 777`, privileged mode or a blanket root user. Those changes can make the symptom disappear while invalidating the intended operating contract.""",
    (
        "Declare the image identity",
        "This Dockerfile fragment runs during image construction.",
        "dockerfile",
        "RUN mkdir -p /data && chown 10001:10001 /data\nUSER 10001:10001",
        "The app defaults to the numeric unprivileged identity and has a deliberate data path.",
    ),
    (
        "Inspect effective identity without secrets",
        "The process prints only numeric identity fields.",
        "sh",
        'docker run --rm --pull never ds60-docker-study:local python -c "import os; print(os.getuid(), os.getgid())"',
        "10001 10001 for the maintained fixture image.",
    ),
    [
        (
            "Predict whether matching usernames guarantee file access.",
            "No; numeric identity and permission bits matter.",
            "Names are lookup labels. Compare numeric IDs and the actual mount ownership before diagnosing a cross-environment permission mismatch.",
            "Compare numeric UIDs on both sides, not names.",
        ),
        (
            "Separate read-only code and writable data paths.",
            "/app is code, /data is retained application state.",
            "This layout limits accidental code mutation while allowing the app’s intended state changes. Do not make the entire filesystem writable to support one data directory.",
            "Ask which paths the app must write at runtime.",
        ),
        (
            "Design a non-root image setup sequence.",
            "Create required paths, set ownership, then select the runtime user.",
            "The sequence makes startup deterministic. Deferring broad permission changes to every launch can hide incorrect packaging and require unnecessary privilege.",
            "Create the directories and set ownership before the USER instruction.",
        ),
        (
            "Diagnose a bind-mount permission failure.",
            "Identify mount path, effective UID and exact denied operation.",
            "A targeted observation narrows the repair. Recursive host ownership changes can damage a developer checkout and are not a general container fix.",
            "Compare the host directory's owner with the container's UID.",
        ),
        (
            "Explain why chmod 777 weakens the evidence.",
            "It allows more writers instead of proving intended ownership.",
            "The repaired system no longer tests the same access contract. Prefer the smallest permission change that grants the required operation to the intended identity.",
            "Ask who else can write after the change.",
        ),
        (
            "Write a permission acceptance check.",
            "Non-root process can write data and cannot mutate packaged code.",
            "Both positive and negative checks matter. Successful persistence alone does not prove that code paths remain protected from accidental writes.",
            "Test one write that must succeed and one that must fail.",
        ),
    ],
    "https://docs.docker.com/reference/dockerfile/#user",
    "https://docs.docker.com/engine/security/userns-remap/",
)

add(
    "Backups, restores and proving data recovery",
    """A backup is a retained copy intended for recovery. A restore is the process of reconstructing usable state from that copy. The existence of an archive file does not prove that recovery works. A useful backup procedure defines consistency, scope, identity, retention and an independent restore test.

A filesystem copy of a live database may be inconsistent even when every file is readable. Applications have their own transactional state and backup protocols. The fixture’s small JSON counter can be exported while the app is stopped, making the consistency boundary easy to explain. That procedure must not be generalized to every database.

Back up only the disposable study volume in this chapter. The main classroom’s learner progress is separate. Never use global volume pruning as part of a backup exercise, and never overwrite the only good copy while testing a restore.""",
    """The fixture README includes an export using the app image’s Python standard library and a separate restore-target volume. Stop the app first, export a small JSON record to the learner copy, inspect its schema, then test restoration into a new owned volume. Record checksums and expected values without treating a checksum as proof of application semantics.

A recovery point objective describes tolerable data loss measured in time. A recovery time objective describes the acceptable time to restore service. They guide backup frequency and practice, but a local teaching experiment only measures its own small workload.""",
    (
        "Read the recovery contract",
        "The sample values are synthetic and make no claim about your volume.",
        "json",
        '{"schema_version": 1, "counter": 7}',
        "A restore must preserve the schema and the counter value, not merely recreate a file with the same name.",
    ),
    (
        "Plan an independent restore",
        "Use the fixture README procedure on a separate target.",
        "text",
        "stop writer -> export owned volume -> validate JSON -> restore into new volume -> start reader -> compare value",
        "The original volume remains untouched while the new target proves recovery.",
    ),
    [
        (
            "Distinguish backup creation and restore acceptance.",
            "An archive exists versus a new instance can use recovered data.",
            "The latter catches missing files, invalid formats and wrong ownership that a successful copy can hide.",
            "Ask what an archive file proves about recovery.",
        ),
        (
            "Predict the risk of copying a live transactional database directory.",
            "The copy may not represent a consistent transaction boundary.",
            "Databases can coordinate several files and buffered writes. Use their documented backup mechanism instead of assuming a file copy captures a valid snapshot.",
            "Ask what the database is doing while you copy its files.",
        ),
        (
            "Design a separate restore target.",
            "A new owned volume with no overwrite of the source.",
            "The test should not destroy the only working state. Keeping the source untouched also makes comparison and rollback possible.",
            "Restore into a new volume and never over the source.",
        ),
        (
            "Diagnose a valid checksum with invalid application data.",
            "Byte identity does not establish schema or semantic correctness.",
            "A checksum proves a relationship between byte sequences. The application must still parse and validate the data it will use.",
            "Ask what a checksum compares and what the application checks.",
        ),
        (
            "Explain RPO and RTO using the counter lab.",
            "Allowed lost updates and time to a usable restored instance.",
            "Name the workload and measurement period. A small local result cannot be advertised as a production recovery guarantee for larger or different data.",
            "Measure the lost increments and the minutes until a restored app works.",
        ),
        (
            "Produce a recovery evidence packet.",
            "Source identity, export hash, restore target, parsed value and cleanup record.",
            "The packet ties the copy to a particular source and proves independent use. Cleanup should remove only the disposable restore resources after review.",
            "Record the source identity, archive hash, restore target and the value the app reads.",
        ),
    ],
    "https://docs.docker.com/engine/storage/volumes/#back-up-restore-or-migrate-data-volumes",
)

add(
    "Resource limits, contention and honest performance experiments",
    """CPU and memory are finite resources shared by containers and other host workloads. Resource controls constrain or weight access; they do not automatically reserve a dedicated physical machine. A process can be throttled, run slowly under contention or be killed after memory pressure, depending on its settings and the kernel.

A CPU quota limits how much CPU time a cgroup can consume over a period. A memory limit constrains accounted memory, with behavior influenced by swap and engine configuration. Containers still share the underlying host or VM budget. Allocating a large limit in Compose does not create physical RAM.

Performance experiments need controlled inputs and measurements. A single fast run can benefit from caches, idle neighbors or a different architecture. Record the workload, image, limits, host allocation and several runs. Avoid deliberately exhausting the host as a lesson demonstration.""",
    """The fixture uses modest `mem_limit`, `cpus` and `pids_limit` settings. These are runtime constraints on the teaching process, not proof of a production capacity plan. `docker stats --no-stream` gives a point-in-time view. Observe trends with bounded sampling if you need a rate, and distinguish cumulative values from instantaneous ones.

For a safe experiment, compare a short CPU computation at two modest limits in the disposable project. Keep data size fixed and avoid claiming that a single elapsed time isolates every scheduler effect. Memory fault experiments require deliberately small inputs and a controlled target.""",
    (
        "Declare bounded teaching resources",
        "This is a Compose service fragment.",
        "yaml",
        "mem_limit: 128m\ncpus: 0.5\npids_limit: 64",
        "The app runs within explicit small constraints; these do not reserve half a physical core exclusively.",
    ),
    (
        "Read a bounded resource sample",
        "Select only the owned app container.",
        "sh",
        'docker stats --no-stream "$(docker compose -p ds60-docker-study ps -q app)"',
        "A point-in-time sample for the owned container; it is not a full capacity study.",
    ),
    [
        (
            "Compare a CPU limit with dedicated hardware.",
            "A quota constrains time; it does not grant exclusive cores.",
            "Shared scheduling and host contention remain. State the actual control rather than translating it into an unsupported performance guarantee.",
            "Ask what cpus: 0.5 limits: cores or CPU time per period.",
        ),
        (
            "Predict the effect of insufficient engine VM memory.",
            "Container limits cannot compensate for missing host capacity.",
            "The VM allocation bounds the resources the engine can manage. Inspect that layer when several individually modest containers compete.",
            "Compare the engine VM's memory setting with the container's mem_limit.",
        ),
        (
            "Design a controlled CPU comparison.",
            "Same input and image, one changed limit, several bounded measurements.",
            "Control enough variables to make the comparison interpretable. Keep architecture and cache state in the evidence record.",
            "Change only the CPU limit and repeat each measurement several times.",
        ),
        (
            "Diagnose slowness without assuming memory failure.",
            "Compare CPU throttling, I/O, requests and memory observations.",
            "Multiple mechanisms produce slow responses. A memory increase is unjustified when the first failing observation is elsewhere.",
            "Collect CPU throttling, I/O wait, request timing and memory figures before choosing a cause.",
        ),
        (
            "Explain why a single docker stats sample is limited.",
            "It does not capture the whole workload or historical peaks.",
            "Sampling frequency and timing influence what is visible. Use a bounded series and application timings when investigating an intermittent issue.",
            "Ask what happened before and after the moment the sample was taken.",
        ),
        (
            "Define a safe resource stress boundary.",
            "Small fixed workload, timeout and owned disposable target.",
            "The goal is to observe a mechanism, not to consume all host resources. Stop when the named failure or performance condition is established.",
            "Choose a fixed amount of work, a timeout and a container you own.",
        ),
    ],
    "https://docs.docker.com/engine/containers/resource_constraints/",
)

add(
    "Read-only filesystems, capabilities and least privilege",
    """Linux capabilities divide some traditional root privileges into named permissions. A process can run without unnecessary capabilities even when an image was built by root. A read-only root filesystem limits writes to packaged paths, while explicit mounts provide the few writable locations the application requires.

`no-new-privileges` prevents a process from gaining privileges through mechanisms such as set-user-ID execution. A process-ID limit bounds process creation. These controls address different mechanisms. Combining them intentionally is more useful than copying a hardening block without understanding which operation each setting permits or refuses.

The local classroom executes trusted learner code and is not a public hostile-code hosting boundary. The Docker study fixture still demonstrates least privilege: no engine socket, no privileged mode, non-root identity, dropped capabilities, read-only root and bounded temporary storage. These settings must be tested against actual functionality.""",
    """In Compose, `cap_drop: [ALL]` drops the default capability set. `read_only: true` changes the root mount. `tmpfs` gives a small temporary path. The app listens on an unprivileged port and writes retained data only to its declared volume. No control should be disabled merely to hide a missing permission contract.

A useful hardening test has two halves: intended behavior still works, and an unintended operation fails. The fixture should answer health and preserve its counter, while writing a new file under `/app` should fail. A control that silently prevents all useful work is not a successful configuration.""",
    (
        "Inspect the fixture hardening model",
        "These settings belong to the app service.",
        "yaml",
        "read_only: true\ncap_drop: [ALL]\nsecurity_opt:\n  - no-new-privileges:true\ntmpfs:\n  - /tmp:rw,noexec,nosuid,size=16m",
        "The app has narrow writable locations and no requested Linux capabilities.",
    ),
    (
        "Separate positive and negative acceptance",
        "This is the intended evidence pair.",
        "text",
        "positive: GET /healthz succeeds; counter persists\nnegative: writing /app/unexpected.txt fails",
        "Least privilege retains the app contract while denying unrelated writes.",
    ),
    [
        (
            "Map each hardening setting to its mechanism.",
            "Mount writes, capabilities, privilege gain and temporary storage.",
            "The settings are complementary rather than synonyms. A clear mapping helps diagnose which boundary rejected an unintended operation.",
            "Take each security line in compose.yaml and name the kernel feature behind it.",
        ),
        (
            "Predict whether read-only root prevents volume writes.",
            "A separately writable data mount can still allow them.",
            "Permissions are applied to the mounted path involved. The design deliberately separates immutable code from intended mutable state.",
            "List the container's mounts and the write policy of each.",
        ),
        (
            "Write a least-privilege acceptance pair.",
            "One required action succeeds and one forbidden action fails.",
            "Checking only failure could describe a broken application. Checking only success could miss unnecessary access.",
            "Pick one action the app needs and one it must never do, and test both.",
        ),
        (
            "Diagnose an app that needs an undocumented cache directory.",
            "Identify the path and provide a bounded intended mount if justified.",
            "Do not make the whole root filesystem writable. Determine whether the cache is temporary, durable or avoidable, then choose the smallest correct storage channel.",
            "Find the path in the error message before adding any mount.",
        ),
        (
            "Explain why privileged mode is inappropriate here.",
            "It grants broad access unrelated to the HTTP fixture.",
            "A privileged container changes the trust boundary substantially. The lesson’s app has no legitimate requirement for device or host-administration capabilities.",
            "List what --privileged grants and compare it with what the HTTP server needs.",
        ),
        (
            "Review a hardening change without overstating security.",
            "State controls tested and the trusted-local-code boundary.",
            "No finite checklist proves a universal sandbox. Report what the actual configuration restricts and which threats remain outside its supported use.",
            "Name the settings you tested and the threats they do not address.",
        ),
    ],
    "https://docs.docker.com/engine/security/",
    "https://docs.docker.com/reference/compose-file/services/#cap_drop",
)

add(
    "Rootless engines, user namespaces and host trust",
    """Rootless mode runs the engine and containers without a root daemon under the user’s identity. User namespaces map container user IDs to different host IDs. These mechanisms can reduce host privilege exposure, but they alter networking, storage and resource-control details that must be qualified on the chosen host.

Root inside a container is not automatically identical to host root under every configuration. It is also not automatically harmless. Capabilities, namespace mappings, mounts and daemon access determine what the process can do. The engine socket is especially important because an authorized client can ask the daemon to create containers with powerful host access.

The teaching application should not receive that socket. Docker lessons run as explicit host commands in a learner-owned project. Ordinary browser execution cannot install an engine, create sibling containers or inspect unrelated workloads. This separation is part of the product design.""",
    """Rootless mode is an engine installation choice, not a Compose flag that magically converts an already running rootful daemon. Inspect the engine’s documented mode and test the app’s required capabilities. Do not require a learner to reconfigure their working engine for this chapter.

Compare the trust paths: browser code talks to a limited classroom endpoint; host Docker client talks to the daemon; daemon creates processes and mounts. Mounting the daemon socket into the classroom would connect those paths and expand browser code’s authority far beyond a lesson pad.""",
    (
        "Trace authority without changing the engine",
        "This is a conceptual flow.",
        "text",
        "host user -> Docker client -> engine API -> containers and mounts\nbrowser lesson -> bounded classroom API -> declared lesson runtime",
        "The second path does not acquire the first path merely because the classroom itself uses Docker.",
    ),
    (
        "Identify a dangerous mount in review",
        "Do not add this illustrative configuration.",
        "yaml",
        "volumes:\n  - /var/run/docker.sock:/var/run/docker.sock",
        "This would expose engine control and is absent from the classroom and study app design.",
    ),
    [
        (
            "Distinguish rootless mode from a non-root app USER.",
            "Engine privilege versus process identity inside one container.",
            "Both can be useful, but they apply at different layers. An app USER instruction does not change the daemon installation.",
            "Ask which process runs as root in each setup: the daemon or the app.",
        ),
        (
            "Predict why low-port or resource behavior may differ.",
            "Rootless networking and delegated controls can have limitations.",
            "Consult the chosen engine’s supported configuration and test required behavior. Do not assume rootful observations transfer unchanged.",
            "Ask what a rootless daemon cannot do that a root daemon can, such as binding ports below 1024.",
        ),
        (
            "Draw the daemon-socket authority path.",
            "Socket access can permit host-impacting container requests.",
            "The risk comes from what the API can create and mount. A read-only-looking filesystem mount of a socket does not turn the daemon protocol into a read-only API.",
            "Follow a docker run request from the socket to the daemon to the host.",
        ),
        (
            "Diagnose a lesson requiring engine access from the browser.",
            "Move it to an explicit host lab with ownership boundaries.",
            "The learning objective does not justify exposing the engine to arbitrary lesson code. A host worksheet can teach the operation honestly.",
            "Ask why the classroom never receives an engine socket.",
        ),
        (
            "Explain user namespace ID mapping.",
            "Container numeric IDs map to a separate host range.",
            "Ownership must be interpreted through the mapping. Matching a container UID to a host filename owner by name alone is insufficient.",
            "Compare a UID inside the container with its mapped UID on the host.",
        ),
        (
            "State a support claim for a new rootless setup.",
            "Actual app build, network, storage and cleanup observations.",
            "Configuration support on paper is weaker than runtime acceptance. Qualify the specific host setup without advertising untested engines or modes.",
            "List the build, network, storage and cleanup checks you actually ran.",
        ),
    ],
    "https://docs.docker.com/engine/security/rootless/",
    "https://docs.docker.com/engine/security/userns-remap/",
)

add(
    "Image names, digests and an offline transfer",
    """An image reference can contain a registry, repository, tag and digest. A tag is a mutable name. A digest identifies content according to its hash format. Tags are convenient for humans; immutable identities are stronger for repeatable delivery and audit.

A local image cache is not a registry. Building an image with a tag does not upload it. `docker image save` exports image data into an archive, and `docker image load` imports an archive. This can support an offline machine after deliberately preparing the correct platform and dependencies.

An archive must be treated as executable supply-chain input. Verify its source and checksum through a trustworthy channel, inspect the imported reference, and execute only the intended image. A checksum copied from the same untrusted source is an integrity hint, not independent authenticity.""",
    """The course uses local builds and performs no registry pushes. Save only the study image to a file in your learner copy. Record the image ID, platform and archive checksum. Load into a deliberately chosen compatible engine and use `--pull never` to ensure the next run does not silently fetch a missing dependency.

An offline application can still contain code that attempts network requests. Image presence is only one prerequisite. The lesson examples use local synthetic inputs so the default application behavior does not depend on external APIs.""",
    (
        "Export one local teaching image",
        "The destination is a new file in the learner copy.",
        "sh",
        "docker image save -o study-image.tar ds60-docker-study:local",
        "An archive containing the selected local image; no registry operation occurs.",
    ),
    (
        "Import and run deliberately offline",
        "Use only your verified archive on a compatible engine.",
        "sh",
        "docker image load -i study-image.tar\ndocker run --rm --pull never --network none ds60-docker-study:local python -c \"print('offline ready')\"",
        "The imported local runtime prints offline ready without an external request.",
    ),
    [
        (
            "Compare tag and digest identity.",
            "A movable label versus content identity.",
            "A tag can resolve to new bytes later. Preserve immutable identity when you need to tie execution evidence to a specific artifact.",
            "Ask which of the two can point to different bytes tomorrow.",
        ),
        (
            "Predict whether docker build uploads an image.",
            "It does not push merely because a tag was assigned.",
            "Building and publishing are separate operations. The course intentionally stays local so learners can inspect output without registry credentials.",
            "Check whether docker build contacts a registry when it tags.",
        ),
        (
            "Design an offline handoff record.",
            "Archive checksum, image identity, platform and expected command.",
            "The receiver needs enough context to verify both bytes and compatibility. A filename alone does not establish which program or architecture the archive contains.",
            "Write down what the receiver needs to verify and run the archive.",
        ),
        (
            "Diagnose a missing image with --pull never.",
            "The run fails rather than silently downloading.",
            "This is useful evidence of an incomplete prepared environment. Repair the preparation deliberately instead of hiding the dependency with an implicit pull.",
            "Read what --pull never does when the image is missing.",
        ),
        (
            "Explain checksum integrity versus authenticity.",
            "Matching bytes do not identify a trustworthy publisher by themselves.",
            "An attacker could supply both a modified archive and its hash. Trust requires an independent source or a signature verification policy.",
            "Ask who could have produced bytes with the same checksum.",
        ),
        (
            "Define offline acceptance for the study app.",
            "Imported image starts with local data and no required external services.",
            "The test should exercise the app behavior you plan to teach. A trivial arithmetic command proves the runtime is present but not every feature of a network-dependent application.",
            "Disconnect from the network and start the imported image.",
        ),
    ],
    "https://docs.docker.com/reference/cli/docker/image/save/",
    "https://docs.docker.com/reference/cli/docker/image/load/",
    "https://docs.docker.com/dhi/core-concepts/digests/",
)

add(
    "Compose overrides, profiles and configuration review",
    """An override file changes a base Compose application model. Profiles select optional services. Both mechanisms can make one project support development, teaching and operations tasks, but they also create more possible effective configurations to review.

The effective model matters more than any one input file. Merge rules differ for scalar values, mappings and sequences. An override can unexpectedly add ports or mounts rather than replace the intended list in the way a beginner assumes. Always inspect or validate the combined model before applying it.

Profiles are not a security boundary. A service omitted from the default startup is still available when explicitly selected or enabled. Use profiles for intentional optional tools and workloads, not for hiding privileged services in a file and assuming they cannot run.""",
    """The fixture’s client has the tools profile. Ordinary `up` starts the app; an explicit tools invocation runs the peer check. For an override experiment, copy the fixture and change only a public message or unused loopback host port. Use `-f` in a fixed order and validate that same order.

Do not print a fully rendered production model containing secrets into a public log. This lesson uses synthetic public values. The goal is to explain which input supplied each final field and how a reviewer can reproduce the exact model.""",
    (
        "Enable the optional client intentionally",
        "The fixture keeps this service out of ordinary startup.",
        "sh",
        "docker compose -p ds60-docker-study --profile tools run --rm client",
        "A short peer request is executed; the client container is removed after completion.",
    ),
    (
        "Review a combined model",
        "Use two files in your own scratch copy.",
        "sh",
        "docker compose -p ds60-docker-study -f compose.yaml -f compose.study.yaml config --quiet",
        "The exact ordered combination validates without creating resources.",
    ),
    [
        (
            "Distinguish profiles and overrides.",
            "Service selection versus model composition.",
            "A profile determines which optional services participate; an override modifies service and resource definitions. They can be used together but answer different questions.",
            "Ask which one chooses services and which one changes service definitions.",
        ),
        (
            "Predict ordinary startup with the tools profile disabled.",
            "The app starts and the optional client is not a persistent service.",
            "The profile communicates intent. An explicit run of the client remains possible, so its commands still need review.",
            "Check which services have a profiles key.",
        ),
        (
            "Create an override for a public message.",
            "Only the intended environment value changes in the effective model.",
            "Keep the experiment narrow enough to inspect. Avoid mixing a message edit with mounts, privilege changes and network modifications.",
            "Put only the changed environment value in the override file.",
        ),
        (
            "Diagnose an unexpected extra port after merging.",
            "Inspect merge behavior and the complete effective ports list.",
            "Do not assume a sequence was replaced. Model composition must be understood for the actual Compose version and fields used.",
            "Run docker compose config with the same files and read the merged ports.",
        ),
        (
            "Explain why a profile is not access control.",
            "Someone with engine and project access can enable it.",
            "Security should come from permissions and the absence of unnecessary authority, not from an optional default selection.",
            "Ask who can run docker compose --profile tools.",
        ),
        (
            "Write a reviewable configuration launch record.",
            "Ordered files, profiles, project name and safe resolved settings.",
            "This makes the effective deployment reproducible. Retain private values separately rather than embedding them in shared evidence.",
            "Record the files in order, the profiles and the project name you used.",
        ),
    ],
    "https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/",
    "https://docs.docker.com/compose/how-tos/profiles/",
)

add(
    "Intermediate capstone: a recoverable two-tier teaching system",
    """This capstone adds peer discovery, constrained execution and a recovery test to the first app. The system still fits on one page: app serves JSON and owns its counter volume; client observes app through service DNS; the browser observes the loopback-published endpoint. Keeping these paths small makes failures explainable.

A recoverable system is more than a system that restarts. It has an identified durable state, a consistency boundary, a backup, an independent restore target and a bounded procedure to regain useful behavior. A second-tier client must also handle a dependency being temporarily unavailable without replaying unsafe writes.

Your deliverable is a short operator guide plus evidence, not a collection of screenshots. A future reader should know which project the commands affect, which volume contains state, how to inspect a failure, and what they can remove without losing the retained counter.""",
    """Work only in the copied fixture. Verify host and peer requests, record the non-root user and read-only configuration, export the stopped app’s counter, restore into a distinct target and compare. A deliberately wrong service port in a scratch client should fail with a bounded transport error.

Do not broaden the project into a real database cluster for this exercise. The purpose is to integrate mechanisms already learned, then clearly state the limitations that a database, public endpoint or multi-host deployment would add.""",
    (
        "Observe both traffic paths",
        "The peer request uses service DNS.",
        "sh",
        "docker compose -p ds60-docker-study up -d --wait\ndocker compose -p ds60-docker-study --profile tools run --rm client",
        "The browser and peer see the same public message through different endpoints.",
    ),
    (
        "Review the operational state machine",
        "The backup and restore details are in the fixture README.",
        "text",
        "ready -> quiesce writer -> export -> validate -> restore separate target -> verify -> resume\nfailure -> preserve logs -> identify phase -> targeted repair -> recheck",
        "Each transition has a specific observation and an owned resource scope.",
    ),
    [
        (
            "Predict which resources are durable.",
            "Only the intended named volume and explicit backup files.",
            "Containers, peer client instances and project networks are replaceable. Do not accidentally rely on writable-layer state when describing recovery.",
            "List which resources survive docker compose down.",
        ),
        (
            "Change only the peer target port in a scratch copy.",
            "The request fails within its timeout while app remains healthy.",
            "The controlled fault separates internal routing from application readiness. Preserve the error rather than changing multiple network settings at once.",
            "Change the port only in the client's request and leave the app unchanged.",
        ),
        (
            "Build an independent restore demonstration.",
            "New target state equals the exported counter while source remains intact.",
            "Recovery evidence requires use of the restored data. A copied file existing at a path is not enough without parsing and an application-level check.",
            "Restore into a new volume and compare it with the source.",
        ),
        (
            "Diagnose a passing host request with failing peer request.",
            "Inspect service DNS, network attachment and internal target port.",
            "The two paths share an application but have different discovery and routing. Their disagreement localizes the fault.",
            "Compare the host's path to the app with the peer's path.",
        ),
        (
            "Explain the limits of this single-engine design.",
            "No multi-host failover or database consistency guarantee is claimed.",
            "A small lab teaches the mechanisms honestly. Production requirements need additional architecture and qualification rather than a larger marketing claim.",
            "List what fails if the engine host goes down.",
        ),
        (
            "Write a beginner operator handoff.",
            "Setup, evidence, failure diagnosis, backup/restore and scoped cleanup.",
            "A good handoff is executable by a reader with the documented prerequisites. It names state retention explicitly and avoids ambient context assumptions.",
            "Write each step as a command plus the evidence that shows it worked.",
        ),
    ],
    "https://docs.docker.com/compose/how-tos/networking/",
    "https://docs.docker.com/engine/storage/volumes/",
)

add(
    "Registries, tags, digests and deliberate publication",
    """A registry stores image manifests and blobs for distribution. A repository groups related image names inside that registry. Authentication determines who can access the registry; authorization determines which operations that identity may perform. Public pull access is different from permission to overwrite a release tag.

A local tag does not publish anything. Publication is a deliberate operation with credentials, destination, retention and rollback implications. This course uses local builds and offline exports by default. You can study a registry workflow without pushing the course or your private code anywhere.

Mutable tags such as latest are useful conveniences but weak deployment identities. A release procedure should resolve or record an immutable digest and relate it to source, build inputs and acceptance evidence. A registry availability problem should not cause an operator to deploy a different unreviewed image merely because its tag looks similar.""",
    """Read a reference as registry/repository:tag or registry/repository@digest. A tag may point to a platform index, which then selects a platform manifest. Keep that level of identity clear when comparing builds. Registry credentials belong in an approved credential store or short-lived CI mechanism, never in a Dockerfile.

The examples below inspect local metadata and a conceptual release record. They intentionally contain no push command. If you later publish your own project, make the destination and intended visibility explicit and verify the uploaded immutable identity after publication.""",
    (
        "Inspect local tags without publication",
        "This uses the locally built study image only.",
        "sh",
        'docker image inspect ds60-docker-study:local --format "{{json .RepoTags}}"',
        "The local tag is visible; this does not prove any registry has a copy.",
    ),
    (
        "Design a release identity record",
        "Use real verified values in a private or public record as appropriate.",
        "json",
        '{"source_revision":"recorded revision","platform":"linux/amd64","image_digest":"recorded immutable digest","acceptance":"separate test receipt"}',
        "Each field has a distinct source of evidence; placeholder text is not a qualified release.",
    ),
    [
        (
            "Parse the components of an image reference.",
            "Registry, repository, optional tag and optional digest.",
            "The registry location and image identity should be unambiguous before any authenticated operation. A familiar short tag can hide a different destination.",
            "Split a reference at the first slash, the colon and the @ sign.",
        ),
        (
            "Predict whether adding a local tag uploads bytes.",
            "No; local naming and registry publication are separate.",
            "This separation lets you prepare and inspect an artifact without distributing it. Publication requires its own intentional command and authorization.",
            "Check whether docker tag contacts a registry.",
        ),
        (
            "Design a release identity record.",
            "Source revision, immutable image identity, platform and tested behavior.",
            "The record should join source and runtime evidence. A tag alone cannot preserve that relationship if it is later moved.",
            "List what someone needs to identify exactly what you tested.",
        ),
        (
            "Diagnose an overwritten mutable release tag.",
            "Compare recorded digest with the currently resolved artifact.",
            "The same label can name different content. Resolve the exact identity before concluding that earlier acceptance evidence applies.",
            "Compare the digest you recorded with what the tag resolves to now.",
        ),
        (
            "Explain why credentials do not belong in the build context.",
            "They can be transferred, layered or logged beyond the intended lifetime.",
            "Registry access is an operation credential, not application source. Use a reviewed credential channel and avoid printing values during diagnostics.",
            "Ask what happens to files in the build context during a build.",
        ),
        (
            "Describe a safe publication review without performing it.",
            "Explicit destination, visibility, immutable artifact and rollback plan.",
            "A reviewable proposal is concrete enough to approve. It should not upload a different artifact later or silently change repository visibility.",
            "Write the destination, visibility, artifact identity and rollback before any push.",
        ),
    ],
    "https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-registry/",
    "https://docs.docker.com/reference/cli/docker/login/",
)

add(
    "Software bills of materials and image provenance",
    """A software bill of materials, or SBOM, lists components included in an artifact. Provenance records how an artifact was built, including inputs and builder information according to its format. Neither document by itself proves that every component is safe or that the claimed builder was trustworthy.

These records become useful when tied to an immutable artifact identity and a verification policy. An SBOM for yesterday’s tag is not necessarily an SBOM for today’s bytes. A provenance claim needs a trustworthy issuer and integrity verification before it can support a release decision.

The teaching image has a deliberately small application surface but still inherits a base operating system and Python runtime. Supply-chain review includes those dependencies. Copying only one server file does not mean the final image contains only one software component.""",
    """BuildKit creates attestations at build time and attaches them to the image index as in-toto JSON. Minimal provenance (`mode=min`) is added by default; `--sbom=true` adds an SPDX SBOM produced by a scanner plugin, and `--provenance=mode=max` records a detailed build statement. Attestations need a builder that can store an image index: the default docker driver requires the containerd image store, a docker-container builder works with either store, and `--push` keeps them in the registry. The `local` and `tar` exporters write them as JSON files, such as `sbom.spdx.json`, in the root of the export. For a pushed image, `docker buildx imagetools inspect IMAGE --format "{{ json .SBOM.SPDX }}"` prints the SBOM without pulling the image.

The scanner itself runs as an image that is downloaded on first use, so treat SBOM generation as a deliberate online step. Compare the exported SBOM with a component inventory derived from the Dockerfile, and note what the source recipe cannot reveal without resolving the base image. Keep metadata generation, artifact delivery and verification as separate steps, and do not fabricate a signed result or claim a scanner passed when it was not run.""",
    (
        "Export an SBOM next to the build result",
        "Run this deliberately from your fixture copy; the scanner and base images may be downloaded on first use.",
        "sh",
        "docker buildx build --sbom=true --output type=local,dest=../ds60-sbom-out .\nls ../ds60-sbom-out/sbom.spdx.json",
        "The export directory holds the image filesystem with sbom.spdx.json at its root; its package list includes the inherited Python runtime and operating-system packages, not only server.py.",
    ),
    (
        "Separate evidence objects",
        "The links are conceptual relationships.",
        "text",
        "source + builder inputs -> image digest\nimage digest -> SBOM\nimage digest -> provenance statement -> issuer verification policy",
        "Documents must refer to the same immutable artifact to support one release claim.",
    ),
    [
        (
            "Distinguish SBOM and provenance.",
            "Component inventory versus build-origin evidence.",
            "They answer complementary questions. An inventory does not explain who built the artifact; a build statement does not enumerate every vulnerability.",
            "Ask which document lists contents and which describes the build.",
        ),
        (
            "Predict what a source-only inventory misses.",
            "Resolved base packages and exact inherited versions.",
            "A Dockerfile tag is an input reference, not a full final filesystem inventory. Resolve and inspect the actual artifact for stronger evidence.",
            "Compare the Dockerfile's FROM line with what the base image actually contains.",
        ),
        (
            "Design an evidence linkage table.",
            "Every record names the same image digest and platform scope.",
            "This prevents acceptance, inventory and provenance from drifting across mutable tags or architecture-specific artifacts.",
            "Make every row refer to the same digest and platform.",
        ),
        (
            "Diagnose an unsigned provenance statement from an unknown source.",
            "It is an untrusted claim until verified under a policy.",
            "Structured metadata is easy to produce. Trust depends on issuer identity, integrity and the permitted build process, not the presence of JSON fields.",
            "Ask who signed the statement and how you would verify it.",
        ),
        (
            "Explain exporter limitations honestly.",
            "Attestation generation and preservation depend on the selected workflow.",
            "Test the actual output route. A feature flag in a build command does not prove a downstream registry or local archive retains the expected metadata.",
            "Check whether your builder driver and image store keep attestations.",
        ),
        (
            "Write a supply-chain review for the fixture.",
            "Known source, resolved base, component record and actual acceptance limits.",
            "Keep unknowns visible. A small educational artifact deserves clear provenance without pretending it has passed a production assurance program.",
            "Separate what you know, what you resolved and what remains untested.",
        ),
    ],
    "https://docs.docker.com/build/metadata/attestations/",
    "https://docs.docker.com/build/metadata/attestations/sbom/",
)

add(
    "Vulnerability findings, patching and dependency updates",
    """A vulnerability finding connects an affected component version to a published issue under a scanner’s knowledge and matching rules. It is evidence for investigation, not a complete exploitability assessment. False matches, missing packages, runtime exposure and available fixes all influence the response.

Patching an image generally means rebuilding from updated inputs and replacing containers with the new image. Installing packages interactively inside a running container makes an untracked difference that disappears on recreation. The maintained build recipe and lock inputs must describe the repair.

A rebuild can introduce regressions as well as fixes. Use a small update scope, preserve the old immutable artifact, run the relevant tests and verify the actual final image. Do not claim that a passing scan proves absence of all vulnerabilities or that an unfixed low-severity finding is automatically harmless.""",
    """Classify findings by component, installed version, fixed version if available, application reachability and required action. Keep the scanner database timestamp and artifact digest. A tag-based report becomes stale when the tag changes.

For this lesson, use a synthetic finding table and prepare an update plan without downloading a scanner or changing the engine. Actual scanning is an optional explicitly prepared tool workflow. The course does not invent a zero-findings badge for an unscanned image.""",
    (
        "Read a synthetic finding",
        "The package and versions are illustrative.",
        "json",
        '{"component":"example-library","installed":"1.0","fixed":"1.1","artifact":"specific image digest","status":"requires review"}',
        "The record is input to a patch decision, not proof of exploitation or a completed fix.",
    ),
    (
        "Trace a reproducible patch",
        "This is the required sequence.",
        "text",
        "update declared input -> build new image -> run tests -> inspect exact digest -> replace owned container -> verify behavior",
        "An interactive package install inside the old container is not the maintained release artifact.",
    ),
    [
        (
            "Separate vulnerability presence and exploitability.",
            "A matched affected component versus a demonstrated reachable exploit condition.",
            "Both matter, but neither should be fabricated. A finding needs triage even when immediate exploitability is uncertain.",
            "Ask whether the vulnerable code is reachable in this app.",
        ),
        (
            "Predict why an interactive patch disappears.",
            "Container recreation returns to the packaged image inputs.",
            "The writable layer is not the source of truth for a reproducible release. Capture the change in the build recipe and rebuild.",
            "Ask what docker compose up does to a container's writable layer.",
        ),
        (
            "Design a minimal base-image update.",
            "Change the resolved base deliberately and rerun relevant acceptance.",
            "Keep other changes small so failures can be attributed. Record both old and new identities for rollback and comparison.",
            "Change the base image reference and rerun the same acceptance checks.",
        ),
        (
            "Diagnose a scan report attached only to a mutable tag.",
            "Resolve the exact scanned artifact before using the result.",
            "The current tag may refer to different bytes. Evidence must be tied to immutable identity and the scanner’s knowledge date.",
            "Resolve the tag to a digest before trusting the report.",
        ),
        (
            "Explain why zero findings is not a universal security proof.",
            "Scanners have scope and knowledge limitations.",
            "Application flaws, configuration issues and unknown vulnerabilities may be outside the scanner’s matching rules. State the actual tool result and limits.",
            "Ask what the scanner's database and matching rules cover.",
        ),
        (
            "Write a patch decision record.",
            "Finding, affected artifact, chosen action, tests and residual risk.",
            "The record should make the operational decision reviewable. It should not replace evidence with an unqualified claim that everything is now safe.",
            "Record the finding, the artifact, the decision, the tests and the remaining risk.",
        ),
    ],
    "https://docs.docker.com/build/building/best-practices/",
    "https://docs.docker.com/scout/explore/exceptions/",
)

add(
    "CI builds, test layers and artifact promotion",
    """Continuous integration runs repeatable checks when source changes. A container pipeline can validate source, build an image, test that image and preserve evidence. These are separate stages: passing source tests does not prove the packaged filesystem or startup command is correct.

Artifact promotion means moving an already tested immutable artifact through delivery stages rather than rebuilding slightly different bytes for each stage. Rebuilding with mutable dependencies can break the connection between the tested image and the deployed image. Record the exact source, build inputs and output identity.

Parallel test jobs can reduce elapsed time, but shared fixtures must remain isolated or intentionally serialized. A database test that resets a shared schema cannot be blindly sharded with another writer. The classroom’s grouped suites reflect this principle, while ordinary runtime groups use disposable projects.""",
    """A useful pipeline has fast static checks, bounded unit tests, image build, real runtime failure/timeout checks and application acceptance. Store small structured receipts and bounded logs. Always execute cleanup for resources the job owns, including on failures, while preserving evidence needed to diagnose the failure.

For this project, images are built locally in CI for testing and are not pushed to a registry. A portable source ZIP is a different artifact from a built image. Both need their own content and integrity checks.""",
    (
        "Design the evidence ladder",
        "Each stage answers a different question.",
        "text",
        "source checks -> unit tests -> image build -> startup -> reference execution\n-> controlled failure -> saved-state replacement -> browser acceptance",
        "No earlier stage substitutes for a later stage’s actual behavior.",
    ),
    (
        "Define a source-bound receipt",
        "This is a schema sketch, not a completed test result.",
        "json",
        '{"source_hash":"measured hash","image_id":"measured image","case":"named reference","status":"observed result","cleanup":"owned resources only"}',
        "The receipt binds a particular test to actual source and runtime identities.",
    ),
    [
        (
            "Predict what a unit test cannot prove about packaging.",
            "Missing image files or a wrong final command can remain undetected.",
            "Unit tests may run in a richer host environment. Execute the final image to observe its real dependency and filesystem contract.",
            "List what a unit test never touches, such as the image's files and command.",
        ),
        (
            "Separate source ZIP and image artifacts.",
            "Source input package versus built executable filesystem.",
            "They have different consumers and validation requirements. A clean archive does not establish that the image starts.",
            "Ask which artifact you would run and which you would review.",
        ),
        (
            "Design a parallel test partition.",
            "Independent groups with explicit ownership for shared fixtures.",
            "Parallelism is valuable only when tests do not corrupt one another’s state. Preserve required serialization for shared resources.",
            "Group the tests so that no two groups write the same fixture.",
        ),
        (
            "Diagnose rebuilding between acceptance and deployment.",
            "The new artifact may not match the tested identity.",
            "Mutable dependencies and timestamps can change output. Promote the tested artifact or qualify the newly built one explicitly.",
            "Compare the digest that passed acceptance with the one deployed.",
        ),
        (
            "Explain cleanup after a failed CI job.",
            "Remove job-owned runtime resources while retaining bounded diagnostic evidence.",
            "Failure should not leave a cluster or volume consuming resources indefinitely. Cleanup must not erase the only failure receipt or affect unrelated projects.",
            "Keep logs and identities, then remove only resources the job created.",
        ),
        (
            "Write a release gate with honest limitations.",
            "Named actual checks on exact artifacts, plus visible skipped surfaces.",
            "A gate should report what ran, not infer broad acceptance from static configuration. Different engines and architectures may still require separate qualification.",
            "Name each check, the artifact it ran on and what was skipped.",
        ),
    ],
    "https://docs.docker.com/build/ci/github-actions/",
    "https://docs.docker.com/build/ci/github-actions/test-before-push/",
)

add(
    "Debugging minimal images without changing the contract",
    """A minimal image may omit a shell, curl, a package manager or debugging tools. Their absence can reduce image size and unnecessary functionality, but it changes how you inspect failures. An application can be correct without a shell; an attempted `docker exec ... sh` failure may describe tooling, not the application.

Debugging should preserve the original artifact and evidence. Installing tools into a live container changes its writable layer and can hide the conditions that caused the failure. Prefer structured inspection, existing runtime libraries, bounded logs and an explicitly prepared diagnostic workflow.

A separate debug image or ephemeral diagnostic container can be useful when its permissions, network access and data exposure are deliberately scoped. `docker run --rm -it --pid=container:APP --network=container:APP TOOLS_IMAGE` starts a tools container that sees the app container's processes and network stack while the app image stays unchanged. It must not become an excuse to mount the whole host or attach to unrelated production workloads.""",
    """The fixture already has Python, so a short standard-library request can test HTTP without adding curl. Use container inspection for configuration and logs for application behavior. If you need a shell in a different project, verify that the selected image actually contains one.

Record whether each diagnostic ran inside the app container, a peer container or the host. The vantage point determines which DNS names, loopback address, files and permissions were observed.""",
    (
        "Use a prepared runtime as a diagnostic",
        "This uses the app’s existing Python standard library.",
        "sh",
        "docker compose -p ds60-docker-study exec app python -c \"import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2).read().decode())\"",
        "A bounded internal health response, with no package installation.",
    ),
    (
        "Label observations by vantage point",
        "A compact incident table should preserve this distinction.",
        "text",
        "host: published mapping and browser request\npeer: service DNS and internal network\napp: local listener, filesystem and effective UID",
        "Different results can localize a failure rather than contradict one another.",
    ),
    [
        (
            "Predict a missing-shell error in a minimal image.",
            "It may be expected image content, not an app crash.",
            "The diagnostic command needs its own dependency. Do not conclude that the application is broken merely because a familiar tool is absent.",
            "Ask whether the image was ever meant to contain sh.",
        ),
        (
            "Choose a prepared tool for one HTTP request.",
            "Use Python already present in the fixture.",
            "Adding a new package is unnecessary for this bounded observation. Reuse a declared runtime while keeping timeout and output limits explicit.",
            "Look for a runtime the image already includes.",
        ),
        (
            "Create a vantage-point diagnosis table.",
            "Host, peer and app observations with distinct address scopes.",
            "The table helps explain why one request works and another fails. It prevents applying a host-network fix to a container-loopback problem.",
            "Record each probe's location: host, peer or app container.",
        ),
        (
            "Diagnose an interactive repair that cannot survive recreation.",
            "The maintained image was never changed.",
            "Record the useful finding, then implement the repair in source and rebuild. Treat the altered live container as diagnostic state, not a release artifact.",
            "Ask what docker compose up does to changes made with docker exec.",
        ),
        (
            "Explain why host filesystem mounts are excessive for this lab.",
            "They expose data unrelated to the app diagnosis.",
            "The fixture can be inspected through its own image, logs and volume. Broader mounts change authority without adding necessary evidence.",
            "Ask what data a host filesystem mount would expose.",
        ),
        (
            "Write a repeatable minimal-image incident procedure.",
            "Preserve artifact, inspect state, run bounded prepared probes and test a source repair.",
            "A repeatable procedure works for another learner and preserves the original symptom. It should not depend on tools installed manually during a previous incident.",
            "Write the order: preserve, inspect, probe, repair in source, retest.",
        ),
    ],
    "https://docs.docker.com/reference/cli/docker/container/exec/",
    "https://docs.docker.com/engine/containers/run/",
)

add(
    "Restart policies, failure loops and idempotent startup",
    """A restart policy tells the engine when to restart an exited container. It is not a repair mechanism for an invalid configuration or corrupted data. A process that crashes on every startup can loop indefinitely, consuming resources and repeating side effects.

Idempotent startup means repeating initialization does not create duplicate or conflicting state. Creating a file exclusively and recognizing its existing valid form is different from appending a new seed record every time. Database migrations need their own concurrency and version rules rather than casual startup scripts.

The study fixture avoids an automatic endless restart loop so a learner can inspect failures directly. In another service, choose a restart policy according to operational intent and test both clean shutdown and crash behavior. Preserve logs and a clear failure condition rather than making the container appear perpetually recovering.""",
    """Policies such as no, on-failure and unless-stopped have different lifecycle semantics. Their exact behavior also depends on successful startup conditions and manual stops. Compose’s dependency restart option is a separate feature from the container restart policy. Do not treat similarly named fields as interchangeable.

Before enabling automatic restart, verify the app’s initialization, bounded retries and data ownership. Retrying an HTTP read is different from retrying a write that may already have committed. Unknown outcome requires reconciliation, not blind replay.""",
    (
        "Read two distinct restart concepts",
        "This fragment illustrates the naming difference.",
        "yaml",
        'services:\n  app:\n    restart: "no"\n  client:\n    depends_on:\n      app:\n        condition: service_healthy\n        restart: true',
        "The service restart policy and dependency update behavior are separate configuration mechanisms.",
    ),
    (
        "Trace an unsafe initializer",
        "The corrected design uses an existence/version check and a safe write.",
        "text",
        "unsafe: every start appends seed record\nsafe: inspect owned state -> validate version -> create only when absent -> serve",
        "Repeated starts should not silently duplicate application data.",
    ),
    [
        (
            "Predict a restart loop with invalid configuration.",
            "The same failure can repeat without fixing its cause.",
            "Automatic restarts can mitigate transient failures but cannot make a malformed required value valid. Preserve the earliest useful error.",
            "Ask whether restarting changes the invalid configuration.",
        ),
        (
            "Distinguish the two restart fields.",
            "Container lifecycle policy versus dependency update behavior.",
            "Read the scope and documentation for each field. Similar words in different parts of the model do not imply identical semantics.",
            "Compare the restart key with the restart field under depends_on.",
        ),
        (
            "Design idempotent counter initialization.",
            "Create absent state once and validate existing state.",
            "Existing data should not be reset merely because the app process restarts. Invalid existing data should produce an explicit recovery decision rather than silent overwrite.",
            "Make initialization check for existing state before creating it.",
        ),
        (
            "Diagnose duplicate records after repeated startup.",
            "Initialization performs a non-idempotent side effect.",
            "Repair the initialization protocol and reconcile existing data. Increasing restart delays alone does not remove the duplication mechanism.",
            "Ask what initialization does every time the container starts.",
        ),
        (
            "Explain unknown write outcomes.",
            "A timed-out client may not know whether the server committed.",
            "Blindly retrying can duplicate the action. Use an operation identity, queryable result or other explicit reconciliation design.",
            "Ask what the client knows when a timeout ends the request.",
        ),
        (
            "Define restart acceptance for a stateful app.",
            "Repeated starts preserve valid data and expose unrecoverable failures clearly.",
            "The test should cover both normal restarts and a controlled failure. A container continuously running says little about whether startup has corrupted its state.",
            "Restart several times and check the data after each start.",
        ),
    ],
    "https://docs.docker.com/engine/containers/start-containers-automatically/",
)

add(
    "Application migrations and durable state versioning",
    """A migration changes stored data or schema from one version to another. Replacing an application image can require such a change, but image rollback does not automatically reverse data migration. Code version and data version are related state machines with different reversibility.

A safe migration procedure identifies the starting schema, validates preconditions, creates a consistent backup, performs a bounded transition and verifies the new invariant. Concurrent old and new application instances complicate this because both may read or write the same data during replacement.

The fixture counter includes a schema_version field so learners can discuss this boundary without a full database. The course does not run destructive migrations on the main classroom’s progress store. Work on copied synthetic records and a separate disposable restore target.""",
    """An expand-and-contract approach first adds a compatible representation, allows both versions to work, migrates data and only later removes the old representation. It costs temporary complexity but can reduce deployment downtime. A tiny offline app may instead choose a documented maintenance window and an exclusive migration.

Atomic file replacement can prevent a partially written JSON file from appearing, but it is not a general distributed transaction. Define locking and single-writer assumptions explicitly. Backups and rollback commands must match the data protocol, not just the image tag.""",
    (
        "Read a versioned teaching record",
        "This is synthetic stored state.",
        "json",
        '{"schema_version":1,"counter":7}',
        "The reader checks the version before interpreting fields.",
    ),
    (
        "Plan a compatible transition",
        "No live data is modified by this outline.",
        "text",
        "v1 reader/writer -> v2 reader accepts v1 and v2 -> migrate owned data\n-> verify v2 -> retire v1 compatibility after rollback window",
        "A rollback plan must state which code versions can still read the stored data.",
    ),
    [
        (
            "Predict whether image rollback reverses a schema change.",
            "It does not automatically restore previous data.",
            "The image and volume have different lifetimes. A rollback that ignores the data format can replace one failure with another.",
            "Ask whether rolling back an image changes files in the volume.",
        ),
        (
            "Identify migration preconditions.",
            "Known schema version, exclusive or compatible writers and a verified backup.",
            "These conditions make the transition reviewable. Guessing the starting format can corrupt records that belong to a different version.",
            "List what must be true before the first record changes.",
        ),
        (
            "Design a v1-to-v2 synthetic record conversion.",
            "Preserve counter value and set a validated new schema version.",
            "Use a pure transformation on copied input first. Reject malformed records instead of silently guessing missing values.",
            "Convert one record and check every field of the result.",
        ),
        (
            "Diagnose an old reader failing after deployment rollback.",
            "The data format may have advanced beyond its compatibility.",
            "Inspect the stored version before restarting repeatedly. Restore or use a compatible reader according to the planned recovery procedure.",
            "Compare the format the old reader expects with the data now stored.",
        ),
        (
            "Explain atomic file replacement limits.",
            "It avoids partial file visibility under stated local assumptions, not all concurrent-write races.",
            "Multiple writers can still overwrite each other’s valid updates without coordination. Name the lock and single-host assumptions.",
            "Ask what an atomic rename protects against and what it does not.",
        ),
        (
            "Write a migration release plan.",
            "Preconditions, backup, transition, validation, compatible rollback and cleanup.",
            "The plan should be concrete enough to rehearse on a copy. A code tag change alone is not a data recovery strategy.",
            "Order the backup, migration, validation and rollback steps.",
        ),
    ],
    "https://docs.docker.com/engine/storage/volumes/",
    "https://www.postgresql.org/docs/current/backup.html",
)

add(
    "Image size, startup latency and measurement",
    """Image size affects transfer and storage, while startup latency depends on pulling, unpacking, container creation and application initialization. These costs overlap but are not identical. A smaller image can still start slowly if it performs expensive runtime work or waits for an unavailable dependency.

Layer sharing changes the amount of new data an engine needs. The displayed total image size is not always the incremental download for an engine that already has the base layers. Compression, cache state and platform also affect measured behavior.

Optimization should preserve correctness and maintainability. Removing a certificate bundle to save space may break HTTPS. Moving dependency installation to startup makes the image look smaller while making every run slower and less reproducible. Measure the user-visible path you actually want to improve.""",
    """Compare cold and warm conditions explicitly. A cold engine or missing-image test includes transfer cost; a warm local restart does not. The course’s local workflow shows build logs so learners can see which layers are reused. Keep at least several observations and record input identity before drawing conclusions.

For a small fixture, inspect image size and measure a bounded short process or readiness interval. Do not remove shared base images or prune the user’s engine merely to manufacture a cold-cache experiment. A disposable engine or CI job is the appropriate environment for that test.""",
    (
        "Read local image size",
        "This is an artifact measurement, not a download benchmark.",
        "sh",
        'docker image inspect ds60-docker-study:local --format "{{.Size}}"',
        "A byte count for the local image representation; interpret it with layer sharing in mind.",
    ),
    (
        "Separate startup phases",
        "The categories guide a measurement plan.",
        "text",
        "image available? -> create container -> start process -> initialize app -> readiness passes\nuser request -> connect -> handler -> response",
        "Measure the phase responsible for the user-visible delay rather than optimizing a different metric.",
    ),
    [
        (
            "Compare total image size and incremental transfer.",
            "Shared cached layers can reduce new transferred bytes.",
            "A displayed size is not a complete network-cost estimate. Record cache state and the actual transfer path.",
            "Ask which layers a host already has.",
        ),
        (
            "Predict why runtime package installation hurts startup.",
            "It adds network and dependency work to every run.",
            "It also makes behavior depend on current repositories. Prepare declared dependencies in the image and keep startup focused on application initialization.",
            "Count the downloads that happen at every start.",
        ),
        (
            "Design a readiness latency measurement.",
            "Fixed image, known cache condition and repeated bounded readiness timing.",
            "Measure the same event each time. Process creation alone is weaker than useful app readiness.",
            "Fix the image and cache state, then time several starts until readiness.",
        ),
        (
            "Diagnose a size optimization that breaks HTTPS.",
            "A required runtime asset may have been removed.",
            "Correctness comes first. Restore the dependency and identify safer size reductions with final-image acceptance.",
            "List the runtime files HTTPS needs, such as CA certificates.",
        ),
        (
            "Explain why broad pruning is not an acceptable benchmark setup.",
            "It destroys shared caches and may affect unrelated work.",
            "Use a disposable environment when cold-cache behavior matters. A performance experiment should not damage a user’s engine state.",
            "Ask what else on the engine uses the cache you would delete.",
        ),
        (
            "Write an optimization recommendation with evidence.",
            "Measured bottleneck, bounded change, correctness recheck and actual improvement.",
            "A useful recommendation ties the change to the intended user experience. Avoid equating smaller bytes with universally better runtime behavior.",
            "Measure before and after the change and recheck correctness.",
        ),
    ],
    "https://docs.docker.com/build/cache/optimize/",
    "https://docs.docker.com/reference/cli/docker/image/inspect/",
)

add(
    "Compose on one host and the limits of orchestration",
    """Compose is excellent for defining and operating a related application on a selected engine. It does not automatically provide a distributed scheduler, multi-node failure recovery or a cloud load balancer. A process can be restarted on one host without making the application resilient to loss of that host.

Orchestration systems coordinate desired state across resources and failure domains. Kubernetes introduces API objects, controllers, scheduling, service discovery and policy with its own complexity. Moving a Compose app to Kubernetes is a design exercise, not a mechanical translation that guarantees reliability.

The correct choice follows the workload. A local learning classroom benefits from a simple single-engine model with explicit volumes. A public service with strict availability and scaling requirements may need a different operational architecture. More infrastructure is not automatically a better educational or production experience.""",
    """Map concepts carefully: an image is reused; a container process still runs; Compose service configuration may inform a Pod template; a named local volume does not automatically become a portable replicated database. Published host ports and Kubernetes Services have different routing and ownership semantics.

Before changing platforms, write the failure model. What happens if a process exits, the engine restarts, the host disk fails, a dependency is unavailable or an availability zone disappears? Each case requires evidence and a recovery mechanism, not merely a new YAML file.""",
    (
        "Compare failure domains",
        "This is a design table.",
        "text",
        "process failure: restart may help\ncontainer replacement: retained volume may preserve data\nhost disk failure: local volume alone is insufficient\nmultiple hosts: scheduling and durable data design required",
        "A mechanism that handles one failure does not automatically handle all the others.",
    ),
    (
        "Map only what actually transfers",
        "These are conceptual correspondences, not generated manifests.",
        "text",
        "image -> same packaged application\nCompose service -> workload requirements to redesign\nlocal volume -> storage/recovery requirement\npublished port -> explicit external traffic design",
        "The migration preserves requirements, not necessarily the original configuration syntax.",
    ),
    [
        (
            "Predict whether Compose survives host loss automatically.",
            "Not without an external recovery design.",
            "Restarting a process on a live host differs from replacing a failed host and recovering its data. State the actual failure domain.",
            "Ask what restarts the project if the host itself fails.",
        ),
        (
            "Identify the classroom reason for Compose.",
            "A reproducible local application with understandable resource ownership.",
            "The product’s scope is one learner machine. A distributed control plane would add prerequisites without automatically improving that experience.",
            "Ask what a learner needs to own and understand on one machine.",
        ),
        (
            "Build a failure-domain matrix.",
            "Process, container, engine, host and external dependency rows.",
            "For each row, name detection, recovery and retained state. Empty cells reveal architecture work still needed.",
            "For each row, name what fails and what recovers it.",
        ),
        (
            "Diagnose a mechanical volume translation to Kubernetes.",
            "A storage class and data recovery model are still required.",
            "A claim in YAML does not prove the storage exists or has the desired durability. Validate the actual provisioner and application data behavior.",
            "Ask what replaces a named volume's storage and its backup in a cluster.",
        ),
        (
            "Explain why a load balancer does not replicate a database.",
            "Traffic distribution and data durability are separate mechanisms.",
            "A request router can select healthy endpoints while all endpoints still depend on one failing data store.",
            "Ask what a load balancer copies: requests or data.",
        ),
        (
            "Choose an orchestration approach for a stated workload.",
            "A reasoned choice based on availability, scaling, operations and learning cost.",
            "Defend the smallest system that meets the actual requirements. A platform name is not a substitute for a failure and recovery design.",
            "Weigh availability needs against operating and learning cost.",
        ),
    ],
    "https://docs.docker.com/compose/intro/features-uses/",
    "https://kubernetes.io/docs/concepts/overview/",
)

add(
    "TLS, reverse proxies and publishing responsibly",
    """TLS authenticates a server identity and encrypts traffic in transit under its certificate trust model. A reverse proxy receives client requests and forwards them to an upstream application. It can terminate TLS, route hostnames and paths, apply limits and emit access logs. It does not automatically make the upstream application authorized or safe for public use.

The study app is intentionally host-loopback only and uses HTTP for local teaching. Publishing it to the internet would create new requirements: identity, access control, TLS certificates, input limits, abuse handling, patching and operational ownership. This chapter designs that boundary without exposing your machine.

Proxy headers such as a forwarded client address are claims from the proxy chain. An application should trust them only from known proxies under an explicit configuration. Accepting arbitrary client-supplied forwarding headers can break rate limits or audit attribution.""",
    """Draw the full request path before configuring a proxy: client name resolution, public endpoint, TLS handshake, proxy routing, upstream connection and application response. Each hop has its own timeout and identity. A certificate for one hostname does not validate a different name merely because both resolve to the same IP.

Use a synthetic configuration review and diagrams here. The course does not register a domain, request certificates or open firewall ports. A production configuration must use the chosen proxy’s actual documentation and a separate deployment review.""",
    (
        "Trace a protected request",
        "This is a conceptual public architecture.",
        "text",
        "browser -> DNS name -> TLS proxy -> private app endpoint\n          certificate name        bounded upstream timeout",
        "TLS protects the client-to-proxy hop; upstream protection and trust are separate design choices.",
    ),
    (
        "Compare identity and routing failures",
        "These synthetic symptoms occur at different stages.",
        "text",
        "certificate name mismatch: TLS identity problem\nHTTP 502 from proxy: upstream handling problem\nHTTP 401 from app: application authentication requirement",
        "Changing a container port does not repair an invalid certificate identity.",
    ),
    [
        (
            "Distinguish TLS and application authorization.",
            "Encrypted authenticated transport versus permission for an action.",
            "A correctly encrypted request can still be unauthorized. The application must decide who may read or change its data.",
            "Ask what TLS proves about the server and what it says about the user.",
        ),
        (
            "Predict the effect of a certificate name mismatch.",
            "The client cannot validate the requested server name normally.",
            "Do not disable verification as the default fix. Correct the intended hostname and certificate relationship.",
            "Compare the requested host name with the names in the certificate.",
        ),
        (
            "Draw proxy and upstream trust boundaries.",
            "Explicit client-facing and internal hops with identities and timeouts.",
            "The drawing should show where TLS terminates and which component validates each request or header.",
            "Mark where TLS ends and which identity each hop trusts.",
        ),
        (
            "Diagnose a proxy 502 separately from an app 404.",
            "Upstream failure versus a completed app route response.",
            "Use logs and direct owned upstream observations to locate the first failing hop without exposing new ports unnecessarily.",
            "Check whether the response came from the proxy or from the app.",
        ),
        (
            "Explain forwarded-header spoofing.",
            "Untrusted clients can send headers unless the proxy boundary sanitizes them.",
            "Treat those values as claims, not facts. Trust only the configured proxy chain and document how original client identity is derived.",
            "Ask who can set an X-Forwarded-For header.",
        ),
        (
            "State what would be required before public exposure.",
            "A separate deployment design covering access, TLS, limits, operations and data.",
            "The local fixture’s simplicity is intentional. Do not advertise a loopback teaching app as public production hosting merely by changing the bind address.",
            "List the access, TLS, limits, operations and data requirements for public use.",
        ),
    ],
    "https://docs.docker.com/engine/network/port-publishing/",
    "https://nginx.org/en/docs/http/ngx_http_proxy_module.html",
)

add(
    "Incident response, disk pressure and scoped cleanup",
    """An incident is an observed deviation from expected behavior that requires diagnosis or recovery. Disk pressure can arise from images, build cache, container writable layers, logs or volumes. These categories have different retention and ownership, so one global delete command is a poor first response.

Pruning means removing resources considered unused by a tool’s rules. Unused does not always mean unimportant to a learner. A stopped container may retain an investigation, and a detached volume may hold progress awaiting the next container. Identify the resource and intended retention before deletion.

A useful incident sequence preserves evidence, assesses current state, identifies the failing layer, applies a scoped repair and verifies recovery. If an engine VM needs restart, that can interrupt unrelated workloads. A course lesson does not authorize such a host-wide action.""",
    """Use read-only inventory first. `docker system df` summarizes storage categories; project-scoped ps, image and volume inspection add ownership. Capture small results privately. Remove only resources you created and have decided to discard, using explicit names or labels checked against the project.

Routine course cleanup uses Compose down without volume deletion. A full disposable-lab reset is separately documented and should name the exact study project and volume. Build cache deletion changes performance and can affect other projects, so it is not hidden in the learner shutdown command.""",
    (
        "Inspect storage before deciding",
        "These reads do not delete resources.",
        "sh",
        "docker system df\ndocker compose -p ds60-docker-study ps -a\ndocker volume ls --filter label=com.docker.compose.project=ds60-docker-study",
        "Storage categories and project ownership are visible before any cleanup.",
    ),
    (
        "Stop only the study application",
        "This retains its named volume.",
        "sh",
        "docker compose -p ds60-docker-study down",
        "The project containers and network stop; retained data remains available to a later start.",
    ),
    [
        (
            "Classify disk usage by resource type.",
            "Images, cache, writable layers, logs and volumes.",
            "Each category has a different owner and retention policy. A single aggregate number does not identify safe deletions.",
            "Run docker system df and read each row.",
        ),
        (
            "Predict the effect of ordinary Compose down.",
            "It preserves named volumes unless explicit volume deletion is requested.",
            "The stop path should not erase learner state. Verify the exact command and project identity before execution.",
            "Compare docker compose down with and without -v.",
        ),
        (
            "Design an incident evidence packet.",
            "Failure symptom, time, resource inventory and bounded relevant logs.",
            "Preserve the original condition before changing the engine. This makes the repair explainable and helps distinguish recovery from coincidental disappearance.",
            "Record the symptom, time, resource inventory and relevant logs before acting.",
        ),
        (
            "Diagnose a detached volume labeled unused.",
            "Determine its owner and retained data purpose before deletion.",
            "A volume can be temporarily unattached between container runs. Tool reachability is not the same as user intent to discard data.",
            "Find who created the volume and what it holds.",
        ),
        (
            "Explain why broad engine pruning is out of scope.",
            "It can affect unrelated workloads and recoverable state.",
            "The study project owns only its own resources. Cleanup authorization should remain as narrow as the task that created them.",
            "Ask which other projects share the engine.",
        ),
        (
            "Write a scoped recovery and cleanup plan.",
            "Explicit targets, retained data, repair check and final ownership readback.",
            "A good plan makes every destructive action reviewable and verifies the intended outcome without claiming unrelated resources were safe to remove.",
            "List the exact targets, what to keep, the repair check and a final readback.",
        ),
    ],
    "https://docs.docker.com/engine/manage-resources/pruning/",
    "https://docs.docker.com/reference/cli/docker/system/df/",
)

add(
    "Advanced capstone: a release, recovery and teaching handoff",
    """The final project is a compact release system rather than a larger application. Starting from the maintained fixture, produce a source-controlled build, an identified image, runtime acceptance, persistence and restore evidence, and a readable operator handoff. The aim is independent reasoning across the complete lifecycle.

An expert explanation separates facts from assumptions. It names the tested engine and platform, the image identity, the source inputs and the behavior actually observed. It can explain why a failure occurs at one layer and which next observation would disprove that explanation. It also knows when a simple local project does not meet public-service or multi-host requirements.

No capstone can certify expertise by itself. Use it to identify gaps: if you cannot explain a mount, signal, cache, network hop or recovery boundary, return to the relevant chapter. Repetition with a changed input is more valuable than copying a completed recipe.""",
    """Create a fresh learner copy, keep public synthetic configuration, build visibly, qualify host and peer requests, test one controlled failure, recreate the app, export and independently restore data, and stop owned resources. Preserve an optional image archive for offline transfer without pushing it anywhere.

Your handoff should contain a diagram, command sequence, expected outputs, failure decision tree and explicit retention policy. Include a coverage table with source checks, image build, actual runtime, browser observation, persistence and restore as separate rows. Mark untested engines or architectures honestly.""",
    (
        "Organize the release evidence",
        "This is a checklist of independent observations.",
        "text",
        "source and context reviewed\nimage identity and platform recorded\nhealth + host request + peer request observed\ncontrolled failure diagnosed\ncontainer replacement preserved data\nindependent restore accepted\nowned cleanup verified",
        "Every row has actual evidence or an explicit not-run statement.",
    ),
    (
        "Explain one complete request",
        "Use values from your owned run.",
        "text",
        "browser -> host loopback:18080 -> published mapping -> app:8080\n-> handler -> volume-backed counter -> JSON response\npeer client -> service DNS app -> app:8080",
        "The diagram distinguishes network scope, process behavior and durable state.",
    ),
    [
        (
            "Predict all outcomes before running the final project.",
            "A written normal, failure, replacement and recovery expectation.",
            "Predictions make the experiment falsifiable. Without them it is easy to reinterpret any output as success.",
            "Write the expected result for the normal, failure, replacement and recovery cases first.",
        ),
        (
            "Change one noncritical configuration and rebuild or recreate appropriately.",
            "The chosen lifecycle action matches the kind of change.",
            "Source changes need a new image; runtime environment changes need application of new container configuration. Explain why your selected action is sufficient.",
            "Decide whether the change needs a rebuild or only a recreation.",
        ),
        (
            "Assemble a source-bound release packet.",
            "Exact source, image, platform, commands and observations.",
            "The packet should let another learner connect each result to the artifact actually tested. Avoid stale screenshots or reports from an earlier image.",
            "Tie every observation to the exact source revision and image identity.",
        ),
        (
            "Diagnose a deliberate single-layer failure.",
            "Minimal evidence locates the fault and a targeted repair restores the invariant.",
            "Do not weaken the acceptance check. Keep the failing observation as a regression case for the repaired configuration.",
            "Break one layer only and collect the smallest evidence that locates it.",
        ),
        (
            "Prove independent data recovery.",
            "A new owned target serves the preserved expected state.",
            "This is stronger than backup existence. Keep the original data intact until the restore has passed its application-level check.",
            "Restore into a new target and read the value through the app.",
        ),
        (
            "Teach the full system and defend its limits.",
            "A beginner can follow the handoff and identify what it does not guarantee.",
            "Good engineering communication states both achieved behavior and the boundaries of evidence. Local Docker success is a foundation for further systems learning, not a blanket production certification.",
            "Explain the system to a beginner and list what it does not guarantee.",
        ),
    ],
    "https://docs.docker.com/build/building/best-practices/",
    "https://docs.docker.com/compose/production/",
)

add(
    "Namespaces, cgroups, OCI and the runtime beneath Docker",
    """A namespace changes which operating-system objects a process can see. Linux provides namespaces for areas including processes, mounts, networking and users. A cgroup groups processes for accounting and resource controls. Visibility isolation and resource limits are different mechanisms, even though both contribute to a container environment.

The Open Container Initiative, or OCI, defines specifications for image and runtime interoperability. Docker tooling can use components such as containerd and an OCI runtime to manage execution. These layers explain why an image format, an engine API and a running process are related but not identical products.

The shared Linux kernel remains an important trust boundary. A container is not a separate guest kernel by default. Kernel vulnerabilities, privileged configuration and host mounts can affect isolation. Rootless mode and least privilege reduce specific risks but do not turn every process into a harmless mathematical function.""",
    """Trace a launch as client request, engine configuration, runtime setup of namespaces and cgroups, filesystem mounts, then the application process. A process still makes ordinary system calls. Its view and allowed operations depend on the setup around it.

Use read-only observations in the fixture. `/proc/self/status` can show process information, while cgroup details vary by host and cgroup version. Do not modify kernel settings or mount host control filesystems to make the lesson output match a screenshot.""",
    (
        "Inspect process namespace evidence",
        "This uses the process view already available in the fixture image.",
        "sh",
        "docker run --rm --pull never ds60-docker-study:local python -c \"import os; print('pid', os.getpid()); print(open('/proc/self/cgroup').read())\"",
        "The process prints its PID and cgroup membership view; exact paths depend on the engine configuration.",
    ),
    (
        "Separate isolation and accounting",
        "This is a mechanism map.",
        "text",
        "network namespace -> interfaces, loopback and routes visible to a process\nmount namespace -> filesystem mount view\ncgroup -> resource accounting and limits\nOCI runtime -> applies a prepared runtime configuration",
        "No single row replaces the other mechanisms.",
    ),
    [
        (
            "Distinguish namespace and cgroup.",
            "Object visibility versus grouping and resource controls.",
            "Both influence container behavior but solve different problems. A memory limit does not define which network interfaces a process can see.",
            "Ask which one hides objects and which one limits resource use.",
        ),
        (
            "Predict whether the container has its own kernel.",
            "Ordinary Linux containers share the engine environment kernel.",
            "On a desktop host that kernel may live in a Linux VM. The container boundary still does not create another guest kernel for each app.",
            "Compare uname -r inside a container with the engine host.",
        ),
        (
            "Draw the client-to-process runtime chain.",
            "Client, engine, runtime setup, mounts and application process.",
            "The chain helps place errors such as daemon connection failure, image unpacking failure and application exceptions at different layers.",
            "Follow a docker run from the CLI to the engine to the OCI runtime.",
        ),
        (
            "Diagnose a missing cgroup path from an example.",
            "Inspect host and cgroup-version differences without changing kernel settings.",
            "Implementation details vary. Preserve the conceptual mechanism and record the observed platform instead of forcing one machine layout.",
            "Check whether the host uses cgroup v1 or v2.",
        ),
        (
            "Explain OCI interoperability limits.",
            "A shared specification does not guarantee every platform or feature is identical.",
            "Image architecture, runtime capabilities and host configuration still matter. Test the actual supported engine path.",
            "Ask what the OCI specification standardizes and what it leaves to implementations.",
        ),
        (
            "Describe the shared-kernel security implication.",
            "Least privilege and patching remain necessary parts of the trust model.",
            "Isolation reduces visibility and authority but depends on kernel enforcement. Do not describe a container as a universal hostile-code sandbox.",
            "Ask what a kernel vulnerability means for every container on the host.",
        ),
    ],
    "https://opencontainers.org/",
    "https://docs.docker.com/engine/security/#kernel-namespaces",
    "https://docs.docker.com/engine/security/#control-groups",
)

add(
    "Runtime secrets, configuration files and controlled disclosure",
    """A runtime secret is sensitive input required while an application runs. It has a different lifecycle from a build secret. Compose can expose declared secrets as files to selected services, while ordinary configuration can be passed through environment variables or files. The exact storage and protection depend on the deployment platform.

Local Compose file-based secrets are not a universal encrypted secret vault. The source file exists on the host and must be protected there. File mounts can avoid some environment-variable exposure paths, but the application can still read and accidentally log the value. Secret handling is a complete data-flow concern.

This lesson uses only an invented value. Never copy a real credential into the repository, a screenshot or a public report. The course fixture needs no password, so the optional example belongs in a separate scratch project and demonstrates a file-reading contract rather than adding a secret requirement to the app.""",
    """A top-level `secrets` entry declares a source, and a service grants itself access by name. Inside the service the file commonly appears under `/run/secrets/NAME`. The app must explicitly read that file or support a documented file-based configuration option.

Rotate a credential by updating the controlled source and applying the appropriate service lifecycle, then verify the new identity and revoke the old credential according to the external service policy. A container restart alone does not prove that an old credential has been invalidated.""",
    (
        "Review a synthetic secret file mount",
        "This is a Compose fragment for a scratch project only.",
        "yaml",
        "services:\n  app:\n    secrets: [demo]\nsecrets:\n  demo:\n    file: ./demo-secret.txt",
        "Only the service granted demo can read its mounted file; host file protection remains relevant.",
    ),
    (
        "Validate presence without disclosure",
        "The application should report a safe readiness fact.",
        "python external",
        'from pathlib import Path\nvalue = Path("/run/secrets/demo").read_text().strip()\nif not value:\n    raise ValueError("demo secret is empty")\nprint("demo input is present")',
        "The secret bytes are not printed; validation distinguishes empty input from a usable configured value.",
    ),
    [
        (
            "Compare build and runtime secrets.",
            "Temporary build input versus application-time input.",
            "Their consumers and lifetimes differ. A build-only credential should not be copied into the final runtime image.",
            "Ask when each secret is needed: during the build or while the app runs.",
        ),
        (
            "Predict whether a local secret file is automatically encrypted everywhere.",
            "No; host storage and platform behavior require separate protection.",
            "The secret abstraction controls delivery, not every storage layer. Describe the actual local Compose implementation honestly.",
            "Check where the file lives on the host and who can read it.",
        ),
        (
            "Design a no-disclosure validation message.",
            "Report presence or a bounded error without the sensitive value.",
            "Useful diagnostics need not reveal bytes. Avoid including environment dumps, full headers or file contents in error reports.",
            "Report whether the value exists and is well formed, never the value itself.",
        ),
        (
            "Diagnose a secret declared but not granted to a service.",
            "The service lacks the intended mounted input.",
            "Check the effective model and service access list before changing file permissions or adding a broad host mount.",
            "Compare the top-level secrets key with the service's secrets list.",
        ),
        (
            "Explain credential rotation beyond restarting a container.",
            "New input must be applied and old authority revoked deliberately.",
            "The external service decides which credential remains valid. A process lifecycle event alone cannot establish that policy change.",
            "Ask whether the old credential still works after the restart.",
        ),
        (
            "Write a secret data-flow review.",
            "Source, host protection, service grant, read path, logs, rotation and deletion.",
            "Following the bytes through their lifetime reveals exposure paths that a single Compose setting cannot address.",
            "Trace the secret from its source to where the app reads it and where it could leak.",
        ),
    ],
    "https://docs.docker.com/compose/how-tos/use-secrets/",
    "https://docs.docker.com/reference/compose-file/secrets/",
)

add(
    "Scaling replicas, shared state and concurrency traps",
    """A replica is another instance of an application role. More replicas can increase capacity or tolerate some process failures, but only if request routing and state design support them. Two processes writing the same local file can lose updates even when each performs an atomic file replacement.

The fixture counter is intentionally a single-process teaching app. Its in-process lock coordinates threads in that process. It does not coordinate separate containers. Scaling it without redesigning the storage protocol would violate its assumption. This is a useful example of knowing when a tutorial pattern stops being valid.

A load balancer distributes requests; it does not automatically synchronize application memory, sessions or files. State can move into a service designed for concurrent transactions, or the workload can be partitioned under an explicit ownership scheme. Both choices need tests for races, failures and retries.""",
    """Compose can request several service instances, but a fixed published host port can collide across replicas. A proxy or another deliberate routing arrangement is needed. Do not run a scaling command against the fixture and assume the engine will infer the intended architecture.

Use a synthetic lost-update trace: two writers read 7, both compute 8, both replace the file, and the final count is 8 instead of 9. Each file write can be atomic while the read-modify-write transaction is not. This distinction connects container operations to concurrency and data modeling.""",
    (
        "Trace a lost update",
        "This table is synthetic and requires no engine activity.",
        "text",
        "writer A reads 7; writer B reads 7\nwriter A writes 8; writer B writes 8\nexpected two increments: 9; observed final value: 8",
        "Atomic replacement does not make the entire read-modify-write sequence transactional.",
    ),
    (
        "Separate scaling requirements",
        "Review these before any real scale experiment.",
        "text",
        "replicas -> routing with no fixed-port collision\nshared data -> transactional or partitioned ownership\nsessions -> deliberate cross-instance model\nretries -> idempotency or outcome reconciliation",
        "Adding process instances does not supply the missing protocols.",
    ),
    [
        (
            "Predict the lost-update result.",
            "The final value can be 8 after two attempted increments.",
            "Both writers used the same old value. Atomic file visibility prevents partial bytes but not stale computations.",
            "Interleave two read-modify-write sequences that both start from 7.",
        ),
        (
            "Identify the scope of the fixture lock.",
            "Threads in one process, not multiple containers.",
            "A lock object in memory is not shared across isolated processes. State the assumption instead of extending it by analogy.",
            "Ask what a threading lock protects across processes.",
        ),
        (
            "Design a replica-readiness checklist.",
            "Routing, state concurrency, sessions, resource budget and recovery.",
            "Each requirement can fail independently. A successful second process start does not prove the application is safely scalable.",
            "List what each replica would share and what must change for it.",
        ),
        (
            "Diagnose a fixed host-port collision.",
            "Several replicas cannot all bind the same host socket independently.",
            "Introduce an intended routing layer or distinct ports for a controlled experiment. Do not disable isolation merely to make startup succeed.",
            "Count how many processes can bind one host port.",
        ),
        (
            "Explain why load balancing does not fix lost updates.",
            "Traffic distribution does not serialize shared-state transactions.",
            "The data store or application protocol must provide the necessary concurrency guarantees regardless of which replica receives the request.",
            "Ask whether spreading requests makes two updates happen in order.",
        ),
        (
            "Propose a correct scaled counter architecture.",
            "A transaction-capable shared store or explicit single-writer ownership.",
            "Defend the consistency and failure semantics. Test concurrent increments and unknown outcomes rather than presenting replica count as correctness evidence.",
            "Choose where increments are serialized: in a database or in one writer.",
        ),
    ],
    "https://docs.docker.com/reference/cli/docker/compose/up/",
    "https://docs.docker.com/compose/how-tos/networking/",
)

# Keep the release capstone last while preserving the authored teaching order.
CHAPTERS = CHAPTERS[:-4] + CHAPTERS[-3:] + [CHAPTERS[-4]]


# Concept terms each lesson teaches, keyed by title so the final reordering above
# cannot misalign them.
CONCEPTS = {
    "Containers, images and the process model": [
        "process",
        "image",
        "container",
        "writable layer",
        "shared kernel",
    ],
    "The Linux engine, WSL 2 and your first inspection": [
        "Docker client",
        "Docker engine",
        "Docker context",
        "WSL 2",
        "docker info",
    ],
    "The filesystem, writable layers and container lifetime": [
        "image layers",
        "writable layer",
        "container lifetime",
        "read-only root filesystem",
    ],
    "Processes, PID 1, signals and graceful shutdown": [
        "PID 1",
        "signals",
        "graceful shutdown",
        "exec form",
        "init process",
    ],
    "Dockerfile instructions and the first reproducible image": [
        "Dockerfile",
        "FROM",
        "COPY",
        "RUN",
        "CMD",
        "image tag",
    ],
    "Build context, .dockerignore and accidental data exposure": [
        "build context",
        ".dockerignore",
        "ignore patterns",
        "layer history",
        "explicit COPY",
    ],
    "Layers, cache invalidation and efficient rebuilds": [
        "build cache",
        "cache invalidation",
        "instruction order",
        "dependency layer",
    ],
    "Environment variables, command arguments and configuration": [
        "environment variables",
        "ENTRYPOINT",
        "CMD",
        "Compose interpolation",
        "configuration validation",
    ],
    "Ports, loopback and the first browser request": [
        "port publishing",
        "loopback address",
        "bind address",
        "host port",
        "container port",
    ],
    "Logs, exit status and observation before repair": [
        "standard streams",
        "container logs",
        "exit status",
        "container state",
        "events",
    ],
    "Compose services, projects and a complete application": [
        "Compose service",
        "Compose project",
        "compose.yaml",
        "project name",
    ],
    "Health checks, startup order and real readiness": [
        "health check",
        "readiness",
        "depends_on",
        "service_healthy",
        "startup order",
    ],
    "Named volumes, bind mounts and persistence experiments": [
        "named volume",
        "bind mount",
        "persistence",
        "container recreation",
    ],
    "First capstone: build, serve, replace and explain": [
        "image rebuild",
        "container replacement",
        "persistent data",
        "evidence record",
    ],
    "BuildKit, cache mounts and build secrets": [
        "BuildKit",
        "cache mount",
        "secret mount",
        "--secret",
        "cold build",
    ],
    "Multi-stage builds and runtime dependency boundaries": [
        "multi-stage build",
        "build stage",
        "COPY --from",
        "runtime image",
        "--target",
    ],
    "CPU architectures, image indexes and cross-platform builds": [
        "CPU architecture",
        "image index",
        "--platform",
        "emulation",
        "cross-compilation",
    ],
    "Bridge networks, service DNS and container-to-container traffic": [
        "bridge network",
        "service DNS",
        "container port",
        "network vantage point",
    ],
    "Network isolation, gateways and outbound connectivity": [
        "network isolation",
        "internal network",
        "gateway",
        "outbound connectivity",
    ],
    "Users, UID ownership and writable data paths": [
        "UID",
        "USER",
        "file ownership",
        "writable data path",
    ],
    "Backups, restores and proving data recovery": [
        "backup",
        "restore",
        "recovery test",
        "volume archive",
    ],
    "Resource limits, contention and honest performance experiments": [
        "memory limit",
        "CPU limit",
        "PID limit",
        "contention",
        "measurement",
    ],
    "Read-only filesystems, capabilities and least privilege": [
        "Linux capabilities",
        "cap_drop",
        "read-only filesystem",
        "no-new-privileges",
        "least privilege",
    ],
    "Rootless engines, user namespaces and host trust": [
        "rootless mode",
        "user namespace",
        "engine socket",
        "host trust",
    ],
    "Image names, digests and an offline transfer": [
        "image reference",
        "tag",
        "digest",
        "docker image save",
        "docker image load",
    ],
    "Compose overrides, profiles and configuration review": [
        "override file",
        "merge rules",
        "profiles",
        "docker compose config",
    ],
    "Intermediate capstone: a recoverable two-tier teaching system": [
        "service discovery",
        "resource limits",
        "recovery test",
        "release review",
    ],
    "Registries, tags, digests and deliberate publication": [
        "registry",
        "repository",
        "tag",
        "digest",
        "publication review",
    ],
    "Software bills of materials and image provenance": [
        "SBOM",
        "provenance",
        "attestation",
        "SPDX",
        "image digest",
    ],
    "Vulnerability findings, patching and dependency updates": [
        "vulnerability finding",
        "affected version",
        "base image update",
        "rebuild and retest",
    ],
    "CI builds, test layers and artifact promotion": [
        "continuous integration",
        "test stage",
        "artifact promotion",
        "immutable digest",
    ],
    "Debugging minimal images without changing the contract": [
        "minimal image",
        "debug container",
        "shared namespaces",
        "diagnostic vantage point",
    ],
    "Restart policies, failure loops and idempotent startup": [
        "restart policy",
        "crash loop",
        "idempotent startup",
        "backoff",
    ],
    "Application migrations and durable state versioning": [
        "migration",
        "schema version",
        "rollback",
        "durable state",
    ],
    "Image size, startup latency and measurement": [
        "image size",
        "startup latency",
        "layer reuse",
        "measurement method",
    ],
    "Compose on one host and the limits of orchestration": [
        "single-host Compose",
        "orchestration",
        "scheduling",
        "failure domain",
    ],
    "TLS, reverse proxies and publishing responsibly": [
        "TLS",
        "reverse proxy",
        "certificate",
        "public exposure",
    ],
    "Incident response, disk pressure and scoped cleanup": [
        "incident response",
        "disk pressure",
        "docker system df",
        "scoped cleanup",
    ],
    "Namespaces, cgroups, OCI and the runtime beneath Docker": [
        "namespaces",
        "cgroups",
        "OCI runtime",
        "container runtime",
    ],
    "Runtime secrets, configuration files and controlled disclosure": [
        "runtime secret",
        "secret file",
        "/run/secrets",
        "controlled disclosure",
    ],
    "Scaling replicas, shared state and concurrency traps": [
        "replica",
        "shared state",
        "race condition",
        "scaling",
    ],
    "Advanced capstone: a release, recovery and teaching handoff": [
        "release record",
        "recovery rehearsal",
        "handoff",
        "acceptance evidence",
    ],
}

REFERENCE_LABELS = {
    "https://docs.docker.com/build/building/best-practices/": "Building best practices",
    "https://docs.docker.com/build/building/multi-platform/": "Multi-platform builds",
    "https://docs.docker.com/build/building/multi-stage/": "Multi-stage builds",
    "https://docs.docker.com/build/building/secrets/": "Build secrets",
    "https://docs.docker.com/build/buildkit/": "BuildKit",
    "https://docs.docker.com/build/cache/": "Docker build cache",
    "https://docs.docker.com/build/cache/invalidation/": "Build cache invalidation",
    "https://docs.docker.com/build/cache/optimize/": "Optimize cache usage in builds",
    "https://docs.docker.com/build/ci/github-actions/": "Docker Build GitHub Actions",
    "https://docs.docker.com/build/ci/github-actions/test-before-push/": "Test before push with GitHub Actions",
    "https://docs.docker.com/build/concepts/context/": "Build context",
    "https://docs.docker.com/build/concepts/dockerfile/": "Dockerfile overview",
    "https://docs.docker.com/build/metadata/attestations/": "Build attestations",
    "https://docs.docker.com/build/metadata/attestations/sbom/": "SBOM attestations",
    "https://docs.docker.com/compose/gettingstarted/": "Docker Compose quickstart",
    "https://docs.docker.com/compose/how-tos/environment-variables/": "Environment variables in Compose",
    "https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/": "Compose variable interpolation",
    "https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/": "Merge Compose files",
    "https://docs.docker.com/compose/how-tos/networking/": "Networking in Compose",
    "https://docs.docker.com/compose/how-tos/profiles/": "Compose profiles",
    "https://docs.docker.com/compose/how-tos/project-name/": "Compose project name",
    "https://docs.docker.com/compose/how-tos/startup-order/": "Control startup order in Compose",
    "https://docs.docker.com/compose/how-tos/use-secrets/": "Secrets in Compose",
    "https://docs.docker.com/compose/intro/compose-application-model/": "Compose application model",
    "https://docs.docker.com/compose/intro/features-uses/": "Why use Compose",
    "https://docs.docker.com/compose/production/": "Compose in production",
    "https://docs.docker.com/desktop/features/wsl/": "Docker Desktop WSL 2 backend",
    "https://docs.docker.com/dhi/core-concepts/digests/": "Image digests",
    "https://docs.docker.com/engine/containers/resource_constraints/": "Resource constraints",
    "https://docs.docker.com/engine/containers/run/": "Running containers",
    "https://docs.docker.com/engine/containers/start-containers-automatically/": "Start containers automatically",
    "https://docs.docker.com/engine/logging/": "Docker logging",
    "https://docs.docker.com/engine/manage-resources/contexts/": "Docker contexts",
    "https://docs.docker.com/engine/manage-resources/pruning/": "Prune unused Docker objects",
    "https://docs.docker.com/engine/network/": "Networking overview",
    "https://docs.docker.com/engine/network/drivers/bridge/": "Bridge network driver",
    "https://docs.docker.com/engine/network/drivers/none/": "None network driver",
    "https://docs.docker.com/engine/network/port-publishing/": "Port publishing and mapping",
    "https://docs.docker.com/engine/security/": "Docker Engine security",
    "https://docs.docker.com/engine/security/#control-groups": "Docker Engine security: control groups",
    "https://docs.docker.com/engine/security/#kernel-namespaces": "Docker Engine security: kernel namespaces",
    "https://docs.docker.com/engine/security/rootless/": "Rootless mode",
    "https://docs.docker.com/engine/security/userns-remap/": "User namespace remapping",
    "https://docs.docker.com/engine/storage/": "Storage overview",
    "https://docs.docker.com/engine/storage/bind-mounts/": "Bind mounts",
    "https://docs.docker.com/engine/storage/drivers/": "Storage drivers",
    "https://docs.docker.com/engine/storage/volumes/": "Volumes",
    "https://docs.docker.com/engine/storage/volumes/#back-up-restore-or-migrate-data-volumes": "Back up, restore or migrate volumes",
    "https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/": "What is a container?",
    "https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-registry/": "What is a registry?",
    "https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/": "What is an image?",
    "https://docs.docker.com/reference/cli/docker/compose/": "docker compose reference",
    "https://docs.docker.com/reference/cli/docker/compose/up/": "docker compose up reference",
    "https://docs.docker.com/reference/cli/docker/container/exec/": "docker container exec reference",
    "https://docs.docker.com/reference/cli/docker/container/inspect/": "docker container inspect reference",
    "https://docs.docker.com/reference/cli/docker/container/stop/": "docker container stop reference",
    "https://docs.docker.com/reference/cli/docker/image/inspect/": "docker image inspect reference",
    "https://docs.docker.com/reference/cli/docker/image/load/": "docker image load reference",
    "https://docs.docker.com/reference/cli/docker/image/save/": "docker image save reference",
    "https://docs.docker.com/reference/cli/docker/login/": "docker login reference",
    "https://docs.docker.com/reference/cli/docker/system/df/": "docker system df reference",
    "https://docs.docker.com/reference/compose-file/networks/": "Compose file reference: networks",
    "https://docs.docker.com/reference/compose-file/secrets/": "Compose file reference: secrets",
    "https://docs.docker.com/reference/compose-file/services/#cap_drop": "Compose file reference: cap_drop",
    "https://docs.docker.com/reference/compose-file/services/#healthcheck": "Compose file reference: healthcheck",
    "https://docs.docker.com/reference/dockerfile/": "Dockerfile reference",
    "https://docs.docker.com/reference/dockerfile/#dockerignore-file": "Dockerfile reference: .dockerignore file",
    "https://docs.docker.com/reference/dockerfile/#entrypoint": "Dockerfile reference: ENTRYPOINT",
    "https://docs.docker.com/reference/dockerfile/#user": "Dockerfile reference: USER",
    "https://docs.docker.com/scout/explore/exceptions/": "Docker Scout exceptions",
    "https://kubernetes.io/docs/concepts/overview/": "Kubernetes overview",
    "https://nginx.org/en/docs/http/ngx_http_proxy_module.html": "nginx proxy module",
    "https://opencontainers.org/": "Open Container Initiative",
    "https://www.postgresql.org/docs/current/backup.html": "PostgreSQL backup and restore",
}

MISTAKES = {
    "Containers, images and the process model": "Treating the image as the running program, so removing an image looks like a way to delete data. Expecting `--rm` to remove the image as well as the container. Assuming a container on macOS or Windows runs on the host's own kernel.",
    "The Linux engine, WSL 2 and your first inspection": "Reading a successful `docker --version` as proof that the engine is running. Running lab commands while a remote or shared context is selected. Using PowerShell paths on Windows instead of the Ubuntu shell under WSL 2.",
    "The filesystem, writable layers and container lifetime": "Writing important data to the container's writable layer and losing it when Compose recreates the service. Expecting a file created in one container to appear in another without a shared mount. Removing `read_only` instead of adding a tmpfs for scratch files.",
    "Processes, PID 1, signals and graceful shutdown": "Starting the server in the background and keeping the container alive with `sleep`. Using shell form, so a shell becomes PID 1 and may not forward SIGTERM. Reading exit code 137 as proof of an out-of-memory kill without checking the OOMKilled state.",
    "Dockerfile instructions and the first reproducible image": "Expecting `RUN` to start the server or `CMD` to run at build time. Copying from a path outside the build context. Treating `EXPOSE` as port publishing.",
    "Build context, .dockerignore and accidental data exposure": "Writing `.env` or `*.log` and expecting nested files to be excluded; only `**/` patterns match at any depth. Assuming `.gitignore` controls the build context. Using `COPY . .` and deleting a secret in a later step.",
    "Layers, cache invalidation and efficient rebuilds": "Copying the whole source tree before installing dependencies, so every edit reinstalls them. Assuming a cached download step fetched fresh bytes. Using `--no-cache` when the stale part was the base image.",
    "Environment variables, command arguments and configuration": "Expecting every `.env` value to appear inside the container. Restarting a container after changing its environment instead of recreating it. Overriding `--entrypoint` and expecting the image's `CMD` to still apply.",
    "Ports, loopback and the first browser request": "Binding the server to 127.0.0.1 inside the container, so the published port cannot reach it. Publishing on all host interfaces when loopback is enough. Using `localhost` in one container to reach another.",
    "Logs, exit status and observation before repair": "Restarting a failing container before saving its logs and exit status. Reading the whole log history instead of a bounded tail. Logging tokens or request bodies to make debugging easier.",
    "Compose services, projects and a complete application": "Running Compose from another directory or without `-p`, so resources land in a different project. Adding `-v` to `docker compose down` as routine cleanup. Starting two copies that share a host port.",
    "Health checks, startup order and real readiness": "Using a check that only proves a process exists. Making the health check call an external service, so the local app looks unhealthy when the internet is down. Expecting `depends_on` to keep a dependency available after startup.",
    "Named volumes, bind mounts and persistence experiments": "Mounting a host directory over `/app` and hiding the packaged code. Changing the project name and then looking for data in the new, empty volume. Deleting volumes as part of routine cleanup.",
    "First capstone: build, serve, replace and explain": "Editing the maintained fixture instead of a learner copy. Treating a successful build as proof that the app serves the right response. Removing the volume when only the container needed replacing.",
    "BuildKit, cache mounts and build secrets": "Passing a password with `--build-arg` or `ENV`. Printing or copying a mounted secret into an image file. Treating the cache mount as the only copy of a dependency.",
    "Multi-stage builds and runtime dependency boundaries": "Testing only in the builder stage and shipping a runtime that lacks a library. Building the wrong `--target`. Assuming a small image is automatically patched and unprivileged.",
    "CPU architectures, image indexes and cross-platform builds": "Assuming Linux means amd64. Treating an emulated run as proof of native performance. Loading a multi-platform index into an image store that holds one platform.",
    "Bridge networks, service DNS and container-to-container traffic": "Connecting from one container to another through `localhost`. Using the host port instead of the container port between services. Hard-coding a container IP that changes when the service is recreated.",
    "Network isolation, gateways and outbound connectivity": "Switching to host networking to make a port problem disappear. Treating a private network as authentication. Attaching every service to every network.",
    "Users, UID ownership and writable data paths": "Fixing permission errors with `chmod -R 777`. Running as root because a bind mount is owned by another UID. Placing writable data under the code directory.",
    "Backups, restores and proving data recovery": "Copying a live database directory instead of making a consistent export. Restoring over the only good copy. Calling a backup successful without a restore test.",
    "Resource limits, contention and honest performance experiments": "Reading `cpus: 0.5` as half of a dedicated core. Raising container limits when the engine VM itself is short of memory. Drawing a conclusion from one `docker stats` sample.",
    "Read-only filesystems, capabilities and least privilege": "Adding capabilities or `--privileged` until an error disappears. Removing `read_only` instead of mounting the one path the app must write. Calling the container secure because it runs as non-root.",
    "Rootless engines, user namespaces and host trust": "Assuming a non-root `USER` makes the engine rootless. Adding a user to the docker group without treating that as root-equivalent access. Mounting the engine socket into a container for convenience.",
    "Image names, digests and an offline transfer": "Treating a tag as an immutable identity. Expecting a tagged build to be published. Trusting a checksum without knowing who supplied it.",
    "Compose overrides, profiles and configuration review": "Forgetting that Compose merges list fields such as `ports` instead of replacing them. Using profiles as a security boundary. Launching with a different file order than the one you reviewed.",
    "Intermediate capstone: a recoverable two-tier teaching system": "Testing only from the host and missing a broken peer path. Restoring over the source volume. Claiming high availability from a single engine.",
    "Registries, tags, digests and deliberate publication": "Publishing by reusing a mutable tag such as `latest`. Leaving credentials in the build context. Assuming a local tag was uploaded.",
    "Software bills of materials and image provenance": "Generating an SBOM for a tag instead of the exact digest you ship. Trusting provenance JSON without verifying its issuer. Expecting attestations to survive a `--load` into the classic image store.",
    "Vulnerability findings, patching and dependency updates": "Patching inside a running container instead of rebuilding the image. Reading zero findings as proof of safety. Applying a scan result to a tag that now points elsewhere.",
    "CI builds, test layers and artifact promotion": "Rebuilding the image after tests and deploying an untested artifact. Letting parallel jobs share one fixture. Hiding skipped checks behind a green summary.",
    "Debugging minimal images without changing the contract": "Installing tools into a live container and losing the original evidence. Reading a missing shell as an application crash. Mounting the host filesystem to debug a single HTTP endpoint.",
    "Restart policies, failure loops and idempotent startup": "Using a restart policy to hide a configuration error. Writing initialization that inserts data on every start. Assuming a timed-out write did not happen.",
    "Application migrations and durable state versioning": "Rolling back the image and expecting the data to roll back too. Migrating without a verified backup. Letting old and new writers run against incompatible formats.",
    "Image size, startup latency and measurement": "Installing packages when the container starts. Removing CA certificates or other runtime assets to save space. Pruning the whole engine before a benchmark.",
    "Compose on one host and the limits of orchestration": "Treating Compose restart policies as host-failure recovery. Translating volumes to Kubernetes without a storage and backup design. Expecting a load balancer to replicate data.",
    "TLS, reverse proxies and publishing responsibly": "Treating HTTPS as authorization. Trusting forwarded headers from any client. Publishing the learning server to the internet.",
    "Incident response, disk pressure and scoped cleanup": "Running `docker system prune -a --volumes` during an incident. Deleting a dangling volume without finding its owner. Cleaning up before recording evidence.",
    "Advanced capstone: a release, recovery and teaching handoff": "Running the final project before writing predictions. Rebuilding when only configuration changed, or only recreating when the image changed. Presenting the handoff without its limits.",
    "Namespaces, cgroups, OCI and the runtime beneath Docker": "Believing each container has its own kernel. Changing kernel or cgroup settings to match an example. Assuming every OCI runtime behaves identically.",
    "Runtime secrets, configuration files and controlled disclosure": "Passing secrets as environment variables that appear in `docker inspect`. Declaring a secret but not granting it to the service. Rotating by restarting without revoking the old credential.",
    "Scaling replicas, shared state and concurrency traps": "Scaling a service that keeps its state in local files. Relying on an in-process lock across containers. Publishing a fixed host port on a scaled service.",
}

KEY_TERMS = {
    "Containers, images and the process model": (
        (
            "Process",
            "A running program together with its memory, open files and operating-system identity.",
        ),
        (
            "Image",
            "A packaged, read-only filesystem plus startup configuration from which containers are created.",
        ),
        (
            "Container",
            "A running or stopped instance created from an image, with its own writable layer and isolation settings.",
        ),
        (
            "Writable layer",
            "The per-container record of file changes made on top of the image's read-only content.",
        ),
        (
            "Shared kernel",
            "The engine's single Linux kernel, which every container on that engine uses instead of booting a guest kernel.",
        ),
    ),
    "The Linux engine, WSL 2 and your first inspection": (
        (
            "Docker client",
            "The command you type, which sends API requests to an engine rather than running containers itself.",
        ),
        (
            "Docker engine",
            "The daemon that receives client requests and builds images and manages containers on its Linux host or VM.",
        ),
        (
            "Docker context",
            "A named client setting that selects which engine endpoint your commands are sent to.",
        ),
        (
            "WSL 2",
            "The Windows Subsystem for Linux version that provides the Ubuntu shell and Linux environment the course uses on Windows.",
        ),
        (
            "`docker info`",
            "A read-only command that asks the selected engine to report its version, operating system and resource settings.",
        ),
    ),
    "The filesystem, writable layers and container lifetime": (
        (
            "Image layers",
            "The read-only filesystem layers an image supplies, shared unchanged by every container created from it.",
        ),
        (
            "Merged view",
            "The single filesystem a container sees, combining the image layers with its own writable changes.",
        ),
        (
            "Container lifetime",
            "The span from creation to removal; a restart keeps the writable layer, while removal and recreation discard it.",
        ),
        (
            "Read-only root filesystem",
            "A runtime setting that refuses writes to packaged paths, so only explicit mounts remain writable.",
        ),
    ),
    "Processes, PID 1, signals and graceful shutdown": (
        (
            "PID 1",
            "The process ID of a container's initial process, which has special Linux signal and child-reaping behavior.",
        ),
        (
            "Signal",
            "A notification delivered to a process, such as SIGTERM asking it to stop or SIGKILL ending it without cleanup.",
        ),
        (
            "Graceful shutdown",
            "Refusing new work, finishing bounded in-flight work, closing resources and exiting before the grace period ends.",
        ),
        (
            "Exec form",
            "The JSON array form of `CMD` or `ENTRYPOINT`, which gives the runtime the arguments directly without starting a shell.",
        ),
        (
            "Init process",
            "A small PID 1 program that reaps adopted child processes and forwards signals to the application.",
        ),
    ),
    "Dockerfile instructions and the first reproducible image": (
        (
            "Dockerfile",
            "A build recipe whose instructions define a sequence of filesystem and configuration changes for an image.",
        ),
        ("`FROM`", "The instruction that selects the base image a build starts from."),
        (
            "`COPY`",
            "The instruction that copies named files from the build context into the image.",
        ),
        (
            "`CMD`",
            "The instruction that supplies the default command a future container runs; it does not execute during the build.",
        ),
        (
            "Image tag",
            "A local, human-readable name for a built image; creating one does not push anything to a registry.",
        ),
    ),
    "Build context, .dockerignore and accidental data exposure": (
        (
            "Build context",
            "The set of files a builder may read during a build, usually the directory passed to the build command.",
        ),
        (
            ".dockerignore",
            "A file of patterns that removes matching paths from the build context before the builder receives it.",
        ),
        (
            "Ignore pattern",
            "One line in .dockerignore, such as a directory name or glob, that excludes matching paths.",
        ),
        (
            "Layer history",
            "The stored record of each image layer, which can keep a file even after a later instruction deletes it.",
        ),
        (
            "Explicit COPY",
            "Copying only named files instead of the whole context, so every file in the image has a known reason to be there.",
        ),
    ),
    "Layers, cache invalidation and efficient rebuilds": (
        ("Layer", "The recorded filesystem changes produced by one build step."),
        (
            "Build cache",
            "Stored results of earlier build steps that the builder reuses when an instruction and its inputs are unchanged.",
        ),
        (
            "Cache invalidation",
            "The point where a changed instruction or input forces that step and every later step to run again.",
        ),
        (
            "Instruction order",
            "The sequence of Dockerfile steps, which decides how much work a single changed input invalidates.",
        ),
        (
            "Dependency layer",
            "A layer built from dependency metadata such as a lockfile, placed before frequently edited source so it stays cached.",
        ),
    ),
    "Environment variables, command arguments and configuration": (
        (
            "Environment variable",
            "A named string value supplied to a process, which the application must parse and validate itself.",
        ),
        (
            "`ENTRYPOINT`",
            "The Dockerfile instruction that sets the executable a container runs, with `CMD` supplying its default arguments.",
        ),
        (
            "Compose interpolation",
            "Substitution of variable references, often from a `.env` file, while Compose renders its model before containers start.",
        ),
        (
            "`env_file`",
            "A service setting that injects the variables from a named file into that service's container environment.",
        ),
        (
            "Configuration validation",
            "Parsing and bounds checking settings at startup, so a missing or malformed value fails with a clear error.",
        ),
    ),
    "Ports, loopback and the first browser request": (
        (
            "Port publishing",
            "Mapping a host address and port to a container port so host traffic can reach a container listener.",
        ),
        (
            "Loopback address",
            "An address such as 127.0.0.1 that points back to the same network namespace, so inside a container it means that container.",
        ),
        (
            "Bind address",
            "The address a server listens on; 0.0.0.0 accepts connections on every interface in its own namespace.",
        ),
        (
            "Host port",
            "The host side of a mapping, such as port 18080 bound to 127.0.0.1 for the fixture.",
        ),
        (
            "Container port",
            "The port the application listens on inside its container, such as 8080 for the fixture.",
        ),
    ),
    "Logs, exit status and observation before repair": (
        (
            "Standard streams",
            "The standard output and standard error channels a process writes to, which Docker's logging driver captures.",
        ),
        (
            "Container logs",
            "The captured stream output for one container, which has bounded retention and is not a database.",
        ),
        (
            "Exit status",
            "The small integer a process returns when it ends, where zero conventionally means success.",
        ),
        (
            "Container state",
            "The engine's record of whether a container is created, running, restarting or exited, plus its exit code.",
        ),
        (
            "Events",
            "The engine's time-ordered stream of lifecycle notices such as create, start, die and stop.",
        ),
    ),
    "Compose services, projects and a complete application": (
        (
            "Compose service",
            "A named definition of how to create containers that share one role, such as `app` or `client`.",
        ),
        (
            "Compose project",
            "The group of containers, networks and volumes that Compose creates and owns for one application.",
        ),
        (
            "`compose.yaml`",
            "The declarative file that describes an application's services, networks and volumes.",
        ),
        (
            "Project name",
            "The explicit identity Compose uses to label and find a project's resources, which keeps commands and cleanup scoped.",
        ),
        (
            "Service name",
            "The key under `services` that also acts as a DNS name for peers on the project's network.",
        ),
    ),
    "Health checks, startup order and real readiness": (
        (
            "Health check",
            "A small command the engine runs on a schedule to classify a container as starting, healthy or unhealthy.",
        ),
        (
            "Readiness",
            "The point where an application can do the work a dependent component needs, which is stronger than its process existing.",
        ),
        (
            "`depends_on`",
            "The Compose setting that orders service startup and can wait for a named condition on a dependency.",
        ),
        (
            "`service_healthy`",
            "A `depends_on` condition that waits until the dependency's health check reports healthy before starting the dependent.",
        ),
        (
            "Startup order",
            "The sequence in which Compose starts services, which helps initialization but does not guarantee later availability.",
        ),
    ),
    "Named volumes, bind mounts and persistence experiments": (
        (
            "Named volume",
            "Engine-managed storage, mounted into containers, that survives container removal and recreation.",
        ),
        (
            "Bind mount",
            "A mapping of an explicitly chosen host path into a container, giving its processes direct access to those host files.",
        ),
        (
            "Temporary filesystem",
            "Volatile storage, usually backed by memory, that disappears when the container stops.",
        ),
        (
            "Container recreation",
            "Removing a container and creating a new one, which discards its writable layer but keeps mounted volumes.",
        ),
        (
            "`volume-nocopy`",
            "A mount option that stops Docker from seeding an empty named volume with the image content at its mount path.",
        ),
    ),
    "First capstone: build, serve, replace and explain": (
        (
            "Image rebuild",
            "Running the build again from current inputs to produce a new image identity for the changed source.",
        ),
        (
            "Container replacement",
            "Removing the old container and starting a new one from the chosen image under the same project.",
        ),
        (
            "Persistent data",
            "State kept on a named volume, such as the fixture counter, that must survive container replacement.",
        ),
        (
            "Image identity",
            "The image ID or digest that shows which build a container actually runs, unlike a reusable tag.",
        ),
        (
            "Health endpoint",
            "A small HTTP path the application answers to report readiness without changing any data.",
        ),
    ),
    "BuildKit, cache mounts and build secrets": (
        (
            "BuildKit",
            "The modern Docker build engine that runs a build graph, reuses cached results and provides special mounts to steps.",
        ),
        (
            "Cache mount",
            "A directory mounted into one build step that keeps reusable downloads between builds without adding them to a layer.",
        ),
        (
            "Secret mount",
            "A file mounted into one build step that exposes sensitive input without copying it into an image layer.",
        ),
        (
            "Build secret",
            "Sensitive build input supplied with the `--secret` option, never through `ARG`, `ENV`, a source file or a command URL.",
        ),
        (
            "Cold build",
            "A build with no reusable cache, which shows the full cost of every step and every external download.",
        ),
    ),
    "Multi-stage builds and runtime dependency boundaries": (
        (
            "Multi-stage build",
            "A Dockerfile with more than one `FROM` instruction, where each stage has its own filesystem and configuration.",
        ),
        (
            "Builder stage",
            "A stage that holds the compilers, tools and tests needed to produce an artifact but not to run it.",
        ),
        (
            "`COPY --from`",
            "The instruction form that copies a chosen artifact from an earlier stage into the current one.",
        ),
        (
            "Final stage",
            "The shipped runtime image, which should contain only what the artifact needs to start and run.",
        ),
        (
            "Target stage",
            "A named stage selected with the `--target` build option, which deliberately stops the build there for debugging or testing.",
        ),
    ),
    "CPU architectures, image indexes and cross-platform builds": (
        (
            "CPU architecture",
            "A machine instruction family such as `amd64` or `arm64` that a binary is compiled for.",
        ),
        (
            "Image index",
            "A multi-platform list that points to platform-specific images so the engine can select a compatible one.",
        ),
        (
            "Target platform",
            "The operating system and architecture pair, such as `linux/arm64`, requested with the `--platform` option.",
        ),
        (
            "Emulation",
            "Executing foreign-architecture instructions through a translator such as QEMU, which is slower and does not prove native behavior.",
        ),
        (
            "Cross-compilation",
            "A compiler running natively while emitting binaries for a different target architecture.",
        ),
    ),
    "Bridge networks, service DNS and container-to-container traffic": (
        (
            "Bridge network",
            "A virtual network on one engine that connects container interfaces; Compose creates a user-defined one per project.",
        ),
        (
            "Service DNS",
            "Name resolution that maps a Compose service name such as `app` to a current container address on the network.",
        ),
        (
            "Container-to-container traffic",
            "Requests between peers on a shared network, such as client to `app:8080`, that never use the host's published port.",
        ),
        (
            "Network vantage point",
            "The namespace a request starts from, which decides what names and addresses such as localhost mean.",
        ),
    ),
    "Network isolation, gateways and outbound connectivity": (
        (
            "Gateway",
            "The router address that forwards a network's traffic to destinations beyond it.",
        ),
        (
            "Internal network",
            "A Docker network marked internal, which blocks external connectivity for the containers attached to it.",
        ),
        (
            "Outbound connectivity",
            "A container's ability to reach destinations outside its network, normally through routing and address translation.",
        ),
        (
            "Network mode none",
            "A setting that gives a container no ordinary external networking, suited to pure computation.",
        ),
        (
            "Host networking",
            "A mode where the container uses the host's network stack directly, removing a major layer of network isolation.",
        ),
    ),
    "Users, UID ownership and writable data paths": (
        (
            "UID",
            "A numeric user ID that the kernel uses for ownership and permission checks, independent of any username label.",
        ),
        (
            "`USER`",
            "The Dockerfile instruction that sets the user, by name or UID, that later steps and the container process run as.",
        ),
        (
            "File ownership",
            "The user and group IDs recorded on a file, which together with its mode decide who can read or write it.",
        ),
        (
            "Writable data path",
            "A directory such as /data that the image deliberately prepares as writable for the non-root process.",
        ),
        (
            "Non-root user",
            "A process identity other than UID 0, which reduces the ordinary privileges of the application.",
        ),
    ),
    "Backups, restores and proving data recovery": (
        ("Backup", "A retained copy of state intended for recovery."),
        ("Restore", "Reconstructing usable state from a backup into a chosen target."),
        (
            "Recovery test",
            "An independent restore followed by checks that prove a backup actually recovers the expected data.",
        ),
        (
            "Volume archive",
            "A tar file of a named volume's contents, made while the application is stopped.",
        ),
        (
            "Consistency boundary",
            "The condition, such as a stopped application, under which copied data is complete and safe to restore.",
        ),
    ),
    "Resource limits, contention and honest performance experiments": (
        (
            "Memory limit",
            "A cap on a container's accounted memory, beyond which its processes can be killed under memory pressure.",
        ),
        (
            "CPU limit",
            "A quota on the CPU time a container's cgroup may use per period, which throttles work but does not reserve a core.",
        ),
        (
            "PID limit",
            "A bound on how many processes a container may create, set in Compose with `pids_limit`.",
        ),
        (
            "Contention",
            "Competition among workloads for the same shared CPU, memory or I/O, which slows each of them.",
        ),
        (
            "Measurement",
            "Several recorded runs with a fixed workload, image, limits and host allocation that support an honest performance claim.",
        ),
    ),
    "Read-only filesystems, capabilities and least privilege": (
        (
            "Linux capabilities",
            "Named pieces of traditional root privilege that can be granted or dropped individually.",
        ),
        (
            "`cap_drop`",
            "The Compose setting that removes listed capabilities, often `ALL`, from a service's processes.",
        ),
        (
            "`read_only`",
            "The Compose setting that makes a container's root filesystem read-only, leaving only explicit mounts writable.",
        ),
        (
            "`no-new-privileges`",
            "A security option that stops a process from gaining privileges through set-user-ID programs or similar mechanisms.",
        ),
        (
            "Least privilege",
            "Granting a process only the permissions its real work needs, then testing that the application still functions.",
        ),
    ),
    "Rootless engines, user namespaces and host trust": (
        (
            "Rootless mode",
            "Running the engine and its containers under an ordinary user identity without a root daemon.",
        ),
        ("User namespace", "A kernel mapping of container user IDs to different host user IDs."),
        (
            "Engine socket",
            "The daemon API endpoint through which any authorized client can create containers with powerful host access.",
        ),
        (
            "Host trust",
            "What a process may do to the host, as decided by its capabilities, ID mappings, mounts and daemon access.",
        ),
        (
            "Root inside a container",
            "UID 0 within a container, which is not automatically host root but is also not automatically harmless.",
        ),
    ),
    "Image names, digests and an offline transfer": (
        (
            "Image reference",
            "A name made of an optional registry, a repository, and an optional tag or digest.",
        ),
        ("Tag", "A mutable, human-friendly name that can be moved to different image content."),
        (
            "Digest",
            "A content hash that identifies exact image bytes and cannot be moved to other content.",
        ),
        (
            "`docker image save`",
            "The command that exports local images into an archive for transfer without a registry.",
        ),
        (
            "Archive checksum",
            "A hash of the archive, compared with a value from a trustworthy channel, that detects altered transfers.",
        ),
    ),
    "Compose overrides, profiles and configuration review": (
        (
            "Override file",
            "A Compose file layered on a base file that changes or adds to the application model.",
        ),
        (
            "Merge rules",
            "The rules for combining Compose files, which differ for scalar values, mappings and sequences such as ports.",
        ),
        (
            "Profile",
            "A label that makes a service optional, so it starts only when that profile is enabled or the service is named.",
        ),
        (
            "Effective model",
            "The combined configuration after every file, override and interpolation has been applied.",
        ),
        (
            "`docker compose config`",
            "The command that renders and validates the effective model without starting anything.",
        ),
    ),
    "Intermediate capstone: a recoverable two-tier teaching system": (
        (
            "Two-tier system",
            "An application tier that owns state plus a client tier that reaches it through service DNS.",
        ),
        (
            "Service DNS",
            "Lookup of a peer by its Compose service name, so the client survives the app container's address changing.",
        ),
        (
            "Resource limits",
            "Bounds on memory, CPU and processes that keep each service's execution constrained and predictable.",
        ),
        (
            "Restore target",
            "A separate, disposable volume or project that receives a backup during a recovery test.",
        ),
        (
            "Operator guide",
            "A short document naming the project, the state volume, inspection steps and what can be removed safely.",
        ),
    ),
    "Registries, tags, digests and deliberate publication": (
        ("Registry", "A service that stores image manifests and blobs for distribution."),
        ("Repository", "A group of related image names, with their tags, inside a registry."),
        (
            "Authorization",
            "The decision about which operations an authenticated identity may perform, such as pull but not overwrite.",
        ),
        (
            "Release tag",
            "A tag used for a published release, which a reviewed process should resolve to an immutable digest.",
        ),
        (
            "Publication review",
            "A deliberate check of credentials, destination, retention and rollback before anything is pushed.",
        ),
    ),
    "Software bills of materials and image provenance": (
        ("SBOM", "A software bill of materials listing the components included in an artifact."),
        (
            "Provenance",
            "A record of how an artifact was built, including its inputs and builder information.",
        ),
        (
            "Attestation",
            "A build statement, such as an SBOM or provenance record, stored with a specific image in its image index.",
        ),
        ("SPDX", "A standard format for exchanging SBOM data about packages, files and licenses."),
        (
            "Image digest",
            "The immutable identity an SBOM or provenance record must be tied to before it supports a release decision.",
        ),
    ),
    "Vulnerability findings, patching and dependency updates": (
        (
            "Vulnerability finding",
            "A scanner's match between a component version and a published issue, which is evidence to investigate, not a verdict.",
        ),
        ("Affected version", "A component version that the published issue lists as vulnerable."),
        (
            "Scanner",
            "A tool that inventories an image's components and matches them against vulnerability data under its own rules.",
        ),
        (
            "Base image update",
            "Moving the `FROM` reference to a patched base so a rebuild picks up fixed operating-system packages.",
        ),
        (
            "Rebuild and retest",
            "Producing a new image from updated inputs and running the relevant tests on that final image before replacing containers.",
        ),
    ),
    "CI builds, test layers and artifact promotion": (
        (
            "Continuous integration",
            "Running repeatable checks automatically whenever source changes.",
        ),
        (
            "CI test stage",
            "A pipeline step that tests the built image itself, beyond the source tests that ran earlier.",
        ),
        (
            "Image promotion",
            "Artifact promotion for containers, moving one already tested immutable image through delivery stages instead of rebuilding different bytes for each.",
        ),
        (
            "Immutable digest",
            "The content identity that links the tested image to the deployed one.",
        ),
        (
            "Parallel jobs",
            "Pipeline jobs that run at the same time and need isolated or deliberately serialized shared fixtures.",
        ),
    ),
    "Debugging minimal images without changing the contract": (
        (
            "Minimal image",
            "An image that omits a shell, package manager and debugging tools to reduce size and unneeded functionality.",
        ),
        (
            "Debug container",
            "A separate, short-lived tools container started deliberately to inspect a running application.",
        ),
        (
            "Shared namespaces",
            "Joining another container's process or network namespace, so a tools container sees the app's processes and network stack.",
        ),
        (
            "Diagnostic vantage point",
            "The namespace and permissions a diagnostic command runs with, which decide what it can actually observe.",
        ),
    ),
    "Restart policies, failure loops and idempotent startup": (
        (
            "Restart policy",
            "A rule telling the engine when to restart an exited container, such as on-failure or unless-stopped.",
        ),
        (
            "Crash loop",
            "Repeated restarts of a process that fails on every startup, consuming resources and repeating side effects.",
        ),
        (
            "Idempotent startup",
            "Initialization that can run again without creating duplicate or conflicting state.",
        ),
        (
            "Backoff",
            "A growing delay between restart attempts that limits how quickly a failing service is retried.",
        ),
    ),
    "Application migrations and durable state versioning": (
        ("Migration", "A change that moves stored data or a schema from one version to another."),
        (
            "Schema version",
            "A stored marker, such as the fixture's `schema_version` field, that tells code which data format it is reading.",
        ),
        (
            "Rollback",
            "Returning to an earlier image, which does not automatically reverse a data migration.",
        ),
        (
            "Durable state",
            "Data that outlives containers and images and therefore carries its own version and recovery needs.",
        ),
        (
            "Precondition",
            "A fact about the starting schema or data that a migration verifies before changing anything.",
        ),
    ),
    "Image size, startup latency and measurement": (
        (
            "Image size",
            "The stored and transferred size of an image, which affects pulls but is only one part of startup cost.",
        ),
        (
            "Startup latency",
            "The time from a start request to a usable application, including pulling, unpacking, creation and initialization.",
        ),
        (
            "Incremental download",
            "The new layer data an engine must fetch, which is often smaller than the displayed total image size.",
        ),
        (
            "Cold cache",
            "A measurement condition with images or build cache missing, so transfer and initialization costs are included.",
        ),
        (
            "Warm restart",
            "A measurement condition with layers already present locally, so transfer cost is excluded and only startup work is timed.",
        ),
    ),
    "Compose on one host and the limits of orchestration": (
        (
            "Single-host Compose",
            "Defining and operating a related application on one selected engine, with no multi-node recovery.",
        ),
        (
            "Orchestration",
            "Coordinating desired state for workloads across many resources and failure domains.",
        ),
        (
            "Scheduling",
            "Deciding which node runs each workload based on resources, constraints and policy.",
        ),
        (
            "Failure domain",
            "A set of resources, such as one host, that can fail together and take every workload on it down.",
        ),
        (
            "Desired state",
            "The declared configuration that an orchestrator's controllers continually work to make true.",
        ),
    ),
    "TLS, reverse proxies and publishing responsibly": (
        (
            "TLS",
            "A protocol that authenticates the server identity and encrypts traffic in transit under a certificate trust model.",
        ),
        (
            "Certificate",
            "A signed document binding a server name to a public key, which clients verify through trusted issuers.",
        ),
        (
            "Reverse proxy",
            "A server that receives client requests and forwards them to an upstream application, often terminating TLS.",
        ),
        (
            "Public exposure",
            "Making a service reachable from the internet, which adds identity, access control, patching and abuse handling duties.",
        ),
        (
            "Forwarded header",
            "A proxy-added claim about the original client, which an application should trust only from known proxies.",
        ),
    ),
    "Incident response, disk pressure and scoped cleanup": (
        (
            "Incident",
            "An observed deviation from expected behavior that requires diagnosis or recovery.",
        ),
        (
            "Disk pressure",
            "A shortage of free disk space caused by images, build cache, writable layers, logs or volumes.",
        ),
        (
            "`docker system df`",
            "A read-only command that reports disk usage by images, containers, local volumes and build cache.",
        ),
        (
            "Pruning",
            "Removing resources that a tool's rules consider unused, which is not the same as unimportant.",
        ),
        (
            "Scoped cleanup",
            "Deleting only identified resources whose ownership and retention are known, then verifying recovery.",
        ),
    ),
    "Namespaces, cgroups, OCI and the runtime beneath Docker": (
        (
            "Namespace",
            "A kernel feature that changes which operating-system objects, such as processes or mounts, a process can see.",
        ),
        ("cgroup", "A kernel group of processes used for resource accounting and limits."),
        (
            "OCI",
            "The Open Container Initiative, which defines image and runtime specifications for interoperability.",
        ),
        (
            "OCI runtime",
            "The low-level program that creates a container process from a bundle according to the OCI runtime specification.",
        ),
        (
            "containerd",
            "The container manager that Docker tooling can use to pull images and supervise containers through an OCI runtime.",
        ),
    ),
    "Runtime secrets, configuration files and controlled disclosure": (
        (
            "Runtime secret",
            "Sensitive input an application needs while it runs, with a different lifecycle from a build secret.",
        ),
        (
            "Secret file",
            "A file that Compose mounts into a selected service to deliver a declared secret's value.",
        ),
        (
            "/run/secrets",
            "The in-container directory where Compose places declared secrets as files.",
        ),
        (
            "Controlled disclosure",
            "Exposing a secret only to the processes that need it and keeping it out of logs, reports and screenshots.",
        ),
        (
            "Rotation",
            "Replacing a secret value with a new one and retiring the old value without exposing either.",
        ),
    ),
    "Scaling replicas, shared state and concurrency traps": (
        (
            "Replica",
            "Another instance of the same application role, which adds capacity only if routing and state design allow it.",
        ),
        (
            "Shared state",
            "Data that several replicas read or write, such as one file or session store.",
        ),
        (
            "Race condition",
            "A defect where the outcome depends on the timing of concurrent operations.",
        ),
        (
            "Lost update",
            "A race where one writer's change overwrites another's because both read the same old value.",
        ),
        (
            "Load balancer",
            "A component that distributes requests among replicas but does not synchronize their memory, sessions or files.",
        ),
    ),
    "Advanced capstone: a release, recovery and teaching handoff": (
        (
            "Release record",
            "A document tying an image identity to its source inputs, tested engine and platform, and observed behavior.",
        ),
        (
            "Recovery rehearsal",
            "Practicing backup and restore against a disposable target to prove the recovery procedure works.",
        ),
        (
            "Handoff",
            "Passing a system to another operator with enough evidence and instructions to run it independently.",
        ),
        (
            "Acceptance evidence",
            "Recorded observations that show the released image meets its runtime, persistence and restore requirements.",
        ),
        (
            "Assumption",
            "A belief not yet verified, which a good release explanation keeps separate from observed facts.",
        ),
    ),
}

# Per-lesson diagnosis advice for the Exercise 4 boundary case, keyed by lesson
# id. Each entry names the first observation for that lesson's own failure.
BOUNDARY = {
    "docker-001": "Compare `docker ps` with `docker ps -a` for the same container ID before deciding anything was deleted, and read the STATUS column rather than the name.",
    "docker-002": "Run `docker version` and read whether the Server section appears at all; a printed client version alone says nothing about the engine, the selected context or socket permission.",
    "docker-003": "Record the container ID from `docker compose ps -q app` before and after `up`, then note which path the missing file was written to, so the evidence separates recreation from a bad write.",
    "docker-004": "List the processes inside the container and identify which one is PID 1 before reading the running status as evidence about the server.",
    "docker-005": "Read the build log line that names the context size and the failing `COPY` source path before moving any file or widening the context directory.",
    "docker-006": "Use `docker history` on the image to list every layer with its size; a later `rm` step does not remove the earlier `COPY` layer from that list.",
    "docker-007": "Compare the text of the cached `RUN` instruction with the bytes it downloads; an unchanged instruction can be served from cache even when the remote file changed.",
    "docker-008": "Print the argument vector the program actually received, and compare the exec array with the shell form, before adding a shell wrapper to the command.",
    "docker-009": "Check which address the server binds inside the container, `127.0.0.1` or `0.0.0.0`, before editing the published mapping or the browser URL.",
    "docker-010": "Send one request to the application and read its status code and log line; a container STATUS of Up only reports that the main process exists.",
    "docker-011": "List the existing projects, containers and published ports with their labels before renaming or removing anything that might belong to another copy.",
    "docker-012": "Run the healthcheck command from inside the container and the browser request from the host, then compare the two paths hop by hop.",
    "docker-013": "Compare the files in `/app` from the image with the files the running container shows, and read the mount table for the same path.",
    "docker-014": "Change only the host side of one published port in a scratch copy, record the first failing request, then restore the mapping and confirm the original request succeeds again.",
    "docker-015": "Search the build output and the final image layers for the secret value's location, not the value itself, before blaming the secret mount option.",
    "docker-016": "Read the `--target` flag and the final stage name in the build command, then list the shipped image's files to see which stage produced it.",
    "docker-017": "Compare the image platform with the host architecture and check the executable's format before reading any application code.",
    "docker-018": "Record the resolved address, then test whether anything listens on that address and port inside the target container before touching DNS settings.",
    "docker-019": "Restore the bridge network, reproduce the original refusal and read the published mapping and listen address that host mode was hiding.",
    "docker-020": "Record the effective UID and GID in the container, the owner and mode of the mounted path on the host, and the exact operation that was denied.",
    "docker-021": "Parse and validate the restored file with the application's own reader; a matching checksum only shows the bytes were copied faithfully.",
    "docker-022": "Check `docker stats` CPU% against the cpus quota and the cgroup `cpu.stat` `nr_throttled` count before reading memory usage.",
    "docker-023": "Read the application's error for the exact path it tried to write, then decide whether that cache is temporary, durable or avoidable before choosing a mount.",
    "docker-024": "Identify which step needs engine access and move it to a host worksheet the learner runs deliberately, rather than granting the browser session a socket.",
    "docker-025": "Run `docker image ls` for the exact repository and tag before the run; with `--pull never` an absent image is reported as an error rather than downloaded.",
    "docker-026": "Render the merged model with `docker compose config` and read the complete `ports` list for the service before assuming an override replaced it.",
    "docker-027": "Send the same request from the host and from a peer container, then compare the host mapping with the service name and internal port the peer used.",
    "docker-028": "Resolve the tag to its current digest and compare it with the digest recorded beside the earlier acceptance evidence.",
    "docker-029": "Identify who issued the provenance statement and whether a verification policy accepts that issuer before reading any of its fields as fact.",
    "docker-030": "Resolve the tag named in the scan report to a digest, compare it with the deployed digest, and note the scanner's database date.",
    "docker-031": "Compare the digest that passed acceptance with the digest being deployed; if they differ, the acceptance result does not yet apply.",
    "docker-032": "Write down what the interactive change revealed, then recreate the container from the maintained image to confirm the repair is gone.",
    "docker-033": "Count the seed records after each start and read the initializer to see whether it checks for existing state before writing.",
    "docker-034": "Read the version marker in the stored data and compare it with the versions the rolled-back reader accepts before restarting it again.",
    "docker-035": "Compare the file lists of the working and optimized images for certificate bundles and libraries before measuring size again.",
    "docker-036": "Name the storage class and provisioner the translated claim depends on, and check whether a restore procedure exists for its data.",
    "docker-037": "Read the proxy log for the upstream it contacted and request the app route directly from an owned vantage point before changing either side.",
    "docker-038": "Read the volume's labels and creating project, and ask who owns its data, before treating unattached as unwanted.",
    "docker-039": "Record the host's cgroup version and mount layout, then map the example's path onto it without changing kernel or boot settings.",
    "docker-040": "Render the effective Compose model and read the service's `secrets` list before editing file permissions or adding a host mount.",
    "docker-041": "Read which replica holds the published host port and which replicas failed to start, then decide between a routing layer and distinct ports.",
    "docker-042": "Write down the single layer you changed, the first observation that failed, and the request that proves the repair, before running the full acceptance again.",
}

# Per-lesson retrieval prompt, keyed by lesson id, used beside worked example 2.
RETRIEVAL = {
    "docker-001": "From memory, give one creation event and one removal event for each of image, container and writable layer.",
    "docker-002": "Without notes, say which command output proves the client works and which proves the engine answers.",
    "docker-003": "Predict whether a file written to `/tmp` in the container survives `restart`, `up --force-recreate` and an image rebuild.",
    "docker-004": "Describe what happens to the main process during `docker compose stop --timeout 10` when it ignores SIGTERM.",
    "docker-005": "List the Dockerfile instructions of the fixture in order and say which one changes when only the source file changes.",
    "docker-006": "Name two files from the fixture directory that should never reach the build context, and the ignore rule that excludes each.",
    "docker-007": "Predict which build steps rerun after editing only `server.py` with the dependency file copied first.",
    "docker-008": "Explain from memory why `restart` keeps the old environment while recreating the service applies the new value.",
    "docker-009": "Trace a host request to `127.0.0.1:18080` and a peer request to `app:8080` without looking at the diagram.",
    "docker-010": "Recall which exit code each program produced and which log line identified the failure.",
    "docker-011": "Name every resource the `ds60-docker-study` project creates and which of them `down` keeps.",
    "docker-012": "Say what `condition: service_healthy` waits for and what it cannot promise about a host browser request.",
    "docker-013": "Predict the counter value after recreating the app with the named volume kept, and after removing that volume.",
    "docker-014": "Recall the container IDs before and after recreation and what their difference proves about replacement.",
    "docker-015": "Explain where the secret is visible during a `RUN --mount=type=secret` step and where it must not appear afterward.",
    "docker-016": "List what the final stage copies from the builder and what it deliberately leaves behind.",
    "docker-017": "Name the image index entry the engine selects on an arm64 host and the error a mismatched binary produces.",
    "docker-018": "Recall which destination the host browser, a peer client and the app healthcheck each use, and why they differ.",
    "docker-019": "Predict the output of the computation under `--network none` and explain why no network was needed.",
    "docker-020": "Recall the UID and GID the fixture image runs as and which host paths it may write.",
    "docker-021": "List the restore steps in order and name the check that proves the restored data is usable.",
    "docker-022": "Say which column in a `docker stats` sample would rise first under CPU contention and which under a memory leak.",
    "docker-023": "Name the positive and negative acceptance checks and what each would show if the root filesystem were writable.",
    "docker-024": "Explain from memory why mounting `/var/run/docker.sock` grants control of the host.",
    "docker-025": "Recall the commands that move an image offline and the flag that proves no download happened.",
    "docker-026": "Predict the merged `ports` list when both Compose files declare a port for the same service.",
    "docker-027": "Draw the recovery state machine and mark where a failure stops the sequence.",
    "docker-028": "List the fields a release identity record needs and say which one never changes after publication.",
    "docker-029": "Explain what an SBOM describes, what a provenance statement claims and which object both refer to.",
    "docker-030": "Trace the patch steps and name the identity you would record before replacing the container.",
    "docker-031": "Recall the receipt fields and say which one ties the test result to the exact artifact.",
    "docker-032": "Name one observation from each vantage point, host, peer and app, without looking back.",
    "docker-033": "Rewrite the unsafe initializer as the safe sequence from memory.",
    "docker-034": "Recall the order of the compatible transition and the point after which rollback needs a migration back.",
    "docker-035": "List the startup phases and say which one an image size reduction can shorten.",
    "docker-036": "Map each Compose concept to the requirement it becomes on a cluster without looking at the table.",
    "docker-037": "Match a certificate mismatch, a proxy 502 and an app 401 to the layer that failed.",
    "docker-038": "Say what `docker compose down` removes and what it leaves for a separate, deliberate decision.",
    "docker-039": "Match network namespace, mount namespace, cgroup and OCI runtime to what each isolates or controls.",
    "docker-040": "Recall how the validator proves the secret is present without printing it.",
    "docker-041": "Name the requirement each of routing, shared data, sessions and retries adds when replicas increase.",
    "docker-042": "Trace one browser request through the system and one peer request, naming every port.",
}
