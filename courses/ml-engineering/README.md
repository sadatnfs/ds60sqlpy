# Machine learning engineering

Build and investigate a connected local ML system: historical features, Feast, train/serve consistency, evaluation, MLflow, real API execution, safe deployment decisions, delayed labels, monitoring, rollback and governance.

Start from the [main Docker instructions](../../README.md). Select this subject in the shared classroom. This path uses the prepared `data-engineering` worker and requires no host compiler or account. All examples use local synthetic inputs after image preparation.

## Route

| Lesson | Stage | Outcome |
| --- | --- | --- |
| [mle-001: Define the decision and the data-product contract](guides/mle-001.md) | beginner | Define an ML product through its decision, information boundary and accepted artifacts. |
| [mle-002: Event time, knowledge time and label maturity](guides/mle-002.md) | beginner | Construct an eligible training cohort from explicit feature and label clocks. |
| [mle-003: Build features without losing the request population](guides/mle-003.md) | beginner | Build features at the decision grain while preserving all requests and missingness categories. |
| [mle-004: Validate structural and semantic feature contracts](guides/mle-004.md) | beginner | Validate a feature interface structurally and semantically. |
| [mle-005: Validation that matches deployment and time](guides/mle-005.md) | beginner | Design evaluation around the target population and information boundary. |
| [mle-006: Register and retrieve actual Feast historical features](guides/mle-006.md) | beginner | Qualify a real feature-store retrieval against independent temporal and coverage checks. |
| [mle-007: Materialization, online retrieval and freshness decisions](guides/mle-007.md) | intermediate | Populate a real online feature store and enforce a consumer freshness contract. |
| [mle-008: One fitted transformation for training and serving](guides/mle-008.md) | intermediate | Package and use a single fitted preprocessing/model interface. |
| [mle-009: Model evaluation, calibration and decision utility](guides/mle-009.md) | intermediate | Evaluate probabilities, ranking and actions with separately interpreted evidence. |
| [mle-010: Actual MLflow tracking and artifact lineage](guides/mle-010.md) | intermediate | Use real tracking APIs to bind parameters, metrics, artifacts and terminal outcomes to an owned run. |
| [mle-011: Model artifacts, registry versions and trusted loading](guides/mle-011.md) | intermediate | Publish and resolve a model artifact with an explicit trusted interface. |
| [mle-012: A real HTTP contract before a network deployment](guides/mle-012.md) | intermediate | Define and test a serving contract with positive and negative requests. |
| [mle-013: Orchestration, checkpoints and safe retries](guides/mle-013.md) | advanced | Define checkpoint and retry behavior using artifact identities. |
| [mle-014: Shadow comparison and stable rollout cohorts](guides/mle-014.md) | advanced | Design stable routing and shadow comparisons with bounded conclusions. |
| [mle-015: Monitoring with delayed labels and bounded service metrics](guides/mle-015.md) | advanced | Monitor operations, data contracts and mature outcomes as distinct signals. |
| [mle-016: Accepted model pointers and rollback after failure](guides/mle-016.md) | advanced | Activate and recover model state through explicit accepted versions. |
| [mle-017: Model cards, slice evidence and data minimization](guides/mle-017.md) | advanced | Write a model card that is grounded in actual data, metrics and operational decisions. |
| [mle-018: A connected local ML product and real service lifecycle](guides/mle-018.md) | advanced | Deliver a connected local ML product with actual tool execution and a reviewable acceptance decision. |

## Authoring

Maintained prose is in `authoring/units.json`; complete programs are in `references/`. Run `python authoring/build.py` from this directory, or use `--check` to detect drift. The three related data courses share `courses/ml-engineering/authoring/publish.py`. Keep the full repository when using the authoring tools. The shared readers are generated separately.

## Complete local project

The owned local-system project adds a real loopback HTTP prediction service with explicit Docker training, persistent local Feast/MLflow/model state, monitoring, controlled activation and rollback. Its lifecycle is separate from the bounded classroom pad; copy and operate it through the documented owner-aware launcher.

Follow the [complete project instructions](projects/local-system/README.md).
