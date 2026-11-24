# spark-deploy-002: Prepare and identify compatible images

Tutorial mode. Stage: beginner. Direct prerequisites: `spark-deploy-001`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Make the environment an explicit input

An image name is a mutable lookup unless it names a digest. A local image ID identifies the bytes already present in one Docker engine. The workshop saves that ID at initialization and uses `pull_policy: never`. Resuming does not resolve a registry tag. Preparing an image and executing a lesson are separate operations.

Use Linux, native architecture, Spark 4.0.1 with Scala binary 2.13, a compatible Java runtime and Python. The Compose probe expects `/opt/spark/bin/spark-submit`, `/opt/spark/bin/spark-class`, `python3` and a usable nonroot UID 65534. A classroom Spark image may be an explicit local override if these interfaces actually exist. Its name is not an independence guarantee. Kubernetes additionally needs Spark's Kubernetes-compatible entrypoint; a pad-worker image is not automatically interchangeable.

## Key terms

- **Image ID:** The identifier of the image bytes already present in one Docker engine, saved at initialization so a resume uses the same environment.
- **Mutable tag:** An image name that can resolve to different contents over time unless it names a digest.
- **pull_policy: never:** The Compose setting that forbids resolving a registry tag, so a missing image fails instead of downloading.
- **Native architecture:** The host CPU architecture, such as ARM64 or AMD64, that the prepared image must match.
- **Image preparation:** The separate operation that builds or loads a compatible Spark image before any lesson executes.

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

## Worked example: checking an image inspect record before saving it

```python
import json

inspect_json = """[{"Id": "sha256:4f1c9a0e7b2d", "RepoTags": ["local/spark:4.0.1"],
  "RepoDigests": [], "Architecture": "arm64", "Os": "linux",
  "Config": {"User": "65534", "Env": ["SPARK_HOME=/opt/spark", "JAVA_HOME=/opt/java/openjdk"]}}]"""
record = json.loads(inspect_json)[0]
problems = []
if record["Os"] != "linux":
    problems.append("not a Linux image")
if record["Architecture"] != "arm64":
    problems.append("architecture " + record["Architecture"])
if not record["RepoDigests"]:
    problems.append("no registry digest: local ID only, not portable")
env = dict(item.split("=", 1) for item in record["Config"]["Env"])
print("save id:", record["Id"], "| tag is a lookup only:", record["RepoTags"][0])
print("SPARK_HOME:", env.get("SPARK_HOME"), "| user:", record["Config"]["User"])
print("notes:", problems or "none")
```

Output from running the block above:

```text
save id: sha256:4f1c9a0e7b2d | tag is a lookup only: local/spark:4.0.1
SPARK_HOME: /opt/spark | user: 65534
notes: ['no registry digest: local ID only, not portable']
```

The inspect record here is a hand written stand in shaped like docker image inspect output, so the identifiers are illustrative rather than taken from a real engine. The check reads the fields that lab.py init cares about: operating system, architecture, the configured user and the Spark home. Note what the output flags: an image built locally has an empty RepoDigests list, so its sha256 ID identifies bytes inside one Docker engine and cannot be pulled elsewhere. The tag `local/spark:4.0.1` is printed only as a lookup name because retagging another build under the same name would silently change what it points at. Saving the ID, refusing a foreign architecture and recording that the digest is missing are three separate facts; a receipt that only records the tag cannot show which bytes a later resume actually started.

## Worked example: probing the interfaces the lab expects inside the image

```bash
IMAGE=YOUR_PREPARED_LOCAL_SPARK_IMAGE
docker image inspect --format '{{.Id}} {{.Os}}/{{.Architecture}}' "$IMAGE"
docker run --rm --pull=never --network=none --user 65534:65534 \
  --entrypoint /bin/sh "$IMAGE" -c '
    test -x /opt/spark/bin/spark-submit && echo spark-submit ok
    test -x /opt/spark/bin/spark-class && echo spark-class ok
    python3 -c "import sys; print(sys.version.split()[0])"
    /opt/spark/bin/spark-submit --version 2>&1 | grep -E "version 4|Scala version"
  '
```

This command sequence runs on a host that already has the prepared image, so no output is shown here. Each step answers a question that inspect metadata cannot: whether spark-submit and spark-class are executable, whether python3 exists for the nonroot UID 65534, and whether the bundled Spark reports version 4.0.1 with Scala 2.13. The run uses --pull=never and --network=none so a missing image fails loudly instead of being fetched, and so the probe cannot download anything to make itself pass. Running as 65534 matters because the Compose services do; a binary readable only by root would pass a root probe and then fail at worker startup with a permission error that looks like a Spark bug. If grep prints nothing, read the full version banner before concluding the version is wrong, since some distributions format the banner differently.

## Worked example: verifying a wheel lock before an offline notebook build

```python
import hashlib

wheels = {
    "pyspark-4.0.1.tar.gz": b"stand-in bytes A",
    "jupyterlab-4.2.5-py3-none-any.whl": b"stand-in bytes B",
}
lock = {
    "pyspark-4.0.1.tar.gz": hashlib.sha256(b"stand-in bytes A").hexdigest(),
    "jupyterlab-4.2.5-py3-none-any.whl": hashlib.sha256(b"stand-in bytes B").hexdigest(),
    "py4j-0.10.9.9-py2.py3-none-any.whl": "0" * 64,
}
for name, expected in lock.items():
    data = wheels.get(name)
    if data is None:
        print(f"MISSING {name}: offline build will fail")
    elif hashlib.sha256(data).hexdigest() != expected:
        print(f"HASH MISMATCH {name}")
    else:
        print(f"ok {name} {expected[:12]}")
```

Output from running the block above:

```text
ok pyspark-4.0.1.tar.gz c4222a4debba
ok jupyterlab-4.2.5-py3-none-any.whl 767a7a3201dd
MISSING py4j-0.10.9.9-py2.py3-none-any.whl: offline build will fail
```

The byte strings here stand in for downloaded wheel files, so the hashes are of those strings and not of real distributions; the point is the comparison logic, not the digests. Two entries match their locked SHA-256 values and print ok with a short prefix. The py4j entry has a lock line but no file in the wheelhouse, which is the situation the chapter describes: the offline notebook build with --network=none cannot fall back to an index, so pip stops instead of quietly resolving a different version. A hash mismatch is reported separately because it means a file was replaced, which is a different finding from a file that was never downloaded. Running this check before docker build turns a long failed build into a short list of names to fetch, and the list itself belongs in the preparation receipt alongside the image ID.

## Diagnose and transfer

An image can pass inspection yet lack a required binary or shared library. Inspect the first container error and the selected image contents before changing resource settings. `exec format error` suggests architecture mismatch; `ModuleNotFoundError` suggests installation or interpreter path mismatch; an ELF loader error concerns native dependencies. Rebuilding a notebook image cannot repair a missing executor dependency in the separate Spark image.

Keep build receipts, image IDs, package lock identity and runtime results separately. A public cloud registry digest is the portable immutable reference; a local engine ID is useful for the local receipt but is not a download address for another machine.

## Primary references

- [Spark images maintained by Apache](https://github.com/apache/spark-docker)
- [Python dependency distribution](https://spark.apache.org/docs/4.0.1/api/python/tutorial/python_packaging.html)
