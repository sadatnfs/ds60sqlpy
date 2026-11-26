# Fresh-machine and assistant onboarding

The repository is the handoff. You do not need an old conversation, an existing
Python environment, local Docker images, MCP connections or GSD session files.
The completed overhaul is closed out; begin a new task rather than automatically
resuming historical plans.

For the completed work, exact verification scope and copy-paste takeover
prompts, read [the progress handoff](TAKEOVER.md).

## 1. Get the maintained checkout

Install Git, Bash and a running Linux-container Docker engine with Compose
2.28.0 or newer. Windows users work inside WSL 2. See the
[setup guide](one-command-classroom.md) for platform installation links.

Clone into a normal local development directory, not a cloud-synchronized
Documents or Desktop folder:

```sh
git clone --branch main https://github.com/sadatnfs/ds60sqlpy.git
cd ds60sqlpy
git status --short --branch
./classroom doctor
```

Give your coding assistant this instruction:

> Read AGENTS.md, docs/fresh-machine.md, CONTRIBUTING.md and .planning/STATE.md.
> This checkout is the source of truth. The overhaul is closed out. Report the
> current branch and prerequisites, preserve learner state, and work only on my
> new request. CVE scanning and CVE-only remediation are opt-in. Do not revive
> historical CVE exceptions or completed phases.

The repository's `.agents/skills/` and `.github/copilot-instructions.md` contain
portable guidance. An optional GSD installation is useful for new planned work,
but is not required to install, run, understand or contribute to the classroom.
Do not restore private chat history or overwrite tracked guidance with an old
machine's `.planning/state.json` or execution flags.

## 2. Choose published images or current source

For the already-published **v2.1.1** classroom, create a separate released-source
worktree. This keeps the maintainer checkout on `main` and pairs the published
images with their exact source tag:

```sh
git worktree add --detach ../ds60sqlpy-release v2.1.1
cd ../ds60sqlpy-release
./classroom doctor
./classroom --all --from-hub sadatnfs --tag 2.1.1
./classroom status
```

Use the printed `/classroom` URL, not a guessed port. For a smaller initial
download, replace `--all` with `--starter`. Other lessons stay readable; their
execution needs the relevant workers. Internet access is needed for the initial
downloads. Ordinary use is offline after preparation. Optional GPU and owned
scientific/service workshops retain their separate setup instructions.

Alternatively, to run **current `main` source**, stay in the main checkout:

```sh
./classroom --starter --local-build
```

Use `--all` instead of `--starter` for all ordinary workers. Source builds are
larger and slower than pulling published images. Changes on `main` after the
release are not retroactively included in v2.1.1 images. Deliberately use
`./classroom --local-build --rebuild` to install changed source into your images.
Do not start both checkouts against the same project concurrently.

## 3. Resume and preserve work

Run `./classroom` from the chosen checkout to reuse its saved selection and
containers. `./classroom resume` strictly refuses downloads and builds;
`./classroom stop` pauses without deleting volumes.

A fresh Git clone does **not** contain the old computer's learner work.
Saved drafts, progress and PostgreSQL data live in named Docker volumes, with
launcher settings in ignored `.classroom/` files. If you want that work on the
new computer, follow [backup and transfer](docker-classroom.md) before erasing
the old machine. Never delete learner volumes as incidental cleanup.

## 4. Prepare contributor tools only when needed

Read [CONTRIBUTING.md](../CONTRIBUTING.md), then install Python 3.12, `uv` and
Node.js 24 for source work. Linux/WSL is the CI-aligned contributor route;
macOS uses the same Docker classroom and can run focused Python checks.
Use your organization's approved package-feed configuration on managed hosts.
Keep environments and package caches outside cloud-synchronized directories.
Do not silently fall back to a public feed when local policy requires a mirror.

From the main checkout:

```sh
uv sync --frozen --extra notebooks --extra data --extra bridge --extra quality --extra professional --extra sql-notebooks
uv run --no-sync python scripts/course.py validate
uv run --no-sync python scripts/check_modules.py
uv run --no-sync python scripts/check_repository_guidance.py
git diff --check
```

Use [validation](validation.md) for the focused tests relevant to a change.
A missing package in an approved feed is a setup blocker, not permission to
rewrite the lock or bypass host policy. Do not install every language toolchain
on the host, rebuild the full image catalog for a documentation edit, or publish
images merely because you were asked to push code.

## 5. Maintenance and release policy

- CVE scans and CVE-only fixes are optional and require an explicit request.
  No automatic image scan, exception renewal or zero-CVE release gate remains.
  `make scan` is retained as a manual diagnostic; existing reports are historical.
- Functional tests, classroom startup/resume, native runtime qualification,
  source/image identity, checksum checks, secret detection and CodeQL remain.
  Unscanned images are not claimed to be vulnerability-free.
- Keep dependency security-update PR automation disabled in the repository's
  GitHub settings unless explicitly re-enabled. Do not dismiss alerts to make
  the dashboard look clean. GitHub settings follow the repository, not a computer;
  a new fork has its own settings.
- Git pushes and Docker Hub publication are separate actions. Follow
  [Docker Hub publication](dockerhub.md) for a new release, including its
  exact-revision PyTorch verification dispatch. Ordinary pushes do not publish.
- `.planning/STATE.md` records the closeout and unperformed human walkthroughs.
  They are not falsely marked passed and are not an automatic work queue.
