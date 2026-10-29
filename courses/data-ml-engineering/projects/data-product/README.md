# Persistent data-product workshop

Follow a complete synthetic snapshot through real HTTP acceptance, SQLite raw
storage, Polars quality checks, DuckDB aggregation, immutable Parquet publication
and verified consumer readback. Controlled process failures demonstrate the
difference between preparing a candidate, changing the accepted pointer and
recording the completion observation.

This is an optional owned project for the Data and ML Engineering book. Ordinary
chapter programs still run in the classroom coding pad. The project needs a
Linux-container Docker engine and Bash; Windows users run the same commands in
WSL 2. No host Python, database or language compiler is required.

## Prepare the image and a new working copy

From the repository root, prepare the ordinary data runtime if it is not already
available. This explicit build shows its logs and does not start the classroom:

```sh
BUILDKIT_PROGRESS=plain ./classroom build --profile data-engineering --local-build
```

Create a new owned folder and copy only public source. The plain `mkdir` below
refuses to overwrite an earlier workshop:

```sh
cd courses/data-ml-engineering/projects/data-product
workshop_dir="$HOME/ds60-workshops/data-product"
mkdir -p "$HOME/ds60-workshops"
mkdir "$workshop_dir"
cp -R product fixtures "$workshop_dir/"
cp run.sh compose.yaml check_project.py README.md DESIGN.md AGENTS.md .gitignore "$workshop_dir/"
cd "$workshop_dir"
./run.sh start
```

Keep WSL working folders in the WSL Linux home directory. Keep an existing owned
copy at its saved location while its containers exist. A source-only copy gets a
new owner, token and state. Do not copy another working folder's `.workshop/` as
part of an ordinary new-project setup.

The default image is `ds60sqlpy-worker-data-engineering:1.1.0`. For a previously
pulled combined Hub release image, select its existing reference on first start:

```sh
DS60_PRODUCT_IMAGE=YOUR_NAMESPACE/ds60sqlpy:1.1.0-worker-data-engineering ./run.sh start
```

The helper never builds or pulls an image. It checks the selected image against
the native Linux engine, saves its immutable identity and uses that identity on
later commands. It refuses automatic architecture emulation. A missing image
produces a preparation diagnostic.

The API binds only to `127.0.0.1:8894`. Set `DS60_PRODUCT_PORT=18894` on the first
start to choose another port. After removing the owned containers with `down`,
`./run.sh configure-port 18894` can change the saved port without replacing data.
Later environment variables do not silently replace saved settings.

## Ingest, publish and read

```sh
./run.sh ingest baseline.json
./run.sh publish baseline
./run.sh product
```

The real published product is:

| route_id | deliveries | packages |
| --- | --- | --- |
| 10 | 2 | 5 |
| 20 | 1 | 1 |

The ingestion response is a raw-acceptance receipt. It does not claim that an
analytical product has been accepted. Repeating the same canonical request
returns the original receipt with `created: false`:

```sh
./run.sh ingest baseline.json
./run.sh snapshot baseline
./run.sh snapshots
```

Changing the content under an existing batch identity or occupying another
batch's source generation is rejected. Object-key order and whitespace are
canonicalized; record-list order remains part of the request identity.

The next fixture is a complete replacement snapshot, not a CDC event. It changes
delivery A from two packages to four:

```sh
./run.sh ingest corrected.json
./run.sh publish corrected
./run.sh product
```

Route 10 now has seven packages; route 20 still has one. No prior raw snapshot or
immutable product is overwritten. A typed but unknown route can be accepted raw
and rejected analytically:

```sh
./run.sh ingest unknown-route.json
./run.sh publish unknown-route
./run.sh product
```

The rejection command exits with status 2, retains bounded quality reasons and
keeps the last accepted pointer. Missing fields, booleans masquerading as
integers, malformed JSON and incorrect expected row counts fail earlier at the
HTTP boundary without partially accepting a raw snapshot.

## Observe a controlled failure

Use these examples in a fresh owned copy so `corrected` has not already been
published. First ingest and publish `baseline`, then ingest `corrected`:

```sh
./run.sh ingest corrected.json
./run.sh publish corrected --failpoint before-pointer
./run.sh product
./run.sh recover
```

The publisher process deliberately exits with status 71 after preparing the
immutable version. The accepted pointer still names the baseline. Recovery
reports the prepared candidate and does not activate it automatically. This
explicit command can validate and activate the already prepared bytes:

```sh
./run.sh publish corrected
```

A later valid snapshot demonstrates the other boundary:

```sh
./run.sh ingest later.json
./run.sh publish later --failpoint after-pointer
./run.sh product
./run.sh recover
./run.sh history
```

The process exits with status 72 after pointer activation. The consumer can
already read nine packages on route 10. Recovery records the missing completion
observation without repeating ingestion or rewriting the immutable product.
An absent terminal observation does not imply that nothing happened.

A changed prepared manifest is rejected before activation, even when its JSON
meaning remains valid. Consumer reads verify the manifest and actual Parquet
bytes before decoding the bounded schema. Corrupt active data is reported rather
than replaced with an earlier result silently.

## Resume and retain progress

```sh
./run.sh stop
./run.sh resume
./run.sh history
./run.sh product
```

Resume starts the exact existing API container from its saved image. It does not
build, pull or create a different project. An explicit replacement applies the
working copy's source using that same saved image:

```sh
./run.sh replace
```

`./run.sh down` removes only owned containers and networks. A later `start`
creates containers from the saved image and existing files. It retains:

| Private path | Purpose |
| --- | --- |
| `.workshop/settings.env` | Fixed project, image identity, port and user selection |
| `.workshop/private/` | Locally generated owner and header token |
| `.workshop/raw/` | Accepted SQLite snapshots and exact raw receipts |
| `.workshop/published/` | Immutable Parquet versions, manifests and active pointer |
| `.workshop/control/` | Publication observations and controlled-writer lock |

Keep the saved image available for exact resume. Published immutable Hub versions
can be pulled again deliberately if needed. A newly rebuilt local image can have
a different identity; the helper does not substitute it silently. State is still
retained when an image is absent. Back up an owned copy with the API stopped and
no publisher active. Private state is excluded from source archives and Git.

Rollback is explicit. Copy a retained accepted version identity from `history`:

```sh
./run.sh rollback VERSION_ID --reason "Review the retained baseline"
```

Rollback retains the accepted source high-water generation. Publishing an older
ordinary candidate afterward cannot silently downgrade that history. A rollback
target needs a completed retained publication; an unactivated staging candidate
does not become accepted merely because its files exist.

## Maintainer acceptance

The standard-library host checker requires a fresh workspace and explicitly
disposable state. It performs real HTTP, analytical and process-exit operations,
then exact resume/replacement, rollback, corruption rejection and scoped cleanup:

```sh
python3 check_project.py --workspace /tmp/ds60-data-product-check --image ds60sqlpy-worker-data-engineering:1.1.0 --report /tmp/ds60-data-product-report.json --confirm-disposable
```

The full source checkout includes `check_project.py`; add it to a copied working
folder if running this maintainer command there. Historical workspaces and reports
are not overwritten. The report records native platform, immutable image identity
and maintained source hashes. Cleanup retains synthetic state and evidence while
removing only that check's owned containers and networks.

The API receives writable raw storage and read-only publication/private mounts.
Only the controlled publisher can change the accepted pointer. One local writer
is enforced with a file lock. This is a trusted local learning fixture with
separate SQLite, file-pointer and observation boundaries; it does not claim a
distributed transaction or public multi-tenant deployment.
