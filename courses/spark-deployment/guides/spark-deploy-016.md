# spark-deploy-016: Constrain identities, secrets and network policy

Tutorial mode. Stage: advanced. Direct prerequisites: `spark-deploy-014`, `k8s-021`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Keep four authorization boundaries distinct

Notebook login authorizes a person to execute code in a kernel. Kubernetes API identity authorizes creation of Pods and related objects. Spark RPC authentication protects supported Spark process connections. Storage credentials authorize reading or writing data. None automatically configures the others.

The example access manifest grants the driver a namespaced Role for Pods, Services and ConfigMaps, plus Pod-log reads. It does not grant cluster-admin. The executor ServiceAccount disables automatic token mounting. Features such as driver-created PVCs need additional reviewed permissions and are deliberately outside that example role.

## Worked case A: inspect the intended permission boundary

After substituting the owned namespace into `kubernetes/access.yaml`, review the permissions with an identity authorized to perform that review:

```sh
kubectl --kubeconfig "$OWNED_KUBECONFIG" --context "$OWNED_CONTEXT" \
  --namespace "$OWNED_NAMESPACE" auth can-i create pods \
  --as "system:serviceaccount:$OWNED_NAMESPACE:spark-driver"
kubectl --kubeconfig "$OWNED_KUBECONFIG" --context "$OWNED_CONTEXT" \
  --namespace "$OWNED_NAMESPACE" auth can-i get secrets \
  --as "system:serviceaccount:$OWNED_NAMESPACE:spark-executor"
```

The intended answers are yes for the driver's required creation and no for executor secret reads. Impersonation itself may be forbidden to the inspecting user, so a failed `--as` review is not evidence of the ServiceAccount's effective permissions. Use an authorized access review or an actual bound identity rather than adding broad privileges just to make a diagnostic work.

## Worked case B: a policy that blocks the API as well as the internet

The supplied NetworkPolicy template permits labeled peers and a common DNS deployment only. It intentionally does not guess a cluster's API-server or object-storage egress addresses. Applying it unchanged to a driver may block executor creation even when RBAC is correct.

```text
DNS works -> API TCP times out -> inspect egress policy/routing
API returns 403 -> inspect authenticated identity and RBAC
API succeeds -> registry pull fails -> inspect node/registry identity separately
```

Tailor API, DNS and storage rules to the actual cluster and CNI, then test positive and negative traffic. A valid NetworkPolicy object proves no enforcement unless the cluster's network implementation applies it. Do not open broad egress permanently merely to avoid identifying a required destination.

## Diagnose and transfer

Mount needed secrets read-only into the precise process that uses them. Do not put tokens in spark-submit arguments, notebooks committed to source, Docker build layers or event-log-visible settings. A secret file path is configuration; its value is not a diagnostic to paste. Prefer workload identity when the selected environment supports it, with explicit provider-specific qualification.

For trusted local Compose, the internal network and loopback UIs constrain access but do not create a secure multi-tenant service. For a shared deployment, review supported Spark transport authentication/encryption, UI authentication and network segmentation together. Do not revive removed Kubernetes PodSecurityPolicy resources; use the cluster's current Pod Security and admission mechanisms.

## Primary references

- [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [NetworkPolicy behavior and enforcement](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Spark security boundaries](https://spark.apache.org/docs/4.0.1/security.html)
