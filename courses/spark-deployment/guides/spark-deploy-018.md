# spark-deploy-018: Build an incident and acceptance dossier

Tutorial mode. Stage: advanced. Direct prerequisites: `spark-deploy-013`, `spark-deploy-017`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Turn a failure into a bounded diagnosis and a reviewable decision

A deployment dossier joins source identity, environment identity and observed behavior. It should make a narrow conclusion easy to check: this exact program completed with these inputs and resource limits on these processes, and these specified failures were handled. A list of configuration files or a green source test does not establish that conclusion.

Use the earliest failing boundary. Preparation failures occur before an application can run. Allocation failures occur before useful task execution. Network failures can occur after executor startup. Numerical failures can occur with healthy infrastructure. Publication/readback can fail after computation succeeds. Preserve the original failure and any repaired run separately.

## Key terms

- **Deployment dossier:** A record joining source identity, environment identity and observed behavior to support one narrow conclusion.
- **Earliest failing boundary:** The first stage, such as preparation, allocation, network, numerics or publication, where a run went wrong.
- **Failure preservation:** Keeping the original failed run separate from any repaired run so diagnosis remains checkable.
- **Acceptance decision:** A reviewable judgment that a specific program, input and topology met its stated criteria.
- **Cleanup export:** Saving bounded logs, event identities, result JSON and failure controls before removing resources.

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

## Worked example: validating an acceptance record before anyone signs it

```python
def problems(record):
    found = [
        k for k, v in record.items() if isinstance(v, str) and v.startswith(("record-", "link-to-"))
    ]
    found = [f"placeholder in {k}" for k in found]
    if record.get("rows") != 100000:
        found.append(f"rows {record.get('rows')} != 100000")
    if record.get("prediction_oracle") != [200003, 200005]:
        found.append("prediction oracle mismatch")
    if record.get("worker_loss") == "passed" and not record.get("retry_attempt_observed"):
        found.append("worker_loss claimed without an observed retry")
    return found


draft = {
    "source_revision": "record-actual-revision",
    "application_id": "app-20260115101500-0004",
    "rows": 87500,
    "prediction_oracle": [200003, 200005],
    "worker_loss": "passed",
}
print(problems(draft))
final = dict(draft, source_revision="9c1e47b", rows=100000, worker_loss="not-run")
print(problems(final))
```

Output from running the block above:

```text
['placeholder in source_revision', 'rows 87500 != 100000', 'worker_loss claimed without an observed retry']
[]
```

The validator turns the chapter's acceptance rules into checks that a reviewer can rerun. The draft fails three ways. Its source revision still holds the `record-actual-revision` placeholder from the example schema. Its row count is 87500, which the chapter says must be rejected even though the slope would still read 2. And it claims worker loss passed without any observed retry attempt, the exact incomplete recovery claim in Worked case B. The corrected record fills a revision, restores 100000 rows and marks worker loss as `not-run`, and the problem list comes back empty. An empty list means only that the record is internally consistent; the revision `9c1e47b` and the application ID here are invented, and the checker cannot tell whether they correspond to real evidence. In a real dossier, each value should link to the receipt it came from, so the reviewer can open the event log or result file rather than trusting the summary.

## Worked example: naming the earliest failing boundary from mixed symptoms

```python
ORDER = ["preparation", "allocation", "network", "numerical", "publication"]
SYMPTOMS = {
    "ImagePullBackOff": "preparation",
    "Pending: exceeded quota": "allocation",
    "executor connection refused to driver:39000": "network",
    "count 87500 != 100000": "numerical",
    "history page missing application": "publication",
    "driver UI gone after completion": None,
}


def earliest(observed):
    boundaries = [SYMPTOMS[s] for s in observed if SYMPTOMS[s]]
    return min(boundaries, key=ORDER.index) if boundaries else "no failure: expected behavior"


print(earliest(["history page missing application", "Pending: exceeded quota"]))
print(earliest(["count 87500 != 100000", "executor connection refused to driver:39000"]))
print(earliest(["driver UI gone after completion"]))
```

Output from running the block above:

```text
allocation
network
no failure: expected behavior
```

When several symptoms appear together, the chapter advises diagnosing the earliest failing boundary first, and this helper makes that order explicit: preparation, allocation, network, numerical, publication. A missing history entry combined with a quota Pending resolves to allocation, because an application that never got executors cannot have produced events worth reading. A short count combined with a refused callback resolves to network, since a partial result may come from a run that lost executors and nothing is gained by debugging partition semantics first. A missing driver UI after completion maps to no failure at all, matching chapter 9's observation that the live UI disappears when the application stops. The symptom table is a small, hand-written sample of the incident list in the chapter, so unknown messages would raise a KeyError instead of guessing, which is the desired behavior. Extend it only with symptoms you have actually observed and attributed to a boundary.

## Diagnose and transfer

Use a compact incident table with observed symptom, boundary, minimal next check and result. For example: missing UI after completion goes to history; executor connection refused goes to advertised driver address; ImagePullBackOff goes to node registry access; Pending goes to quota/placement; wrong aggregate goes to partition/data semantics. Do not label all of these as Spark instability.

Before cleanup, export bounded logs, event identities, result JSON and failure controls. Stop only the owned application and containers, preserve saved state and required images, and record what remains. Normal stop, exact-container resume, retained-state replacement and state destruction are separate operations. This project deliberately has no command that deletes state.

The independent modeling packages need additional API-specific numerical oracles, copied-project preparation and actual fit/predict/forecast/recovery checks. The classroom deployment route explains the infrastructure used by those tests; it cannot substitute its linear fixture for their scientific acceptance.

## Primary references

- [Spark monitoring evidence](https://spark.apache.org/docs/4.0.1/monitoring.html)
- [Kubernetes application troubleshooting](https://kubernetes.io/docs/tasks/debug/debug-application/)
