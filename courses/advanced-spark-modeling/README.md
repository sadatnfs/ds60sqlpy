# Advanced Spark modeling: likelihoods, autodiff and engine internals

A 38-chapter worked route through distributed custom likelihoods, Scala extension mechanisms, Spark/Torch execution and the boundaries of Spark/TMB modeling.

Start after the Scala/Spark foundation route. Mathematical bridges explain the exact objective before a distributed implementation. Public Spark examples use tiny deterministic CPU data; combined Torch/TMB and Catalyst projects have explicit preparation and evidence requirements. Reading a guide or running a reference does not establish mastery or cluster-scale performance.

Start with the [classroom installation guide](../../README.md). These are complete worked tutorials. Sources and notes are saved; reading markers do not certify mastery.

| Unit | Topic | Runtime |
| --- | --- | --- |
| [asm-001](guides/asm-001.md) | What Spark distributes | spark-local-python |
| [asm-002](guides/asm-002.md) | The additive likelihood theorem | spark-local-python |
| [asm-003](guides/asm-003.md) | Independent group fits and one shared model | spark-local-python |
| [asm-004](guides/asm-004.md) | Whole-group memory, shuffle and skew | spark-local-python |
| [asm-005](guides/asm-005.md) | Stable global logistic likelihood in Spark SQL | spark-local-python |
| [asm-006](guides/asm-006.md) | Loss, count and gradient summaries | spark-local-python |
| [asm-007](guides/asm-007.md) | A driver optimizer over distributed passes | spark-local-python |
| [asm-008](guides/asm-008.md) | Merge precision, unequal partitions and one penalty | spark-local-python |
| [asm-009](guides/asm-009.md) | Retry-safe evaluation and external side effects | spark-local-python |
| [asm-010](guides/asm-010.md) | Nonlinear global maximum likelihood | spark-local-python |
| [asm-011](guides/asm-011.md) | When a likelihood is not separable | spark-local-python |
| [asm-012](guides/asm-012.md) | State-space boundaries and complete-series ownership | spark-local-python |
| [asm-013](guides/asm-013.md) | Typed Scala aggregation and merge laws | spark-local-scala |
| [asm-014](guides/asm-014.md) | Registering a SQL aggregate with explicit nulls | spark-local-scala |
| [asm-015](guides/asm-015.md) | Built-in expression or Scala UDF | spark-local-scala |
| [asm-016](guides/asm-016.md) | A custom Transformer and durable parameters | spark-local-scala |
| [asm-017](guides/asm-017.md) | A custom Estimator and fitted Model lifecycle | spark-local-scala |
| [asm-018](guides/asm-018.md) | Arrow batches and pandas partition functions | reading |
| [asm-019](guides/asm-019.md) | Analyzed, optimized and physical plans | spark-local-scala |
| [asm-020](guides/asm-020.md) | Generated operator code and evaluation fallback | spark-local-scala |
| [asm-021](guides/asm-021.md) | Injecting an exact-version Spark extension | reading |
| [asm-022](guides/asm-022.md) | Writing a Catalyst likelihood expression | reading |
| [asm-023](guides/asm-023.md) | An optimizer rule with a proof obligation | reading |
| [asm-024](guides/asm-024.md) | Forward-mode dual numbers inside JVM rows | spark-local-scala |
| [asm-025](guides/asm-025.md) | Why a query plan is not a global autodiff tape | spark-local-scala |
| [asm-026](guides/asm-026.md) | Preparing a combined Spark and Torch environment | reading |
| [asm-027](guides/asm-027.md) | TorchDistributor with one CPU process | reading |
| [asm-028](guides/asm-028.md) | Two CPU ranks, exact shards and gradient scaling | reading |
| [asm-029](guides/asm-029.md) | Lightning under a Spark launcher | reading |
| [asm-030](guides/asm-030.md) | Data delivery, epochs and restart boundaries | reading |
| [asm-031](guides/asm-031.md) | Independent TMB fits on complete Spark groups | reading |
| [asm-032](guides/asm-032.md) | Distributing compiled models and their ABI | reading |
| [asm-033](guides/asm-033.md) | Independent latent groups and Laplace sums | reading |
| [asm-034](guides/asm-034.md) | Optimizing global TMB loss and gradient summaries | reading |
| [asm-035](guides/asm-035.md) | A coupled random-effect counterexample | reading |
| [asm-036](guides/asm-036.md) | Comparing MLE, Laplace and Bayesian targets | reading |
| [asm-037](guides/asm-037.md) | Measure scheduling, transfer and arithmetic separately | reading |
| [asm-038](guides/asm-038.md) | A custom-model-at-scale review dossier | reading |

See [authoring ownership](authoring/README.md), [coverage](coverage.json), and [qualification boundaries](QUALIFICATION.md).
