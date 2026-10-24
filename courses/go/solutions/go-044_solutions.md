# go-044: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

Authentication establishes who is calling; authorization determines which operations that identity may perform. A ServiceAccount gives an in-cluster workload an identity, and RBAC binds subjects to rules over API groups, resources, verbs and sometimes resource names. A Role applies within a namespace; a ClusterRole can describe cluster-scoped permissions or be bound within a namespace. A RoleBinding and ClusterRoleBinding have different scopes. Avoid wildcard grants when a controller only needs a few resource operations. Read access to Secrets is sensitive even though it does not mutate objects. Network reachability and RBAC are separate gates: an allowed identity can still have a broken network path.

Rules name API resource plurals such as pods, and subresources such as deployments/status. get, list and watch are different verbs. A controller updating status needs the appropriate subresource permission rather than unrestricted object replacement. The fixture checks an explicitly limited rule model; Kubernetes authorization has richer semantics and additive bindings. Validate actual access using the owned cluster and intended identity rather than a privileged developer context.

## 1. Admit a required read

Allow get on pods in the lesson namespace.

```go
rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"get", "list", "watch"}}
check(allowed(rule, "lesson", "pods", "get"), "read")
```

**Expected:** The request is admitted by the local rule model.

The rule expresses resource and namespace scope in addition to the verb. Matching only one component would overgrant access.

## 2. Reject an unneeded mutation

Try delete against the read-only rule.

```go
rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"get"}}
check(!allowed(rule, "lesson", "pods", "delete"), "mutation")
```

**Expected:** The request is rejected.

A read-oriented controller should not inherit deletion authority merely for convenience.

## 3. Reject cross-namespace access

Use the lesson rule against another namespace.

```go
rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"get"}}
check(!allowed(rule, "other", "pods", "get"), "namespace")
```

**Expected:** The local model rejects it.

Namespace boundaries should be explicit. A ClusterRoleBinding can widen scope and therefore deserves separate review.

## 4. Separate resource and subresource

Grant update on deployments/status but request update on deployments.

```go
rule := Rule{Namespace: "lesson", Resource: "deployments/status", Verbs: []string{"update"}}
check(allowed(rule, "lesson", "deployments/status", "update") && !allowed(rule, "lesson", "deployments", "update"), "subresource")
```

**Expected:** The whole-object update is rejected.

Status reporting and desired-state mutation are different authorities. The controller should request only what its design needs.

## 5. Treat secret reads as authority

Check a pods-only rule against secrets.

```go
rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"get"}}
check(!allowed(rule, "lesson", "secrets", "get"), "secret boundary")
```

**Expected:** Secret read access is rejected.

Read-only does not mean harmless. Confidential configuration can be exposed without any mutation.

## 6. Transfer verb distinction

Grant list but not watch and inspect both.

```go
rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"list"}}
check(allowed(rule, "lesson", "pods", "list") && !allowed(rule, "lesson", "pods", "watch"), "verbs")
```

**Expected:** Only list is admitted.

A list request and a long-lived watch have separate permission checks. Controller installation documentation should name both when needed.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
