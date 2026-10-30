# Prepare a standalone Spark/PyTorch environment

Copy the entire `spark-likelihood` directory into a fresh project and run commands
from that copied directory. It can be renamed. This route needs neither another
DS60 checkout nor an R installation. The Python wheel contains the independent
package; Spark, Java, Torch and scientific libraries are explicit environment
preparation.

## Install the lightweight package

```sh
python -m pip install .
```

Core imports use the standard library. Optional extras in `pyproject.toml`
describe compatible interfaces; they are not an architecture-specific CPU lock.
Choose the appropriate framework distribution deliberately. The reproducible CPU
image below uses exact package-local locks, native Linux ARM64 or AMD64, Python
3.12, Spark 4.0.1/Scala 2.13 and Java 17. GPU support is not implied.

## Build the neutral default image

On a machine authorized and able to obtain the public base images and locked
packages:

```sh
docker build --tag spark-likelihood:0.2.0 .
```

The defaults are `python:3.12.12-slim-bookworm` and
`spark:4.0.1-scala2.13-java17-python3-ubuntu`. The Dockerfile copies the Spark
distribution into the neutral Python environment, installs Java/libgomp and the
package-owned CPU/scientific locks, builds a wheel in a separate stage and
installs it noneditably. It retains the wheel under `/opt/spark-likelihood-wheels`.

The image's copied source is documentation and validation input, not an import
path. Preparation verifies that installed Python source matches that copy and
that `ds60sqlpy` is not importable. A managed `.pth` file selects the bundled
Spark and matching Py4J archives. The image requires no host Python SDK or R.

The source recipe is implemented; **a build and runtime qualification of these
neutral default bases remain pending**. Existing prepared-image receipts do not
qualify different default bases. Hash-locked Python packages do not pin the apt
repository or make public image tags immutable digests. Record the actual base
image identities, native platform and final image identity when qualifying a
build. Resolve approved immutable base digests for a retained release build.

## Keep Spark launcher preparation explicit

Spark 4.0.1's reviewed Torch launcher can otherwise report success after a rank
fails. During image preparation, `tooling/prepare_environment.py --apply` invokes
the installed package's existing exact-source correction. The original and
patched wrapper hashes are retained in `/opt/spark-likelihood/preparation.json`.
Unknown source is rejected; neither the wrapper identity nor its exit-status
check is weakened. No model import, fit or runtime callback applies the patch.

`/opt/spark-likelihood/environment.json` records dependency versions, Java,
selected archive identities and installed-source parity. It explicitly states
that no Spark application or distributed trainer ran during that import check.
The package's [training guide](distributed-training.md) explains the separate
actual launcher-failure and DDP/Lightning examples.

## Prepare an offline or cached compatibility build

An offline build requires all base images already present locally and all
needed wheels in `tooling/wheelhouse`. Use the explicit native Linux preparation
command in [tooling](../tooling/README.md) to populate a wheelhouse before going
offline. The installer has no fallback from offline mode to a public index.

```sh
docker build --pull=false --network=none \
  --build-arg PYTHON_IMAGE=YOUR_PREPARED_LOCAL_PYTHON_IMAGE \
  --build-arg SPARK_IMAGE=YOUR_PREPARED_LOCAL_SPARK_IMAGE \
  --build-arg PREPARED_OS_PACKAGES=1 \
  --build-arg OFFLINE_PYTHON=1 \
  --tag spark-likelihood:0.2.0-offline .
```

Verify those two image names exist locally and match the native engine before
invoking the build. `PREPARED_OS_PACKAGES=1` skips apt preparation only for an
image that already has the required Java and system libraries. Dependency
imports and Java checks still run. It is not permission to pull a missing image
from this machine.

If the chosen Python image already contains **every exact CPU and scientific
lock version**, additionally use `--build-arg PREPARED_PYTHON_PACKAGES=1`. This
verifies every pin instead of reinstalling those packages. The separate wheel
builder still needs the exact build-tool wheels in offline mode. The source
wheel, installed-source checks, trusted Spark launcher preparation and final
imports still run. A missing or different prepared dependency fails clearly.

A classroom-derived cached image may be an explicit compatibility override.
It does not become a mandatory package dependency and does not qualify the
neutral defaults. Do not use cross-architecture emulation as native evidence.
If this host cannot access a registry, use the authorized hosted preparation
path or already retained local bases; do not attempt a local registry login,
pull or manifest lookup.

## Run the installed package after preparation

For an owned local CPU check:

```sh
docker run --rm --pull=never --network none --hostname localhost \
  --memory 4g --cpus 2 --pids-limit 1024 --read-only \
  --tmpfs /tmp:rw,exec,nosuid,nodev,size=1073741824,mode=1777 \
  --env SPARK_LOCAL_IP=127.0.0.1 \
  spark-likelihood:0.2.0 --master 'local[2]' \
  /opt/spark-likelihood/examples/validate_installed.py spark
```

The image runs as UID 65534, with a private writable temporary Java home and no
engine socket. Executable temporary storage supports native libraries such as
zstd. The local example is a real Spark check when executed, but it does not
establish separate-container recovery, multi-host scale or GPU behavior.

Use the copied package's [integration harness](../integration/README.md) for the
master, two workers and separate driver proof, with an exact freshly built wheel
and a fresh evidence directory. It supplies its own network/resource/ownership
contract and requires actual fitting, response-free predictions, partition
coverage and controlled worker loss. Current future-covariate point predictions
are not a conditional-history forecast API or arbitrary distributed Torch
program support.

## Develop and verify the source

```sh
python -m pip install -e '.[test,scipy]'
python -m pytest tests
python -m unittest discover -s tooling/tests -v
```

For scientific or Spark tests, prepare their dependencies and Java first. Report
optional skips as unavailable checks, not passes. A noneditable wheel test must
run outside the source project's import path. Build-time source checks,
installed-wheel imports, numerical oracles, actual Spark, process coordination
and distributed topology remain separate evidence. No command here publishes
to PyPI or a container registry.
