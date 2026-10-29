# Owned TMB project

This project compiles nine original statistical models inside a prepared Linux
R environment. It is separate from the ordinary single-file R classroom pad.
The chapter companions remain runnable without TMB. See the [protocol](PROTOCOL.md)
for fixed model names, parameter order and request/response semantics.

## Preparation

Prepare the classroom's native R statistics image first. Supply its exact local
image tag or immutable image ID as `R_BASE_IMAGE`; do not substitute a different
R/Matrix ABI. The dependency installer requires R4.6.1, Matrix1.7.6 and Rcpp1.1.2,
then verifies measured SHA256 pins for RcppEigen0.3.4.0.2 and TMB1.9.25. Downloads
occur only during build. Model evaluation is offline.

```bash
cd courses/tmb-modeling/projects/tmb-local
docker build --progress=plain --build-arg R_BASE_IMAGE=ds60sqlpy-worker-r-statistics:1.1.0 -t ds60-tmb-local:lesson .
```

Use the existing R image's actual tag when it differs. A native ARM base produces
ARM libraries; a native AMD64 base produces AMD64 libraries. This recipe does not
run an emulator or claim qualification on a second architecture. The builder
needs a C++ compiler already present in the reviewed R image and compiles serially.
Reserve roughly 3 GiB memory for preparation and avoid overlapping heavy builds.

The build checks all original models before producing the project image. It keeps
the package dependency licenses installed by R. Review distribution obligations
before publishing an optional combined runtime; this project does not publish it.

## Run numerical acceptance

```bash
docker run --rm --network none --cpus 2 --memory 3g --read-only --tmpfs /tmp:rw,size=256m ds60-tmb-local:lesson
```

This executes actual compiled-model acceptance. It checks Gaussian normalization,
analytic and numerical gradients, known ML estimates, regression, exact Gaussian
latent integration, AR1 covariance, count/censor terms, nonlinear and panel fits,
curvature, sdreport and one/two-thread OpenMP parity. It does not claim browser,
Spark, multi-node, GPU or rpy2 acceptance.

## Evaluate an explicit parameter vector

Create `request.json` as in the protocol, then mount that one file read-only:

```bash
docker run --rm --network none --cpus 2 --memory 3g --read-only --tmpfs /tmp:rw,size=256m \
  -v "$PWD/request.json:/request.json:ro" ds60-tmb-local:lesson \
  R/evaluate.R /opt/tmb-project /request.json
```

The command prints detached JSON. Redirect it to a local file if you want a durable
receipt. No named learner volume is touched. Compilation and scratch files must
stay separate from learner progress and source. Never mount a Docker socket into
this project or compile a downloaded model from an unreviewed tutorial.

## Python bridge

`python/bridge.py` contains a lazy, scoped rpy2 regression bridge with explicit
schema, finite-value and row-identity checks. It requires a separately prepared
Python3.12 environment linked to this R shared library. The separately qualified
combined runtime uses NumPy2.2.6, pandas2.2.3, rpy2 meta3.6.9, rpy2-rinterface3.6.7
and rpy2-robjects3.6.6. The R-only image recipe above does not claim that dependency
stage is present. Do not install Python packages during a learner run.

The release coordinator can prepare and qualify this additional environment with
`tests/bridge_acceptance.py`. Its actual native ARM success is recorded independently in the qualification ledger. For
process-isolated evaluation, the JSON/Rscript interface remains usable without
embedded R. Python must not send a TMB native pointer to another process.

## Developing a model

Edit original source, copy it into an owned build directory, compile there and
load it in a fresh R process. Test values before gradients, then optimization and
uncertainty. Deliberate compile-failure tests use disposable source copies. Keep
original source, compiled library identity and diagnostic receipts together.

`tests/test_reference.py` is a fast standard-library algebra and schema test. It
is useful before native compilation but is not evidence that TMB ran. The full
track [qualification ledger](../../QUALIFICATION.md) records evidence boundaries.

## Public API probe

`tests/public_api.R` exercises the pinned export inventory, map construction,
report methods, ABI/version metadata, configuration, profiles and interval roots,
simulation consistency, sparse Newton optimization, grid descriptors, authoring
scaffolds and benchmark plotting. Run it inside the prepared image:

```bash
docker run --rm --network none --cpus 1 --memory 1g --read-only --tmpfs /tmp:rw,size=256m ds60-tmb-local:lesson tests/public_api.R
```

The probe checks profile/root endpoints against the known-variance Gaussian
formula. Its fixed 100-replicate score diagnostic is retained as statistical
output, not converted into an unconditional model-quality guarantee. The
normalization, OSA, specialized sparse, debugger, precompile and experimental
TMBad/autopar paths are taught but need their own prepared runtime probes.
