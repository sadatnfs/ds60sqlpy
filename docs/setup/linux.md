# Start the classroom on Linux

Install a local Docker engine, its Compose plugin and Bash. The course's
language runtimes and database run in Linux containers, so ordinary study
requires no host Python, Java, C++ compiler or PostgreSQL server.

## 1. Install the engine for your distribution

Use Docker's [Linux installation index](https://docs.docker.com/engine/install/)
and the instructions for your distribution, such as
[Ubuntu](https://docs.docker.com/engine/install/ubuntu/).
Install the Compose plugin as part of that setup. Follow the distribution's
documented service startup and update procedure.

A desktop alternative is [Rancher Desktop](https://docs.rancherdesktop.io/getting-started/installation/)
with [dockerd/Moby](https://docs.rancherdesktop.io/ui/preferences/container-engine/general/).
The launcher needs Docker API/CLI compatibility; a containerd-only setup using
`nerdctl` is a different interface.

Verify engine access from the account that will run the course:

```sh
docker info --format '{{.OSType}}'
docker compose version
bash --version
```

Expect `linux` and Compose **2.28.0 or newer**. If engine access is denied,
follow Docker's [post-installation guidance](https://docs.docker.com/engine/install/linux-postinstall/).
Membership in the Docker group grants substantial host authority, so choose the
appropriate user-access setup deliberately. Do not make the socket writable
by everyone or run the classroom as root merely to hide a permission problem.

## 2. Get the course

Use an authorized Git clone or an extracted starter ZIP. The repository is
currently private and requires access from its owner.

```sh
git clone https://github.com/sadatnfs/ds60sqlpy.git
cd ds60sqlpy
```

For a ZIP, enter its extracted directory instead. Confirm that the directory
contains `classroom`, `README.md` and `compose.classroom.yaml`.

## 3. Prepare a first session

```sh
./classroom doctor
./classroom --starter
```

This smaller selection prepares Python and PostgreSQL and serves the complete
library. Choose `./classroom --all` when you want every ordinary worker, or
select only the languages you need:

```sh
./classroom --profile cpp20 --profile java21
```

An explicit selection replaces the remembered selection with Core plus those
profiles. It does not stop workers already running. To reduce the running set,
stop this classroom first, then start with the smaller selection.

Build logs show downloaded dependencies and reused cached layers. The initial
build needs internet. Once readiness succeeds, open the printed browser URL.
If your desktop has no browser-opening command, copy the URL yourself or use
`--no-browser`.

## 4. Keep the same workspace

```sh
./classroom status
./classroom stop
./classroom resume
```

Strict resume never builds or pulls. Normal `./classroom` can prepare missing
images while reusing existing ones. A source update requires a deliberate
`./classroom --local-build --rebuild` for a local-build project.
Always repeat your custom `--project NAME` if you used one.

Saved pads, notes and results live in a named learning volume. PostgreSQL has
a separate data volume. The checkout's `.classroom/` folder remembers launcher
settings, not the learning data. Keep the same engine and project name, and
follow [backup and transfer](../one-command-classroom.md#backup-and-transfer)
before moving to another machine.

## Optional capabilities

NVIDIA GPU access, owned Kubernetes clusters, pretrained model assets and
multi-file projects have separate preparation instructions. The ordinary
CPU workers and reading paths remain available without those capabilities.
See [runtime profiles](../docker-profiles.md) and
[CUDA setup](../cuda-classroom.md).

Continue with [your first successful session](first-success.md).
