# Docker learning lab, from a new computer to your first lesson

This guide starts before the terminal commands. You will install a local
container engine, download the course, start its Python and PostgreSQL
backends, and use the lessons in your browser. You can follow this route
without installing a native PostgreSQL server, Jupyter, or the course's Python
packages on your computer.

The included PowerShell and Bash launchers open the browser and need no host
Python installation. The first build downloads images and packages; ordinary
later starts reuse them. Codex is an optional tutor.

## 1. Know the few names you will see

| Name | Meaning in this course |
| --- | --- |
| Host | Your Windows, Mac, or Linux computer. Its ordinary folders can hold your saved work. |
| Container engine | The local service that runs the course's Linux containers. Start it before starting the course. |
| Image | The installed recipe containing the course runtime and packages. Building an image does not publish it. |
| Container | A running instance of an image. You can replace it while retaining separately stored learning data. |
| Compose | The `docker compose` command that starts the app and PostgreSQL together from `compose.yaml`. |
| Bind mount | A real folder on your host exposed inside a container. The course uses it for saved learning work. |
| Database volume | Docker-managed storage for PostgreSQL. It is separate from the host folder holding your progress. |
| Port | A numbered local connection endpoint. The browser and database use different ports. |

Commands in a code block are what you type. Do not type the surrounding
backticks, the word `powershell` or `bash`, or a terminal prompt such as `$`.
Press Enter after a command and wait for it to finish. An error is a reason
to inspect that step before continuing, not a reason to delete saved data.

## 2. Install one local container engine

Choose the instructions for your operating system. You need a working
**Docker CLI**, **Docker API**, and **Compose v2**. Docker Desktop bundles these
components. Docker Engine users install the Compose plugin separately.
[Docker's Compose installation guide](https://docs.docker.com/compose/install/)
explains that distinction.

Rancher Desktop with **dockerd (moby)** is also suitable. Its Moby engine
exposes the Docker API; its containerd choice uses a different command-line
workflow. The repository's actual macOS container verification used Rancher
Desktop with Moby. Other operating-system installation steps below follow
vendor documentation and include checks you can perform locally.
[Rancher's engine documentation](https://docs.rancherdesktop.io/ui/preferences/container-engine/general/)
explains the engine choices.

### Windows: start with the first-run wizard

For a new Windows computer, begin with the course ZIP and its launcher. You do
not need to install Python or Git, open Ubuntu, or type Docker commands first.
The guided fresh installation targets supported **Windows 11 x64** machines.
An existing compatible local engine can be reused without reinstalling it.
Use an internet connection for initial downloads; other architectures or
managed installation policies use the manual vendor/IT route below.

1. Download the supplied **`DS60LearningLab-0.3.0-Windows-Starter.zip`**.
   Alternatively, use **Code**, then **Download ZIP** on a
   [repository version](https://github.com/sadatnfs/ds60sqlpy) that includes
   `START_DOCKER_LAB.cmd` and `scripts/start_docker_windows.ps1`. Sign in if
   repository access requires it.
2. In File Explorer, right-click the ZIP and choose **Extract All**. Extract
   the complete course into a normal user-owned folder. Open the extracted
   folder containing `README.md`, `compose.yaml`, and `scripts`.
3. Double-click **`START_DOCKER_LAB.cmd`**. Do this from the extracted folder,
   not from the compressed ZIP preview. Keep the setup window open so you can
   read its progress and any instruction.
4. The first-run wizard inspects the local runtime. If a compatible engine is
   already ready, it uses it and starts the lab. If setup is missing, it offers
   the supported installation path and asks before installing software. For
   the recommended fresh setup, type `R` for Rancher Desktop, then type `Y`
   only when you approve the described installation. `D` selects Docker
   Desktop; pressing Enter at the choice cancels without installing.
5. If Windows requests administrator approval, approve only the installation
   or WSL action you chose. If a restart is required, save other work, restart
   Windows yourself, and double-click the **same** `START_DOCKER_LAB.cmd`
   again. It rechecks what is installed and continues from the current machine
   state. The wizard does not force a restart.
6. Once the engine and app are ready, the browser opens at the printed local
   address, normally `http://127.0.0.1:8765/learn`. Continue with
   [your first Python and SQL results](#5-get-one-python-result-and-one-sql-result).

This is one entry point for setup and later starts. Windows can still require
installation consent, its administrator prompt, or a reboot before containers
can run. WSL installation runs in an elevated child process when needed;
the desktop engine and browser start in your original user session. Missing
hardware virtualization or organization-managed installation
restrictions need the machine owner's normal setup process; the course cannot
change firmware or bypass a policy.

The recommended fresh Windows engine is **Rancher Desktop** with
**dockerd (moby)** and Kubernetes disabled. Fresh configuration is applied only
after you choose that installation. After a requested reboot, a newly
installed, unused Rancher application may ask separately to initialize those
settings; approve that step only when it matches your choice. An already
initialized or uncertain existing profile is left unchanged and may need its
normal first-run UI completed manually. Docker Desktop with its WSL 2 backend
is another choice; its guided Windows 11 installation requires version 23H2
(build 22631) or newer and a release still supported by Microsoft, plus the
[current Docker hardware requirements](https://docs.docker.com/desktop/setup/install/windows-install/).
An existing engine, its workloads, and its saved
learning data are preserved; installing another engine is not a required step
when a compatible local engine already works.

WSL means Windows Subsystem for Linux. Its version 2 provides the Linux backend
for the desktop engine. The wizard's WSL installation uses `--no-distribution`,
so this Windows-folder route does not require an Ubuntu account or Linux
terminal. If you already prefer a Linux-local checkout, the
[optional WSL terminal workflow](#9-recommended-windows-wsl-2-terminal-workflow)
remains available after setup.

If WinGet, Microsoft's application installer command, is unavailable or blocked,
use the official installer guidance shown by the wizard, then rerun the same
course launcher. Use your organization's approved engine on managed machines.
The launcher does not delete database volumes, reset WSL distributions, or
replace an existing `.learning` folder to repair setup.

For read-only troubleshooting, the wizard also has a diagnostic mode:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_docker_windows.ps1 -DiagnosticsOnly
```

It reports readiness without installing software or starting the course. Keep
the output if you need help with the first failing prerequisite. It does not
require you to reveal a database password.

#### Manual Windows setup alternative

For manual installation or an IT-managed machine, use the current
[Docker Desktop Windows requirements](https://docs.docker.com/desktop/setup/install/windows-install/)
or [Rancher Desktop installation instructions](https://docs.rancherdesktop.io/getting-started/installation/).
WSL setup and its possible reboot are documented by
[Microsoft](https://learn.microsoft.com/en-us/windows/wsl/install).
A manual WSL installation can be started from PowerShell opened with
**Run as administrator**:

```powershell
wsl --install --no-distribution
```

Restart when requested. Use an ordinary PowerShell window to inspect/update
WSL, or follow the installer if it requests elevation for an update:

```powershell
wsl --update
wsl --version
```

Start the selected desktop engine and wait for it to become ready. Rancher
Desktop users choose Moby; Docker Desktop users use Linux containers with its
[WSL 2 engine](https://docs.docker.com/desktop/features/wsl/). Then rerun
`START_DOCKER_LAB.cmd`. Keep a native Windows checkout in a Windows folder;
choose a separate Linux-home checkout only when following the optional WSL
terminal instructions. [WinGet documentation](https://learn.microsoft.com/en-gb/windows/package-manager/winget/)
explains the application-installation tool used when it is available.

### macOS: install and start the desktop engine

1. Open the Apple menu and **About This Mac**. Note whether it says an Apple
   chip such as M1/M2/M3 or an Intel processor.
2. Download the matching Mac installer from
   [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/)
   or [Rancher Desktop](https://docs.rancherdesktop.io/getting-started/installation/).
   Check the vendor's current supported macOS versions.
3. For a Docker `.dmg`, open it, drag Docker to Applications, then open Docker
   from Applications and finish the displayed setup. For Rancher Desktop,
   follow its installer and choose **dockerd (moby)**.
4. Leave the application running and wait for its engine to become ready.
5. Open **Terminal** from Applications, then Utilities. A new Terminal window
   picks up command-line tools installed by the desktop application.

Choose the native installer for your Mac architecture. The container engine
handles Linux containers; you do not install a separate Linux desktop to use
this browser lab.

### Linux: install Engine and the Compose plugin

Open Terminal from your desktop's application menu. Follow the
[Docker Engine installer for your distribution](https://docs.docker.com/engine/install/).
Choose the instructions matching your actual distribution, which you can
inspect with:

```bash
cat /etc/os-release
```

For Ubuntu, the [official Ubuntu procedure](https://docs.docker.com/engine/install/ubuntu/)
first configures Docker's package repository, then installs the Engine, CLI,
Buildx, and **docker-compose-plugin** packages. Follow both parts; an install
command copied without the repository setup can select a different package or
fail. Other distributions have their own package names and repository steps.

Complete Docker's [post-installation access setup](https://docs.docker.com/engine/install/linux-postinstall/)
so your normal user can run `docker info`. If your administrator chooses the
Docker group route, group membership takes effect after logging out and back
in. Docker group membership gives administrative control of the local engine.
The course launcher runs as your ordinary user and expects its Docker access
to be configured; it does not elevate itself with `sudo`.

A distribution-supported Docker Desktop or Rancher Desktop installation is an
alternative. Start the chosen engine and use its Docker-compatible Moby
configuration. Keep the same local engine/context for the course's later
starts so you see the same images and database volumes.

### Verify the installation before downloading course packages

Run these in PowerShell on Windows, or Terminal on macOS/Linux:

```text
docker --version
docker compose version
docker info
```

The first two print version information. `docker info` must also show server
information without a connection or permission error. A working CLI version
alone does not prove an engine is running. If more than one engine or remote
context is configured, inspect:

```text
docker context show
docker context ls
```

Use your intended **local** desktop/Engine context. This course mounts local
folders; a remote Docker daemon does not see files on your computer in the
same way. Docker explains host-path behavior in its
[bind-mount documentation](https://docs.docker.com/engine/storage/bind-mounts/).

## 3. Download and open the course folder

You do not need Git for a first visit:

1. Open the [repository page](https://github.com/sadatnfs/ds60sqlpy) in your browser.
2. Select **Code**, then **Download ZIP**. If access requires signing in, use
   the account that has repository access.
3. Extract the ZIP completely. On Windows use **Extract All**; on a Mac open
   the ZIP; on Linux use the archive manager's Extract action.
4. Move the extracted folder to a normal user-owned local location, such as
   Documents. You may rename it `ds60sqlpy` to match the examples below.
5. Open that folder. You should see `README.md`, `compose.yaml`, `Dockerfile`,
   and `scripts`. Do not run from a compressed-folder preview.

If you already use Git, the equivalent is:

```text
git clone https://github.com/sadatnfs/ds60sqlpy.git
```

The **repository root** means the folder containing those files. Your terminal
must point there before running course commands.

Windows PowerShell example, for a checkout stored in the Windows filesystem:

```powershell
Set-Location "C:\Users\Ada\Documents\ds60sqlpy"
Test-Path .\compose.yaml
```

Replace the example folder with your actual extracted path, keeping quotes
around a path containing spaces. The second command should print `True`.
You can copy the folder path from File Explorer's address bar.

macOS/Linux example, when you chose the Documents location above:

```bash
cd "$HOME/Documents/ds60sqlpy"
pwd
ls compose.yaml
```

`pwd` prints the current folder and `ls` should find `compose.yaml`. If your
folder is elsewhere, change the quoted path. These commands do not create or
change a database.

## 4. Start the lab and open the browser

The repository includes a PowerShell launcher for Windows and a Bash launcher
for macOS, Linux, and WSL. They use the installed Docker CLI and open the host
browser after the app is ready. You do not need to create a native `.venv` or
install Python to use these launchers.

With the engine running and the repository extracted:

- **Windows PowerShell workflow:** double-click `START_DOCKER_LAB.cmd` in
  File Explorer. For a Linux-local WSL checkout use the Bash command below.
- **macOS:** double-click `START_DOCKER_LAB.command`. If you prefer Terminal,
  use the command below.
- **Linux:** use the terminal command below from the repository root.

The double-click Windows launcher includes first-run setup. The following
PowerShell command is the **runtime-only** alternative for an engine that is
already configured and running:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\docker_lab.ps1 start
```

macOS/Linux alternative:

```bash
bash scripts/docker_lab.sh start
```

The PowerShell execution-policy option applies only to this script process;
it does not change your machine's permanent policy. If Finder does not launch
a downloaded `.command` file, the Bash command above works from Terminal
without making the script executable. An optional Python interface also exists
at `scripts/docker_lab.py` for people who already use supported host Python.

On a first start, expect an announced connected build, package/image download
output, database startup, and an HTTP-readiness check. Wait for the printed
ready address. The launcher opens the browser **on your computer** after the
app responds. The normal address is
[http://127.0.0.1:8765/learn](http://127.0.0.1:8765/learn).
If the browser does not open, copy that exact printed URL into its address bar.
Use `127.0.0.1`, rather than substituting a different host label, because the
app validates its local Host header.

No website account is needed. The Docker database's course login is
`admin` with password `admin`; the app supplies it internally. This is a
limited local database role. The separate bootstrap administrator is not the
pad's login. The browser does not ask you to type a database password.

The first build needs internet access and can take several minutes. Subsequent
starts reuse the selected local image. The launcher does not upload an image
or your learning work.

### Direct Compose alternative, without host Python

The wrappers normally prepare the host directory and user identity for you.
For a manual Compose start, do that explicitly in the same terminal first.
These directory commands preserve an existing `.learning` folder.

```powershell
# Windows PowerShell, repository root
New-Item -ItemType Directory -Force .\.learning | Out-Null
$env:DS60_LEARNING_DIR = (Resolve-Path .\.learning).Path
$env:DS60_UID = "1000"
$env:DS60_GID = "1000"
docker compose --project-name ds60-learning --profile lab up --build --detach
```

```bash
# macOS/Linux/WSL, repository root
mkdir -p .learning
export DS60_LEARNING_DIR="$(pwd -P)/.learning"
export DS60_UID="$(id -u)"
export DS60_GID="$(id -g)"
docker compose --project-name ds60-learning --profile lab up --build --detach
```

On macOS/Linux this runs the app with your own user/group identifiers, so the
host files stay writable to you. Repeat the environment assignments in a new
terminal. The long-syntax bind mount deliberately refuses a missing host path;
it does not silently create one owned by the wrong user. These manual identity
examples assume an ordinary local engine. For a rootless engine, use the
included launcher: it detects that mode and supplies the mapped identity
instead of asking you to guess ownership settings.

Then open the exact browser URL manually. On later starts with images already
present:

```text
docker compose --project-name ds60-learning --profile lab up --detach --no-build --pull never
```

The direct command does not open a host browser automatically. Use the included
PowerShell/Bash launcher for readiness checking and automatic opening.

## 5. Get one Python result and one SQL result

In the browser's left sidebar, enter `python-01` under **Or open a stable lesson
ID**, then choose **Open lesson**. The guide appears beside the coding pad.

1. Keep **Workspace** set to **Python**.
2. In **Your code**, enter:

   ```python
   print(2 + 3)
   ```

3. Choose **Run code**. The output should contain `5` and a successful exit.
4. Choose **Save pad**. In **Work the idea through**, write a short prediction
   or observation and choose **Save evidence**.

Now open `sql-start-01` in the same sidebar. Choose **PostgreSQL** under
**Workspace**, then choose **SQL snippet** under **Mode**. Enter:

```sql
SELECT current_database() AS database_name, 2 + 3 AS first_result;
```

Choose **Run code**. Expect one row containing `advanced_sql_training` and `5`.
This first query needs no seed or reset. Choose **Save pad**.

For the full beginner lesson, switch **Mode** to **Whole SQL lesson (psql)**,
choose **Load lesson starter**, and run its complete temporary-table fixture
in one submission. Keep the fixed script directives intact. It ends in `ROLLBACK`.
Later historical lessons that need seeded tables use **Prepare the disposable
SQL training data**, then **Reset and verify training schema**. Read the
notice and type `RESET TRAINING` only when you want to replace the course-owned
training schema. That reset preserves saved pads and progress; it does replace
SQL training data. Use only the disposable course database.

Choose a learning goal and **Build my route** when you are ready for the
ordered lessons. Completion is your confirmed evidence, not an automatic
award for opening the page or running these two checks.

Python notebook starters retain `# %%` cell boundaries. One Run executes their
cells in order with shared names, while the next Run starts a fresh process.
Keep dependent cells together. `%timeit` and `%%sql` use the notebook-aware
backend; the Docker Core image includes IPython. **Run limit** offers 15, 60,
or 120 seconds. For heavier packages, build the
[optional Docker profiles](docker-profiles.md) before studying offline.

## 6. Find the host files that preserve your work

The launcher's default learning folder is **`.learning` inside your course
folder**. It is bind-mounted as `/workspace/.learning` inside the app container.
The container path and host path name the same saved files. A bind mount
persists because the files live in your own folder, independently of a
particular container.

| Host path under `.learning/` | Saved work |
| --- | --- |
| `progress.json` | Recorded lesson completion |
| `coaching.json` | Your predictions, attempts, comparisons, and explanations |
| `pads/` | Saved Python/SQL pads and earlier saved versions |
| `home/` | Container user settings and caches kept outside the replaceable image |
| `cache/matplotlib/` | Reusable platform-specific plotting/font metadata |
| Other files you deliberately save there | Your own exported practice artifacts |

On macOS/Linux, a name beginning with a dot is usually hidden in the file
manager. In Terminal, `ls -a` shows it. On Windows you can paste the complete
`.learning` folder path into File Explorer's address bar. Keep the course
folder or your chosen data folder when replacing containers.

The database uses a separate Compose volume named from the project, normally
`ds60-learning_postgres-data`. Its tables are not stored in progress.json.
Backing up `.learning` protects learning work; a PostgreSQL dump protects
personal database tables. Neither backup replaces the other.

Only saved work under the bind-mounted `.learning` tree has this host-folder
persistence contract. Code can write other files inside its container, so put
practice exports you want to keep under `.learning/`. Printed output and
rendered figures are observations; save the code/evidence needed to reproduce
them. Some files appear only after the corresponding save or completion
operation. After working through a lesson's exercises, save prediction,
attempt, and explanation evidence before checking the confirmation and choosing
**Record demonstrated lesson**. The two environment checks above do not by
themselves establish lesson mastery.

### Keep the same learning folder across a future checkout

You can choose an absolute folder outside the checkout. For example:

```powershell
# Windows PowerShell; choose a real, user-owned path
powershell -ExecutionPolicy Bypass -File .\scripts\docker_lab.ps1 start -DataDir "C:\Users\Ada\Documents\DS60 learning data"
```

```bash
# macOS/Linux
bash scripts/docker_lab.sh start --data-dir "$HOME/Documents/DS60 learning data"
```

Use that same folder on future starts, including from a new checkout:
`--data-dir` in Bash/Python or `-DataDir` in PowerShell. The image supplies
course code. Keep the same project (`--project` or `-Project`) when you also
want the same database volume. A new project name creates a different database-volume namespace.

## 7. Stop, resume, and rebuild without losing progress

From the same repository folder and using the same data/project choices:

```powershell
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File .\scripts\docker_lab.ps1 stop
powershell -ExecutionPolicy Bypass -File .\scripts\docker_lab.ps1 start
```

```bash
# macOS/Linux
bash scripts/docker_lab.sh stop
bash scripts/docker_lab.sh start
```

Closing a browser tab does not stop the containers. The launcher's stop command
stops services and preserves your host learning folder and database volume.
`start` reuses them. A readiness failure is not a reason to erase either store.

For a deliberate connected image rebuild after updating the course source:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\docker_lab.ps1 start -Build
```

```bash
bash scripts/docker_lab.sh start --build
```

Rebuilding the image changes the installed runtime/course payload. It does not
replace the host `.learning` folder. Recreating or removing only containers
also keeps that folder. Keep the same data path and project when restarting.
Avoid volume-deletion and system-prune commands as routine troubleshooting:
those operate on database storage or other projects, unlike an ordinary stop.

To inspect without changing course state:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\docker_lab.ps1 doctor
powershell -ExecutionPolicy Bypass -File .\scripts\docker_lab.ps1 status
```

```bash
bash scripts/docker_lab.sh doctor
bash scripts/docker_lab.sh status
```

## 8. Back up and restore the learning folder

Save the current pad and evidence in the browser, then stop the course. Copy
the **whole host learning folder** to a new backup location, including hidden
files and saved history. Use a new destination; do not overwrite another
backup.

Windows PowerShell example, from the repository root:

```powershell
$LearningSource = (Resolve-Path .\.learning).Path
$LearningBackup = Join-Path $env:USERPROFILE "Documents\DS60-learning-backup-20261022"
if (Test-Path $LearningBackup) { throw "Choose a new backup folder name." }
Copy-Item -LiteralPath $LearningSource -Destination $LearningBackup -Recurse -Force -ErrorAction Stop
```

macOS/Linux example:

```bash
LearningBackup="$HOME/DS60-learning-backup-20261022"
if [ -e "$LearningBackup" ]; then
  printf '%s\n' "Choose a new backup folder name."
else
  cp -R .learning "$LearningBackup"
fi
```

The POSIX example checks that the destination is unused before copying, so a
previous backup is not merged or replaced. The date is just an example label.
If you chose a custom data folder, copy it instead of the default repository
`.learning`.

To use a backup in a new container, keep the backup untouched and make a new
working copy in an unused folder. Start the launcher with `--data-dir` pointing
to that copy. Open a saved lesson and inspect its code and evidence before
recording more progress. Do not merge two active `.learning` trees or edit
JSON state while the app is writing it.

For example, restore by making an unused working copy and mounting that copy:

```powershell
# Windows PowerShell, repository root
$LearningBackup = Join-Path $env:USERPROFILE "Documents\DS60-learning-backup-20261022"
$LearningRestored = Join-Path $env:USERPROFILE "Documents\DS60-restored-learning"
if (-not (Test-Path $LearningBackup -PathType Container)) { throw "Backup folder not found." }
if (Test-Path $LearningRestored) { throw "Choose a new working folder name." }
Copy-Item -LiteralPath $LearningBackup -Destination $LearningRestored -Recurse -Force -ErrorAction Stop
powershell -ExecutionPolicy Bypass -File .\scripts\docker_lab.ps1 start -DataDir $LearningRestored
```

```bash
# macOS/Linux/WSL, repository root
LearningBackup="$HOME/DS60-learning-backup-20261022"
LearningRestored="$HOME/DS60-restored-learning"
if [ -d "$LearningBackup" ] && [ ! -e "$LearningRestored" ]; then
  cp -R "$LearningBackup" "$LearningRestored" &&
    bash scripts/docker_lab.sh start --data-dir "$LearningRestored"
else
  printf '%s\n' "Check the backup path and choose an unused working folder."
fi
```

The Bash launcher runs only if the copy succeeds. Use your actual backup path;
WSL users may choose a folder under their Linux home instead of Documents.
The original backup stays untouched. On future starts choose that same restored
working folder, rather than silently switching back to the default.

An older course version may have stored work only in the Docker-managed
`learner-work` volume. First inspect `docker compose ls` to find its original
project. The following example uses the old default `ds60sqlpy`; replace it
with your actual old project name. Stop its app, then export into a **new,
unused** destination under `work/`:

```text
docker compose --project-name ds60sqlpy stop lab
docker compose --project-name ds60sqlpy cp lab:/workspace/.learning work/legacy-learning-export-20261022
```

Check that the destination does not exist before copying, and choose a fresh
name when needed. This works with a stopped container that still exists.
Inspect the exported progress, coaching, and pads before making a separate
working copy for `--data-dir` on Bash or `-DataDir` on PowerShell. Existing host
`.learning` data wins: do not merge the export into it or overwrite it.
Keep the old volume until you have verified the copied files. The detailed
database migration in
[the application guide](offline-app.md#bootstrap-role-volumes-side-by-side-migration)
is separate from moving learner notes and progress.

## 9. Recommended Windows WSL 2 terminal workflow

For Windows learners working in Ubuntu, the recommended layout is a
Linux-local checkout and learning folder. The PowerShell alternative also uses
WSL 2 through the engine, but keeps its files in the Windows filesystem.
To use the Linux-terminal workflow:

1. In PowerShell, confirm the Ubuntu distribution is version 2 with
   `wsl -l -v`.
2. In Docker Desktop, enable that distribution under WSL Integration. Rancher
   Desktop users follow its distribution integration settings.
3. Open Ubuntu from the Start menu. `pwd` now reports a Linux path, not a
   Windows PowerShell location.
4. Keep the Linux checkout and its host learning folder in the Linux home
   filesystem, for example `/home/ada/ds60sqlpy`. To copy a downloaded/extracted
   course folder without installing Git, run the following in Ubuntu:

   ```bash
   cd "$HOME"
   explorer.exe .
   ```

   The File Explorer window now shows your Linux home. Copy the extracted
   course folder into it, using an unused folder name. If you name it
   `ds60sqlpy`, return to Ubuntu and run:

   ```bash
   cd "$HOME/ds60sqlpy"
   ls compose.yaml
   bash scripts/docker_lab.sh start
   ```

   No Windows `.venv` or host Python is needed. Use this Linux checkout for
   later Bash starts, and back up its `.learning` folder from the same place.
5. Open `http://127.0.0.1:8765/learn` in the Windows browser if automatic browser
   opening is unavailable. The launcher also prints its actual ready URL.

Microsoft recommends keeping files in the filesystem matching the terminal
you use. `C:\Users\Ada\Documents\ds60sqlpy` appears to WSL as
`/mnt/c/Users/Ada/Documents/ds60sqlpy`, while `/home/ada/ds60sqlpy` is Linux-local.
These are different storage locations. Use `explorer.exe .` from the Ubuntu
terminal to inspect its current folder in Windows File Explorer.
[Microsoft's filesystem guide](https://learn.microsoft.com/en-us/windows/wsl/filesystems)
explains the path translation. Do not point two simultaneous Windows/WSL course
instances at one learning folder.

## 10. Ports and common first-start problems

The launcher defaults to browser port **8765** and host database port **55432**.
The app still reaches PostgreSQL at port 5432 inside the container network.
If a port is already occupied, choose another without stopping an unrelated
application:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\docker_lab.ps1 start -Port 8766 -DatabasePort 55433
```

```bash
bash scripts/docker_lab.sh start --port 8766 --database-port 55433
```

Open the URL printed for port 8766 in that example, and reuse the same settings
on later starts. The local database is `advanced_sql_training`, with the course
login `admin` and password `admin` on a fresh installation. Changing Compose
credentials does not rewrite accounts in an existing database volume.

| Symptom | First useful check | Next action |
| --- | --- | --- |
| `docker` is not recognized | New terminal; desktop engine's CLI installation | Finish the engine installer, restart the terminal, and rerun all three Docker checks |
| Cannot connect to Docker | Engine application and `docker info` | Start the intended engine and wait for server information |
| Compose command missing | `docker compose version` | Install/update the Compose v2 plugin supplied by the selected engine |
| WSL/virtualization error | WSL version and official Windows requirements | Complete WSL installation/reboot and the vendor's virtualization instructions |
| `compose.yaml` not found | Current folder and extracted ZIP | Change to the actual repository root |
| Downloaded launcher does not open | The matching shell launcher in Terminal/PowerShell | Run the explicit Bash or PowerShell command above; no host Python is required |
| Browser does not open | Printed ready URL and chosen port | Paste the exact `127.0.0.1` URL; inspect status if it does not load |
| Database role/password error | Fresh versus preexisting database volume | Follow the explicit legacy-role/migration section; rebuilding does not change stored accounts |
| Host folder is not writable | Chosen `--data-dir`, engine file sharing, Linux user identity | Choose a user-owned local folder and follow the launcher's diagnostic; preserve the original data |
| Saved work seems absent | Exact data folder and project used at start | Stop and locate the previous `.learning` folder before creating replacement evidence |
| Download or TLS error | Build output and network trust | Use the documented TLS-verified fallback or correct the network trust; do not disable verification |

For a network that rejects Docker Hub's CDN but trusts the alternate official
endpoints, follow [the TLS-verified Rancher/build fallback](offline-app.md#a-tls-verified-fallback-for-a-blocked-docker-hub-cdn).
It keeps certificate verification enabled. [Offline preparation](setup/offline.md)
explains caching optional lesson assets before disconnecting.
