# Scala adapter qualification

The [source-bound receipt](qualification.json) records actual native Linux ARM64
compilation and execution on 2026-10-29. The two original Scala sources compiled
with Spark 4.0.1 / Scala 2.13 jars and JDK 21.0.12.1. The executed DataFrame
adapter called the real shared Python JSON CLI, fresh R processes and the
prepared normal C++/TMB model. No numerical result was mocked.

The probe ran in the existing parent image
`sha256:73f68961fbf3e6f1f524a92eafb140a6463af3072e3387b23f653bf41730a5e8`
with read-only current project source, no network, temporary scratch, two CPUs
and 3 GiB RAM. It used no learner volume. The image contains the prepared native
model; mounted current source contains the new CLI and Scala adapter. This is
not yet evidence that an older sealed image already includes the adapter.

## Observed results

- All three partition/batch cases matched the independently calculated normal
  objective with absolute error zero. Both gradient components also agreed
  within 1e-10. Actual nonempty counts included the unequal layout 3/3/2/2/2.
- A separate two-row, five-partition case exercised empty partition identities.
- Generic driver BFGS reached mean 2.0000000856 and log scale 0.1115717440,
  matching mean two and ML variance 1.25. The maximum absolute gradient was
  8.22e-7, within the unchanged 1e-6 criterion, after 11 iterations and
  12 objective evaluations.
- A non-diagonal positive-definite quadratic independently checked the BFGS
  implementation and decreasing accepted objective values.
- Closed objectives, an exhausted evaluation budget, nonfinite parameters,
  unknown models, duplicate observation IDs, missing/text projections,
  null model data and inappropriate complete-group row batching were rejected.
- The caller's cache survived closing the adapter-owned RDD cache. No raw
  observation table was collected on the driver.
- Scala, runner, CLI, registry, R protocol and C++ model source hashes were
  unchanged before and after the final probe. The receipt retains them.

## Scope

The example is a small single-host CPU correctness investigation. Process
startup, JSON conversion and repeated native tape construction have material
costs; no speedup is claimed. The Scala row adapter supports declared
independent-row objectives only. It does not partition coupled latent models
or qualify arbitrary registered scientific assumptions.

Host tests check preparation guards, the shared protocol/model ownership and
this source-bound runtime receipt. A compiler-only pass, host test or current
source mount is not a sealed-image, remote-cluster or native AMD64 acceptance.
The parent integration owner controls its next image rebuild and workshop
entrypoint. No forced parent-crash or remote recovery test was executed here.
