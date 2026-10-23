# Docker-only classroom

Use the browser classroom on Windows, macOS, or Linux with a local
Linux-container engine and **Docker Compose v2.24.4 or newer**. Legacy
`docker-compose` v1 is not supported. The course itself needs
no host Python, PowerShell script, Bash script, or native PostgreSQL. Download
and fully extract the course ZIP, then open a terminal in the folder containing
`compose.classroom.yaml`. The Docker commands below are identical across OSes;
Windows can use Command Prompt. Run each command separately and stop if it fails.

For engine installation, see [the beginner setup guide](docker-beginners.md#2-install-one-local-container-engine).
Its Windows installation wizard is optional. Once an engine is ready, Windows
users may double-click `START_DOCKER_CLASSROOM.cmd`; Mac users may double-click
`START_DOCKER_CLASSROOM.command`. Both prepare the Python/NumPy starter. The
manual commands below expose the same preparation and are useful on every OS.

## 1. Check the engine and configuration

```text
docker compose version
docker info --format "{{.OSType}}"
docker compose -f compose.classroom.yaml config --quiet
```

The engine type must be `linux`; the configuration check should finish without
an error. Select your local engine rather than a remote Docker context.
An unknown `!reset` tag means Compose needs updating. A plain YAML validator
does not understand every Compose tag.

## 2. Build the starter, with visible logs

First preparation needs internet and several gigabytes of free disk. Heavy
framework and Spark images need additional space. Build one image at a time
and keep the terminal open until each command succeeds:

```text
docker compose -f compose.classroom.yaml pull postgres
docker compose -f compose.classroom.yaml --parallel 1 --progress plain build lab
docker compose -f compose.classroom.yaml --profile python-core --parallel 1 --progress plain build python-core-worker
```

Build the lab first; its Python worker reuses that base. These foreground
builds show download and package-install output; they do not publish images.
Later starts reuse the prepared local images.

## 3. Start and practice

```text
docker compose -f compose.classroom.yaml --profile python-core up -d --no-build --pull never --wait lab python-core-worker
docker compose -f compose.classroom.yaml --profile "*" ps
```

Wait for readiness, then open [the module classroom](http://127.0.0.1:8765/journeys)
yourself. [The original Python/SQL lab](http://127.0.0.1:8765/learn) is also
available. No website account is needed. The initializer prepares private worker
credentials and writable learner storage inside Docker volumes.

Start with a reading lesson or a `python-core` lesson such as `llm-002`.
Read the guide, predict the result, edit and save your source, then choose Run.
Save your explanation as well as your code. A successful example run does not
complete the six exercises or establish mastery. Planned lessons remain planned.

If a runtime is unavailable, prepare that profile before running its lesson:

| Profile | Service to build/start | Used for |
| --- | --- | --- |
| `python-core` | `python-core-worker` | NumPy, current LLM foundations, early TensorFlow math |
| `cpp20` | `cpp-worker` | C++20 compilation |
| `tensorflow-cpu` | `tensorflow-worker` | Actual TensorFlow tensors and gradient updates |
| `scala-jvm` | `scala-worker` | Standalone Scala/JVM |
| `spark-local-scala` | `spark-scala-worker` | Local Spark using Scala |
| `spark-local-python` | `spark-python-worker` | Local Spark using Python |

For example, add C++ after the starter:

```text
docker compose -f compose.classroom.yaml --profile cpp20 --parallel 1 --progress plain build cpp-worker
docker compose -f compose.classroom.yaml --profile python-core --profile cpp20 up -d --no-build --pull never --wait lab python-core-worker cpp-worker
```

Use the matching profile and service names for another subject. Build selected
workers sequentially and start only those you need. The current NumPy LLM pilot
needs no downloaded model or PyTorch image. CPU PyTorch is a separate recipe,
outside these six qualified classroom profiles.

## 4. Pause, return, and keep your work

```text
docker compose -f compose.classroom.yaml --profile "*" stop
```

To return, start the same engine, open the same course folder, and repeat your
Step 3 `up` command with the same profiles. Replacing app containers preserves
the named volumes. The default project is **`ds60-classroom`**:

| Docker volume | What it keeps |
| --- | --- |
| `ds60-classroom_classroom-learning` | Pads, module drafts, notes, saved results, history, progress and caches |
| `ds60-classroom_postgres-data` | PostgreSQL tables |
| `ds60-classroom_classroom-runtime` | Private worker credential, excluded from learning exports |

This is machine-local Docker storage, usually inside the engine's Linux VM.
It is **not** the visible `.learning` folder beside your checkout. The older
host-folder launchers keep using their own storage; switching routes does not
copy or merge either learning work or databases. Keep the same Docker project
to resume the same classroom. A different project name selects different volumes.

Use `stop` for ordinary pauses. **Do not use `down -v` or remove these volumes
to troubleshoot:** that can delete saved work and database data. Engine removal
or a factory reset can also remove volumes. Export before moving machines.

## 5. Export learning work and the database

Choose unused host filenames for every backup. The date below is just an example;
change it for a new backup. Save all drafts and let active Runs finish first.
With PostgreSQL still running, create and copy its ordinary dump file:

```text
docker compose -f compose.classroom.yaml exec -T postgres pg_dump -U ds60_admin -d advanced_sql_training -Fc -f /tmp/classroom-database.dump
docker compose -f compose.classroom.yaml cp postgres:/tmp/classroom-database.dump ./classroom-database-20261022.dump
docker compose -f compose.classroom.yaml --profile "*" stop
```

Now archive only the learning volume through a temporary container. Verify the
volume name first. If it is missing, stop and check the project name rather
than creating an empty replacement. The helper name must also be unused:

```text
docker volume inspect ds60-classroom_classroom-learning --format "{{.Name}}"
docker create --name ds60-classroom-backup --network none --mount type=volume,source=ds60-classroom_classroom-learning,target=/learning,readonly --entrypoint tar postgres:17 -czf /tmp/classroom-learning.tar.gz -C /learning .
docker start -a ds60-classroom-backup
docker inspect --format "{{.State.ExitCode}}" ds60-classroom-backup
docker cp ds60-classroom-backup:/tmp/classroom-learning.tar.gz ./classroom-learning-20261022.tar.gz
```

The exit-code check must print `0` before copying. Check the copied archive
in your normal file manager or archive utility.
It should contain the saved learning files you used, including `modules/` for
module drafts. Keep both the learning archive and database dump in your backup
location. After the copy succeeds, remove **only** the temporary helper:

```text
docker rm ds60-classroom-backup
```

The source volume was read-only; private runtime credentials were not mounted
or exported. These commands avoid binary shell redirection and work without
a host Python installation. The database dump and learning archive protect
different data; neither replaces the other.

To transfer, copy both exports to the new machine and retain the originals.
An archive utility lets you inspect the exported source and notes. For a few
exercises, copy that source into a fresh workspace and Save; this does not move
its full history or database. The optional [host-folder route](docker-beginners.md#keep-the-same-learning-folder-across-a-future-checkout)
has a different storage contract. Full database/volume restoration needs a
deliberate target and ownership checks; the export commands here do not import,
merge, or overwrite another classroom.

If you chose another Compose project, substitute its actual learning-volume
name and keep that project consistent throughout. Never include the private
`classroom-runtime` volume or a Kubernetes session in a learning backup.

## Troubleshooting and optional Kubernetes

Inspect startup without deleting data:

```text
docker compose -f compose.classroom.yaml --profile "*" ps -a
docker compose -f compose.classroom.yaml logs --tail 100 lab classroom-init postgres
```

If port 8765 is already occupied, stop the other course instance you own before
starting this one. A worker health failure needs its service log, for example
`docker compose -f compose.classroom.yaml logs --tail 100 cpp-worker`.

Kubernetes remains an extra [owned host-preparation workflow](modules-runtime.md#prepare-and-run-the-owned-kubernetes-lab)
with an expiring scoped lease. It is not created by these commands. No engine
socket is mounted into the ordinary app or its six workers. The optional
PowerShell/Bash launchers remain available for the existing host-folder route.

Command semantics checked against Docker's official [Compose profiles](https://docs.docker.com/compose/how-tos/profiles/),
[volume storage](https://docs.docker.com/engine/storage/volumes/) and
[file-copy reference](https://docs.docker.com/reference/cli/docker/container/cp/),
plus the [Compose merge requirements](https://docs.docker.com/reference/compose-file/merge/)
on 22 October 2026. Runtime qualification is recorded in the
[implementation checkpoint](implementation/CHECKPOINT.md).
