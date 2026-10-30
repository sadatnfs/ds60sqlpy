# spark-deploy-009: Inspect a live Spark UI securely

Tutorial mode. Stage: intermediate. Direct prerequisites: `spark-deploy-007`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Inspect the application without publishing its control plane

Spark exposes several different UIs: the Standalone master, each worker, the live application driver and the History Server. The master describes cluster allocation. The driver describes one application's stages, tasks, executors and environment. A completed driver normally removes its live UI. The History Server reconstructs retained application history; it is not the running driver.

The workshop binds published HTTP ports to host loopback. It does not publish the Spark RPC port or worker UIs. This is appropriate for a trusted single-user machine, not authentication for a shared host. A person who can reach loopback in that host's context may still access it. Event details and configuration can reveal paths or sensitive application information.

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

## Diagnose and transfer

For SSH access to a trusted remote host, use a loopback-bound tunnel to the existing private UI, with the remote server and destination deliberately selected. Do not forward an unknown host or bypass a failed TLS/authentication check. A public shared UI needs a reviewed authenticating proxy, TLS, network restrictions and Spark's appropriate UI access controls. UI ACLs alone do not provide an authentication mechanism.

Redact sensitive application arguments before they enter configuration or logs. A proxy cannot remove secrets already persisted in event logs. Separate notebook authentication, Kubernetes API authorization, Spark RPC authentication and UI access: success in one does not imply the others are configured.

## Primary references

- [Spark UI and History Server](https://spark.apache.org/docs/4.0.1/monitoring.html)
- [Spark UI authentication and authorization](https://spark.apache.org/docs/4.0.1/security.html)
- [Kubernetes driver inspection](https://spark.apache.org/docs/4.0.1/running-on-kubernetes.html#accessing-driver-ui)
