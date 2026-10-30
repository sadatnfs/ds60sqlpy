# spark-deploy-002: Prepare and identify compatible images

Tutorial mode. Stage: beginner. Direct prerequisites: `spark-deploy-001`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Make the environment an explicit input

An image name is a mutable lookup unless it names a digest. A local image ID identifies the bytes already present in one Docker engine. The workshop saves that ID at initialization and uses `pull_policy: never`. Resuming does not resolve a registry tag. Preparing an image and executing a lesson are separate operations.

Use Linux, native architecture, Spark 4.0.1 with Scala binary 2.13, a compatible Java runtime and Python. The Compose probe expects `/opt/spark/bin/spark-submit`, `/opt/spark/bin/spark-class`, `python3` and a usable nonroot UID 65534. A classroom Spark image may be an explicit local override if these interfaces actually exist. Its name is not an independence guarantee. Kubernetes additionally needs Spark's Kubernetes-compatible entrypoint; a pad-worker image is not automatically interchangeable.

## Worked case A: inspect and save an existing image

From an owned copy of `projects/cluster-lab`, choose a local image you deliberately prepared:

```sh
python3 lab.py init --image YOUR_PREPARED_LOCAL_SPARK_IMAGE
python3 lab.py status
```

`init` uses local `docker image inspect`, rejects another architecture, creates a private state root and saves its owner, source and image binding. `status` can be empty before startup. No pull, build, login or registry inspection occurs. The expected evidence is an `owner.json` in `.workshop`, not a successful Spark fit. Never paste a private token or full Docker configuration into a report.

## Worked case B: prepare a notebook image independently

The optional `Dockerfile.notebook` requires a reviewed Spark base plus a complete wheelhouse and a hash-checked `notebook.lock`. Prepare that lock using the dependency tooling you already trust, including transitive dependencies for the selected Python/native platform. Inspect it before building:

```sh
docker build --pull=false --network=none \
  --build-arg SPARK_BASE=YOUR_LOCAL_SPARK_BASE \
  -f Dockerfile.notebook -t owned-spark-notebook:reviewed .
python3 lab.py --state .notebook-lab init \
  --image YOUR_PREPARED_LOCAL_SPARK_IMAGE \
  --notebook-image owned-spark-notebook:reviewed
```

The recipe deliberately has no hidden network fallback: missing wheels or hashes cause preparation to fail. The expected observation is an installed JupyterLab and Spark 4.0.1 import inside the built image. This source recipe does not supply a prequalified notebook wheel lock or claim that every architecture has those wheels. Record that preparation gap until its actual build succeeds.

## Diagnose and transfer

An image can pass inspection yet lack a required binary or shared library. Inspect the first container error and the selected image contents before changing resource settings. `exec format error` suggests architecture mismatch; `ModuleNotFoundError` suggests installation or interpreter path mismatch; an ELF loader error concerns native dependencies. Rebuilding a notebook image cannot repair a missing executor dependency in the separate Spark image.

Keep build receipts, image IDs, package lock identity and runtime results separately. A public cloud registry digest is the portable immutable reference; a local engine ID is useful for the local receipt but is not a download address for another machine.

## Primary references

- [Spark images maintained by Apache](https://github.com/apache/spark-docker)
- [Python dependency distribution](https://spark.apache.org/docs/4.0.1/api/python/tutorial/python_packaging.html)
