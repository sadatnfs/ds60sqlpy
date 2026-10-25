# Build locally, publish deliberately, and pull a classroom release

The classroom still builds locally by default. Docker Hub is an optional way
to distribute an already reviewed image set. Nothing in `./classroom` uploads
images, signs in to an account, deletes volumes or changes Docker Hub settings.

The publisher uses **one repository**, `YOUR_DOCKERHUB_USER/ds60sqlpy`, with a
separate tag for each image and CPU architecture. For example:

```text
YOUR_DOCKERHUB_USER/ds60sqlpy:0.4.0-lab-arm64
YOUR_DOCKERHUB_USER/ds60sqlpy:0.4.0-worker-python-core-arm64
YOUR_DOCKERHUB_USER/ds60sqlpy:0.4.0-worker-php-cli-arm64
```

Use your actual lowercase Docker Hub username wherever this guide says
`YOUR_DOCKERHUB_USER`. GitHub and Docker Hub are separate accounts. A private
GitHub repository does not make a Docker Hub repository private. A public image
contains the shipped application and course sources, so choose repository
visibility deliberately before uploading. The build excludes learner state,
Git history and private runtime credentials; still review the release payload.

## 1. Build and try the release on your machine

Run these commands in the repository folder using Terminal on macOS, a Linux
terminal, or Ubuntu inside WSL 2 on Windows. Start your Linux-container engine
first. The following command shows the build logs, starts the classroom and
opens the browser:

```sh
./classroom --all --local-build --tag 0.4.0 --rebuild
```

This includes the app, PostgreSQL and sixteen ordinary runtime workers. HTML
and CSS previews run in the browser. PHP has its own worker. Optional NVIDIA
workers are excluded from `--all` and from the normal publisher; see
[CUDA classroom setup](cuda-classroom.md) before choosing them.

Use `--project NAME` on this and every later command if your existing workspace
has a custom name. The default project is `ds60-classroom`. A new project has
its own saved work; changing its name is not a way to recover previous progress.

For a build without starting anything, use:

```sh
./classroom build --all --local-build --tag 0.4.0
```

Check representative reading and runnable lessons, compiler errors, switching
between subjects, saved drafts and prior results. Verify the normal lifecycle:

```sh
./classroom stop
./classroom resume
```

The repository's [validation guide](validation.md) describes contributor checks
and runtime acceptance. Passing a finite test suite is useful release evidence;
it cannot prove zero defects or qualify hardware that was never tested. Keep a
record of the Git revision, image set, architecture and checks used for release.

## 2. Prepare your Docker Hub account

Sign in through Docker Hub and create a repository called `ds60sqlpy`. Choose
public or private visibility according to who should be able to download it.
Check your current account's repository and transfer limits before sharing a
large image set. A private repository requires learners to authenticate too.

Authenticate the local Docker CLI:

```sh
docker login --username YOUR_DOCKERHUB_USER
```

At the password prompt, use a Docker Hub personal access token with the needed
read/write permission. Do not put a token in a command, `.env`, Git, a screenshot
or a lesson. Docker's credential helper stores authentication separately from
the classroom. [Docker access-token documentation](https://docs.docker.com/security/access-tokens/)

## 3. Review the complete image mapping, then publish

The first command only inspects local images and prints their destination tags:

```sh
./scripts/publish-images --namespace YOUR_DOCKERHUB_USER --version 0.4.0
```

It requires the complete ordinary image set to exist locally and checks that
the images are Linux images for one consistent architecture. It captures their
immutable local IDs before any upload. It does not rebuild missing images or
infer that an image passed the test suite.

After reviewing that output and your release checks, explicitly publish:

```sh
./scripts/publish-images --namespace YOUR_DOCKERHUB_USER --version 0.4.0 --push
```

The script tags the inspected local IDs and pushes them sequentially. PostgreSQL
is pulled from its existing upstream/mirror source and is not republished as
your own image. GPU worker publication is excluded because it needs separate
hardware qualification. The Docker Hub Tags page lets you confirm the uploaded
set. [Docker image publishing](https://docs.docker.com/docker-hub/repos/manage/hub-images/push/)

An interrupted upload can leave a partial release. Repeat the same command to
finish its missing layers, but do not announce that release until every image
has uploaded successfully. Treat released tags as immutable: use a new version
when contents change, rather than silently overwriting a tag other learners use.

### Architecture matters

A normal build on Apple Silicon produces Linux `arm64` images. A normal build
on an Intel/AMD computer produces Linux `amd64` images. These are different from
the host OS name: Windows WSL 2 usually uses Linux `amd64` containers.

The publisher adds the actual image architecture to every tag. The launcher
selects the suffix matching the Docker engine. Publishing an `arm64` set does
not provide an `amd64` set automatically. To serve both, build and qualify the
same release on both architectures, or use the optional native-runner workflow
below separately for each architecture. A missing platform tag fails visibly;
the launcher will not silently rebuild or run an emulated release instead.

## 4. Start from published images

The learner still needs a matching checkout or starter ZIP for the launcher
and Compose files. After you have published the required architecture, they run:

```sh
./classroom --from-hub YOUR_DOCKERHUB_USER --tag 0.4.0
```

This pulls missing classroom images, starts the services and opens the browser.
It never falls back to a local build in Hub mode. A smaller installation is:

```sh
./classroom --starter --from-hub YOUR_DOCKERHUB_USER --tag 0.4.0
```

The project saves its source, namespace and version in
`.classroom/PROJECT/images.env`. These are declarative preferences, not shell
code and not the learning database. Subsequent commands retain that selection:

```sh
./classroom stop
./classroom resume
```

`resume` and `--no-build` never build or pull, including in Hub mode. Missing
containers may be recreated from matching local images while keeping volumes.
If an image is missing, ordinary `./classroom` can prepare it according to the
saved image source; `resume` instead explains what is missing.

To download the selected images without starting services:

```sh
./classroom pull --from-hub YOUR_DOCKERHUB_USER --tag 0.4.0
```

To switch an existing locally built project to the published release, explicitly
apply the configuration change while preserving its volumes:

```sh
./classroom --from-hub YOUR_DOCKERHUB_USER --tag 0.4.0 --rebuild
```

In Hub mode, `--rebuild` refreshes the selected published images and applies the
update. It does not compile them. To return to local development:

```sh
./classroom --local-build --tag 0.4.0 --rebuild
```

Always use the matching source release and image tag. Preserve a learning backup
before a version upgrade. Keep your project name unchanged. Do not delete named
volumes as an image-update step.

## 5. Optional GitHub Actions publication

The repository includes **Publish classroom images (manual)**. It has no push,
tag or scheduled trigger. Its default is a build/validation rehearsal without
publishing. It only runs from `main`, checks that the requested version matches
the source, and requires successful **Course validation** and **Application
builds** push runs for the exact same Git revision.

No Docker Hub secret or account configuration has been created for you. When
you are ready:

1. Create a Docker Hub access token with read/write permission. Keep the value
   private and revoke it if it is exposed.
2. In GitHub repository **Settings → Secrets and variables → Actions**, add the
   repository variable `DOCKERHUB_USERNAME` with your Docker Hub namespace.
3. Add the secret `DOCKERHUB_TOKEN` containing the token value. Do not create a
   plain variable for the token.
4. Create a `dockerhub` environment. If your GitHub plan supports the relevant
   protection rules, require a reviewer and restrict it to the release branch.
5. First run the workflow with `publish` left **false**, choosing `0.4.0` and
   one architecture. It rebuilds and exercises each ordinary image on a native
   runner. The jobs are limited to two at a time, but the full set still consumes
   substantial Actions minutes and needs available runners.
6. Review all jobs. Then deliberately set the repository variable
   `DOCKERHUB_PUBLISH_ENABLED` to the exact value `true`.
7. Run the same workflow with `publish` **true**. Login occurs only after that
   image's checks, and tokens are passed through standard input. Repeat for the
   other architecture only if you intend to support and qualify it.

The workflow can publish individual image tags before other jobs finish. A
partially failed workflow is not a complete release. Do not distribute its
version as ready until the whole architecture set succeeds. GPU images remain
outside this workflow. Hosted CI, a dry run and a successful registry push are
three different results; record them separately.

## Troubleshooting without losing progress

| Observation | Smallest useful next step |
| --- | --- |
| `manifest unknown` | Check namespace, release, image suffix and engine architecture. Confirm publication finished. |
| `unauthorized` or `denied` | Check repository visibility and Docker login in this terminal. Keep tokens out of logs. |
| Hub rate or account limit | Check the current Docker Hub account limits; local-build mode remains available. |
| Configuration mismatch during resume | Keep the project name and volumes; use the explicit matching-version update command. |
| Missing local image during resume | Run ordinary `./classroom` to prepare missing images from the saved source. |
| Snapshot/layer extraction errors | Inspect the engine's storage health. Source changes and tag retries do not repair corrupted storage. Back up saved work before destructive engine recovery. |
| GPU worker unavailable | Use CPU/reading variants and the separate CUDA setup guide. Ordinary Hub images do not establish GPU readiness. |
