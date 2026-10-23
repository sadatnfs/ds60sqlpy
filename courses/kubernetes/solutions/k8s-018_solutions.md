# k8s-018: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A ServiceAccount is a Kubernetes workload identity, not a human login name and not a secret value. A RoleBinding grants that identity a defined set of API actions in a scope. A token authenticates the identity; it does not by itself define what the identity is authorized to do.

The course worker uses a short-lived scoped credential held outside learner storage. Workload Pods have automatic service-account token mounting disabled because the synthetic application does not need Kubernetes API access. The worker's own permission to create a fixed workload is separate from any permission granted to the workload process.

This reading/host-observation lesson inspects a real Role and RoleBinding example and a positive/negative authorization matrix. The normal learner identity cannot create arbitrary RBAC objects, read Secrets or widen its own privileges. The manifest example illustrates the relationship; it is not a command to install a new grant through the browser.

## Exercise 1: Identify the ServiceAccount

A token proves possession of an identity credential under the server's validation rules. The RoleBindings determine what that identity may do. Recording the identity does not require exposing the token.

**Expected:** A nonsecret identity record is distinct from credential bytes and permissions.

## Exercise 2: Trace the binding scope

The fields are easy to confuse because both can contain namespace names. A live setup must use exact provisioned identities and verify effective behavior. The synthetic lesson-auth name is not an ambient target.

**Expected:** Subject identifies the ServiceAccount; binding scope determines the namespaced grant.

## Exercise 3: Predict allowed and denied requests

A narrow role does not grant adjacent actions by implication. The negative checks are part of the successful access-boundary demonstration, not errors to fix by adding wildcard permissions.

**Expected:** Only the intended own-namespace Pod reads are allowed; Secrets and privilege changes denied.

## Exercise 4: Protect workload credentials

The host worker needs scoped API access to manage the fixture. The application itself does not, so mounting a token would be unnecessary exposure. This control does not prove all possible credential paths are absent in arbitrary workloads.

**Expected:** The synthetic workload does not receive an automatic API token mount.

## Exercise 5: Rehearse expiry handling

The refusal preserves the identity and cleanup budget. An operational retry should not modify the runtime to ignore expiry. Keep release bounded to the recorded cluster/container/namespace identity and preserve learner source.

**Expected:** Guard refuses; exact owned session is released and a fresh session is prepared immediately before use.

## Exercise 6: Record live effective evidence

The live result supports the effective policy claim for that target and moment. It does not authorize future operations beyond the lease or prove that all admission/runtime checks will succeed.

**Expected:** Identity, target, verb/resource, result and time are recorded; token/kubeconfig contents are excluded.

## Boundary and troubleshooting review

A yes/no self-authorization result describes a requested action for an identity at a point in time. It does not prove that a later API request will pass every admission or object-state check. Conversely, a denied Secret read is expected in this lab and should not trigger a broader Role.

Use nonsecret request tuples and results in the worksheet. Do not impersonate a more privileged user, print tokens or copy a real Secret to demonstrate that access is absent. The offline matrix is a model of the intended policy, not a live control-plane response.
