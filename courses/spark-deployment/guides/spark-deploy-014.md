# spark-deploy-014: Submit Kubernetes cluster-mode applications

Tutorial mode. Stage: advanced. Direct prerequisites: `spark-deploy-005`, `k8s-018`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Submit a driver Pod to an explicit Kubernetes target

In Kubernetes cluster mode, submission creates a driver Pod and that driver creates executor Pods. The Kubernetes API authenticates those operations. Image preparation, cluster access, namespace ownership, Spark networking and data storage are independent prerequisites. The local Compose proof does not qualify this path.

Use an explicitly owned namespace, an explicit kubeconfig and context, and a prepared image digest. The project's `kubernetes/submit.py` prints a concrete plan by default. It makes no Kubernetes request until `--execute` is supplied. The workshop does not provision a cloud cluster or choose an ambient account.

## Key terms

- **Kubernetes cluster mode:** Submission that creates a driver Pod, which then creates executor Pods through the Kubernetes API.
- **Pod:** The smallest Kubernetes workload unit, here one Spark driver or executor.
- **Owned namespace:** An explicitly selected namespace whose objects the deployment controls and can safely create or delete.
- **Kubeconfig context:** The explicit cluster, user and namespace selection used for API requests instead of an ambient account.
- **Dry-run plan:** The concrete submission plan that submit.py prints by default before any request is made with --execute.

## Worked case A: review a bounded submission plan

Prepare `Dockerfile.cluster` from a reviewed Spark 4.0.1 Python base that retains the supported Kubernetes entrypoint. Deliberately publish or load that image through your authorized environment. Then:

The submission helper assembles a `spark-submit` command whose Kubernetes settings
are explicit rather than inherited:

From [`projects/cluster-lab/kubernetes/submit.py`](../projects/cluster-lab/kubernetes/submit.py):

```python fragment
return [
    args.spark_submit,
    "--master",
    args.master,
    "--deploy-mode",
    "cluster",
    "--name",
    "ds60-kubernetes-partition-proof",
    "--conf",
    "spark.kubernetes.context=" + args.context,
    "--conf",
    "spark.kubernetes.namespace=" + args.namespace,
    "--conf",
    "spark.kubernetes.container.image=" + args.image,
    "--conf",
    "spark.kubernetes.authenticate.driver.serviceAccountName=spark-driver",
    "--conf",
    "spark.kubernetes.authenticate.executor.serviceAccountName=spark-executor",
    "--conf",
    "spark.kubernetes.driver.label.ds60-workshop=spark-deployment",
    "--conf",
    "spark.kubernetes.executor.label.ds60-workshop=spark-deployment",
    "--conf",
    "spark.executor.instances=2",
    "--conf",
    "spark.executor.cores=1",
    "--conf",
    "spark.executor.memory=512m",
    "--conf",
    "spark.driver.memory=1g",
    "--conf",
    "spark.driver.maxResultSize=1m",
    "--conf",
    "spark.kubernetes.driver.limit.cores=1",
    "--conf",
    "spark.kubernetes.executor.limit.cores=1",
    "--conf",
    "spark.kubernetes.submission.waitAppCompletion=true",
    "local:///opt/spark/work-dir/kubernetes_job.py",
]
```

`--deploy-mode cluster` starts the driver as a pod; the two service-account settings
give the driver and the executors different identities; the labels let the network
policy in chapter 16 select these pods; and `waitAppCompletion=true` makes the
submitting process wait for the application's final state.

```sh
python3 kubernetes/submit.py \
  --kubeconfig "$OWNED_KUBECONFIG" \
  --context "$OWNED_CONTEXT" \
  --namespace ds60-spark-study \
  --master "$SPARK_K8S_MASTER" \
  --image "$QUALIFIED_SPARK_IMAGE_DIGEST"
```

The master value has form `k8s://https://API_HOST:PORT`, matching the selected context. The image value is an immutable registry digest. The script requests two one-core executors and a 1 MiB driver result bound. Its `local:///opt/spark/work-dir/kubernetes_job.py` path refers to a file baked into the image, not a file on the submitting laptop.

Before deliberate execution, prepare the namespace-scoped driver access, verify image-pull access and compare the effective API server to the intended cluster. Add `--execute` only within that authorized target. The expected result is eight partition summaries with 100000 rows and exact sum 4999950000, plus actual driver/executor Pod identities.

## Worked case B: separate image failure from code failure

```text
Pod Pending with ImagePullBackOff: image name, digest or registry access
Pod Pending with insufficient memory: requested resources and node placement
Driver Running, executor create forbidden: driver ServiceAccount/RBAC
Executor running, callback refused: driver address or network policy
```

Inspect Pod conditions and events before editing the application. A nonexistent image cannot be repaired with a new Spark partition count. A driver Pod created successfully does not prove it can create executors. Keep the precise failed stage in the receipt.

## Worked example: pod memory requests against the namespace quota

```python
import math

MIN_OVERHEAD_MIB = 384
NON_JVM_FACTOR = 0.40


def pod_memory(heap_mib):
    return heap_mib + max(MIN_OVERHEAD_MIB, math.floor(heap_mib * NON_JVM_FACTOR))


driver, executor = pod_memory(1024), pod_memory(512)
quota = {"pods": 8, "requests.cpu": 4, "requests.memory": 6 * 1024}
used = {"pods": 3, "requests.cpu": 1 + 2 * 1, "requests.memory": driver + 2 * executor}
print("driver pod", driver, "MiB; executor pod", executor, "MiB")
for key in quota:
    print(f"{key:16} {used[key]:>6} of {quota[key]}")
headroom = {
    "pods": quota["pods"] - 1,
    "requests.cpu": quota["requests.cpu"] - 1,
    "requests.memory": (quota["requests.memory"] - driver) // executor,
}
print("max executors per limit:", headroom, "-> binding:", min(headroom, key=headroom.get))
```

Output from running the block above:

```text
driver pod 1433 MiB; executor pod 896 MiB
pods                  3 of 8
requests.cpu          3 of 4
requests.memory    3225 of 6144
max executors per limit: {'pods': 7, 'requests.cpu': 3, 'requests.memory': 5} -> binding: requests.cpu
```

The arithmetic uses Spark's documented rule for Kubernetes pod memory: heap plus overhead, where overhead is the larger of 384 MiB and a factor times heap, and the factor defaults to 0.40 for non-JVM applications such as this Python job. The 1g driver therefore requests 1433 MiB and each 512m executor requests 896 MiB. Against the workshop `resources.yaml` quota, the submission uses 3 of 8 pods, 3 of 4 requested CPUs and 3225 of 6144 MiB. Scaling up, CPU binds first at three executors, before memory allows five and pods allow seven. This is a calculation, not an observation, so confirm it against the actual pod spec with `kubectl get pod -o yaml` after submission, since a cluster admission controller or explicit `memoryOverhead` setting can change the numbers. When a fourth executor stays Pending with an exceeded quota event, this table explains why without any application change, and the chapter's rule applies: that is an allocation failure, not a numerical one.

## Worked example: reading pod conditions before touching application code

```bash
K="kubectl --kubeconfig $OWNED_KUBECONFIG --context $OWNED_CONTEXT --namespace ds60-spark-study"
$K get pods -l ds60-workshop=spark-deployment \
  -o custom-columns=NAME:.metadata.name,PHASE:.status.phase,ROLE:.metadata.labels.spark-role
$K describe pod OBSERVED_DRIVER_POD | sed -n '/^Events:/,$p'
$K get events --field-selector involvedObject.name=OBSERVED_DRIVER_POD \
  --sort-by=.lastTimestamp
$K logs OBSERVED_DRIVER_POD --tail=200 | grep -E 'Forbidden|ImagePull|Exception' || true
```

These commands gather the evidence that separates the four failure lines in Worked case B, and they print nothing here because no owned cluster is attached to this page. Listing pods with the workshop label and the `spark-role` column shows whether the driver exists and whether any executors were ever created. The Events section of `describe` and the filtered `get events` surface image pull errors, failed scheduling with insufficient memory or exceeded quota, and admission rejections, all of which happen before the application code runs. The final log search looks for the `Forbidden` text that appears when the driver ServiceAccount cannot create executor pods. `OBSERVED_DRIVER_POD` must be replaced with the pod name that the submission actually produced, and the explicit kubeconfig and context keep the queries from landing on an ambient cluster. Save the event output before cleanup, because Kubernetes expires events after a retention window and the receipt needs the exact failing stage.

## Diagnose and transfer

Fetch only the observed application's Pods and logs using explicit target flags. Retain completed driver logs and events before cleanup. Remove only resources carrying the owned identity, with UID checks if another process may replace them. Namespace deletion is not a shortcut when the namespace contains other work or retained storage.

Client tooling may be able to reach the API while nodes cannot reach the registry or storage. Validate each network origin separately. This template is portable instruction, not a claim that every cloud provider, storage class or CNI was tested locally.

## Primary references

- [Spark Kubernetes cluster mode](https://spark.apache.org/docs/4.0.1/running-on-kubernetes.html#cluster-mode)
- [Kubernetes Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
