# spark-deploy-015: Connect Kubernetes notebook drivers

Tutorial mode. Stage: advanced. Direct prerequisites: `spark-deploy-006`, `spark-deploy-014`, `k8s-057`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Give a notebook driver a stable identity and route

A notebook inside Kubernetes can host a client-mode Spark driver. Executors need a stable DNS name for that driver, and their lifecycle should be tied to the owning Pod. A Service selector that accidentally matches two notebooks can route callbacks to the wrong kernel. Use one unique session label, verify exactly one endpoint and preserve the actual Pod name.

The supplied `notebook-service.yaml` is a headless Service template for driver RPC 39000, block traffic 39001 and UI 4040. Substitute its namespace and unique session selector in an owned copy. It does not create a notebook Pod or configure authentication for you. Prepare that Pod's reviewed image, authentication, storage and ServiceAccount deliberately.

## Worked case A: configure the in-cluster client

Inside the prepared notebook kernel, after resolving the actual namespace and Pod name:

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.appName("owned-notebook-client")
    .master("k8s://https://kubernetes.default.svc:443")
    .config("spark.kubernetes.namespace", owned_namespace)
    .config("spark.kubernetes.driver.pod.name", observed_notebook_pod)
    .config("spark.driver.host", "notebook-driver")
    .config("spark.driver.bindAddress", "0.0.0.0")
    .config("spark.driver.port", "39000")
    .config("spark.driver.blockManager.port", "39001")
    .config("spark.kubernetes.container.image", qualified_image_digest)
    .config("spark.executor.instances", "2")
    .config("spark.driver.maxResultSize", "1m")
    .getOrCreate()
)
```

The three Python variables are explicit values you obtained from the owned environment. They are not secrets and should not be inferred from an unrelated default context. The in-cluster API path and projected ServiceAccount identity must be valid in that environment. Inspect driver Pod ownership and executor owner references, then execute a bounded aggregate and stop the session.

## Worked case B: detect a selector collision

```sh
kubectl --kubeconfig "$OWNED_KUBECONFIG" --context "$OWNED_CONTEXT" \
  --namespace "$OWNED_NAMESPACE" get endpointslice \
  -l kubernetes.io/service-name=notebook-driver
```

If two unrelated notebook Pods appear as endpoints, stop before accepting a session. Narrow the Service selector to the unique notebook session label and inspect the resulting endpoint identity. A Service existing with no ready endpoint is a different failure from two eligible endpoints. DNS resolution alone does not distinguish them.

## Diagnose and transfer

Spark uses the named driver Pod to establish executor ownership in this client path. Supplying another Pod's name can cause incorrect garbage-collection behavior. Observe owner references and test shutdown in an owned namespace; do not claim automatic cleanup from configuration alone. Keep notebooks and user-authored code on separately retained storage.

For an external laptop notebook, advertise an address reachable from executor Pods and explicitly design routes/firewalls. A browser port-forward does not provide arbitrary executor-to-laptop RPC. Running the notebook inside the cluster can simplify routing but still requires notebook authentication and Kubernetes authorization.

## Primary references

- [Spark Kubernetes client mode and garbage collection](https://spark.apache.org/docs/4.0.1/running-on-kubernetes.html#client-mode)
- [Kubernetes headless Services](https://kubernetes.io/docs/concepts/services-networking/service/#headless-services)
