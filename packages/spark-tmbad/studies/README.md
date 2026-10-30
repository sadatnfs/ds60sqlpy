# Modeling simulation studies

These original studies compare `ds60-spark-tmbad` and `ds60-spark-likelihood`
without changing either core package. The first experiments use their existing
normal, linear, nonlinear and complete-group likelihood interfaces. Broader
models have explicit implementation requirements; a feature listed in the
research matrix is not a claim of package support.

Start with [the methods contract](design/METHODS.md),
[the feature matrix](design/FEATURE-MATRIX.md), and
[the proposed classroom placements](design/CLASSROOM-PLACEMENT.md).
[The study catalog](design/studies.json) specifies 37 studies and meaningful
contrasts. [The source index](SOURCE-INDEX.json) pins the primary repositories,
licenses and inspected file hashes. Current study runtime observations are kept
separate from these designs.

Two important scientific boundaries govern all examples:

- Both current packages' scalar L2 option penalizes the whole optimized vector.
  For a Gaussian regression that includes its intercept and `log_sigma`. It is
  not automatically a conventional slope-only ridge penalty.
- A likelihood fit, a MAP estimate, a random-effect Laplace integral, and a
  parameter posterior are different objects. Conditional random-effect moments
  at fitted population parameters do not include uncertainty in those parameters.

The shared fixtures are synthetic, keyed by study/scenario/replicate/split and
retained as canonical JSON. Both backends receive the same bytes. Existing
qualification-gallery fixtures are preserved unchanged. Small driver-side
reference calculations operate on those already generated tiny fixtures; the
library calls do not collect real training observations onto the driver.

The initial workflow will generate fixtures, run standalone mathematical
references, and select one explicitly prepared Spark backend. A smoke run checks
execution and numerical contracts. Larger studies report failed fits, Monte Carlo
standard errors and prediction coverage with the correct denominator. No backend,
compiler, dataset, GPU runtime or external R package is installed during a study.

This study stream is separate from the current classroom release and has not yet
been admitted as lessons or qualified as a Monte Carlo benchmark. Read the
individual source/observation status rather than interpreting source presence as
a passed runtime.

## Run the current references

Use an existing Python environment for these standard-library references. They
install nothing and do not start Spark:

```bash
python3 packages/spark-tmbad/studies/run_reference.py --replicates 8 --output /tmp/modeling-reference.json
python3 packages/spark-tmbad/studies/run_global_reference.py --output /tmp/global-gaussian-reference.json
python3 -m unittest discover -s packages/spark-tmbad/studies/tests -v
```

Choose a new output filename for each run; earlier evidence is preserved. The
checked-in `fixtures/smoke.json` is the shared original data. Regeneration uses
`generate_fixtures.py --output NEW_FILE --replicates 2`. Its keyed uniform streams
are deterministic; retained fixture bytes are authoritative when comparing
platforms because floating transcendental implementations can differ slightly.
Byte-for-byte `--check` is a generator/environment check, not a promise that every
platform's math library emits identical final decimal digits.

## Prepared Spark study commands

The following are source-prepared commands for the separately prepared runtime;
they are not evidence that those study gates have run. The native command requires
the matching installed Python wheel, native artifact and JAR. The Torch command
requires its installed package and prepared Spark/Torch/SciPy dependencies.
Run them inside the prepared Linux environment with an output directory mounted
from the host if results must survive container removal.

```bash
spark-submit --jars /opt/spark-tmbad/spark-tmbad.jar packages/spark-tmbad/studies/run_spark.py --backend native --manifest /opt/spark-tmbad/artifact.json --study sim-001 --replicate 0 --output /output/native-normal-r0.json
spark-submit packages/spark-tmbad/studies/run_spark.py --backend torch --study sim-001 --replicate 0 --output /output/torch-normal-r0.json
python3 packages/spark-tmbad/studies/compare_results.py --native /output/native-normal-r0.json --torch /output/torch-normal-r0.json --output /output/normal-pair-r0.json
```

Select sim-001, sim-002, sim-006 or sim-008 for the four current paired runners.
Read [their worked guide](guides/initial-package-studies.md) before comparing
parameters or predictions. A completed shard may include failed fits; its receipt
keeps those failures visible. Unclassified execution failures interrupt the run.

`aggregate_results.py --reports FILE... --output NEW_FILE` summarizes completed
replications. It refuses duplicate replications, changed source/runtime artifacts,
changed statistical targets and incomplete method coverage. It does not hide
failed fits or pool overlapping forecast origins as independent Monte Carlo runs.

The [global Gaussian reference](guides/global-gaussian-sufficient-statistics.md)
shows a rigorously restricted exception to naive independent-group decomposition.
Its current partition slices and dense oracle are a mathematical reference, not
an implemented Spark package backend or a general sparse-Laplace engine.

Current project order puts classroom publication and wrap-up first, independent
native modeling next, and broader Torch expansion afterward. These studies and
all sim-* curriculum placements are explicitly next-stage work. Existing lesson
IDs and the active release source remain unchanged.
