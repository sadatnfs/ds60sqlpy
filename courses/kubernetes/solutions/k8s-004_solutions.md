# k8s-004: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A Kubernetes request has a caller identity, a target API server, a resource scope and an action. Authentication establishes who the caller is. Authorization decides whether that identity may perform the requested verb on the resource. A namespace is a scope for many objects, not a complete security boundary by itself. Cluster-scoped objects such as Nodes and namespaces require separate permissions.

The course uses a private lease for one disposable cluster and namespace. Its namespace name, UID, owner marker and expiry must agree with fresh readback. A familiar name or a selected terminal context is not enough. Names can be reused after deletion, and an ambient kubeconfig can point somewhere unrelated.

This lesson is a reading and explicitly targeted host-observation worksheet. The browser can run a fixed workload under its lease, but it does not accept arbitrary authorization commands or Role manifests. The supplied Role is a real namespaced API example for inspection; it does not grant the learner permission to create roles.

## Exercise 1: Identify the request tuple

The API authorizes a specific action against a resource scope. An object name without namespace and caller information is incomplete. The learner record should identify the private context by its nonsecret name while keeping credential contents private.

**Expected:** A six-field request includes apps/deployments, hello, get and the explicit leased namespace.

## Exercise 2: Read the Role grant

The Role contains one named read permission. It does not imply list or create rights, and namespace creation is cluster-scoped. Other bindings could add permissions, so this static inspection is a prediction to confirm with the actual owned identity.

**Expected:** Only get hello is granted by this Role; list and namespace creation are absent.

## Exercise 3: Check namespace identity

Deleting and recreating a namespace creates a new identity. Continuing with an old receipt could act on an unrelated replacement. The UID mismatch is therefore a decisive boundary, not a warning to ignore because the visible name looks familiar.

**Expected:** Refuse despite the matching namespace name and owner label.

## Exercise 4: Observe least privilege

The live observation establishes effective policy for that identity and time. It should include the requested verb/resource and nonsecret target. A denied action is a successful negative check when the curriculum intends the identity to lack that permission.

**Expected:** Actual allow/deny results are recorded separately from source policy; no credentials enter the worksheet.

## Exercise 5: Inspect expiry and cleanup reserve

The worker must retain enough credential lifetime to clean up after interruption. A lease that covers only nominal work can fail at the recovery boundary. The calculation is synthetic; a real run uses observed current time and the private receipt expiry.

**Expected:** Refuse because30<80.

## Exercise 6: Explain additive authorization

A complete access claim must account for the identity's other bindings and admission/runtime controls where relevant. The course avoids relying on a visual policy snippet alone and keeps the private session scoped and short-lived.

**Expected:** A written answer includes other RoleBindings/ClusterRoleBindings and actual effective authorization evidence.

## Boundary and troubleshooting review

Separate missing authentication, an expired lease, a wrong target UID and an authorization denial. They have different repairs. Retrying with an ambient administrator context would change the experiment and bypass the intended boundary. A successful own-namespace read does not prove cluster-wide permission, and a Role YAML file does not prove the server loaded that policy.

The offline checker models only the explicit permission matrix and receipt equality. It makes no API request. A live claim requires the actual owned identity, a fresh namespace readback and positive/negative authorization observations.
