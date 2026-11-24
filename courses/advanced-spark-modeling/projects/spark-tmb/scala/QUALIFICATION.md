# Scala adapter qualification

The [source-bound receipt](qualification.json) records actual native Linux ARM64
compilation and execution on 2026-11-24. The two original Scala sources compiled
with Spark 4.3.0 / Scala 2.13 jars and JDK 21.0.13. The executed DataFrame
adapter called the real shared Python JSON CLI, fresh R processes and the
prepared normal C++/TMB model. No numerical result was mocked.

The probe ran the documented command in the sealed project image
`sha256:3b498bd5ed45619e68a7977fb16585ec55acaa60389c6a391f1b872f416c2dab`,
built from the current source on the Debian 13 Spark Python layer and the R
4.6.1 worker. It used no network, no source mount, temporary scratch, two CPUs
and 3 GiB RAM, and no learner volume. Every Scala, runner, CLI, registry, R and
C++ hash in the receipt equals the repository tree. The earlier Spark 4.0.1
receipts are kept in `qualification-history/`; the last of them is
[2026-10-29-spark-4.0.1-arm64.json](qualification-history/2026-10-29-spark-4.0.1-arm64.json).

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
this source-bound runtime receipt. A compiler-only pass or host test is not a
remote-cluster or native AMD64 acceptance; CI qualifies both architectures.
The parent integration owner controls its next image rebuild and workshop
entrypoint. No forced parent-crash or remote recovery test was executed here.
