# spark-deploy-009: Inspect a live Spark UI securely

Tutorial mode. Stage: intermediate. Direct prerequisites: `spark-deploy-007`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Inspect the application without publishing its control plane

Spark exposes several different UIs: the Standalone master, each worker, the live application driver and the History Server. The master describes cluster allocation. The driver describes one application's stages, tasks, executors and environment. A completed driver normally removes its live UI. The History Server reconstructs retained application history; it is not the running driver.

The workshop binds published HTTP ports to host loopback. It does not publish the Spark RPC port or worker UIs. This is appropriate for a trusted single-user machine, not authentication for a shared host. A person who can reach loopback in that host's context may still access it. Event details and configuration can reveal paths or sensitive application information.

## Key terms

- **Live application UI:** The driver's view of one running application's stages, tasks, executors and environment, removed when the driver exits.
- **Master UI:** The Standalone master's view of cluster allocation across workers and applications.
- **Loopback binding:** Publishing a port only on 127.0.0.1, which limits reach on a trusted single-user host but is not authentication.
- **Port forwarding:** A Kubernetes-authorized tunnel that connects a local browser port to an in-cluster UI.
- **Information exposure:** The risk that event details and configuration in a UI reveal paths or sensitive application data.

## Worked case A: inspect a live held application

```sh
python3 lab.py submit --hold-seconds 120
```

In another terminal:

```sh
python3 lab.py urls
```

Open the driver URL during the hold. Match the application ID to the JSON report and inspect two executor identities and the stages that produced the eight partition summaries. Check the Environment tab for `spark.driver.maxResultSize=1m`. A screenshot alone is weak evidence unless its application identity and source receipt are connected.

The hold is bounded and occurs after computation; the app then stops explicitly. A missing UI afterward is normal. The result file persists independently. Do not keep a session alive forever just to preserve a dashboard.

## Worked case B: reach an owned Kubernetes driver securely

After selecting the exact context, namespace and observed driver Pod:

```sh
kubectl --kubeconfig "$OWNED_KUBECONFIG" --context "$OWNED_CONTEXT" \
  --namespace "$OWNED_NAMESPACE" port-forward \
  --address 127.0.0.1 pod/OBSERVED_DRIVER_POD 4040:4040
```

The placeholder must be replaced with the actual owned Pod identity. The browser connects to local loopback; the Kubernetes API authorizes the port-forward. This command does not create a public LoadBalancer or an unauthenticated Ingress. Stop the forwarding process when inspection ends. If another local process already occupies 4040, select a different local port such as 14040 while retaining the Pod port.

## Worked example: checking that every published UI port is loopback only

```python
published = [
    "127.0.0.1:${DS60_MASTER_UI_PORT:-0}:8080",
    "127.0.0.1:${DS60_DRIVER_UI_PORT:-0}:4040",
    "127.0.0.1:${DS60_HISTORY_UI_PORT:-0}:18080",
    "127.0.0.1:${DS60_NOTEBOOK_PORT:-0}:8888",
    "127.0.0.1:${DS60_NOTEBOOK_UI_PORT:-0}:14040",
]
proposed = published + ["7077:7077", "0.0.0.0:39000:39000"]
for entry in proposed:
    host_part, container_port = entry.rsplit(":", 1)
    bound = host_part.split(":", 1)[0] if ":" in host_part else "all interfaces"
    verdict = "ok" if bound == "127.0.0.1" else "REJECT"
    print(f"{verdict:6} container {container_port:>5} bound to {bound}")
```

Output from running the block above:

```text
ok     container  8080 bound to 127.0.0.1
ok     container  4040 bound to 127.0.0.1
ok     container 18080 bound to 127.0.0.1
ok     container  8888 bound to 127.0.0.1
ok     container 14040 bound to 127.0.0.1
REJECT container  7077 bound to all interfaces
REJECT container 39000 bound to 0.0.0.0
```

The first five entries mirror the published ports in the workshop's `compose.yaml`: master UI 8080, driver UI 4040, History Server 18080, notebook 8888 and the notebook's Spark UI 14040, each bound to host loopback with a host port chosen by the launcher. All five pass. The two extra entries are the kind of change someone makes while chasing a callback failure: publishing master RPC 7077 without an address binds every interface, and `0.0.0.0:39000` exposes driver RPC to the LAN. Both are rejected, since neither port is ever published in this lab and neither would fix an executor-to-driver problem inside the internal network anyway. The parser handles only the short Compose syntax used here; the long form with `host_ip` fields needs its own check. Loopback binding limits who can connect, but it is not authentication, so on a shared machine another local account could still reach these UIs.

## Worked example: redacting an Environment tab export before attaching it

```python
import re

environment = {
    "sparkProperties": [
        ["spark.app.id", "app-20260115101500-0004"],
        ["spark.driver.maxResultSize", "1m"],
        ["spark.hadoop.fs.s3a.secret.key", "EXAMPLE-NOT-A-REAL-KEY"],
        ["spark.ssl.keyStorePassword", "changeit"],
        ["spark.executorEnv.API_TOKEN", "tok_example"],
    ]
}
SENSITIVE = re.compile(r"secret|password|token|credential", re.I)
clean = [
    [k, "*********(redacted)" if SENSITIVE.search(k) else v]
    for k, v in environment["sparkProperties"]
]
for key, value in clean:
    print(f"{key:34} {value}")
```

Output from running the block above:

```text
spark.app.id                       app-20260115101500-0004
spark.driver.maxResultSize         1m
spark.hadoop.fs.s3a.secret.key     *********(redacted)
spark.ssl.keyStorePassword         *********(redacted)
spark.executorEnv.API_TOKEN        *********(redacted)
```

Exports from the Environment tab or the REST endpoint often get pasted into tickets, and that is where credentials leak. The stand-in property list combines two harmless settings, the application ID and `spark.driver.maxResultSize=1m` that the chapter asks you to confirm, with three entries whose names signal secrets: an S3A secret key, a keystore password and an executor environment token. The pattern masks all three while leaving the evidence you actually need intact. Spark itself applies a similar rule through `spark.redaction.regex`, whose default matches names containing secret, password, token and a few others, and the replacement text shown mirrors what the UI prints. Name-based redaction has a gap, though: a credential embedded in a URI or a job argument has an innocent key and passes straight through, and the event log already holds the raw value. Treat this as a final scrub, not as permission to put secrets in Spark configuration.

## Diagnose and transfer

For SSH access to a trusted remote host, use a loopback-bound tunnel to the existing private UI, with the remote server and destination deliberately selected. Do not forward an unknown host or bypass a failed TLS/authentication check. A public shared UI needs a reviewed authenticating proxy, TLS, network restrictions and Spark's appropriate UI access controls. UI ACLs alone do not provide an authentication mechanism.

Redact sensitive application arguments before they enter configuration or logs. A proxy cannot remove secrets already persisted in event logs. Separate notebook authentication, Kubernetes API authorization, Spark RPC authentication and UI access: success in one does not imply the others are configured.

## Primary references

- [Spark UI and History Server](https://spark.apache.org/docs/4.0.1/monitoring.html)
- [Spark UI authentication and authorization](https://spark.apache.org/docs/4.0.1/security.html)
- [Kubernetes driver inspection](https://spark.apache.org/docs/4.0.1/running-on-kubernetes.html#accessing-driver-ui)
