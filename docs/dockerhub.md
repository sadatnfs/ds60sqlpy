# Publish and install a classroom release

Docker Hub distribution is optional. Ordinary `./classroom` startup, builds,
pulls and resumes never upload images. There are three explicit publication routes:

- **GitHub Actions:** a push to `main` whose HEAD commit message contains
  `[publish-docker]` builds and qualifies Linux AMD64 and ARM64 images, then
  promotes combined release tags for every ordinary profile.
- **Targeted GitHub Actions:** `[build-test-ALIAS]` qualifies a complete
  native group without uploading. `[publish-ALIAS]` on `main` publishes a
  partial versioned release with App, Core and that complete group.
- **Local publisher:** `./classroom publish` previews already built images.
  Adding `--push` uploads the selected images for their one actual architecture.

All publication routes use one repository, `YOUR_DOCKERHUB_USER/ds60sqlpy`. Replace the placeholder
with the actual lowercase username or organization namespace. The app and every
ordinary worker have separate tags. PostgreSQL keeps its upstream/mirror image;
GPU workers, SDK/tooling base images and unrelated local images are excluded.

This checkout targets **1.2.0**. Its publication, native image indexes and fresh
pull/resume acceptance must be checked for that exact release. A version string
or an earlier successful run does not establish those gates.

## Published release and its evidence

The [1.1.0 publisher](https://github.com/sadatnfs/ds60sqlpy/actions/runs/40961726148)
completed successfully from
[source `59a0d116`](https://github.com/sadatnfs/ds60sqlpy/tree/59a0d116a1759d5d509718c52c4f3439e1986644).
It promoted 26 combined version indexes and 26 latest aliases in
`sadatnfs/ds60sqlpy`, after both native ordinary-worker and scientific-project
gates passed. Its separate native AMD64 and ARM64 acceptance jobs pulled and
started App/Core, retained the saved release and learner marker, and passed
stop/resume with the same stateful containers and volumes.

The original acceptance started App/Core only. The additional
[all-module pull audit](https://github.com/sadatnfs/ds60sqlpy/actions/runs/40999272225)
accepted 19 native groups and retained 19 failed groups. A later authenticated
[metadata-only observation](https://github.com/sadatnfs/ds60sqlpy/actions/runs/41019340315)
returned HTTP 404 for the 1.1.0 App tag on October 30, 2026. Keep the original
receipts as historical evidence and verify current tag availability separately.
Worker runtime qualification, canonical publication, fresh module pulls and
saved-state acceptance remain separate gates.

Use the [exact 1.1.0 source ZIP](https://github.com/sadatnfs/ds60sqlpy/archive/59a0d116a1759d5d509718c52c4f3439e1986644.zip)
or its matching release starter for reproducibility. The launcher compares the
resolved app version with its checked-in version; it does not require the local
Git HEAD to equal the publisher SHA. A later checkout still labeled 1.1.0 can
contain changes that those images do not include. In particular, the later
`packages/spark-tmbad/` native package is not part of this published source.
The independent `ds60-spark-likelihood` distribution has its own package version;
that version does not select a classroom image tag.

## Tag layouts

| Publication route | App tag | Example worker tag |
| --- | --- | --- |
| Full CI release after promotion | `1.2.0`, with `latest` then pointing to that completed release | `1.2.0-worker-python-core` |
| Manual architecture set | `1.2.0-lab-arm64` or `1.2.0-lab-amd64` | `1.2.0-worker-python-core-arm64` or `1.2.0-worker-python-core-amd64` |

A candidate such as
`ci-59a0d116a1759d5d509718c52c4f3439e1986644-40961726148-1-r-statistics-amd64`
records the source, run, attempt, profile and native architecture. It is a
staging tag. Normal R setup uses `1.2.0-worker-r-statistics`; the corresponding
moving alias is `latest-worker-r-statistics`. All ordinary worker aliases use
`latest-<catalog suffix>`. Do not enter a `ci-*` candidate as the learner release.

Each combined release tag points to an image index containing Linux
`amd64` and `arm64` variants. Docker selects the variant matching the engine. This is the default `--from-hub` layout.
Manual architecture tags require the consumer's explicit `--architecture-tags`
option. Publishing ARM64 images from a Mac does not create AMD64 images for a
typical Windows/WSL machine, and the local publisher does not create a combined
manifest. [Docker multi-platform images](https://docs.docker.com/build/building/multi-platform/)

### Subjects, runtime profiles and canonical images

The app contains the complete shipped reading library. A worker image contains
the prepared tools for its execution profile. Several subjects can share a
compatible worker, and a subject can offer variants using different workers.
There is no separate image for each lesson. The following mapping comes from
`ModuleCatalog` and [`docker/classroom-images.tsv`](../docker/classroom-images.tsv).
Every tag below is under `sadatnfs/ds60sqlpy:` for the 1.2.0 release layout.
They are available only after its completed publication and acceptance.
Each row describes only the lessons or variants declaring that profile. App is
always included; use `--profile` for ordinary workers and `--image-tag app=VERSION`
when explicitly choosing the app version.

| Subjects using the execution profile | Image profile | Canonical version tag |
| --- | --- | --- |
| Complete reading library, classroom UI and coordination | `app` | `1.2.0` |
| Applied Science; Bayesian Computing; CUDA CPU study variants; Data and ML Engineering; Data Visualization; TensorFlow; Applied LLMs; LLM Evaluation; LLM Theory; NLP; Statistics and ML | `python-core` | `1.2.0-worker-python-core` |
| C++ | `cpp20` | `1.2.0-worker-cpp20` |
| Java | `java21` | `1.2.0-worker-java21` |
| JavaScript and TypeScript | `javascript-node` | `1.2.0-worker-javascript-node` |
| JavaScript and TypeScript | `typescript-node` | `1.2.0-worker-typescript-node` |
| CUDA CPU study variants; TensorFlow | `tensorflow-cpu` | `1.2.0-worker-tensorflow-cpu` |
| CUDA CPU study variants; Custom Likelihoods; Data and ML Engineering; PyTorch; Applied LLMs; LLM Evaluation; LLM Theory | `llm-torch-cpu` | `1.2.0-worker-llm-torch-cpu` |
| Scala and Spark | `scala-jvm` | `1.2.0-worker-scala-jvm` |
| Advanced Spark Modeling; CUDA CPU study variants; Scala and Spark | `spark-local-scala` | `1.2.0-worker-spark-local-scala` |
| Advanced Spark Modeling; CUDA CPU study variants; Data and ML Engineering; Scala and Spark | `spark-local-python` | `1.2.0-worker-spark-local-python` |
| C | `c17` | `1.2.0-worker-c17` |
| Go | `go` | `1.2.0-worker-go` |
| C# | `csharp-dotnet` | `1.2.0-worker-csharp-dotnet` |
| Rust | `rust-stable` | `1.2.0-worker-rust-stable` |
| Swift | `swift-linux` | `1.2.0-worker-swift-linux` |
| Web Development | `php-cli` | `1.2.0-worker-php-cli` |
| JAX | `jax-cpu` | `1.2.0-worker-jax-cpu` |
| Bayesian Computing; Statistics and ML | `bayesian-cpu` | `1.2.0-worker-bayesian-cpu` |
| R; TMB Modeling | `r-statistics` | `1.2.0-worker-r-statistics` |
| Data and ML Engineering; dbt; ML Engineering; Polars | `data-engineering` | `1.2.0-worker-data-engineering` |
| Apache and Open Data Platforms | `data-platforms-python` | `1.2.0-worker-data-platforms-python` |
| Bayesian Computing | `stan-cpu` | `1.2.0-worker-stan-cpu` |
| Julia | `julia` | `1.2.0-worker-julia` |
| dbt | `dbt-duckdb` | `1.2.0-worker-dbt-duckdb` |
| Python Web Development | `python-web` | `1.2.0-worker-python-web` |

Legacy Python and Python/PostgreSQL bridge work also uses the Core environment;
PostgreSQL uses its separately selected upstream database image. Browser
JavaScript/D3, HTML/CSS previews, reading lessons and offline DAX do not need
additional ordinary worker images. Optional CUDA profiles and the owned
Kubernetes adapter are outside the full ordinary image set. Persistent service
workshops have their own explicit preparation and state contracts.

For R and TMB lesson pads, select the R profile with the matching source release:

```sh
./classroom --profile r-statistics --from-hub sadatnfs --tag 1.2.0
```

That selects App, Core, R and PostgreSQL. It does not pull all unrelated language
workers or prepare the separate Spark/TMB reference workshop. For the classroom's
Scala and PySpark pads, explicitly select `scala-jvm`, `spark-local-scala` and
`spark-local-python` as needed. Those ordinary local Spark profiles do not start
a distributed cluster or install either independent modeling package.

## 1. Build and try the release on your machine

The CI route builds its own images on native runners. The commands in this
section prepare a local installation or the manual publisher's input images.
Use Terminal on macOS, a Linux terminal, or Ubuntu inside WSL 2 on Windows.

Build the complete ordinary set with visible logs and start the classroom:

```sh
./classroom --all --local-build --tag 1.2.0 --rebuild
```

To build without starting services:

```sh
./classroom build --all --local-build --tag 1.2.0
```

Already built and tested the matching image set? No rebuild is required merely
to publish it manually. Check actual lessons, compiler diagnostics, figures,
saved drafts and prior results, then verify stop/resume:

```sh
./classroom stop
./classroom resume
```

Keep the same `--project NAME` on later commands if you chose a custom project.
Use [validation](validation.md) to distinguish source checks, actual runtime
execution, browser behavior and platform qualification. A finite test pass
does not establish that every workload or hardware configuration is correct.

## 2. Prepare your Docker Hub account

Create a repository named `ds60sqlpy` in the intended namespace. Choose its
visibility deliberately: a private GitHub repository does not make the Hub
repository private. The published app image includes the shipped course and
application sources. The provided build excludes learner state, Git history
and private runtime credentials.

For CI, configure the two **repository Actions secrets** described in
[section 5](#5-github-actions-publication). No local Docker login is required
for that workflow. For manual publication, the operator authenticates on the
publishing machine if it is not already logged in:

```sh
docker login
```

Docker Hub normally uses a device-code/browser sign-in flow. An interactive
username-and-token login is available through
`docker login --username YOUR_LOGIN_USERNAME`. Keep credentials in Docker's
configured credential store and out of source files, commands, screenshots and
lessons. Organization destinations need write access from the authenticated
account. The local publisher never logs in or reads a password.
[Docker login](https://docs.docker.com/reference/cli/docker/login/),
[access tokens](https://docs.docker.com/security/access-tokens/).

## 3. Review the complete image mapping, then publish manually

Preview the complete local image set without tagging or uploading:

```sh
./classroom publish --to-hub YOUR_DOCKERHUB_USER --tag 1.2.0
```

Omitting a selection, or adding `--all`, includes the app and every ordinary
worker in `docker/classroom-images.tsv`. All selected images must exist and
agree on one Linux architecture before any tag or push operation. The tag
defaults to the checked-in source version; an explicit version must match it.
Each invocation inspects the current local images and pins their immutable IDs.
It neither builds missing images nor proves that existing images passed tests.

After reviewing the mapping and your local qualification, upload deliberately:

```sh
./classroom publish --to-hub YOUR_DOCKERHUB_USER --tag 1.2.0 --push
```

Keep the tested image set unchanged between review and upload. A missing image
stops preflight before any selected image is tagged or pushed. Prepare the
complete set first, or explicitly select a smaller distribution.

For a starter-only set, preview both necessary images:

```sh
./classroom publish --to-hub YOUR_DOCKERHUB_USER --tag 1.2.0 --profile app --profile python-core
```

Append `--push` only when ready to upload that same selection. Repeated
`--profile` options select exact images, with no implicit app or Core.
`--all` and `--profile` cannot be combined. A partial set cannot serve a full
`--all` installation. The older `./scripts/publish-images` entrypoint and
`--namespace`/`--version` aliases remain supported; supply one spelling per
namespace/version option.

This route creates architecture tags only. A learner on that architecture uses:

```sh
./classroom --all --from-hub YOUR_DOCKERHUB_USER --tag 1.2.0 --architecture-tags
```

Use `--starter` instead of `--all` for the explicitly published starter set.
There is no manual `latest` shortcut. Treat released architecture tags as
immutable and use a new checked-in version when image content changes.

## 4. Start from published images

Download the checkout or starter ZIP matching the release for its launcher
and Compose files. After a full `[publish-docker]` publication, pull and start the
combined release:

```sh
./classroom --all --from-hub YOUR_DOCKERHUB_USER --tag 1.2.0
```

For a new project, omitting `--tag` resolves the app's `latest` alias and
saves its concrete version. The accepted partial 1.0.0 release contains App,
Core, JavaScript and TypeScript. Select only those workers and pin that release,
including after `latest` moves to a later completed full release:

```sh
./classroom --profile javascript-node --profile typescript-node \
  --from-hub YOUR_DOCKERHUB_USER --tag 1.0.0
```

The launcher includes Python Core with any profile selection. `--all`
requires every ordinary worker at the app version, which a partial release
may not provide. A missing selected worker stops before containers start and
keeps saved volumes.

Hub mode pulls the selected images and validates their native Linux platform
before creating or refreshing services. It never falls back to local builds
or silently emulates a mismatched architecture. Private repositories require
Docker authentication. Use `--starter` for a smaller prepared installation.

### Choosing latest safely

For a new Hub selection after a completed full release:

```sh
./classroom --all --from-hub YOUR_DOCKERHUB_USER
```

For a partial release, use the selected-profile command above in place of
`--all`. The launcher resolves the app's `latest` tag to a concrete release, requires
that release to match the source checkout, and uses its immutable versioned
worker tags. It saves the concrete version for the project. A mismatch asks
you to update the checkout or starter ZIP before continuing. `latest` works
only with the combined Hub layout, not local builds or `--architecture-tags`.

Later `./classroom`, `./classroom resume` and a repeated same-namespace
`--from-hub USER` retain the saved concrete version. They do not follow a
moving `latest` tag automatically. Use `--tag latest --rebuild` to choose a
new completed app release. No worker is selected from an independently moving
latest alias unless you ask for that worker with `--image-tag PROFILE=latest`.

### Pin each selected image

`--tag VERSION` sets the default app and worker version. Repeat
`--image-tag PROFILE=VERSION` to choose individual images from the catalog,
including `app`. For example:

```sh
./classroom --profile javascript-node --profile typescript-node \
  --from-hub YOUR_DOCKERHUB_USER --tag 1.0.0 \
  --image-tag app=1.0.0 \
  --image-tag javascript-node=1.0.0 \
  --image-tag typescript-node=1.0.0
```

An individual `VERSION` may be `latest`. The launcher uses Docker Buildx to
read that worker alias's published OCI index, checks its profile, source
revision and Linux AMD64/ARM64 platforms, and saves its actual version. If
Buildx or valid index metadata is unavailable, choose a concrete version.
Any different worker patch version must stay in the app's major.minor line
and have the same published source revision. Current CI binds one checked-in
version to each source revision, so its releases do not qualify mixing worker
images from different versions. A different revision stops before startup.
Manual architecture tags do not support latest aliases or mixed-version selections.
The project's saved image settings remain compatible with older three-field
and four-field selections.
Use `--image-tag javascript-node=default --rebuild` to remove a saved worker
pin and make it inherit the app's version again. An explicit `--tag VERSION`
sets a new default and resets previous worker pins unless you repeat them.

### Pull-only setup and strict resume

For a new project using a completed full release, separate downloading from startup:

```sh
./classroom pull --all --from-hub YOUR_DOCKERHUB_USER --tag 1.2.0
./classroom resume
```

The project records the namespace, layout, profiles and concrete release.
`resume` and `--no-build` never pull, build or resolve latest. Ordinary startup can prepare
missing images from the saved source. Pull-only preparation leaves existing
containers unchanged.

Existing saved Hub settings from older versions retain their architecture-tag
layout. A new explicit `--from-hub` selection defaults to the combined layout;
add `--architecture-tags` when selecting a manual/older architecture release.

### Apply an update while retaining progress

For an existing local project, an architecture-layout project moving to CI
tags, or an intentional Hub version update, keep the project name and apply
the intended full release explicitly:

```sh
./classroom --all --from-hub YOUR_DOCKERHUB_USER --tag 1.2.0 --rebuild
```

Use the matching new source version when upgrading. To deliberately follow
`latest` again, update the checkout/ZIP and use `--tag latest --rebuild`.
In Hub mode, `--rebuild` pulls and applies images; it never compiles locally.
A new download alone does not replace running containers.

To return to local development:

```sh
./classroom --local-build --tag 1.2.0 --rebuild
```

Keep the same custom `--project NAME` on every command. Images contain runtime
tools and course sources, not saved drafts, notes, receipts or database state.
Named volumes retain that state. Moving machines requires the separate
[backup and transfer procedure](one-command-classroom.md#backup-and-transfer).

## 5. GitHub Actions publication

The separate [targeted image workflow](targeted-images.md) accepts a HEAD
marker such as `[build-test-js]` to qualify the JavaScript and TypeScript
group on both native platforms without publishing. `[publish-js]` on `main`
publishes App, Core and that group after the required checks. Profile names
are aliases for their complete qualification group. Its partial versioned
release needs selected profiles in the install command above.

The **full publication workflow** runs only for a push to `main` whose HEAD
message contains `[publish-docker]`. The targeted workflow accepts one
`[build-test-ALIAS]` on a branch or one `[publish-ALIAS]` on `main`.
The marker must identify a declared complete group or ordinary profile alias.
HEAD is the newest commit in that push. An unmarked push, a pull request, a
tag push, or a marker only on an earlier commit does not opt in. Unknown,
malformed or multiple Docker markers are rejected by the matching intent
check. Routine validation retains its own triggers. Leave publication markers
out of ordinary checkpoint messages unless publication is intended.

Set these two repository secrets under **Settings → Secrets and variables →
Actions → Repository secrets**:

| Secret | Purpose |
| --- | --- |
| `DOCKERHUB_USERNAME` | The destination Docker Hub account/namespace used by the workflow |
| `DOCKERHUB_TOKEN` | A token authorized to push to that repository |

No additional repository variables, enable flag or protected-environment
configuration is required. Never commit the secret values or print them in
workflow logs. The workflow handles authentication on its runners.

After local checks, stage the reviewed release changes on `main` and create
the opt-in commit, for example:

```sh
git commit -m "Release the reviewed version [publish-docker]"
git push origin main
```

The checked-in source version is `1.2.0`. A new image release from changed source
needs the next coherent checked-in version before this commit. The workflow
reads that version rather than inventing a registry-only version. Do not combine
a publication commit with a CI-skip marker or overwrite an existing release.

### Native builds, staging and promotion

The gate waits for the exact revision's source validation and Docker starter
checks, and promotion rechecks that qualification before canonical tag writes.
The ordinary Docker runtime matrix is skipped for this marked main push because
the publication workflow performs the native runtime qualification itself.

1. Native Linux AMD64 and ARM64 runners build and qualify their app and Python
   Core seed images, then the ordinary worker groups. Builds and runtime
   qualification are real work and can take substantial time.
2. Images are uploaded under commit-specific staging tags in the same Hub
   repository. Small receipts bind source revision, profile, platform,
   immutable image identity and qualification evidence. Image layers move
   through the registry; the workflow does not transfer giant Docker image
   archives through Actions artifacts.
3. The dedicated scientific-project jobs prepare and qualify the installed
   Spark/Torch package and optional R/TMB reference serially on each native
   architecture, using this run's exact qualified bases. Their complete
   source-bound receipts are also required.
4. Promotion requires the complete ordinary image set for both architectures
   and all required checks to succeed. It publishes and validates the worker
   version tags first, then the app version tag. Worker latest aliases follow,
   and the app `latest` pointer moves last.

Staging uploads can occur before the full matrix completes. A staging tag is
not a completed release. Normal installation uses the completed app/version
pointer and its concrete worker version tags. This order avoids selecting a
new app before its required worker versions are available.

### Retrying an interrupted run

Registry operations across multiple tags are not a transaction. **Re-run failed
jobs** can reuse successful receipts from earlier attempts of the same workflow
run and source revision. The selected receipts must be unique and valid, and
worker receipts must bind the exact app/Core seed digests they used. Receipts
from another run or revision are rejected; rebuilt seeds cannot silently be
combined with old worker results.

A failed promotion can complete matching partial version tags using those
original image identities, without rewriting completed matching tags. A new
commit or a full rebuild that encounters partial or conflicting immutable tags
must finish the original failed promotion or use a consistent checked-in patch
bump, such as `1.2.1` after 1.2.0. No registry-only version is invented.

A complete same-revision release can be recognized without rebuilding or used
to finish missing latest aliases. Older reruns cannot move latest backward.
Do not delete or overwrite a published version merely to make a run succeed.

If promotion succeeds but the later Hub pull check fails, the canonical
version tags already exist and must remain immutable. The dispatch-only
`verify-published-images.yml` workflow can check the original partial 1.0.0
receipt and tags from a verifier-only source commit, with no stage or push
operation. Its [native read-only acceptance](https://github.com/sadatnfs/ds60sqlpy/actions/runs/40787547771)
passed on AMD64 and ARM64 after a test expectation and learner-identity fix.
A new release still needs its own promotion and automatic pull acceptance.

Review the actual workflow result, receipts and published manifests before
announcing availability. The historical 1.1.0 evidence is identified above;
configuration, staging pushes and local tests do not establish a later release.

### Audit every published module without republishing

[`audit-published-release.yml`](https://github.com/sadatnfs/ds60sqlpy/blob/main/.github/workflows/audit-published-release.yml)
is a dispatch-only full-release verifier. It uses the original promotion receipt
and exports the exact published Git tree for the launcher, Compose files and
catalog. The current verifier source must pass its own exact-revision source CI.
The workflow records both revisions, so a later verifier does not change which
source the immutable images contain. This is separate from the historical
partial-1.0.0 recovery workflow.

A repository maintainer with permission to dispatch Actions can select **Audit
published full classroom release** in GitHub, or use the authenticated
[GitHub CLI workflow command](https://cli.github.com/manual/gh_workflow_run):

```sh
gh workflow run audit-published-release.yml \
  --repo sadatnfs/ds60sqlpy --ref main \
  -f published_run_id=40961726148 \
  -f published_sha=59a0d116a1759d5d509718c52c4f3439e1986644 \
  -f published_attempt=1 -f check_latest=true
```

The workflow's `GITHUB_TOKEN` has repository-content and Actions read permissions. Hosted
runners use the existing Docker Hub account secrets for authenticated pulls;
no local Docker Hub login or access is needed. The verifier has no build,
staging, push or promotion operation. It shares the publication concurrency
group so canonical pointers remain stable during readback. Existing immutable
tags and the original publisher result remain unchanged.

The published catalog currently produces 19 groups on each native architecture,
with at most four isolated audit jobs running concurrently. Each job pulls only
App/Core plus its chosen group. It checks the combined indexes and native image
identities, saved version and selected profiles, pull-only preparation without
runtime resources, strict startup, exact service selection and stop/resume with
retained learner state. It retains bounded JSON evidence and failure diagnostics
before cleaning its own disposable project. Learner projects are not audit targets.

`check_latest=true` also requires the current selected aliases to match this
release. For a historical release whose aliases have legitimately advanced,
choose `check_latest=false`; canonical version, source, platform and lifecycle
checks still run. Aggregate every required group/architecture receipt before
claiming complete module pull coverage. Pull/setup acceptance does not rerun all
scientific reference programs or establish another host's GPU/cluster readiness.
Runner capacity, image downloads and account pull limits still apply.

### Inspect registry metadata and resume an interrupted audit

The separate
[`inspect-registry-metadata.yml`](https://github.com/sadatnfs/ds60sqlpy/blob/main/.github/workflows/inspect-registry-metadata.yml)
workflow runs focused, hash-locked diagnostic tests followed by native metadata
observations. It uses authenticated and anonymous-control HEAD requests to
observe quota, plus an authenticated canonical App HEAD. It does not pull images
or write registry tags, and it does not claim classroom or whole-source
acceptance. It retains config-binding booleans, numeric quota/status/retry fields
and proxy/mirror presence without credentials, raw token claims, IP headers,
config contents or response bodies.

A maintainer can dispatch that observation with:

```sh
gh workflow run inspect-registry-metadata.yml \
  --repo sadatnfs/ds60sqlpy --ref main -f version=1.2.0
```

A successful login alone does not prove how every later request was attributed.
Authenticated requests can still meet shared-IP throttling. Missing quota headers
mean unknown, not unlimited capacity; deleting images does not reset a pull-rate
limit. Use the actual status and available quota observations to decide whether
to wait or investigate auth/config propagation. A missing canonical-tag HEAD
alone does not distinguish a missing tag from a missing/private repository.
[Docker pull-limit diagnostics](https://docs.docker.com/docker-hub/usage/pulls/)
and [429 troubleshooting](https://docs.docker.com/docker-hub/troubleshoot/).

The full module audit keeps its seven-job source gate. After that gate and
current registry state have been reconciled, `resume_runs` accepts completed
prior full-audit run IDs and follows their bounded recovery ancestry. It validates
and retains their raw accepted receipts, source/verifier/job identities and
hashes. Recovery selects one unresolved canary by default. The optional `cases`
input can select up to six unresolved `group/architecture` pairs, separated by
commas; an already accepted case is refused. At most four selected cases run
concurrently, and known exhausted quota or rejected registry observations stop before image pulls.

Prior receipts remain historical evidence. They do not establish current
availability after tags or repositories have been removed or changed. Inspect
current canonical identities before treating retained scope as live coverage.
Do not overwrite immutable versions, replay every accepted group blindly, or
reinterpret a metadata-only workflow result as a completed module audit.

### Transfer and account limits

The first upload includes the app and ordinary worker set for both
architectures and can be large. Later pushes can reuse unchanged registry
layers, but changed layers still transfer and qualification still consumes
runner time. Staging tags can remain after a failed or interrupted run.

Docker currently lists **200 pulls per 6 hours for authenticated Personal
accounts**, subject to its usage rules. Do not promise unlimited free pulls,
transfer or storage. Docker's fair-use policy permits restrictions or charges
for excessive usage. Check the current account limits and GitHub runner
allowances before scheduling repeated full builds.
[Docker Hub pull limits](https://docs.docker.com/docker-hub/usage/pulls/),
[Docker Hub fair use](https://docs.docker.com/docker-hub/usage/).

GPU hardware, optional cluster operations and external services remain separate
qualification paths. Combined Linux image tags do not establish host-engine
setup, GPU readiness or correctness for every possible workload.

## Troubleshooting without losing progress

| Observation | Next step |
| --- | --- |
| No publication run | Check the branch, push event and exact marker in the HEAD commit message. |
| Version conflict | Preserve the published tags; update the source release consistently and requalify. |
| `latest` differs from the checkout | Obtain the matching source release or starter ZIP, then retry explicitly. |
| Missing image tag | Check release completion, namespace and whether combined or architecture layout was selected. |
| Wrong Linux architecture | Publish and qualify the missing native platform; renaming a tag does not convert it. |
| Unauthorized or denied | Check the operator's Docker login or the two repository secrets, without exposing values. |
| Pull-rate or usage limit | Review current provider limits and avoid repeated unnecessary pulls. |
| Missing image during strict resume | Use ordinary startup to prepare the saved release, or the deliberate update path. |
| Progress appears missing | Return to the original project/engine and verify its volumes; an image pull does not transfer progress. |
