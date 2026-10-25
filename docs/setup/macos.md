# Start the classroom on macOS

The supported classroom runs Linux containers and opens in your browser.
macOS supplies Terminal and Bash. Course Python packages, PostgreSQL, compilers
and framework tools are prepared inside Docker images.

## 1. Prepare the engine

Choose a local Linux-container engine:

- Install [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/)
  using the download matching Apple silicon or Intel.
- Or install [Rancher Desktop](https://docs.rancherdesktop.io/getting-started/installation/)
  and select [dockerd/Moby](https://docs.rancherdesktop.io/ui/preferences/container-engine/general/)
  for Docker API compatibility.

Start the application and wait for the engine to become ready. Follow its
current OS requirements and resource settings. Keep your existing engine
selection when resuming work because another engine has a different image and
volume store.

Open **Terminal** and check:

```sh
docker info --format '{{.OSType}}'
docker compose version
bash --version
```

Expect `linux` and Compose **2.28.0 or newer**. An installed Docker command
without a reachable engine is not ready for the classroom.

## 2. Open the course directory

Clone the repository if you have access, or extract the complete starter ZIP.
Repository access is currently private; use an authenticated Git credential
manager or the owner's supplied archive. Never put a token in a clone URL.

```sh
git clone https://github.com/sadatnfs/ds60sqlpy.git
cd ds60sqlpy
```

For a ZIP, use `cd` with its actual extracted directory instead. Check that
`ls classroom README.md` lists both files. Quote a path containing spaces.

## 3. Prepare and open the classroom

```sh
./classroom doctor
./classroom --starter
```

The starter prepares Python and PostgreSQL while keeping every subject
readable. Use `./classroom --all` for all sixteen ordinary workers. A first
build requires internet and disk space for images and intermediate build
layers; the [one-command guide](../one-command-classroom.md) explains resources
and choosing a smaller selection.

The launcher prints the actual loopback URL and tries to open it. Paste that
URL into your browser if necessary. You can also double-click
**START_DOCKER_CLASSROOM.command** after engine setup. It uses the same saved
selection as the terminal launcher.

If extraction removed executable permissions, use `bash classroom doctor` and
`bash classroom --starter`. A macOS security dialog about a downloaded file is
a host decision; the terminal route remains available after inspecting the
downloaded source.

## 4. Pause, return and update

```sh
./classroom stop
./classroom resume
```

Stopping preserves named volumes. Strict `resume` uses prepared images without
downloads or builds. Normal `./classroom` also resumes, preparing only missing
images when needed. After obtaining changed source files, deliberately update
local images with:

```sh
./classroom --local-build --rebuild
```

Keep a custom `--project NAME` consistent across commands. Use
`./classroom status` to find the current URL, especially with automatic ports.
Copying the source folder alone does not transfer Docker-volume progress.

## Apple silicon and optional GPU work

Ordinary workers use their supported Linux architecture. Local images built
on Apple silicon are normally ARM64; a Hub release must provide matching
architecture tags. See [image distribution](../dockerhub.md).

CUDA requires supported NVIDIA hardware and software. An Apple GPU does not
become a CUDA device inside Docker. The CUDA subject offers reading and CPU
models on this Mac, with explicitly separate NVIDIA or non-CUDA project
routes. See [CUDA setup](../cuda-classroom.md).

Portable Swift/Foundation lessons run in the Linux worker. Apple app projects
deliberately use the Swift course's separate macOS/Xcode instructions. They
do not change the prerequisites for ordinary classroom study.

Continue with [your first successful session](first-success.md), then
[the classroom guide](../classroom-experience.md).
