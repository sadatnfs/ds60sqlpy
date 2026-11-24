# spark-deploy-016: Constrain identities, secrets and network policy

Tutorial mode. Stage: advanced. Direct prerequisites: `spark-deploy-014`, `k8s-021`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Keep four authorization boundaries distinct

Notebook login authorizes a person to execute code in a kernel. Kubernetes API identity authorizes creation of Pods and related objects. Spark RPC authentication protects supported Spark process connections. Storage credentials authorize reading or writing data. None automatically configures the others.

The example access manifest grants the driver a namespaced Role for executor Pods and their ConfigMap, plus Pod-log reads. It grants no Services, because in cluster mode the submitting identity creates the driver Service. It does not grant cluster-admin. The executor ServiceAccount disables automatic token mounting. Features such as driver-created PVCs need additional reviewed permissions and are deliberately outside that example role.

## Key terms

- **RBAC Role:** A namespaced Kubernetes permission set, here for executor Pods, their ConfigMap and Pod-log reads, with no Service or cluster-admin grant.
- **ServiceAccount:** The Kubernetes identity a Pod uses for API requests; the executor account disables automatic token mounting.
- **Spark RPC authentication:** Protection for supported connections between Spark processes, separate from notebook login and API identity.
- **Storage credential:** An authorization to read or write data that none of the other three boundaries configures.
- **NetworkPolicy:** A Kubernetes rule that restricts Pod traffic; it takes effect only when the cluster's network implementation enforces it.

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

The template allows traffic between pods carrying the workshop label and DNS
lookups to `kube-dns`, and nothing else:

From [`projects/cluster-lab/kubernetes/network-policy.yaml`](../projects/cluster-lab/kubernetes/network-policy.yaml):

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: spark-namespace-boundary
  namespace: NAMESPACE
spec:
  podSelector:
    matchLabels:
      ds60-workshop: spark-deployment
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        - podSelector:
            matchLabels:
              ds60-workshop: spark-deployment
  egress:
    - to:
        - podSelector:
            matchLabels:
              ds60-workshop: spark-deployment
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

Because `policyTypes` lists `Egress` and no rule names the API server, a driver
under this policy cannot ask the API server to create executor pods.

```text
DNS works -> API TCP times out -> inspect egress policy/routing
API returns 403 -> inspect authenticated identity and RBAC
API succeeds -> registry pull fails -> inspect node/registry identity separately
```

Tailor API, DNS and storage rules to the actual cluster and CNI, then test positive and negative traffic. A valid NetworkPolicy object proves no enforcement unless the cluster's network implementation applies it. Do not open broad egress permanently merely to avoid identifying a required destination.

## Worked example: evaluating the example Role offline

```python
role_rules = [
    {"resources": {"pods"}, "verbs": {"create", "get", "list", "watch", "delete"}},
    {"resources": {"configmaps"}, "verbs": {"create", "get", "list", "delete"}},
    {"resources": {"pods/log"}, "verbs": {"get"}},
]
bindings = {"spark-driver": role_rules, "spark-executor": []}
questions = [
    ("spark-driver", "create", "pods"),
    ("spark-driver", "get", "pods/log"),
    ("spark-driver", "create", "persistentvolumeclaims"),
    ("spark-driver", "get", "secrets"),
    ("spark-executor", "get", "secrets"),
    ("spark-executor", "list", "pods"),
]
for account, verb, resource in questions:
    allowed = any(resource in r["resources"] and verb in r["verbs"] for r in bindings[account])
    print(f"{account:15} {verb:7} {resource:23} {'yes' if allowed else 'no'}")
```

Output from running the block above:

```text
spark-driver    create  pods                    yes
spark-driver    get     pods/log                yes
spark-driver    create  persistentvolumeclaims  no
spark-driver    get     secrets                 no
spark-executor  get     secrets                 no
spark-executor  list    pods                    no
```

The rules are copied from the Role in `access.yaml`, and the evaluator answers the same questions as `kubectl auth can-i` without needing a cluster or impersonation rights. The driver can create pods and read pod logs, which covers executor creation and diagnosis. It cannot create PersistentVolumeClaims, so a configuration that asks Spark to provision on-demand volumes would fail with Forbidden until a reviewed rule is added. Neither account can read Secrets, and the executor account has no binding at all, matching its disabled token mount. This model is intentionally narrow: it ignores ClusterRoles, aggregated roles, wildcards and resource names, any of which a real cluster may add through other bindings, so a no here does not prove the live answer is no. Use it to review a change to the manifest before applying it, then confirm the effective permissions with an authorized access review on the owned namespace as the chapter describes.

## Worked example: an explicit egress rule for the API server

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: spark-driver-api-egress
  namespace: NAMESPACE
spec:
  podSelector:
    matchLabels:
      ds60-workshop: spark-deployment
      spark-role: driver
  policyTypes: [Egress]
  egress:
    - to:
        - ipBlock:
            cidr: OBSERVED_API_SERVER_IP/32
      ports:
        - protocol: TCP
          port: 443
```

This additive policy is the piece Worked case B says the template leaves out on purpose. Kubernetes NetworkPolicies are unioned, so applying it alongside `spark-namespace-boundary` lets pods labeled as the Spark driver open TCP connections to one API server address while every other egress rule stays as strict as before. The `spark-role: driver` label is set by Spark on driver pods, and executors do not receive this rule because they never call the API. `OBSERVED_API_SERVER_IP` must be the address the driver actually reaches, which on many managed clusters is the `kubernetes` Service endpoint in the default namespace and may not be what the kubeconfig URL shows; port 443 may also need to be 6443 depending on that endpoint. Nothing is printed because enforcement depends on the cluster's CNI. Test both directions: executor creation should now succeed, and a connection from the same pod to an unrelated external address should still time out.

## Diagnose and transfer

Mount needed secrets read-only into the precise process that uses them. Do not put tokens in spark-submit arguments, notebooks committed to source, Docker build layers or event-log-visible settings. A secret file path is configuration; its value is not a diagnostic to paste. Prefer workload identity when the selected environment supports it, with explicit provider-specific qualification.

For trusted local Compose, the internal network and loopback UIs constrain access but do not create a secure multi-tenant service. For a shared deployment, review supported Spark transport authentication/encryption, UI authentication and network segmentation together. Do not revive removed Kubernetes PodSecurityPolicy resources; use the cluster's current Pod Security and admission mechanisms.

## Primary references

- [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [NetworkPolicy behavior and enforcement](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Spark security boundaries](https://spark.apache.org/docs/4.0.1/security.html)
