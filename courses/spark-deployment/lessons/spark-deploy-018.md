# spark-deploy-018: Build an incident and acceptance dossier

Tutorial mode. Stage: advanced. Direct prerequisites: `spark-deploy-013`, `spark-deploy-017`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Turn a failure into a bounded diagnosis and a reviewable decision

A deployment dossier joins source identity, environment identity and observed behavior. It should make a narrow conclusion easy to check: this exact program completed with these inputs and resource limits on these processes, and these specified failures were handled. A list of configuration files or a green source test does not establish that conclusion.

Use the earliest failing boundary. Preparation failures occur before an application can run. Allocation failures occur before useful task execution. Network failures can occur after executor startup. Numerical failures can occur with healthy infrastructure. Publication/readback can fail after computation succeeds. Preserve the original failure and any repaired run separately.

## Worked case A: assemble a local acceptance record

```json
{
  "source_revision": "record-actual-revision",
  "image_id": "record-actual-local-image-id",
  "platform": "record-actual-native-platform",
  "topology": "master,two-worker-containers,separate-driver",
  "application_id": "record-observed-application-id",
  "partition_coverage": "link-to-actual-eight-partition-receipt",
  "fit_oracle": "intercept=3,slope=2",
  "prediction_oracle": "200003,200005",
  "worker_loss": "not-run-until-host-action-and-task-events-are-bound",
  "cloud": "not-run"
}
```

This is an example schema with explicit placeholders, not a successful receipt. Replace a field only with observed evidence. Record source hashes when a clean revision does not fully identify the working files. Keep the exact engine image identity and native architecture. Bind the host container IDs to executor/task hosts before calling a topology qualified.

## Worked case B: reject a plausible but incomplete recovery claim

```text
Claim: the fit returned slope 2 after a worker was stopped.
Missing: stop occurred after the final stage, no retry was observed.
Decision: ordinary fit passed; controlled in-flight recovery remains not run.
```

A changed condition that occurs after useful work cannot test its recovery. Repeat only the missing controlled experiment, with an observed active stage and exact owned worker identity. Do not rerun every already accepted numerical model unless changed source or new evidence justifies it. If the final count is 87500 rather than 100000, reject the numerical result even if its slope is still 2.

## Diagnose and transfer

Use a compact incident table with observed symptom, boundary, minimal next check and result. For example: missing UI after completion goes to history; executor connection refused goes to advertised driver address; ImagePullBackOff goes to node registry access; Pending goes to quota/placement; wrong aggregate goes to partition/data semantics. Do not label all of these as Spark instability.

Before cleanup, export bounded logs, event identities, result JSON and failure controls. Stop only the owned application and containers, preserve saved state and required images, and record what remains. Normal stop, exact-container resume, retained-state replacement and state destruction are separate operations. This project deliberately has no command that deletes state.

The independent modeling packages need additional API-specific numerical oracles, copied-project preparation and actual fit/predict/forecast/recovery checks. The classroom deployment route explains the infrastructure used by those tests; it cannot substitute its linear fixture for their scientific acceptance.

## Primary references

- [Spark monitoring evidence](https://spark.apache.org/docs/4.0.1/monitoring.html)
- [Kubernetes application troubleshooting](https://kubernetes.io/docs/tasks/debug/debug-application/)
