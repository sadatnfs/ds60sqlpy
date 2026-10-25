# Classroom troubleshooting

Start from the failing machine and the exact command and error. A successful
run on another computer does not establish this computer's engine state.
Keep saved volumes intact while diagnosing. Run commands from the course
folder in Bash on macOS/Linux or Ubuntu in Windows WSL 2.

## First checks

```bash
docker context show
docker info --format '{{.OSType}}'
docker compose version
./classroom doctor
./classroom status
```

Use the same `--project NAME` on classroom commands if you chose a custom
project. Keep useful error lines and runtime versions; do not share environment
files, credentials, tokens or full database URLs.

## The engine is unavailable

Start Docker Desktop or Rancher Desktop and wait for its engine to become
ready. On Linux, check the installed Docker service and your user's access.
`docker version` must show a server as well as a client. A remote Docker
context is not the supported local-browser setup. Rancher Desktop must use
**Moby**, since its containerd mode uses a different tool interface.

On Windows, use WSL 2 and enable your engine's integration with the Ubuntu
distribution you are running. Check `wsl --list --verbose` from Windows
Terminal. Do not install a second competing daemon inside Ubuntu just to hide
an integration problem. See the [Windows guide](setup/windows.md).

On Linux, follow the engine's documented permissions setup. Do not make the
Docker socket writable by everyone or run the entire classroom as root.
Membership in the Docker group carries substantial host privileges.

## Compose rejects the configuration

The classroom needs Compose **2.28.0 or newer**, invoked as `docker compose`.
An error involving `!reset`, unsupported service options or a missing Compose
command can indicate an older or incomplete installation. Upgrade the Compose
plugin through the engine's documented installation route. A generic YAML
parser is not a full Compose validator.

## The launcher cannot be found or executed

Run it from the extracted folder containing `classroom` and
`compose.classroom.yaml`. A ZIP viewer is not an extracted directory. If an
archive or filesystem lost the executable bit, use `bash classroom --starter`
or `chmod +x classroom` before retrying. Quote paths containing spaces.

Windows uses Ubuntu/WSL for `./classroom`; the thin `.cmd` launcher delegates
to that environment. It does not install Docker, Python or PostgreSQL. See
[OS setup](README.md) if the engine or WSL distribution is missing.

## The browser did not open or shows an old page

Run `./classroom status` and open the current printed `/classroom` URL.
Browser opening can be unavailable from WSL or a headless shell even when the
server is healthy. A changed automatic port can make an old bookmark obsolete.
Use `./classroom --no-browser` when you prefer to open it yourself.

If edited source is absent, remember that an image contains the files present
at build time. Install source updates deliberately with
`./classroom --local-build --rebuild`. Strict `resume` intentionally does not
rebuild. In Hub mode, use the publisher's matching updated tag instead.

## A port is already in use

The launcher normally chooses available loopback ports and remembers settings.
Do not stop an unrelated service to claim its port. Choose unused ports with
`--port` and `--database-port` when preparing this classroom, and use the
current address reported by status. Read the
[one-command guide](one-command-classroom.md) before changing remembered port
settings for an existing project.

## Startup asks for a build, but I only want my previous work

```bash
./classroom resume
```

This forbids both builds and pulls. If a required image is absent, the error
identifies what must be prepared. Check that you selected the same engine,
context, project and image mode. Rebuilding an image does not restore deleted
volumes, and using another project does not open the original saved work.

For normal reuse, `./classroom` starts existing resources and prepares only
missing images. `--rebuild` is a deliberate update action. An explicit
`--profile` selection replaces the remembered worker list, not the saved pads.

## Build downloads fail

Read the first failing download or package step. Registry rate limits,
authentication, proxy configuration, insufficient disk and TLS certificate
errors are different problems. Retry only after addressing the cause.
Do not disable TLS verification. The launcher provides `--registry mirrors`
and `--registry upstream` for supported base-image selection; neither option
repairs an untrusted certificate configuration or publishes your images.

Hub mode needs an existing release tag and platform image in the selected
namespace. `manifest unknown`, access denied or an unavailable architecture
can mean the publisher has not supplied it. Return to local source builds with
`--local-build`, or use a verified tag. See [Hub usage](dockerhub.md).

## Docker reports missing parent snapshots or AlreadyExists

Errors such as `failed to prepare extraction snapshot`, `missing parent`,
`target snapshot ... already exists` or `bucket: not found` occur in the
engine's image storage before the course runs. Repeated course-code edits do
not repair that storage.

1. Stop retrying concurrent builds. Check engine disk space and diagnostics.
2. Export saved learning work and the database while the engine can still
   read them. See [backup instructions](docker-classroom.md#5-export-learning-work-and-the-database).
3. Restart the engine normally and retry the specific image operation.
4. If the problem persists, use the engine vendor's supported storage repair
   or reset procedure after protecting data. A factory reset or global prune
   can affect every project on that engine, not just this classroom.

Switching engines or storage implementations can hide images and volumes
without moving them. Do not conclude that data is gone merely because another
context shows an empty image list. Avoid manual edits to internal snapshot
folders. Keep the original error and engine version for vendor diagnostics.

## A language cannot run

Open the lesson's capability notice. Prepare the matching ordinary profile
from [the runtime table](docker-profiles.md), for example:

```bash
./classroom --profile cpp20 --profile php-cli
```

C++ and Java are compiled in their workers. Node JavaScript and browser
JavaScript have different APIs. HTML/CSS runs in the browser preview, while
PHP executes in the PHP CLI worker. A lesson about HTTP sessions may use its
separate documented project fixture; the single-file PHP pad does not create
a permanent web server.

GPU execution needs a compatible NVIDIA host and explicit preparation. Apple
GPU, AMD GPU and CPU-only learners can use the CUDA conceptual/CPU variants
without claiming CUDA hardware execution. An unavailable GPU variant must not
silently substitute CPU results. Kubernetes live work needs an explicitly
owned local cluster. Neither capability is enabled by ordinary `--all`.

## Preview or output looks wrong

The reader renders code highlighting and mathematics locally. In a browser
HTML/JavaScript lesson, check the console panel for syntax or runtime errors.
External network assets and navigation are restricted; use bundled/local
lesson resources and read the preview capability notice. Live preview is
opt-in, and **Pause** or **Stop** prevents automatic reruns. A saved observation
is a point-in-time record, not permission to execute source when revisiting it.

A worker run's output belongs to the source saved with that run. Later edits to
the pad do not rewrite history. Read the exit status and diagnostic text, not
only whether a chart appeared or stdout contains a success-looking message.

## PostgreSQL or whole SQL lessons fail

SQL snippets accept ordinary SQL. Full course scripts may contain `psql`
commands, so choose **Whole SQL lesson (psql)** for those artifacts. Read the
first PostgreSQL error and the transcript. Check the database identity and
expected schema before modifying a query to make it pass.

A training reset replaces course-owned training data. It is a deliberate
operation, not a general error-recovery button. Warehouse Days 52 through 54
have their own stateful progression. See [PostgreSQL setup](setup/postgresql.md).
For optional JupySQL kernels, use the separate
[notebook guide](setup/jupyter-postgresql.md); Docker worker packages are not
installed into a host notebook interpreter.

## Progress appears missing

Wait for the saved confirmation before leaving a pad. Reopen the same lesson
and variant, then check the engine context and project name. Saved source,
notes and results live in `<project>_classroom-learning`; database tables live
in `<project>_postgres-data`. They are separate from the source checkout and
`.classroom/` launcher settings.

A new source ZIP or rebuilt image does not contain personal progress. Do not
prune volumes, run `down -v`, or reset the engine while investigating missing
work. Restore from a deliberate backup only after checking the exact target.
If volumes were deleted, a source Git checkout cannot reconstruct them.

## Optional models and offline study

An installed package does not imply its model weights, dataset, tokenizer or
compiler cache has been prepared. Read the lesson's offline variant and
preparation disclosure. Do not download models automatically just because a
reference describes them. See [offline preparation](setup/offline.md).

## Reporting a reproducible issue

Include the command, selected project/profile/variant, operating system,
engine and Compose versions, lesson ID, first relevant error and whether the
same saved source reproduces it. State whether you were building, resuming,
reading, compiling or executing. Redact private paths and secrets. For
contributor checks and evidence scope, see [validation](validation.md).
