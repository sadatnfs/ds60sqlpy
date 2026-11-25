# go-044: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-044_solution.go` implements all six cases.

## Mechanism

Authentication establishes who is calling; authorization determines which operations that identity may perform. A ServiceAccount gives an in-cluster workload an identity, and RBAC binds subjects to rules over API groups, resources, verbs and sometimes resource names. A Role applies within a namespace; a ClusterRole can describe cluster-scoped permissions or be bound within a namespace. A RoleBinding and ClusterRoleBinding have different scopes. Avoid wildcard grants when a controller only needs a few resource operations. Read access to Secrets is sensitive even though it does not mutate objects. Network reachability and RBAC are separate gates: an allowed identity can still have a broken network path.

Rules name API resource plurals such as pods, and subresources such as deployments/status. get, list and watch are different verbs. A controller updating status needs the appropriate subresource permission rather than unrestricted object replacement. The fixture checks an explicitly limited rule model; Kubernetes authorization has richer semantics and additive bindings. Validate actual access using the owned cluster and intended identity rather than a privileged developer context.

## 1. Admit a required read: change one input

Copy worked example 1, change `rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"get", "list", "watch"}}` to `rule := Rule{Namespace: "lesson!", Resource: "pods", Verbs: []string{"get", "list", "watch"}}` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"get", "list", "watch"}}
check(allowed(rule, "lesson", "pods", "get"), "read")
```

**Expected:** The edited run panics with `read` because `allowed(rule, "lesson", "pods", "get")` no longer holds.

**Verify:** Restoring `rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"get", "list", "watch"}}` makes the check pass again with the worked observation: the request is admitted by the local rule model.

The rule expresses resource and namespace scope in addition to the verb. Matching only one component would overgrant access.

## 2. Reject an unneeded mutation: diagnose an edited check

A careless edit rewrote the check in worked example 2 as `check(allowed(rule, "lesson", "pods", "delete"), "mutation")`. Explain the failure, then restore it.

The unchanged code is worked example 2:

```go
rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"get"}}
check(!allowed(rule, "lesson", "pods", "delete"), "mutation")
```

**Expected:** The defective run panics with `mutation`; after restoring `check(!allowed(rule, "lesson", "pods", "delete"), "mutation")`, the request is rejected.

**Verify:** The edited check fails with message `mutation` for a state that `!allowed(rule, "lesson", "pods", "delete")` accepts.

A read-oriented controller should not inherit deletion authority merely for convenience.

## 3. Reject cross-namespace access

Use the lesson rule against another namespace.

```go
rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"get"}}
check(!allowed(rule, "other", "pods", "get"), "namespace")
```

**Expected:** The local model rejects it.

**Verify:** Your solution must keep `!allowed(rule, "other", "pods", "get")` true. Control: changing `check(!allowed(rule, "other", "pods", "get"), "namespace")` to `check(allowed(rule, "other", "pods", "get"), "namespace")` panics with message `namespace`; revert it.

Namespace boundaries should be explicit. A ClusterRoleBinding can widen scope and therefore deserves separate review.

## 4. Separate resource and subresource

Grant update on deployments/status but request update on deployments.

```go
rule := Rule{Namespace: "lesson", Resource: "deployments/status", Verbs: []string{"update"}}
check(allowed(rule, "lesson", "deployments/status", "update") && !allowed(rule, "lesson", "deployments", "update"), "subresource")
```

**Expected:** The whole-object update is rejected.

**Verify:** Your solution must keep `allowed(rule, "lesson", "deployments/status", "update") && !allowed(rule, "lesson", "deployments", "update")` true. Control: changing `rule := Rule{Namespace: "lesson", Resource: "deployments/status", Verbs: []string{"update"}}` to `rule := Rule{Namespace: "lesson!", Resource: "deployments/status", Verbs: []string{"update"}}` panics with message `subresource`; revert it.

Status reporting and desired-state mutation are different authorities. The controller should request only what its design needs.

## 5. Treat secret reads as authority

Check a pods-only rule against secrets.

```go
rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"get"}}
check(!allowed(rule, "lesson", "secrets", "get"), "secret boundary")
```

**Expected:** Secret read access is rejected.

**Verify:** Your solution must keep `!allowed(rule, "lesson", "secrets", "get")` true. Control: changing `check(!allowed(rule, "lesson", "secrets", "get"), "secret boundary")` to `check(allowed(rule, "lesson", "secrets", "get"), "secret boundary")` panics with message `secret boundary`; revert it.

Read-only does not mean harmless. Confidential configuration can be exposed without any mutation.

## 6. Transfer verb distinction

Grant list but not watch and inspect both.

```go
rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"list"}}
check(allowed(rule, "lesson", "pods", "list") && !allowed(rule, "lesson", "pods", "watch"), "verbs")
```

**Expected:** Only list is admitted.

**Verify:** Your solution must keep `allowed(rule, "lesson", "pods", "list") && !allowed(rule, "lesson", "pods", "watch")` true. Control: changing `rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"list"}}` to `rule := Rule{Namespace: "lesson!", Resource: "pods", Verbs: []string{"list"}}` panics with message `verbs`; revert it.

A list request and a long-lived watch have separate permission checks. Controller installation documentation should name both when needed.

## Transfer after comparison

When a client-go call returns forbidden, read the error: it names the user, verb, resource and namespace, which maps directly onto a missing rule. Use kubectl auth can-i with --as to test a ServiceAccount before deploying. Review RBAC in the same pull request as the code that needs it, so authority grows only with a stated reason.
