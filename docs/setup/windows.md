# Start the classroom on Windows with WSL 2

The classroom runs in Linux containers and opens in your usual Windows browser.
Prepare Ubuntu in WSL 2 and a Docker-compatible engine once. The course supplies
Python, PostgreSQL, compilers and framework libraries inside its images.

## 1. Install and open Ubuntu

Follow Microsoft's [WSL installation guide](https://learn.microsoft.com/en-us/windows/wsl/install).
The usual first command, run in an administrator Windows Terminal, is:

```powershell
wsl --install -d Ubuntu
```

Restart Windows if requested, then open **Ubuntu** from Start and finish its
Linux username and password setup. This is a Linux account for the terminal;
it is separate from your Windows account and the course database.

In Windows Terminal, inspect the installed distributions:

```powershell
wsl --list --verbose
```

Your Ubuntu distribution should show version `2`. If its name differs from
`Ubuntu`, use the actual name shown in that list. Microsoft's
[WSL command reference](https://learn.microsoft.com/en-us/windows/wsl/basic-commands)
explains version conversion and selecting a default distribution. The course
does not install, unregister or reset a distribution.

## 2. Start one Linux-container engine

Choose one engine and follow its current installation requirements:

- **Docker Desktop:** enable the WSL 2 backend and integration for your Ubuntu
  distribution using [Docker's WSL instructions](https://docs.docker.com/desktop/features/wsl/).
- **Rancher Desktop:** use [dockerd/Moby](https://docs.rancherdesktop.io/ui/preferences/container-engine/general/)
  for the Docker API and enable your distribution's integration. Its
  [installation guide](https://docs.rancherdesktop.io/getting-started/installation/)
  and [WSL troubleshooting](https://docs.rancherdesktop.io/troubleshooting-tips/)
  describe engine and socket access.

Having the engine's internal WSL distribution is different from having your
own Ubuntu shell ready. Open **Ubuntu** and run:

```sh
docker info --format '{{.OSType}}'
docker compose version
bash --version
```

The first command should print `linux`. Compose must be **2.28.0 or newer**.
If Docker is unavailable in Ubuntu, check the running engine and its
distribution integration. Do not install a second daemon as an automatic fix.
Keep the same engine when returning to existing course volumes.

## 3. Get the course folder

Use a starter ZIP, a repository ZIP or a Git clone. A public repository can be
downloaded without signing in; a restricted fork requires an account with
access or an owner-provided archive. A ZIP does not require Git on your machine. Extract the complete folder before launching; do not run
files from the archive preview.

A Windows folder such as `C:\Users\Ada\Downloads\DS60LearningLab` appears in
Ubuntu as `/mnt/c/Users/Ada/Downloads/DS60LearningLab`. Open that folder with:

```sh
cd "/mnt/c/Users/Ada/Downloads/DS60LearningLab"
ls classroom README.md
```

Replace the example path with your actual extracted folder. A checkout inside
Ubuntu's Linux filesystem is also supported. The correct directory contains
`classroom`, `README.md` and `compose.classroom.yaml`.

## 4. Start a first session

From Ubuntu, in that course directory:

```sh
./classroom doctor
./classroom --starter
```

The smaller starter prepares Python, PostgreSQL and the full reading library.
The first preparation needs internet and shows build logs. To prepare all
ordinary language/framework workers instead, use `./classroom --all`.
Optional NVIDIA workers and owned Kubernetes clusters have separate setup.

When ready, use the exact browser URL printed by the launcher. Copy it into
your Windows browser if automatic opening is unavailable. Continue with
[your first successful session](first-success.md).

If ZIP extraction removed executable permissions, use `bash classroom` in
place of `./classroom`. No separate host Python or compiler installation is
needed for these commands.

## Use the Windows launcher

After WSL and the engine are ready, you can double-click
**START_DOCKER_CLASSROOM.cmd**, or use `classroom.cmd` from Command Prompt.
Both delegate to the same Bash launcher through the default WSL distribution.
Make your normal Ubuntu distribution the default if required:

```powershell
wsl --set-default Ubuntu
```

Use the actual distribution name from `wsl --list --verbose`. The wrapper
retains the selected course directory. A new default project selects all
the ordinary workers; running `./classroom --starter` once in Ubuntu saves
the smaller selection for subsequent launches.

## Return without rebuilding

Start the same engine, open the same course folder in Ubuntu and run:

```sh
./classroom resume
```

This uses already prepared images and never builds or pulls. Use
`./classroom stop` to pause while retaining saved work. Repeat a custom
`--project NAME` on later commands if you chose one. Follow the
[one-command guide](../one-command-classroom.md) for profiles, updates, ports
and backups.

If the browser cannot connect, inspect `./classroom status` and use its current
URL. If progress appears missing, check the engine and project name before
creating anything new. A container, an image and a named volume are different
objects; deleting a volume deletes its saved data.
