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

Both use one repository, `YOUR_DOCKERHUB_USER/ds60sqlpy`. Replace the placeholder
with the actual lowercase username or organization namespace. The app and every
ordinary worker have separate tags. PostgreSQL keeps its upstream/mirror image;
GPU workers, SDK/tooling base images and unrelated local images are excluded.

## Tag layouts

| Publication route | App tag | Example worker tag |
| --- | --- | --- |
| Combined CI release | `1.0.0`, with `latest` pointing to a completed release | `1.0.0-worker-python-core` |
| Manual architecture set | `1.0.0-lab-arm64` or `1.0.0-lab-amd64` | `1.0.0-worker-python-core-arm64` or `1.0.0-worker-python-core-amd64` |

Each combined release tag points to an image index containing Linux
`amd64` and `arm64` variants. Docker selects the variant matching the engine. This is the default `--from-hub` layout.
Manual architecture tags require the consumer's explicit `--architecture-tags`
option. Publishing ARM64 images from a Mac does not create AMD64 images for a
typical Windows/WSL machine, and the local publisher does not create a combined
manifest. [Docker multi-platform images](https://docs.docker.com/build/building/multi-platform/)

## 1. Build and try the release on your machine

The CI route builds its own images on native runners. The commands in this
section prepare a local installation or the manual publisher's input images.
Use Terminal on macOS, a Linux terminal, or Ubuntu inside WSL 2 on Windows.

Build the complete ordinary set with visible logs and start the classroom:

```sh
./classroom --all --local-build --tag 1.0.0 --rebuild
```

To build without starting services:

```sh
./classroom build --all --local-build --tag 1.0.0
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
./classroom publish --to-hub YOUR_DOCKERHUB_USER --tag 1.0.0
```

Omitting a selection, or adding `--all`, includes the app and every ordinary
worker in `docker/classroom-images.tsv`. All selected images must exist and
agree on one Linux architecture before any tag or push operation. The tag
defaults to the checked-in source version; an explicit version must match it.
Each invocation inspects the current local images and pins their immutable IDs.
It neither builds missing images nor proves that existing images passed tests.

After reviewing the mapping and your local qualification, upload deliberately:

```sh
./classroom publish --to-hub YOUR_DOCKERHUB_USER --tag 1.0.0 --push
```

Keep the tested image set unchanged between review and upload. A missing image
stops preflight before any selected image is tagged or pushed. Prepare the
complete set first, or explicitly select a smaller distribution.

For a starter-only set, preview both necessary images:

```sh
./classroom publish --to-hub YOUR_DOCKERHUB_USER --tag 1.0.0 --profile app --profile python-core
```

Append `--push` only when ready to upload that same selection. Repeated
`--profile` options select exact images, with no implicit app or Core.
`--all` and `--profile` cannot be combined. A partial set cannot serve a full
`--all` installation. The older `./scripts/publish-images` entrypoint and
`--namespace`/`--version` aliases remain supported; supply one spelling per
namespace/version option.

This route creates architecture tags only. A learner on that architecture uses:

```sh
./classroom --all --from-hub YOUR_DOCKERHUB_USER --tag 1.0.0 --architecture-tags
```

Use `--starter` instead of `--all` for the explicitly published starter set.
There is no manual `latest` shortcut. Treat released architecture tags as
immutable and use a new checked-in version when image content changes.

## 4. Start from published images

Download the checkout or starter ZIP matching the release for its launcher
and Compose files. After a full `[publish-docker]` publication, pull and start the
combined release:

```sh
./classroom --all --from-hub YOUR_DOCKERHUB_USER --tag 1.0.0
```

For a new project, omitting `--tag` resolves the app's `latest` alias and
saves its concrete version. If only the app, Core, JavaScript and TypeScript
were published for a partial release, select those available workers:

```sh
./classroom --profile javascript-node --profile typescript-node --from-hub YOUR_DOCKERHUB_USER
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
./classroom pull --all --from-hub YOUR_DOCKERHUB_USER --tag 1.0.0
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
./classroom --all --from-hub YOUR_DOCKERHUB_USER --tag 1.0.0 --rebuild
```

Use the matching new source version when upgrading. To deliberately follow
`latest` again, update the checkout/ZIP and use `--tag latest --rebuild`.
In Hub mode, `--rebuild` pulls and applies images; it never compiles locally.
A new download alone does not replace running containers.

To return to local development:

```sh
./classroom --local-build --tag 1.0.0 --rebuild
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
git commit -m "Release 1.0.0 [publish-docker]"
git push origin main
```

The source version is `1.0.0` for this release. The workflow reads the checked-in
version rather than inventing a registry-only version. Do not combine a
publication commit with a CI-skip marker.

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
3. Promotion requires the complete ordinary image set for both architectures
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
bump, such as `1.0.1`. No registry-only version is invented.

A complete same-revision release can be recognized without rebuilding or used
to finish missing latest aliases. Older reruns cannot move latest backward.
Do not delete or overwrite a published version merely to make a run succeed.

Review the actual workflow result, receipts and published manifests before
announcing availability. Local tests, source configuration, staging pushes
and successful final promotion are different evidence. This guide does not
claim that a particular registry upload has completed.

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
