# LLM evaluation and alignment

A 24-unit course in scientific evaluation and bounded alignment mechanisms. The route uses authored synthetic research-support records, not outputs from a pretrained model. Python Core runs the statistical and finite-policy examples; two units perform actual small CPU PyTorch optimization. No model, dataset, account or service is fetched by opening or running a lesson.

Start with the [main classroom instructions](../../README.md). Existing [LLM mechanisms](../llm-theory/README.md), [applied systems](../llm-applied/README.md), [NLP](../nlp/README.md) and the [statistics book](../statistics-ml/README.md) provide the direct prerequisites.

| Unit | Stage | Topic | Runtime |
| --- | --- | --- | --- |
| [eval-001](guides/eval-001.md) | beginner | Evaluation contracts, populations and estimands | `python-core` |
| [eval-002](guides/eval-002.md) | beginner | Evaluation data, grouping and contamination | `python-core` |
| [eval-003](guides/eval-003.md) | beginner | Annotation rubrics and construct validity | `python-core` |
| [eval-004](guides/eval-004.md) | beginner | Agreement, prevalence and adjudication uncertainty | `python-core` |
| [eval-005](guides/eval-005.md) | beginner | Stratified sampling and population weighting | `python-core` |
| [eval-006](guides/eval-006.md) | intermediate | Paired comparisons and clustered uncertainty | `python-core` |
| [eval-007](guides/eval-007.md) | intermediate | Multiplicity and sequential release decisions | `python-core` |
| [eval-008](guides/eval-008.md) | intermediate | Retrieval evaluation and ranking denominators | `python-core` |
| [eval-009](guides/eval-009.md) | intermediate | Claim support, citations and evidence provenance | `python-core` |
| [eval-010](guides/eval-010.md) | intermediate | Abstention, coverage and decision costs | `python-core` |
| [eval-011](guides/eval-011.md) | intermediate | Judge calibration and presentation bias | `python-core` |
| [eval-012](guides/eval-012.md) | intermediate | Prompt, model and seed effects | `python-core` |
| [eval-013](guides/eval-013.md) | intermediate | Selection procedures and protected holdouts | `python-core` |
| [eval-014](guides/eval-014.md) | advanced | Robustness, access policy and adversarial evaluation | `python-core` |
| [eval-015](guides/eval-015.md) | advanced | Monitoring, delayed labels and online experiments | `python-core` |
| [eval-016](guides/eval-016.md) | advanced | A reproducible evaluation decision packet | `python-core` |
| [eval-017](guides/eval-017.md) | advanced | Preference data and Bradley-Terry reward models | `python-core` |
| [eval-018](guides/eval-018.md) | advanced | Train and audit a small reward model | `llm-torch-cpu` |
| [eval-019](guides/eval-019.md) | advanced | KL-regularized policies and reward exploitation | `python-core` |
| [eval-020](guides/eval-020.md) | advanced | Direct Preference Optimization from ratios to gradients | `python-core` |
| [eval-021](guides/eval-021.md) | advanced | Temporal credit, GAE and the PPO clipped objective | `python-core` |
| [eval-022](guides/eval-022.md) | advanced | Actual CPU PPO updates on a finite contextual policy | `llm-torch-cpu` |
| [eval-023](guides/eval-023.md) | advanced | GRPO groups, normalization and KL estimators | `python-core` |
| [eval-024](guides/eval-024.md) | advanced | Off-policy evaluation and the final alignment audit | `python-core` |

## Evidence and boundaries

The corpus is synthetic. Enumerated finite policies and tiny learned reward/policy networks make mathematics inspectable; they are not pretrained assistants. Advanced guides explicitly separate an objective value, its sampled estimator, its derivative and the deployment claim. RAG support labels are authored judgments, not automated proofs of entailment. Statistical thresholds do not replace access-control or critical-error gates. See [fixture provenance](fixtures/README.md) and [authoring](authoring/README.md).
