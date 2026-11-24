# spark-deploy-017: Transfer to cloud storage and scheduling

Tutorial mode. Stage: advanced. Direct prerequisites: `spark-deploy-011`, `spark-deploy-016`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Carry contracts to a cloud without inventing qualification

The portable parts are application source, image/dependency identity, schema, partition/result bounds and expected numerical oracles. A cloud deployment adds concrete choices: cluster version and CNI, registry access, identity provider, filesystem connector, storage class, zone placement, resource quota and cost controls. A local Compose pass does not answer those questions.

A deployment record should name the selected provider and actual target only when one is authorized. This course supplies instructions and templates; it does not select a real account, create a cluster or claim cloud execution. Keep local qualification and provider-specific acceptance in separate receipts.

## Key terms

- **Portable contract:** The parts that carry across providers: source, image identity, schema, partition and result bounds and numerical oracles.
- **Provider-specific choice:** A cloud decision such as cluster version and CNI, registry access, identity provider, connector or storage class.
- **Zone placement:** Scheduling Pods and storage in particular availability zones; multi-zone claims need their own observations.
- **Resource quota:** A namespace limit on CPU, memory or objects that bounds what a deployment can consume.
- **Provider acceptance:** Separate evidence that an authorized cloud target actually ran the workload, kept apart from local qualification.

## Worked case A: translate storage without changing the result contract

```text
Local input: deterministic Spark-generated range
Cloud input: immutable versioned object-store dataset with recorded schema/hash
Local event log: file:/events on one shared host
Cloud event log: authorized shared filesystem/object-store URI
Unchanged: eight-partition fixture oracle and bounded report contract
```

The cloud image needs a connector compatible with its Hadoop/Spark distribution and the correct identity path. Do not assume a URI scheme alone installs that connector. Validate a tiny read and an owned write/readback before the fitting job. Confirm that credentials are available to the executors that perform I/O, not only the submitting gateway.

The deterministic range fixture remains valuable as a deployment control because it removes storage from the first diagnosis. After it passes, adding a stored dataset changes one meaningful condition. Record that new source identity and compare its independent oracle. Do not silently replace missing cloud input with a synthetic range and report the original data job as passed.

## Worked case B: place resources across zones deliberately

```text
Request: two executors, one core each
Constraint: each needs a volume available in the selected zone
Failure: one Pod Pending because its volume and node affinity conflict
Response: inspect scheduling events and storage topology before changing Spark code
```

Node selectors, affinity, tolerations and available capacity all affect placement. A PodDisruptionBudget can constrain voluntary disruptions but is not a general guarantee against node failure. Autoscaling needs actual metrics and compatible cluster capacity; an executor count setting does not provision machines by itself.

## Worked example: the fixture oracle that must survive a move to cloud storage

```python
import hashlib

import numpy as np

x = np.arange(100000, dtype=np.int64)
y = 3 + 2 * x
slope, intercept = np.polyfit(x.astype(float), y.astype(float), 1)
print("rows", x.size, "sx", int(x.sum()))
print(f"intercept {intercept:.6f} slope {slope:.6f}")
print("predictions", [int(round(intercept + slope * v)) for v in (100000, 100001)])

payload = "x,y\n" + "\n".join(f"{a},{b}" for a, b in zip(x[:5], y[:5])) + "\n"
print(
    "stand-in object sha256",
    hashlib.sha256(payload.encode()).hexdigest()[:16],
    "bytes",
    len(payload),
)
truncated = x[:87500]
print("truncated input passes slope check but fails count:", truncated.size != 100000)
```

Output from running the block above:

```text
rows 100000 sx 4999950000
intercept 3.000000 slope 2.000000
predictions [200003, 200005]
stand-in object sha256 9d9054411eeda562 bytes 25
truncated input passes slope check but fails count: True
```

Moving the job to cloud storage changes where data comes from, so the oracle must be fixed before the move. NumPy stands in for Spark here: it rebuilds the 100000 row fixture with y = 3 + 2x, checks the exact `sx` of 4999950000, fits intercept 3 and slope 2, and reproduces the predictions 200003 and 200005 that the bounded job records. Those are the numbers the cloud run must match on the deterministic range before a stored dataset is introduced. The hash line computes a digest over a tiny CSV stand-in only to show the shape of a source identity; a real record would hash the versioned object or its manifest, not five rows. The last check prints True because a truncated 87500 row input still fits slope 2 perfectly. A slope comparison alone would pass that broken read, and only the row count catches it, which is why the acceptance record keeps both.

## Worked example: pinning executors to the zone that holds their volume

```yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    ds60-workshop: spark-deployment
spec:
  serviceAccountName: spark-executor
  automountServiceAccountToken: false
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: topology.kubernetes.io/zone
                operator: In
                values: [SELECTED_ZONE]
  containers:
    - name: spark-kubernetes-executor
      resources:
        requests:
          ephemeral-storage: 1Gi
```

This executor pod template fragment expresses the zone constraint from Worked case B explicitly instead of leaving it to chance. It keeps the workshop label, the executor ServiceAccount and the disabled token mount from `executor-template.yaml`, and adds a required node affinity on `topology.kubernetes.io/zone`. `SELECTED_ZONE` should be the zone in which the executors' volumes or nearby storage actually live; with a ReadWriteOnce disk bound to one zone, an executor scheduled elsewhere would stay Pending with a volume node affinity conflict. Spark reads such a file through `spark.kubernetes.executor.podTemplateFile` and merges its own container settings into it. No output is shown because only a scheduler can evaluate placement. The trade-off is availability: requiring one zone means a zonal outage or a full zone stops the job instead of moving it, so record that choice next to cost and residency constraints rather than treating it as a default for every deployment.

## Diagnose and transfer

Separate application latency from provisioning, image pull, data transfer and scheduling delay. More executors can increase cost and communication without improving a small fit. Measure useful work and failure behavior under a fixed budget before scaling. Data residency, access control and egress costs belong to the real selected environment, not a portable placeholder paragraph.

A provider acceptance should retain image digest, native platform, driver/executor identities, partition coverage, numerical outputs, resource events, storage readback and controlled failure evidence. GPU, multi-host and multi-zone claims each need their own actual observations. Mark unavailable targets as not run rather than filling a table with assumed success.

## Primary references

- [Spark Kubernetes scheduling and resources](https://spark.apache.org/docs/4.0.1/running-on-kubernetes.html)
- [Kubernetes topology-aware volume scheduling](https://kubernetes.io/docs/concepts/storage/storage-classes/#volume-binding-mode)
- [Kubernetes assigning Pods to nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)
