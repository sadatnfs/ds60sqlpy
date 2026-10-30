# Docker classroom operations

Use `./classroom` as the shared entrypoint on Linux, macOS and Windows WSL 2.
It prepares or resumes one project, waits for readiness and opens the unified
browser classroom. For a first installation, use the
[beginner guide](docker-beginners.md). This reference explains deliberate builds,
profiles, persistence and backup without a second application launcher.

## 1. Check the engine

From the repository or extracted starter folder:

```bash
docker info --format '{{.OSType}}'
docker compose version
./classroom doctor
```

The engine must provide Linux containers and Compose **2.28.0 or newer**.
Rancher Desktop must use Moby for Docker API compatibility. Use a local engine;
the loopback addresses and automatic browser opening assume the engine runs on
your computer. An unknown `!reset` tag usually indicates an older Compose.

## 2. Build with visible logs

For a small first session:

```bash
./classroom --starter
```

For all ordinary workers:

```bash
./classroom --all
```

These commands build missing local images and then start services. To build
without starting, use `./classroom build --all --local-build`. To deliberately
install updated local source and start it:

```bash
./classroom --all --local-build --rebuild
```

Build output stays visible in the terminal. No command here pushes an image.
The ordinary selection excludes optional NVIDIA GPU and owned Kubernetes
capabilities. Avoid replacing it with Compose's wildcard profile selector,
which can select additional capabilities.

The launcher remembers local-build or Hub mode. In Hub mode, `--rebuild`
refreshes published images rather than compiling local source. Use
`--local-build` when the intended input is your checkout. Hub pulls require a
publisher's actual namespace, tag and matching architecture; see
[Docker Hub](dockerhub.md). TLS verification remains enabled for registry
requests. Fix trusted certificate/proxy configuration or choose an approved
registry option rather than disabling verification.

## 3. Select runtimes and practice

`--starter` selects Python Core. `--all` selects the ordinary workers.
`--profile NAME` selects Python Core plus the explicitly named profiles and
replaces the remembered selection; repeat the option to add several:

```bash
./classroom --profile cpp20 --profile php-cli
```

The website and PostgreSQL service are included. HTML/CSS and browser
JavaScript/D3 run in the isolated browser preview, so `html-browser` and
`javascript-browser` are not launcher worker flags. See
[all runtime profiles](docker-profiles.md) for the actual worker names,
source-file contracts and external-project boundaries.

Open the URL printed by the launcher. Read capability notices before running:
not every lesson artifact is a single-file program, and a Python worker is not
a substitute for a missing framework, cluster or GPU. The
[classroom guide](classroom-experience.md) explains reading, code, notes,
manual runs and live preview. The service is for a trusted local learner,
not a public multi-user code execution service.

## 4. Pause, resume and keep state

```bash
./classroom stop
./classroom resume
./classroom status
```

`resume` never builds or pulls. It restarts retained containers and recreates
missing ones only from existing local images. Keep the same project name on
every command, for example `./classroom resume --project my-classroom`.
The default is `ds60-classroom`. The browser port can change during recovery;
use the current printed URL. See [fixed ports](one-command-classroom.md) if a
stable address is needed.

| Storage | Purpose |
| --- | --- |
| `.classroom/<project>/selection.env` | Remembered worker selection and registry settings |
| `.classroom/<project>/ports.env` | Saved port settings |
| `.classroom/<project>/images.env` | Local-build or published-image selection |
| `<project>_classroom-learning` Docker volume | Saved source, notes, progress, results and caches |
| `<project>_postgres-data` Docker volume | PostgreSQL database files |
| `<project>_classroom-runtime` Docker volume | Private runtime credentials; exclude from learner exports |

Docker volumes are normally inside the engine's Linux VM or storage area.
They are not the host checkout's `.learning/` folder. A different engine,
context or project can show a different classroom. Replacing containers keeps
named volumes; deleting volumes or factory-resetting the engine can remove
saved work. Use `stop`, not `down -v`, for an ordinary pause.

## 5. Export learning work and the database

A complete backup has two independent parts: the learning-volume archive holds
saved source, notes, progress and run records; a PostgreSQL logical dump holds
the course database. Neither contains the other. Save your drafts, wait for
active runs to finish and close other tools that can change this database.
This procedure stops the app while taking the dump, then stops the classroom
while archiving learning files, and finally resumes the same project.

Run the following complete block from the course folder in **Bash**, including
Terminal on macOS/Linux or Ubuntu on Windows WSL 2. Change `study_project` if
you use a custom project. The project must already be running. The block creates
a new private backup directory under Documents, creating that parent if needed.
Its parentheses keep `set -eu` local to the procedure: a failed command stops
this backup instead of continuing to later steps.

```bash
(
  set -eu
  study_project=ds60-classroom
  mkdir -p "$HOME/Documents"
  backup_dir="$HOME/Documents/DS60-backup-$(date +%Y%m%d-%H%M%S)"
  mkdir -m 700 "$backup_dir"
  compose=(docker compose --project-name "$study_project" -f compose.classroom.yaml)
  db_container=$("${compose[@]}" ps -q postgres)
  app_container=$("${compose[@]}" ps -q lab)
  [ -n "$db_container" ] && [ -n "$app_container" ]
  backup_image=$(docker inspect --format '{{.Image}}' "$db_container")
  app_image=$(docker inspect --format '{{.Image}}' "$app_container")
  learning_volume="${study_project}_classroom-learning"
  docker volume inspect "$learning_volume" --format '{{.Name}}'
  "${compose[@]}" stop lab
  "${compose[@]}" exec -T postgres pg_dump -U ds60_admin -d advanced_sql_training -Fc -f /tmp/classroom-database.dump
  "${compose[@]}" cp postgres:/tmp/classroom-database.dump "$backup_dir/classroom-database.dump"
  ./classroom stop --project "$study_project"
  backup_helper="${study_project}-backup-$(date +%Y%m%d-%H%M%S)"
  docker create --name "$backup_helper" --pull never --network none --mount "type=volume,source=$learning_volume,target=/learning,readonly" --entrypoint tar "$backup_image" -czf /tmp/classroom-learning.tar.gz -C /learning .
  docker start -a "$backup_helper"
  [ "$(docker inspect --format '{{.State.ExitCode}}' "$backup_helper")" = 0 ]
  docker cp "$backup_helper:/tmp/classroom-learning.tar.gz" "$backup_dir/classroom-learning.tar.gz"
  docker run --rm -i --pull never --network none --read-only --mount "type=bind,source=$backup_dir,target=/backup,readonly" --entrypoint python "$app_image" - <<'PY' >"$backup_dir/SHA256SUMS"
from hashlib import file_digest
from pathlib import Path
for name in ("classroom-learning.tar.gz", "classroom-database.dump"):
    path = Path("/backup") / name
    if path.stat().st_size == 0:
        raise SystemExit("Refusing an empty backup file")
    with path.open("rb") as stream:
        print(f"{file_digest(stream, 'sha256').hexdigest()}  {name}")
PY
  printf 'Source project: %s\nApp image: %s\nPostgreSQL image: %s\n' "$study_project" "$app_image" "$backup_image" >"$backup_dir/backup-info.txt"
  tar -tzf "$backup_dir/classroom-learning.tar.gz" >"$backup_dir/archive-files.txt"
  docker rm "$backup_helper"
  ./classroom resume --project "$study_project" --no-browser
  printf 'Export complete: %s\n' "$backup_dir"
)
```

Read the printed export path. Inspect `archive-files.txt` for expected saved
work and check that both backup files are nonempty. Keep the entire directory,
including `SHA256SUMS` and `backup-info.txt`. Store a second copy somewhere that
will survive an engine reset or loss of this computer. Backup files may contain
your personal notes, code and database records; keep them private.

The helpers use already installed image IDs, never pull images, and mount the
source learning volume read-only. The private `classroom-runtime` credential
volume is neither mounted nor exported. Checksums detect changed backup bytes;
they do not authenticate an archive from someone else. Use backups you created
and trust. A source ZIP, image archive or `.classroom/` settings folder is not
a substitute for this backup.

If a command fails, inspect its first error and retain the partial backup for
diagnosis. The source volumes remain in place. The app may remain stopped;
after addressing the failure, use `./classroom resume --project YOUR_PROJECT`
to return to it. Do not delete source volumes merely because an export failed.
The automatically named helper, if still present, is the only container this
procedure creates outside the source project; remove that exact helper only
once you have inspected the outcome.

This recipe assumes the standard classroom PostgreSQL role `ds60_admin`,
learning UID/GID `1000:1000` and PostgreSQL 17. A logical database dump does not
include cluster-wide role definitions. If you deliberately introduced custom
roles, ownership or external tablespaces, review those dependencies separately
before restoring; do not conceal ownership failures with a blanket role change.
Record the source course release and retain matching source files as well.

### Restore into a new project

Transfer the complete backup directory to the destination computer. Prepare
Docker and the matching course source and local starter images **before** this
procedure. Images must support the destination CPU architecture. Begin with the
same course release as the backup; upgrade the restored installation separately
after verifying it. The example tag below is this source release. Change it if
your backup was made with another release. Do not reuse a previous classroom's
project name.

The procedure below restores only into a new project. It refuses existing
launcher settings, project containers, networks and volumes, and checks the
three standard volume names even if their Compose labels are absent. It also
refuses a nonempty learning volume, bad checksums, traversal paths, archive
links and special files. Standard classroom files are restored as the classroom
user, with private permissions and any owner executable bit preserved. A
backup containing intentional links requires separate review rather than
silently following them.

Edit `backup_dir` to the actual absolute backup path and set `restore_tag`
to the installed image version matching the backup. The example uses the full
1.1.0 release. The generated `restore_project` must be unused. Run the **entire** block from the course
folder in Bash; do not skip the destination checks and run only `pg_restore`.
It uses existing local images and strict `resume`, so missing image preparation
causes a failure instead of an unexpected build or download.

```bash
(
  set -eu
  backup_dir="$HOME/Documents/REPLACE_WITH_YOUR_BACKUP_FOLDER"
  restore_project="ds60-restored-$(date +%Y%m%d-%H%M%S)"
  restore_tag=1.1.0
  [[ "$restore_project" =~ ^[a-z0-9][a-z0-9_-]*$ ]]
  docker info --format '{{.OSType}}'
  [ -d "$backup_dir" ]
  if [ -e ".classroom/$restore_project" ]; then
    echo "Refusing existing destination settings: $restore_project" >&2
    exit 1
  fi
  existing_containers=$(docker ps -aq --filter "label=com.docker.compose.project=$restore_project")
  existing_networks=$(docker network ls -q --filter "label=com.docker.compose.project=$restore_project")
  existing_volumes=$(docker volume ls -q --filter "label=com.docker.compose.project=$restore_project")
  if [ -n "$existing_containers$existing_networks$existing_volumes" ]; then
    echo "Refusing existing destination Docker resources: $restore_project" >&2
    exit 1
  fi
  for suffix in classroom-learning postgres-data classroom-runtime; do
    if docker volume inspect "${restore_project}_${suffix}" >/dev/null 2>&1; then
      echo "Refusing an existing destination volume: ${restore_project}_${suffix}" >&2
      exit 1
    fi
  done
  app_image=$(docker image inspect "ds60sqlpy-lab:$restore_tag" --format '{{.Id}}')
  restore_volume="${restore_project}_classroom-learning"
  docker volume create --label "com.docker.compose.project=$restore_project" --label com.docker.compose.volume=classroom-learning "$restore_volume"
  docker run --rm -i --pull never --network none --read-only --user 0:0 --cap-drop ALL --cap-add CHOWN --cap-add DAC_OVERRIDE --cap-add FOWNER --security-opt no-new-privileges --mount "type=bind,source=$backup_dir,target=/backup,readonly" --mount "type=volume,source=$restore_volume,target=/restore,volume-nocopy" --entrypoint python "$app_image" - <<'PY'
import os
import tarfile
from hashlib import file_digest
from pathlib import Path, PurePosixPath

backup = Path('/backup')
destination = Path('/restore')
if any(destination.iterdir()):
    raise SystemExit('Refusing a nonempty destination learning volume')
expected = {}
for line in (backup / 'SHA256SUMS').read_text().splitlines():
    digest, name = line.split('  ', 1)
    if name in expected:
        raise SystemExit('Duplicate backup checksum entry')
    expected[name] = digest
if set(expected) != {'classroom-learning.tar.gz', 'classroom-database.dump'}:
    raise SystemExit('Unexpected backup checksum inventory')
for name, digest in expected.items():
    with (backup / name).open('rb') as stream:
        if file_digest(stream, 'sha256').hexdigest() != digest:
            raise SystemExit('Backup checksum mismatch: ' + name)
with tarfile.open(backup / 'classroom-learning.tar.gz', 'r:gz') as archive:
    members = archive.getmembers()
    names = set()
    for member in members:
        path = PurePosixPath(member.name)
        if path.is_absolute() or '..' in path.parts or '\\' in member.name:
            raise SystemExit('Unsafe archive member path')
        if not (member.isfile() or member.isdir()):
            raise SystemExit('Archive links and special files require separate review')
        normalized = str(path)
        if normalized in names:
            raise SystemExit('Duplicate archive member path')
        names.add(normalized)
    archive.extractall(destination, members=members, filter='data')
for path in (destination, *destination.rglob('*')):
    os.chown(path, 1000, 1000, follow_symlinks=False)
    path.chmod(0o700 if path.is_dir() else 0o600 | (path.stat().st_mode & 0o100))
print('Checksums verified; learner files restored to the empty destination')
PY
  ./classroom resume --starter --project "$restore_project" --tag "$restore_tag" --local-build --no-browser
  restore_compose=(docker compose --project-name "$restore_project" -f compose.classroom.yaml)
  "${restore_compose[@]}" stop lab
  "${restore_compose[@]}" cp "$backup_dir/classroom-database.dump" postgres:/tmp/classroom-database.dump
  "${restore_compose[@]}" exec -T postgres pg_restore -U ds60_admin -d advanced_sql_training --clean --if-exists --exit-on-error /tmp/classroom-database.dump
  ./classroom resume --project "$restore_project" --no-browser
  printf 'Restored into new project: %s\n' "$restore_project"
)
```

The `--clean --if-exists` flags replace database objects **inside that newly
created destination database** with the dump's definitions and data. The
original classroom and backup files are not modified. The normal initializer
creates a new private worker credential for the destination; no source token is
copied. Only the starter worker is enabled initially. Every saved subject and
variant remains in the learning archive; add other runtime profiles when needed.

If restoration fails after creating the destination, keep that destination for
inspection and retain the original backup. The same block will refuse to reuse
it. Diagnose the error, then choose another unused project for a clean retry;
do not remove a preflight guard to overwrite a partially restored classroom.
There is no automatic merge of two learners' histories or databases.

### Verify before retiring the source

Run `./classroom status --project YOUR_RESTORED_PROJECT`, open its printed URL
and check all of the following:

1. Open several familiar lessons and variants. Compare their exact source,
   predictions and notes with your backup, and save a small new note to confirm
   that the restored storage is writable.
2. Open an original saved run and inspect its recorded source and output without
   rerunning it. A preserved receipt remains evidence about its original runtime,
   not a new execution on this computer.
3. Query a known table or row from the original PostgreSQL database. An empty
   training schema can be correct if that was the backed-up state; do not reset
   the database to make a restore appear successful.
4. Stop and resume the restored project. Recheck the same saved work and SQL
   state. For a deliberate recovery drill, containers may be replaced while
   retaining these new named volumes, then checked again.
5. Keep the original backup and source project until those checks pass. Compile
   and run new attempts using the destination's prepared workers; old compiled
   artifacts or framework caches are not proof of portability to a new CPU/GPU.

On the restored project, continue using its explicit `--project` name for
start, stop, status and future backups. Restoring data does not make the default
`ds60-classroom` project point to it. For a small amount of work, manually copying
selected source and notes into a fresh browser pad is also possible, but that
does not transfer full history or database state.

## Diagnostics and direct Compose

Prefer `./classroom status`, `./classroom logs` and `./classroom doctor` for
normal diagnosis. When using Compose directly, carry the exact project name,
file and selected profiles. Compose does not automatically read the launcher's
remembered selection or port choices.

```bash
docker compose --project-name ds60-classroom -f compose.classroom.yaml logs --tail 100 lab postgres classroom-init
```

Use [troubleshooting](troubleshooting.md) for port conflicts, disk pressure,
corrupted engine snapshots and missing runtimes. Optional
[GPU/CUDA setup](cuda-classroom.md) and [Kubernetes setup](modules-runtime.md#prepare-and-run-the-owned-kubernetes-lab)
have additional capability requirements. Ordinary classroom execution does not
mount the engine socket into learner workers.
