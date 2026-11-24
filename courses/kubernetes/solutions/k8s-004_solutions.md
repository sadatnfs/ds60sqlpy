# k8s-004: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A Kubernetes request has a caller identity, a target API server, a resource scope and an action. Authentication establishes who the caller is. Authorization decides whether that identity may perform the requested verb on the resource. A namespace is a scope for many objects, not a complete security boundary by itself. Cluster-scoped objects such as Nodes and namespaces require separate permissions.

The course uses a private lease for one disposable cluster and namespace. Its namespace name, UID, owner marker and expiry must agree with fresh readback. A familiar name or a selected terminal context is not enough. Names can be reused after deletion, and an ambient kubeconfig can point somewhere unrelated.

This lesson is a reading and explicitly targeted host-observation worksheet. The browser can run a fixed workload under its lease, but it does not accept arbitrary authorization commands or Role manifests. The supplied Role is a real namespaced API example for inspection; it does not grant the learner permission to create roles.

## Exercise 1: Identify the request tuple

The API authorizes a specific action against a resource scope. An object name without namespace and caller information is incomplete. The learner record should identify the private context by its nonsecret name while keeping credential contents private.

**Expected:** A six-field request includes apps/deployments, hello, get and the explicit leased namespace.

**Solution reasoning**

- **Approach:** Split the read into who asks, which server and namespace, which API group and resource, which object name and which verb.
- **Why it is correct:** Authorization in this lesson is evaluated per request tuple, so `get` on `deployments.apps/hello` in the leased namespace is a different question from the same verb in another namespace.
- **Plausible wrong approach:** Writing only `hello` and `get` omits the caller and namespace, so the record could describe a read against an ambient context the lease never authorized.
- **How to verify:** The tuple must translate field by field into one `kubectl auth can-i get deployments.apps/hello` command with explicit kubeconfig, context and namespace flags.

## Exercise 2: Read the Role grant

The Role contains one named read permission. It does not imply list or create rights, and namespace creation is cluster-scoped. Other bindings could add permissions, so this static inspection is a prediction to confirm with the actual owned identity.

**Expected:** Only get hello is granted by this Role; list and namespace creation are absent.

**Solution reasoning**

- **Approach:** Match each of the three requests against the Role rules, requiring verb, resource and resourceNames to agree within a single rule.
- **Why it is correct:** The example Role names `hello` under `resourceNames` with only `get`, so a list of all Deployments has no matching rule, and Namespaces are cluster-scoped and cannot be granted by a namespaced Role at all.
- **Plausible wrong approach:** Assuming `get` on one Deployment implies `list` treats verbs as a hierarchy, but RBAC verbs are independent strings and list returns every object, including ones the name restriction excludes.
- **How to verify:** Exactly one of the three requests (get hello) should have a fully matching rule; the other two should have none.

## Exercise 3: Check namespace identity

Deleting and recreating a namespace creates a new identity. Continuing with an old receipt could act on an unrelated replacement. The UID mismatch is therefore a decisive boundary, not a warning to ignore because the visible name looks familiar.

**Expected:** Refuse despite the matching namespace name and owner label.

**Solution reasoning**

- **Approach:** Compare `metadata.uid` from the ns-1 receipt with the uid in the ns-2 readback before looking at any other field.
- **Why it is correct:** A namespace UID is assigned by the API server at creation, so a deleted and recreated namespace keeps its name and labels but receives a new UID.
- **Plausible wrong approach:** Accepting the readback because the name and owner label both match would let a stale receipt act on a replacement namespace that another process may now own.
- **How to verify:** The two UIDs differ, so the decision is refuse; changing the label or name in your notes must not flip that answer.

## Exercise 4: Observe least privilege

The live observation establishes effective policy for that identity and time. It should include the requested verb/resource and nonsecret target. A denied action is a successful negative check when the curriculum intends the identity to lack that permission.

**Expected:** Actual allow/deny results are recorded separately from source policy; no credentials enter the worksheet.

**Solution reasoning**

- **Approach:** Ask the server about one permitted own-namespace action and one action the identity should lack, such as listing Secrets or reading Nodes, under the explicit lease.
- **Why it is correct:** Only the server's answer for this identity at this time reflects every binding that applies, which the single Role file cannot show.
- **Plausible wrong approach:** Recording the Role YAML as the result skips the observation, and pasting the kubeconfig to prove the identity would leak the credential the exercise is meant to protect.
- **How to verify:** Each row names verb, resource and namespace with the server's yes or no, and a text search of the record finds no token or certificate data.

## Exercise 5: Bind a ClusterRole inside one namespace

Binding a ClusterRole with a RoleBinding reuses the role's rules without widening their scope: the grant applies only in the RoleBinding's namespace. Only a ClusterRoleBinding grants the rules across all namespaces. The default view ClusterRole allows reading most namespaced objects but deliberately omits Secrets, because Secret contents can include ServiceAccount credentials that would let a reader escalate. Confirm the effective answer with `kubectl auth can-i` under the owned receipt instead of reasoning only from the YAML.

**Expected:** Pods in lesson-a: allowed. Pods in lesson-b: denied, because a RoleBinding grants only inside its own namespace. Secrets in lesson-a: denied, because the default view role excludes Secrets.

**Solution reasoning**

- **Approach:** Resolve the binding's scope first (namespace lesson-a), then check each requested resource against the rules of the `view` ClusterRole.
- **Why it is correct:** A RoleBinding confines whatever role it references to its own namespace, and the built-in `view` role lists Pods but omits Secrets.
- **Plausible wrong approach:** Reading `ClusterRole` in the roleRef as cluster-wide access would wrongly allow Pods in lesson-b; that scope only comes from a ClusterRoleBinding.
- **How to verify:** Expect allowed, denied, denied for Pods in lesson-a, Pods in lesson-b and Secrets in lesson-a, matching `kubectl auth can-i` with `--as` and explicit `--namespace`.

## Exercise 6: Explain additive authorization

A complete access claim must account for the identity's other bindings and admission/runtime controls where relevant. The course avoids relying on a visual policy snippet alone and keeps the private session scoped and short-lived.

**Expected:** A written answer includes other RoleBindings/ClusterRoleBindings and actual effective authorization evidence.

**Solution reasoning**

- **Approach:** Treat the Role as one input to a union of all bindings that reference the identity, its groups and any ServiceAccount it uses.
- **Why it is correct:** Kubernetes RBAC is purely additive with no deny rules, so another RoleBinding or a ClusterRoleBinding to a group can add permissions this file never mentions.
- **Plausible wrong approach:** Concluding least privilege from the narrow Role alone ignores group bindings such as a ClusterRoleBinding for `system:authenticated`, which could grant far more.
- **How to verify:** Name at least one binding outside the file that could widen access and cite `kubectl auth can-i --list` in the leased namespace as the effective set.

## Boundary and troubleshooting review

Separate missing authentication, an expired lease, a wrong target UID and an authorization denial. They have different repairs. Retrying with an ambient administrator context would change the experiment and bypass the intended boundary. A successful own-namespace read does not prove cluster-wide permission, and a Role YAML file does not prove the server loaded that policy.

The offline checker models only the explicit permission matrix and receipt equality. It makes no API request. A live claim requires the actual owned identity, a fresh namespace readback and positive/negative authorization observations.
