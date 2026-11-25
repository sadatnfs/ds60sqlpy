# spark-deploy-015: Connect Kubernetes notebook drivers

Tutorial mode. Stage: advanced. Direct prerequisites: `spark-deploy-006`, `spark-deploy-014`, `k8s-057`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Give a notebook driver a stable identity and route

A notebook inside Kubernetes can host a client-mode Spark driver. Executors need a stable DNS name for that driver, and their lifecycle should be tied to the owning Pod. A Service selector that accidentally matches two notebooks can route callbacks to the wrong kernel. Use one unique session label, verify exactly one endpoint and preserve the actual Pod name.

The supplied `notebook-service.yaml` is a headless Service template for driver RPC 39000, block traffic 39001 and UI 4040. Substitute its namespace and unique session selector in an owned copy. It does not create a notebook Pod or configure authentication for you. Prepare that Pod's reviewed image, authentication, storage and ServiceAccount deliberately.

## Key terms

- **In-cluster client mode:** Running the driver inside a notebook Pod while executors run as separate Pods.
- **Headless Service:** A Kubernetes Service without a cluster IP that gives the driver Pod a stable DNS name for RPC, block and UI ports.
- **Session selector:** A unique label that must match exactly one notebook Pod so callbacks reach the right kernel.
- **Driver Pod name:** The observed name passed in spark.kubernetes.driver.pod.name so executors are owned by that Pod.
- **Garbage collection:** Kubernetes deletion of executor Pods through owner references when the owning driver Pod is removed.

## Worked case A: configure the in-cluster client

Inside the prepared notebook kernel, after resolving the actual namespace and Pod name:

```python external
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

## Worked example: rendering an owned Service copy and refusing leftover placeholders

```python
import re

template = """apiVersion: v1
kind: Service
metadata:
  name: notebook-driver
  namespace: NAMESPACE
spec:
  clusterIP: None
  selector:
    ds60-session: NOTEBOOK_SESSION
  ports:
    - name: driver-rpc
      port: 39000
    - name: blocks
      port: 39001
    - name: spark-ui
      port: 4040
"""


def render(values):
    text = template
    for placeholder, value in values.items():
        text = text.replace(placeholder, value)
    leftover = re.findall(r"\b[A-Z][A-Z_]{5,}\b", text)
    if leftover:
        raise ValueError(f"unsubstituted: {leftover}")
    return text


try:
    render({"NAMESPACE": "ds60-spark-study"})
except ValueError as error:
    print(error)
owned = render({"NAMESPACE": "ds60-spark-study", "NOTEBOOK_SESSION": "nb-7f3c2a"})
print(
    [line.strip() for line in owned.splitlines() if "namespace:" in line or "ds60-session" in line]
)
print("ports:", re.findall(r"port: (\d+)", owned))
```

Output from running the block above:

```text
unsubstituted: ['NOTEBOOK_SESSION']
['namespace: ds60-spark-study', 'ds60-session: nb-7f3c2a']
ports: ['39000', '39001', '4040']
```

Substituting the template by hand invites a forgotten placeholder, and a Service whose selector still reads `NOTEBOOK_SESSION` silently matches nothing. The renderer replaces only the values it is given and then scans for any remaining all-caps token of six or more characters. The first call supplies the namespace but not the session label, so it is refused with the missing name. The second call fills both and the output shows the owned namespace `ds60-spark-study`, the unique session label `nb-7f3c2a` and the three ports from `notebook-service.yaml`: 39000 for driver RPC, 39001 for blocks and 4040 for the UI. The inline template omits `targetPort` lines for brevity, so render from the real file in practice. The regex is a heuristic tuned to this manifest's placeholder style; it would miss a lowercase placeholder and could flag a legitimate uppercase value, so the rendered copy still needs a human diff and a server-side dry run before it is applied.

## Worked example: counting endpoints behind the driver Service

```python
def verdict(slice_json):
    ready = [
        e["targetRef"]["name"]
        for e in slice_json["endpoints"]
        if e["conditions"].get("ready") and e.get("targetRef", {}).get("kind") == "Pod"
    ]
    if len(ready) == 1:
        return f"accept: single driver endpoint {ready[0]}"
    if not ready:
        return "reject: Service has no ready endpoint (wrong label or pod not ready)"
    return f"reject: selector matches {len(ready)} pods {ready}"


def endpoint(name, ready=True):
    return {"conditions": {"ready": ready}, "targetRef": {"kind": "Pod", "name": name}}


cases = {
    "unique session label": [endpoint("nb-alice-0")],
    "shared label": [endpoint("nb-alice-0"), endpoint("nb-bob-0")],
    "pod still starting": [endpoint("nb-alice-0", ready=False)],
}
for label, endpoints in cases.items():
    print(f"{label:22} {verdict({'endpoints': endpoints})}")
```

Output from running the block above:

```text
unique session label   accept: single driver endpoint nb-alice-0
shared label           reject: selector matches 2 pods ['nb-alice-0', 'nb-bob-0']
pod still starting     reject: Service has no ready endpoint (wrong label or pod not ready)
```

Worked case B asks you to look at EndpointSlices before accepting a notebook session, and this function encodes the decision. Only endpoints that are ready and point at a Pod count. One ready endpoint is accepted and its pod name is recorded so it can be compared with `spark.kubernetes.driver.pod.name`. Two ready endpoints mean the selector matched another notebook as well, so executor callbacks could reach Bob's kernel instead of Alice's, and the session is rejected. A single endpoint that is not ready yields the third outcome, which DNS alone cannot distinguish from the collision because a headless Service resolves either way or not at all. The case data are hand-built dictionaries shaped like the `endpoints` array of a real `kubectl get endpointslice -o json` response, not captured cluster output. In use, collect every slice for `kubernetes.io/service-name=notebook-driver`, since a Service can be split across several slices, and merge their endpoints before applying the rule.

## Diagnose and transfer

Spark uses the named driver Pod to establish executor ownership in this client path. Supplying another Pod's name can cause incorrect garbage-collection behavior. Observe owner references and test shutdown in an owned namespace; do not claim automatic cleanup from configuration alone. Keep notebooks and user-authored code on separately retained storage.

For an external laptop notebook, advertise an address reachable from executor Pods and explicitly design routes/firewalls. A browser port-forward does not provide arbitrary executor-to-laptop RPC. Running the notebook inside the cluster can simplify routing but still requires notebook authentication and Kubernetes authorization.

## Primary references

- [Spark Kubernetes client mode and garbage collection](https://spark.apache.org/docs/4.0.1/running-on-kubernetes.html#client-mode)
- [Kubernetes headless Services](https://kubernetes.io/docs/concepts/services-networking/service/#headless-services)
