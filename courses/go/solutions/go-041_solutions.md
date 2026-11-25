# go-041: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-041_solution.go` implements all six cases.

## Mechanism

client-go provides typed Kubernetes clients, discovery, watches, caches and work queues. It is a dependency project, not part of the Go standard library. Keep k8s.io/api, apimachinery and client-go on compatible release lines and review the documented compatibility matrix for the target cluster. Configuration carries authority: a kubeconfig can name a cluster, credentials and executable authentication plugins. Do not discover an ambient configuration for a teaching program that is supposed to use a disposable target. The ordinary pad below validates a deliberately constrained connection description and constructs a request without sending it. A separately prepared project fixture shows the actual typed client and explicit-context loading.

The prepared project uses clientcmd loading rules with one explicit kubeconfig path and a named context override, then kubernetes.NewForConfig. CoreV1().Pods(namespace).List(ctx, metav1.ListOptions{Limit:...}) invokes a typed resource client. Context and request timeout bound work; pagination must be handled rather than assuming one list is complete. The project is read-only and still requires exact disposable target identification, minimal RBAC and deliberate execution.

## 1. Accept explicit secure configuration: predict an edited check

Copy worked example 1, change `check(validateTarget("https://cluster.invalid:6443", "lesson", "owned-lesson") == nil, "target")` to `check(validateTarget("https://cluster.invalid:6443!", "lesson", "owned-lesson") == nil, "target")` inside its check and predict whether it still passes; then restore it.

The unchanged code is worked example 1:

```go
check(validateTarget("https://cluster.invalid:6443", "lesson", "owned-lesson") == nil, "target")
```

**Expected:** The edited check panics with `target` even though `validateTarget("https://cluster.invalid:6443", "lesson", "owned-lesson") == nil` still holds.

**Verify:** Restoring `check(validateTarget("https://cluster.invalid:6443", "lesson", "owned-lesson") == nil, "target")` makes the check pass again with the worked observation: the configuration is accepted.

The hostname is a nonresolving fixture and no request is sent. Real target ownership requires stronger runtime evidence than these syntax checks.

## 2. Reject insecure transport: diagnose an edited check

A careless edit rewrote the check in worked example 2 as `check(validateTarget("http://cluster.invalid", "lesson", "owned-lesson") == nil, "TLS")`. Explain the failure, then restore it.

The unchanged code is worked example 2:

```go
check(validateTarget("http://cluster.invalid", "lesson", "owned-lesson") != nil, "TLS")
```

**Expected:** The defective run panics with `TLS`; after restoring `check(validateTarget("http://cluster.invalid", "lesson", "owned-lesson") != nil, "TLS")`, the configuration is rejected.

**Verify:** The edited check fails with message `TLS` for a state that `validateTarget("http://cluster.invalid", "lesson", "owned-lesson") != nil` accepts.

TLS policy protects transport identity. Disabling certificate verification is not a reasonable response to a configuration error.

## 3. Reject ambient context selection

Omit the context name.

```go
check(validateTarget("https://cluster.invalid", "lesson", "") != nil, "explicit context")
```

**Expected:** Validation rejects the configuration.

**Verify:** Your solution must keep `validateTarget("https://cluster.invalid", "lesson", "") != nil` true. Control: changing `check(validateTarget("https://cluster.invalid", "lesson", "") != nil, "explicit context")` to `check(validateTarget("https://cluster.invalid", "lesson", "") == nil, "explicit context")` panics with message `explicit context`; revert it.

An explicit context prevents silently inheriting whichever cluster happens to be current in a developer configuration.

## 4. Constrain a namespace

Attempt a namespace containing a slash.

```go
check(validateTarget("https://cluster.invalid", "lesson/other", "owned") != nil, "namespace")
```

**Expected:** Validation rejects it.

**Verify:** Your solution must keep `validateTarget("https://cluster.invalid", "lesson/other", "owned") != nil` true. Control: changing `check(validateTarget("https://cluster.invalid", "lesson/other", "owned") != nil, "namespace")` to `check(validateTarget("https://cluster.invalid", "lesson/other", "owned") == nil, "namespace")` panics with message `namespace`; revert it.

This small validator is deliberately conservative. Real Kubernetes names have a documented grammar and should use the appropriate library validation.

## 5. Construct a bounded request

Build an HTTPS list request with a live context without sending it.

```go
req, err := http.NewRequestWithContext(context.Background(), "GET", "https://cluster.invalid/api/v1/namespaces/lesson/pods?limit=20", nil)
check(err == nil && req.Method == "GET" && req.URL.Path == "/api/v1/namespaces/lesson/pods", "request")
```

**Expected:** The method and URL path are correct.

**Verify:** Your solution must keep `err == nil && req.Method == "GET" && req.URL.Path == "/api/v1/namespaces/lesson/pods"` true. Control: changing `https://cluster.invalid/api/v1/namespaces/lesson/pods?limit=20` to `https://cluster.invalid/api/v2/namespaces/lesson/pods?limit=20` panics with message `request`; revert it.

Constructing a request proves neither authentication nor authorization nor API availability. It is useful local boundary evidence only.

## 6. Transfer userinfo rejection

Reject an endpoint embedding userinfo.

```go
target := url.URL{Scheme: "https", Host: "cluster.invalid", User: url.UserPassword("sample-user", "sample-value")}
check(validateTarget(target.String(), "lesson", "owned") != nil, "userinfo")
```

**Expected:** The embedded credential form is rejected.

**Verify:** Your solution must keep `validateTarget(target.String(), "lesson", "owned") != nil` true. Control: changing `check(validateTarget(target.String(), "lesson", "owned") != nil, "userinfo")` to `check(validateTarget(target.String(), "lesson", "owned") == nil, "userinfo")` panics with message `userinfo`; revert it.

Credentials should not be hidden in endpoint strings that might be logged. The real client handles credentials through an explicit reviewed configuration path.

## Transfer after comparison

Every later lesson that touches a cluster starts from configuration like this. In real tools, build the rest.Config from an explicitly named kubeconfig context, print the target before mutating anything and refuse to run when the context is unset. Apply the same discipline to cloud SDKs and database connection strings: authority should never come from an ambient default.
