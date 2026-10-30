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
