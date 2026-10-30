# spark-deploy-017: Transfer to cloud storage and scheduling

Tutorial mode. Stage: advanced. Direct prerequisites: `spark-deploy-011`, `spark-deploy-016`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Carry contracts to a cloud without inventing qualification

The portable parts are application source, image/dependency identity, schema, partition/result bounds and expected numerical oracles. A cloud deployment adds concrete choices: cluster version and CNI, registry access, identity provider, filesystem connector, storage class, zone placement, resource quota and cost controls. A local Compose pass does not answer those questions.

A deployment record should name the selected provider and actual target only when one is authorized. This course supplies instructions and templates; it does not select a real account, create a cluster or claim cloud execution. Keep local qualification and provider-specific acceptance in separate receipts.

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

## Diagnose and transfer

Separate application latency from provisioning, image pull, data transfer and scheduling delay. More executors can increase cost and communication without improving a small fit. Measure useful work and failure behavior under a fixed budget before scaling. Data residency, access control and egress costs belong to the real selected environment, not a portable placeholder paragraph.

A provider acceptance should retain image digest, native platform, driver/executor identities, partition coverage, numerical outputs, resource events, storage readback and controlled failure evidence. GPU, multi-host and multi-zone claims each need their own actual observations. Mark unavailable targets as not run rather than filling a table with assumed success.

## Primary references

- [Spark Kubernetes scheduling and resources](https://spark.apache.org/docs/4.0.1/running-on-kubernetes.html)
- [Kubernetes topology-aware volume scheduling](https://kubernetes.io/docs/concepts/storage/storage-classes/#volume-binding-mode)
- [Kubernetes assigning Pods to nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)
